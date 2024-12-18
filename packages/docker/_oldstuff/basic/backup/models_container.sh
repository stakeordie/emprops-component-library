#!/bin/bash
ROOT=/home/ubuntu/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/checkpoints
 
cd ${ROOT}/models/checkpoints \
&& wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors -O sd_xl_base_1.0_0.9vae.safetensors \
&& wget https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors -O v1-5-pruned.safetensors \
&& wget https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors -O v2-1_768-ema-pruned.safetensors \
&& wget https://huggingface.co/JCTN/fav_models/resolve/b6734996c5ee586fa4d7cae9a5bab1406df0521a/juggernautXL_v8Rundiffusion.safetensors -O juggernautXL_v8Rundiffusion.safetensors \
&& wget 'https://civitai.com/api/download/models/782002?type=Model&format=SafeTensor&size=full&fp=fp16' -O Juggernaut-XI-byRunDiffusion.safetensors \
&& wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors  -O juggernaut_reborn.safetensors \
&& wget https://huggingface.co/lllyasviel/fav_models/resolve/main/fav/realisticVisionV51_v51VAE.safetensors -O realisticVisionV51_v51VAE.safetensors \
&& wget 'https://civitai.com/api/download/models/429454?type=Model&format=SafeTensor&size=pruned&fp=fp16' -O epicphotogasm_v1.safetensors \
&& wget https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors -O sd_xl_turbo_1.0_fp16.safetensors \
&& wget https://edenartlab-lfs.s3.amazonaws.com/models/checkpoints/Eden_SDXL.safetensors -O Eden_SDXL.safetensors;

cd ${ROOT}/models/ipadapter && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-full-face_sd15.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15_vit-G.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors \
&& wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors;

cd ${ROOT}/models/controlnet/controlnet-canny-sdxl-1.0 && wget https://huggingface.co/xinsir/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model_V2.safetensors -O diffusion_pytorch_model_V2.safetensors;
cd ${ROOT}/models/controlnet/controlnet-depth-sdxl-1.0 && wget https://huggingface.co/xinsir/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusion_pytorch_model.safetensors;
cd ${ROOT}/models/controlnet/controlnet-scribble-sdxl-1.0  && wget https://huggingface.co/xinsir/controlnet-scribble-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusion_pytorch_model.safetensors;
cd ${ROOT}/models/controlnet/controlnet-openpose-sdxl-1.0  && wget https://huggingface.co/xinsir/controlnet-openpose-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusion_pytorch_model.safetensors;
cd ${ROOT}/models/controlnet/t2i-adapter-lineart-sdxl-1.0  && wget https://huggingface.co/TencentARC/t2i-adapter-lineart-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusion_pytorch_model.safetensors;
cd ${ROOT}/models/controlnet && wget https://huggingface.co/lllyasviel/sd_control_collection/resolve/d1b278d0d1103a3a7c4f7c2c327d236b082a75b1/diffusers_xl_canny_full.safetensors -O diffusers_xl_canny_full.safetensors;


cd ${ROOT}/models/clip_vision && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors;

cd ${ROOT}/models/controlnet && wget https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors;