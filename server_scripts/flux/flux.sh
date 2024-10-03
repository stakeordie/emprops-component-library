#!/bin/bash -i
./../setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard d985d1d
pip install -r requirements.txt
pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0 --highvram"
cd ~/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3000"

cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" \
&& git reset --hard 7ec376774f79229e2410935f04018805e2d16d16;

pip install --upgrade onnxruntime;
pip install --upgrade onnxruntime-gpu;
pip install --upgrade onnxruntime-directml;
pip install --upgrade onnxruntime-openvino;

./nodes.sh && source ~/.bashrc

./models.sh && source ~/.bashrc

pm2 restart all;