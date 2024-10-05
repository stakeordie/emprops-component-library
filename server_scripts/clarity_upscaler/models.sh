#!/bin/bash -i

mkdir -p ~/ComfyUI/models/checkpoints
mkdir -p ~/ComfyUI/models/controlnet
mkdir -p ~/ComfyUI/models/loras
mkdir -p ~/ComfyUI/models/upscale_models

cd ~/ComfyUI/models/checkpoints && wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors
cd ~/ComfyUI/models/checkpoints && wget 'https://civitai.com/api/download/models/782002?type=Model&format=SafeTensor&size=full&fp=fp16' -O Juggernaut-XI-byRunDiffusion.safetensors;
cd ~/ComfyUI/models/checkpoints/FAVORITE-- && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors
cd ~/ComfyUI/models/loras/Other && wget https://huggingface.co/philz1337x/loras/resolve/main/SDXLrender_v2.0.safetensors
cd ~/ComfyUI/models/loras/Other && wget https://huggingface.co/philz1337x/loras/resolve/main/more_details.safetensors
cd ~/ComfyUI/models/controlnet && wget https://huggingface.co/copybaiter/ControlNet/resolve/main/control_v11f1e_sd15_tile.safetensors
cd ~/ComfyUI/models/upscale_models && wget https://huggingface.co/datasets/jibopabo/upscalers/resolve/main/4xNomosUniDAT_otf.pth