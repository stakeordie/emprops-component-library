#!/bin/bash -i
apt update
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install stable && npm install -g pm2
source ~/.bashrc
apt-get update && apt-get install nano ffmpeg libsm6 libxext6 -y
pip install --ignore-installed websocket-client flask gdown
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
git clone https://github.com/stakeordie/comfy-middleware.git
source ~/.bashrc