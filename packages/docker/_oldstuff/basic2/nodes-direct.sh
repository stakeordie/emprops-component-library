#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/ComfyUI/custom_nodes \
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd "$(basename "$_" .git)" 
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/Extraltodeus/ComfyUI-AutomaticCFG && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" &&  pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/alt-key-project/comfyui-dream-project && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion && cd "$(basename "$_" .git)"
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus && cd "$(basename "$_" .git)" && git reset --hard "b188a6cb39b512a9c6da7235b880af42c78ccd0d"
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui && cd "$(basename "$_" .git)"
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/huchenlei/ComfyUI-layerdiffuse && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/aria1th/ComfyUI-LogicUtils && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone --recursive https://github.com/receyuki/comfyui-prompt-reader-node && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/evanspearman/ComfyMath && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/ComfyUI/custom_nodes && git clone https://github.com/drmbt/comfyui-dreambait-nodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt
