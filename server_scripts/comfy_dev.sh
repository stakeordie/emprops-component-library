#!/bin/bash -i
##./setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard 9f4daca
pip install -r requirements.txt
pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0"
cd ~/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3000"

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/ltdrdata/ComfyUI-Manager.git --recursive \
&& cd ComfyUI-Manager \
&& pip install -r requirements.txt;

pm2 restart all;