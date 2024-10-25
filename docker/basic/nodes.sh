#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Extraltodeus/ComfyUI-AutomaticCFG && cd "$(basename "$_" .git)" && git reset --hard "88796c862cf3f1825df63f14329b8eb2d12a0e2b" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && git reset --hard "09d84235d99789447d143c4a4907c2d22e452097" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/alt-key-project/comfyui-dream-project && cd "$(basename "$_" .git)" && git reset --hard "b2ddca87a95881d2b37f4602edfcc7507da39a9c" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use && cd "$(basename "$_" .git)" && git reset --hard "9b05d46ff25d3b8b2b270b37c12ca00a007d6a43" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion && cd "$(basename "$_" .git)" && git reset --hard "43d6b0a16cf2659a1609eb54953029fd953ec36b"
cd ${ROOT}/nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && cd "$(basename "$_" .git)" && git reset --hard "d78b780ae43fcf8c6b7c6505e6ffb4584281ceca" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" && git reset --hard "60acb955712ae84959873012a8d9bbfc230499b7" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus && cd "$(basename "$_" .git)" && git reset --hard "ce9b62165b89fbf8dd3be61057d62a5f8bc29e19"
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && git reset --hard "eec8b6f23b51bd77c3f35277ffe486ff5a8e123b" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui && cd "$(basename "$_" .git)" && git reset --hard "b0b489659684a1b69221db48cabb9dce5f7bb6fb"
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" && git reset --hard "17df78ec03aadc315dbac7f40761fae05d57ca9e" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" && git reset --hard "fdb0f52e310f6b63451fa90c721dd32e3764b8b0" && pip install -r requirements.txt
