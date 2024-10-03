#!/bin/bash -i
apt update
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install stable && npm install -g pm2 yarn
mkdir installs
cd installs
wget https://go.dev/dl/go1.23.2.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin >> ~/.bashrc
cat <<'EOF' >>~/.bashrc

# set PATH so it includes GOPATH/bin if it exists
if [ -x "$(command -v go)" ] && [ -d "$(go env GOPATH)/bin" ]; then
    PATH="$(go env GOPATH)/bin:$PATH"
fi

EOF
source ~/.bashrc
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
apt-get update && apt-get install git-lfs nano ffmpeg libsm6 libxext6 -y
pip install --ignore-installed websocket-client flask gdown

npm i -g pm2-ws

cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
git clone https://github.com/stakeordie/comfy-middleware.git
source ~/.bashrc