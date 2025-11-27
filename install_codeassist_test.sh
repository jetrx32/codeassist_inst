
HFTOKEN=$1

git clone https://github.com/gensyn-ai/codeassist
cd codeassist

wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/tmux_controller_api.py
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/fastapi_clf.py

chmod +x cloudflared-linux-amd64
apt install python3-pip -y
python3 -m pip install uvicorn flask fastapi

nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:3000 > "/root/codeassist/cloudflared.log" 2>&1 &
nohup python3 fastapi_clf.py  > "/root/codeassist/fastapi_cloudflared.log" 2>&1 &


tmux new-session -d -s codeassist "export HF_TOKEN='$HFTOKEN' && uv run run.py; bash"
tmux new-session -d -s control_api 'python3 tmux_controller_api.py; bash'
