
HFTOKEN=$1

git clone https://github.com/gensyn-ai/codeassist
cd codeassist
wget https://raw.githubusercontent.com/jetrx32/codeassist_inst/refs/heads/main/tmux_controller_api.py

apt install python3-pip -y
tmux new-session -d -s codeassist 'export HF_TOKEN=$HFTOKEN && uv run run.py'
tmux new-session -d -s codeassist 'python3 tmux_controller_api.py'
