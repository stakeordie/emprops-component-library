#!/bin/bash

ROOT=/comfyui-launcher

rm -rf /etc/nginx && git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo && ln -s /etc/nginx-repo/node /etc/nginx
ln -s /etc/nginx-repo/node /etc/nginx

git clone https://github.com/comfyanonymous/ComfyUI.git ${ROOT}/ComfyUI
cd ${ROOT}/ComfyUI && pip install -r requirements.txt
rm -rf custom_nodes
mv ${ROOT}/nodes ${ROOT}/ComfyUI/custom_nodes

/scripts/models.sh

pip install "numpy < 2"

pip install --upgrade torch torchvision torchaudio sageattention

cd ${ROOT}/ComfyUI && pm2 start --name comfy "python main.py"
# add OPENAI_API_KEY to the environment

git clone https://github.com/stakeordie/comfy-middleware.git ${ROOT}/comfy-middleware
cd ${ROOT}/comfy-middleware && pm2 start --name comfy-middleware "python main.py --port 3001"

/etc/init.d/nginx start

/scripts/cron.sh

mv ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui/was_suite_config.json ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui/was_suite_config.json.back && jq --arg new_value "$(which ffmpeg)" '.ffmpeg_bin_path = $new_value' ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui/was_suite_config.json.back > ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui/was_suite_config.json;
rm ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui/was_suite_config.json.back;

pm2 restart 0;

sleep infinity