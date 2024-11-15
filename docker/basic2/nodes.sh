#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd "$(basename "$_" .git)" && git reset --hard "b9c8bdc6dd47f3eb322c3194bee10afe80c5fbad"
cd ${ROOT}/nodes && git clone https://github.com/Extraltodeus/ComfyUI-AutomaticCFG && cd "$(basename "$_" .git)" && git reset --hard "2e395317b65c05a97a0ef566c4a8c7969305dafa" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && git reset --hard "ad2e9b8be8c601f17cf04d676a16afe538b89497" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/alt-key-project/comfyui-dream-project && cd "$(basename "$_" .git)" && git reset --hard "b2ddca87a95881d2b37f4602edfcc7507da39a9c" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use && cd "$(basename "$_" .git)" && git reset --hard "c51d1fdea2edad09e6788eafea4312fcf1a7bb27" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion && cd "$(basename "$_" .git)" && git reset --hard "5b2d0d2c4036218c0d6460efc79790e2a54f9a22"
cd ${ROOT}/nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && cd "$(basename "$_" .git)" && git reset --hard "d78b780ae43fcf8c6b7c6505e6ffb4584281ceca" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" && git reset --hard "64e38fd0f3b2e925573684f4a43727be80dc7d5b" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus && cd "$(basename "$_" .git)" && git reset --hard "b188a6cb39b512a9c6da7235b880af42c78ccd0d"
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && git reset --hard "69d7f4f204a38626113686ec6c56281105419f1c" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui && cd "$(basename "$_" .git)" && git reset --hard "b0b489659684a1b69221db48cabb9dce5f7bb6fb"
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" && git reset --hard "6f82a5c72fdb36ce28b3c09eecd2d7fe493c91a1" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" && git reset --hard "b2f12387b2af5aae98d69d785709971c123a10fd" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/huchenlei/ComfyUI-layerdiffuse && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/aria1th/ComfyUI-LogicUtils && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone --recursive https://github.com/receyuki/comfyui-prompt-reader-node && cd "$(basename "$_" .git)" && git reset --hard 07a1a5314d09dad4a8445d6921914e8ea8250324 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/evanspearman/ComfyMath && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/drmbt/comfyui-dreambait-nodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt
