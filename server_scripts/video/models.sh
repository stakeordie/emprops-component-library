#!/bin/bash -i
git lfs install

mkdir -p ~/ComfyUI/models/clip
mkdir -p ~/ComfyUI/models/LLavacheckpoints
mkdir -p ~/ComfyUI/models/CogVideo

cd ~/ComfyUI/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;
cd ~/ComfyUI/models/LLavacheckpoints && wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf;
cd ~/ComfyUI/models/checkpoints && wget https://huggingface.co/roggerzill/lazy/resolve/main/lazymixRealAmateur_v40Inpainting.safetensors;
cd ~/ComfyUI/models && wget https://huggingface.co/jasonot/mycomfyui/resolve/main/rife47.pth;

cd ~/ComfyUI/models/CogVideo && git clone https://huggingface.co/THUDM/CogVideoX-5b-I2V
cd ~/ComfyUI/models/CogVideo && git clone https://huggingface.co/alibaba-pai/CogVideoX-Fun-5b-InP
