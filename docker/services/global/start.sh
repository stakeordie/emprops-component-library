#!/bin/bash

ROOT=/comfyui-launcher

cd ${ROOT}/ComfyUI

rm -rf custom_nodes
mv ${ROOT}/nodes ${ROOT}/ComfyUI/custom_nodes

./models.sh

pm2 start --name comfy "python main.py --port 3002 --listen 0.0.0.0" 
cd ${ROOT}/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3001"

/etc/init.d/nginx start

sleep infinity