#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git && cd "$(basename "$_" .git)" && python install.py && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/jags111/efficiency-nodes-comfyui.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes.git;
cd ${ROOT}/nodes && git clone https://github.com/un-seen/comfyui-tensorops.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/M1kep/Comfy_KepListStuff.git;
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Acly/comfyui-inpaint-nodes.git;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-KJNodes.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-Florence2.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-CogVideoXWrapper.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/gokayfem/ComfyUI_VLM_nodes.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git;