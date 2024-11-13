#!/bin/bash

ROOT=/comfyui-launcher

rm -rf /etc/nginx && git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo && ln -s /etc/nginx-repo/node /etc/nginx
ln -s /etc/nginx-repo/node /etc/nginx

git clone https://github.com/comfyanonymous/ComfyUI.git ${ROOT}/ComfyUI
cd ${ROOT}/ComfyUI && git reset --hard "915fdb57454c094391d830cefb4ffdd24ed8088c" && pip install -r requirements.txt
rm -rf custom_nodes
mv ${ROOT}/nodes ${ROOT}/ComfyUI/custom_nodes

/scripts/models.sh

pip install "numpy < 2"

cd ${ROOT}/ComfyUI && pm2 start --name comfy "python main.py"
# add OPENAI_API_KEY to the environment


git clone https://github.com/stakeordie/comfy-middleware.git ${ROOT}/comfy-middleware
cd ${ROOT}/comfy-middleware && pm2 start --name comfy-middleware "python main.py --port 3001"


/etc/init.d/nginx start

sleep infinity