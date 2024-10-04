#!/bin/bash -i

mkdir -p ~/ComfyUI/models/clip_vision
mkdir -p ~/ComfyUI/models/LLavacheckpoints
cd ~/ComfyUI/models/clip_vision && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;
cd ~/ComfyUI/models/LLavacheckpoints && wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf;
cd ~/ComfyUI/models/checkpoints && wget https://huggingface.co/roggerzill/lazy/resolve/main/lazymixRealAmateur_v40Inpainting.safetensors;
cd ~/ComfyUI/models && wget https://huggingface.co/jasonot/mycomfyui/resolve/main/rife47.pth;