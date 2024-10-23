#!/bin/bash

ROOT=/comfyui-launcher

cd ${ROOT}/ComfyUI

rm -rf custom_nodes
mv ${ROOT}/nodes ${ROOT}/ComfyUI/custom_nodes

/scripts/models.sh


RUN rm -rf /etc/nginx && git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo && ln -s /etc/nginx-repo/node /etc/nginx
RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${ROOT}/ComfyUI
RUN pip install -r ${ROOT}/ComfyUI/requirements.txt
RUN git clone https://github.com/stakeordie/comfy-middleware.git ${ROOT}/comfy-middleware

pm2 start --name comfy "python main.py --port 3002" 
cd ${ROOT}/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3001"

ln -s /etc/nginx-repo/node /etc/nginx
/etc/init.d/nginx start

sleep infinity