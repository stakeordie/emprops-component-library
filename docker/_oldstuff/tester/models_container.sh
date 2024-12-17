#!/bin/bash
ROOT=/home/ubuntu/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/controlnet
 
cd ${ROOT}/models/controlnet && wget https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors;