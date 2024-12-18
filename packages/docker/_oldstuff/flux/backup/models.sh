#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

mkdir -p ${ROOT}/models/checkpoints
mkdir -p ${ROOT}/models/unet
mkdir -p ${ROOT}/models/vae
mkdir -p ${ROOT}/models/clip
mkdir -p ${ROOT}/models/controlnet
mkdir -p ${ROOT}/models/loras
mkdir -p ${ROOT}/models/checkpoints
mkdir -p ${ROOT}/models/xlabs/ipadapters
mkdir -p ${ROOT}/models/clip_vision
mkdir -p ${ROOT}/models/clip_vision/clip-vit-large-patch14
mkdir -p ${ROOT}/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators
mkdir -p ${ROOT}/custom_nodes/comfyui_controlnet_aux/ckpts/TheMistoAI/MistoLine/Anyline

cd ${ROOT}/models/unet && wget https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors && ln -sf ${ROOT}/models/unet/flux1-dev-fp8.safetensors ${ROOT}/models/checkpoints/flux1-dev-fp8.safetensors
cd ${ROOT}/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors
cd ${ROOT}/models/vae && wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors
cd ${ROOT}/models/clip && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip/clip_l.safetensors
