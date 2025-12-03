
HFTOKEN=$1

# Остановка и удлаение
docker stop codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
docker rm codeassist-zero-style-ui codeassist-solution-tester codeassist-state-service codeassist-web-ui codeassist-policy-model codeassist-ollama
docker network rm codeassist_network
tmux kill-session -t codeassist
tmux kill-session -t control_api
pkill -f "cloudflared-linux-amd64 tunnel"
pkill -f "python3 fastapi_clf.py"
rm -rf codeassist

# Усатновка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Копирование репы codeassist
git clone https://github.com/jetrx32/codeassist
cd codeassist
docker network create --subnet=32.32.0.0/16 --gateway=32.32.0.1 codeassist_network
cd web-ui
 docker build \
  --build-arg NEXT_PUBLIC_TESTER_URL="/api/tester" \
  --build-arg NEXT_PUBLIC_STATE_SERVICE_URL="/api/backend" \
  --build-arg NEXT_PUBLIC_POLICY_MODELS_URL="/api/policy" \
  --build-arg NEXT_PUBLIC_ALCHEMY_API_KEY="wvs3CE89g2JwoshNNCMe1" \
  --build-arg NEXT_PUBLIC_SIMULATION_MODE="false" \
  --build-arg NEXT_PUBLIC_ZERO_STYLE_MODE="false" \
  -t gensynai/codeassist-web-ui:main .
cd ..
# Установка вспомогоательных скриптов и инструементов
wget -O tmux_controller_api.py https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/tmux_newcontroller.py
wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/fastapi_clf.py

apt install python3-pip -y
python3 -m pip install uvicorn flask fastapi psutil


# Запуск тунела и апи для пересылки на тунел по ip port
nohup /root/cloudflared/cloudflared tunnel --url http://localhost:4004 > "/root/codeassist/cloudflared.log" 2>&1 &
nohup python3 fastapi_clf.py  > "/root/codeassist/fastapi_cloudflared.log" 2>&1 &

# Запуск codeassist и api для управления
tmux new-session -d -s codeassist "export HF_TOKEN='$HFTOKEN' && /root/.local/bin/uv run run.py -p 4004; bash"
tmux new-session -d -s control_api 'python3 tmux_controller_api.py; bash'
