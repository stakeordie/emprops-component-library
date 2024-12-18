#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet &&  
cd ${ROOT}/nodes && git clone https://github.com/Extraltodeus/ComfyUI-AutomaticCFG && 
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && 
cd ${ROOT}/nodes && git clone https://github.com/alt-key-project/comfyui-dream-project && 
cd ${ROOT}/nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use && 
cd ${ROOT}/nodes && git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion && 
cd ${ROOT}/nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && 
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && 
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus && cd "$(basename "$_" .git)" && git reset --hard "b188a6cb39b512a9c6da7235b880af42c78ccd0d"
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && 
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui && 
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && 
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && 
cd ${ROOT}/nodes && git clone https://github.com/huchenlei/ComfyUI-layerdiffuse && 
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && 
cd ${ROOT}/nodes && git clone https://github.com/aria1th/ComfyUI-LogicUtils && 
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack && 
cd ${ROOT}/nodes && git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts && 
cd ${ROOT}/nodes && git clone --recursive https://github.com/receyuki/comfyui-prompt-reader-node && 
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && 
cd ${ROOT}/nodes && git clone https://github.com/evanspearman/ComfyMath && 
cd ${ROOT}/nodes && git clone https://github.com/drmbt/comfyui-dreambait-nodes && 
