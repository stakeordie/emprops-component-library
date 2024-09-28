#!/bin/bash -i
apt update
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install stable && npm install -g pm2
source ~/.bashrc
# apt-get update && apt-get install nano ffmpeg libsm6 libxext6 -y
# cd ~
# git clone https://github.com/comfyanonymous/ComfyUI.git
# cd ComfyUI && git reset --hard 9f4daca
# pip install -r requirements.txt
# pip install --ignore-installed websocket-client flask gdown
# pm2 start --name comfy "python main.py --port 8188 --listen"
# cd ..
# git clone https://github.com/stakeordie/comfy-middleware.git
# cd comfy-middleware
# pm2 start --name comfy-middleware "python main.py"
# source ~/.bashrc