
HFTOKEN=$1

# Остановка и удлаение
docker stop codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
docker rm codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
tmux kill-session -t codeassist
tmux kill-session -t control_api
pkill -f "cloudflared-linux-amd64 tunnel"
pkill -f "python3 fastapi_clf.py"
rm -rf codeassist

# Усатновка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Копирование репы codeassist
git clone https://github.com/gensyn-ai/codeassist
cd codeassist

# Установка вспомогоательных скриптов и инструементов
wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/tmux_controller_api.py
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/fastapi_clf.py

chmod +x cloudflared-linux-amd64
apt install python3-pip -y
python3 -m pip install uvicorn flask fastapi


# Запуск тунела и апи для пересылки на тунел по ip port
nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:3000 > "/root/codeassist/cloudflared.log" 2>&1 &
nohup python3 fastapi_clf.py  > "/root/codeassist/fastapi_cloudflared.log" 2>&1 &

# Запуск codeassist и api для управления
tmux new-session -d -s codeassist "source ~/.bashrc && export HF_TOKEN='$HFTOKEN' && uv run run.py; bash"
tmux new-session -d -s control_api 'python3 tmux_controller_api.py; bash'
