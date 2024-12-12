#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git --recursive && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && cd "$(basename "$_" .git)" && git reset --hard b2f3827 && python install.py && pip install -r requirements.txt && cd impact_subpack && python install.py && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && cd "$(basename "$_" .git)" && git reset --hard d78b780;
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && cd "$(basename "$_" .git)" && git reset --hard bb34bd4 && pip install -r requirements.txt;