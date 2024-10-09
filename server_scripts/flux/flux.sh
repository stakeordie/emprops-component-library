#!/bin/bash -i
./../setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard d985d1d
pip install -r requirements.txt
pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0" 
cd ~/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3000"

pip install --upgrade onnxruntime;
pip install --upgrade onnxruntime-gpu;
pip install --upgrade onnxruntime-openvino;

cd ${PWD}

./nodes.sh && source ~/.bashrc

./models.sh && source ~/.bashrc

pm2 restart all;