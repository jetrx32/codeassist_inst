import subprocess
import signal
import sys
from flask import Flask, request, jsonify
import time
import os
import psutil

app = Flask(__name__)

class TmuxController:
    def __init__(self, session_name="codeassist"):
        self.session_name = session_name
    
    def session_exists(self):
        try:
            cmd = f"tmux has-session -t {self.session_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Ошибка проверки сессии: {e}")
            return False
    
    def get_last_pane_line(self):
        """Получает последнюю строку из активной панели tmux сессии"""
        try:
            if not self.session_exists():
                return None
            
            # Получаем содержимое панели (последние 50 строк)
            cmd = f"tmux capture-pane -t {self.session_name} -p -S -50"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    # Возвращаем последнюю непустую строку
                    for line in reversed(lines):
                        if line.strip():
                            return line.strip()
            return None
        except Exception as e:
            print(f"Ошибка получения последней строки: {e}")
            return None
    
    def send_ctrl_c(self):
        try:
            if not self.session_exists():
                return {"success": False, "message": f"Сессия {self.session_name} не найдена"}
            
            # Отправляем Ctrl+C
            cmd = f"tmux send-keys -t {self.session_name} C-c"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "message": "Ctrl+C отправлен в сессию"}
            else:
                return {"success": False, "message": f"Ошибка отправки: {result.stderr}"}
                
        except Exception as e:
            return {"success": False, "message": f"Исключение: {str(e)}"}
    
    def start_session(self):
        try:
            if self.session_exists():
                cmd = f"tmux send-keys -t {self.session_name} 'uv run run.py' Enter"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {"success": True, "message": "Команда запущена в существующей сессии"}
                else:
                    return {"success": False, "message": f"Ошибка запуска: {result.stderr}"}
            else:
                cmd = f"tmux new-session -d -s {self.session_name} 'uv run run.py'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {"success": True, "message": "Новая сессия создана и команда запущена"}
                else:
                    return {"success": False, "message": f"Ошибка создания сессии: {result.stderr}"}
                    
        except Exception as e:
            return {"success": False, "message": f"Исключение: {str(e)}"}
    
    def is_model_training_running(self):
        """Проверяет, запущен ли процесс обучения модели"""
        try:
            # Ищем процессы python3 с аргументом policy_models.cli.run_tasks train_from_episodes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if (len(cmdline) >= 2 and 
                        'python3' in cmdline[0] and 
                        'policy_models.cli.run_tasks' in cmdline and
                        'train_from_episodes' in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            print(f"Ошибка при проверке процессов: {e}")
            return False
    
    def get_session_status(self):
        try:
            # Сначала проверяем запущен ли процесс обучения модели
            if self.is_model_training_running():
                return {"status": "model_training", "message": "Процесс обучения модели запущен"}
            
            # Если обучение не запущено, проверяем статус tmux сессии
            if not self.session_exists():
                return {"status": "not_exists", "message": "Сессия не существует"}
            
            # Проверяем активность сессии
            cmd = f"tmux list-panes -t {self.session_name} -F '#{{pane_active}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"status": "active", "message": "Сессия активна"}
            else:
                return {"status": "exists", "message": "Сессия существует но не активна"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

tmux = TmuxController("codeassist")

def signal_handler(signum, frame):
    print("\nПолучен сигнал Ctrl+C, завершаем работу API сервера...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@app.route('/stop', methods=['POST'])
def stop_session():
    try:
        result = tmux.send_ctrl_c()
        if result["success"]:
            return jsonify({"status": "success", "message": result["message"]})
        else:
            return jsonify({"status": "error", "message": result["message"]}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/start', methods=['POST'])
def start_session():
    try:
        result = tmux.start_session()
        if result["success"]:
            return jsonify({"status": "success", "message": result["message"]})
        else:
            return jsonify({"status": "error", "message": result["message"]}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/restart', methods=['POST'])
def restart_session():
    try:
        stop_result = tmux.send_ctrl_c()
        
        time.sleep(120)
        
        start_result = tmux.start_session()
        
        return jsonify({
            "status": "success", 
            "message": f"Перезапуск выполнен: {stop_result['message']}, затем {start_result['message']}"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    try:
        status = tmux.get_session_status()
        return jsonify({"status": "success", "data": status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/installstatus', methods=['GET'])
def get_install_status():
    """Проверяет статус установки по последней строке в tmux сессии"""
    try:
        last_line = tmux.get_last_pane_line()
        
        if last_line is None:
            return jsonify({
                "status": "success",
                "install_complete": False,
                "message": "Не удалось получить информацию из сессии или сессия не существует",
                "last_line": ""
            })
        
        # Проверяем, содержит ли последняя строка нужное сообщение
        install_complete = "Running... Press Ctrl+C trigger training" in last_line
        
        return jsonify({
            "status": "success",
            "install_complete": install_complete,
            "message": "Установка завершена" if install_complete else "Установка в процессе",
            "last_line": last_line
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "tmux-controller-api"})

if __name__ == '__main__':
    print("=" * 50)
    print("TMUX Controller API Server")
    print("Сессия: codeassist")
    print("Команда: uv run run.py")
    print("=" * 50)
    print("Доступные endpoints:")
    print("POST /start         - Запустить приложение")
    print("POST /stop          - Остановить приложение (Ctrl+C)")
    print("POST /restart       - Перезапустить приложение")
    print("GET  /status        - Статус сессии")
    print("GET  /installstatus - Статус установки (по последней строке)")
    print("GET  /health        - Health check")
    print("=" * 50)
    
    try:
        check_cmd = "tmux -V"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("ВНИМАНИЕ: tmux не установлен или недоступен!")
        else:
            print(f"Tmux доступен: {result.stdout.strip()}")
    except Exception as e:
        print(f"Ошибка проверки tmux: {e}")
    
    app.run(host='0.0.0.0', port=58963, debug=False)
