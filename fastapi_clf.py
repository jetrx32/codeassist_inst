import re
import time
import threading
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

LOG_FILE = '/root/codeassist/cloudflared.log'
app = FastAPI()

cloudflared_url = None
url_lock = threading.Lock()

def find_last_url_in_file(log_file):
    """Сканирует весь лог и возвращает последнюю найденную Cloudflared-ссылку"""
    last_url = None
    pattern = re.compile(r'https://[a-z0-9\-]+\.trycloudflare\.com')
    with open(log_file, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                last_url = match.group(0)
    return last_url

def tail_log_and_update_url(log_file):
    """Следит за логом и обновляет URL при появлении новых"""
    global cloudflared_url
    pattern = re.compile(r'https://[a-z0-9\-]+\.trycloudflare\.com')

    # Переход в конец лога
    with open(log_file, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            match = pattern.search(line)
            if match:
                new_url = match.group(0)
                with url_lock:
                    if new_url != cloudflared_url:
                        cloudflared_url = new_url
                        print(f"[INFO] Обновлён URL туннеля: {cloudflared_url}")

@app.get("/{path:path}")
def redirect(path: str = ""):
    with url_lock:
        url = cloudflared_url
    if url:
        return RedirectResponse(url=f"{url}/{path}" if path else url)
    return {"error": "Cloudflared URL ещё не найден"}

if __name__ == "__main__":
    # Сначала читаем весь лог и инициализируем ссылку, если она уже есть
    last_url = find_last_url_in_file(LOG_FILE)
    if last_url:
        with url_lock:
            cloudflared_url = last_url
        print(f"[INIT] Найден существующий Cloudflared URL: {cloudflared_url}")

    # Запускаем фоновую слежку за логами
    thread = threading.Thread(target=tail_log_and_update_url, args=(LOG_FILE,), daemon=True)
    thread.start()

    print("✅ Сервер запущен: http://0.0.0.0:22535")
    uvicorn.run(app, host="0.0.0.0", port=22535)
