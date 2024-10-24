#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && pip install -r requirements.txt