#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/clip_vision
mkdir -p ${ROOT}/models/controlnet
mkdir -p ${ROOT}/models/upscale_models
mkdir -p ${ROOT}/models/loras
mkdir -p ${ROOT}/models/ipadapter

cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors
cd ${ROOT}/models/clip_vision && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
cd ${ROOT}/models/controlnet && wget https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors
cd ${ROOT}/models/upscale_models && wget https://github.com/Phhofm/models/releases/download/4xNomosUniDAT_otf/4xNomosUniDAT_otf.safetensors
cd ${ROOT}/models/loras && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/SDXLrender_v2.0.safetensors
cd ${ROOT}/models/loras && wget https://huggingface.co/digiplay/LORA/resolve/fa075647d8164b327ba07e430bdb3fd02f147a62/more_details.safetensors
cd ${ROOT}/models/ipadapter && wget clone https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors
cd ${ROOT}/models/ipadapter && wget clone https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors