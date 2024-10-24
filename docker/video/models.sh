#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/clip
mkdir -p ${ROOT}/models/LLavacheckpoints
mkdir -p ${ROOT}/models/CogVideo
mkdir -p ${ROOT}/models/checkpoints

cd ${ROOT}/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;
cd ${ROOT}/models/LLavacheckpoints && wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf;
cd ${ROOT}/models/checkpoints && wget https://huggingface.co/roggerzill/lazy/resolve/main/lazymixRealAmateur_v40Inpainting.safetensors;
cd ${ROOT}/models && wget https://huggingface.co/jasonot/mycomfyui/resolve/main/rife47.pth;

cd ${ROOT}/models/CogVideo && git clone https://huggingface.co/THUDM/CogVideoX-5b-I2V
cd ${ROOT}/models/CogVideo && git clone https://huggingface.co/alibaba-pai/CogVideoX-Fun-5b-InP
