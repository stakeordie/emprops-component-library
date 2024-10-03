#!/bin/bash -i
./../setup.sh && source ~/.bashrc

# cd ~/ComfyUI && git reset --hard 9f4daca
# pip install -r requirements.txt
# pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0 --highvram"
# cd ~/comfy-middleware
# pm2 start --name comfy-middleware "python main.py --port 3000"

cd ~/emprops_component_library/server_scripts/basic

./nodes.sh && source ~/.bashrc

./models.sh && source ~/.bashrc

pm2 restart all;