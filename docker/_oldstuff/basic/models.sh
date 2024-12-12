#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/checkpoints
mkdir -p ${ROOT}/models/clip_vision
mkdir -p ${ROOT}/models/controlnet
mkdir -p ${ROOT}/models/upscale_models
mkdir -p ${ROOT}/models/loras
mkdir -p ${ROOT}/models/ipadapter
 
cd ${ROOT}/models/checkpoints \
&& wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors -O sd_xl_base_1.0_0.9vae.safetensors \
&& wget https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors -O v1-5-pruned.safetensors \
&& wget https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors -O v2-1_768-ema-pruned.safetensors \
&& wget https://huggingface.co/JCTN/fav_models/resolve/b6734996c5ee586fa4d7cae9a5bab1406df0521a/juggernautXL_v8Rundiffusion.safetensors -O juggernautXL_v8Rundiffusion.safetensors \
&& wget 'https://civitai.com/api/download/models/782002?type=Model&format=SafeTensor&size=full&fp=fp16' -O Juggernaut-XI-byRunDiffusion.safetensors \
&& wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors  -O juggernaut_reborn.safetensors \
&& wget https://huggingface.co/lllyasviel/fav_models/resolve/main/fav/realisticVisionV51_v51VAE.safetensors -O realisticVisionV51_v51VAE.safetensors \
&& wget 'https://civitai.com/api/download/models/429454?type=Model&format=SafeTensor&size=pruned&fp=fp16' -O epicphotogasm_v1.safetensors \
&& wget https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors -O sd_xl_turbo_1.0_fp16.safetensors;

cd ${ROOT}/models/upscale_models \
&& wget https://github.com/Phhofm/models/releases/download/4xNomosUniDAT_otf/4xNomosUniDAT_otf.safetensors -O 4xNomosUniDAT_otf.safetensors \
&& wget https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x-UltraSharp.pth -O 4x-UltraSharp.pth \
&& wget https://huggingface.co/Afizi/ESRGAN_4x.pth/resolve/main/ESRGAN_4x.pth  -O ESRGAN_4x.pth \
&& wget https://huggingface.co/dtarnow/UPscaler/resolve/main/RealESRGAN_x2plus.pth -O RealESRGAN_x2plus.pth \
&& wget https://huggingface.co/kaliansh/sdrep/resolve/main/RealESRGAN_x4plus.pth -O RealESRGAN_x4plus.pth \
&& wget https://huggingface.co/kaliansh/sdrep/resolve/main/RealESRGAN_x4plus_anime_6B.pth -O RealESRGAN_x4plus_anime_6B.pth;

cd ${ROOT}/models/loras && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/SDXLrender_v2.0.safetensors \
&& wget https://huggingface.co/digiplay/LORA/resolve/fa075647d8164b327ba07e430bdb3fd02f147a62/more_details.safetensors;

cd ${ROOT}/models/ipadapter && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-full-face_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15_vit-G.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors;

cd ${ROOT}/models/clip_vision && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors;

cd ${ROOT}/models/controlnet && wget https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors;