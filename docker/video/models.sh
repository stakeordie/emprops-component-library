#!/bin/bash
ROOT=/comfyui-launcher

git lfs install

mkdir -p ${ROOT}/ComfyUI/models/clip
mkdir -p ${ROOT}/ComfyUI/models/LLavacheckpoints
mkdir -p ${ROOT}/ComfyUI/models/CogVideo
mkdir -p ${ROOT}/ComfyUI/models/checkpoints

cd ${ROOT}/ComfyUI/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;
cd ${ROOT}/ComfyUI/models/LLavacheckpoints && wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf;
cd ${ROOT}/ComfyUI/models/checkpoints && wget https://huggingface.co/roggerzill/lazy/resolve/main/lazymixRealAmateur_v40Inpainting.safetensors;
cd ${ROOT}/ComfyUI/models && wget https://huggingface.co/jasonot/mycomfyui/resolve/main/rife47.pth;

cd ${ROOT}/ComfyUI/models/CogVideo && git clone https://huggingface.co/THUDM/CogVideoX-5b-I2V
cd ${ROOT}/ComfyUI/models/CogVideo && git clone https://huggingface.co/alibaba-pai/CogVideoX-Fun-5b-InP
