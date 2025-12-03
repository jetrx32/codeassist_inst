ARCH=$(uname -m)
apt install ufw -y && \
ufw default allow incoming && \
echo "y" | ufw enable && \
ufw allow 22 && \
ufw allow 80 && \
ufw allow 443 && \
ufw deny out from any to 0.0.0.0/8 && \
ufw deny out from any to 10.0.0.0/8 && \
ufw deny out from any to 100.64.0.0/10 && \
ufw deny out from any to 100.79.0.0/16 && \
ufw deny out from any to 100.113.0.0/16 && \
ufw deny out from any to 169.254.0.0/16 && \
ufw deny out from any to 172.0.0.0/8 && \
ufw deny out from any to 172.16.0.0/12 && \
ufw deny out from any to 192.0.0.0/24 && \
ufw deny out from any to 192.0.2.0/24 && \
ufw deny out from any to 192.88.99.0/24 && \
ufw deny out from any to 192.168.0.0/16 && \
ufw deny out from any to 198.18.0.0/15 && \
ufw deny out from any to 198.51.100.0/24 && \
ufw deny out from any to 203.0.113.0/24 && \
ufw deny out from any to 224.0.0.0/4 && \
ufw deny out from any to 240.0.0.0/4 && \
ufw status



sudo sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin without-password/' /etc/ssh/sshd_config && \
sudo systemctl restart sshd && \
apt update && apt upgrade -y && apt install ca-certificates curl gnupg2 lsb-release htop ncdu wget git mc jq apparmor libpq-dev -y && \
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
apt update && apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y && \
sudo systemctl start docker && \
sudo systemctl enable docker

mkdir -p /root/cloudflared
if [ "$ARCH" = "x86_64" ]; then
    wget -O /root/cloudflared/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
fi

if [ "$ARCH" = "aarch64" ]; then
    wget -O /root/cloudflared/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm
fi
chmod +x /root/cloudflared/cloudflared
/root/cloudflared/cloudflared --help
