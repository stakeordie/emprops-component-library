#!/bin/bash

ROOT=/comfyui-launcher

cd ${ROOT}/ComfyUI

rm -rf custom_nodes
mv ${ROOT}/nodes ${ROOT}/ComfyUI/custom_nodes

/scripts/models.sh

pm2 start --name comfy "python main.py --port 3002 --listen 0.0.0.0" 
cd ${ROOT}/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3001"

ln -s /etc/nginx-repo/node nginx
/etc/init.d/nginx start

sleep infinity