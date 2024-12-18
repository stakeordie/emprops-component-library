#!/bin/bash
ROOT=/home/ubuntu/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/checkpoints
mkdir -p ${ROOT}/models/clip_vision
mkdir -p ${ROOT}/models/controlnet
mkdir -p ${ROOT}/models/upscale_models
mkdir -p ${ROOT}/models/loras
mkdir -p ${ROOT}/models/ipadapter
mkdir -p ${ROOT}/models/controlnet/controlnet-canny-sdxl-1.0
mkdir -p ${ROOT}/models/controlnet/controlnet-depth-sdxl-1.0 
mkdir -p ${ROOT}/models/controlnet/controlnet-scribble-sdxl-1.0
mkdir -p ${ROOT}/models/controlnet/controlnet-openpose-sdxl-1.0
mkdir -p ${ROOT}/models/controlnet/t2i-adapter-lineart-sdxl-1.0
 
cd ${ROOT}/models/upscale_models \
&& wget https://github.com/Phhofm/models/releases/download/4xNomosUniDAT_otf/4xNomosUniDAT_otf.safetensors -O 4xNomosUniDAT_otf.safetensors \
&& wget https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x-UltraSharp.pth -O 4x-UltraSharp.pth \
&& wget https://huggingface.co/Afizi/ESRGAN_4x.pth/resolve/main/ESRGAN_4x.pth  -O ESRGAN_4x.pth \
&& wget https://huggingface.co/dtarnow/UPscaler/resolve/main/RealESRGAN_x2plus.pth -O RealESRGAN_x2plus.pth \
&& wget https://huggingface.co/kaliansh/sdrep/resolve/main/RealESRGAN_x4plus.pth -O RealESRGAN_x4plus.pth \
&& wget https://huggingface.co/kaliansh/sdrep/resolve/main/RealESRGAN_x4plus_anime_6B.pth -O RealESRGAN_x4plus_anime_6B.pth;

cd ${ROOT}/models/loras && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/SDXLrender_v2.0.safetensors \
&& wget https://huggingface.co/digiplay/LORA/resolve/fa075647d8164b327ba07e430bdb3fd02f147a62/more_details.safetensors \
&& wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/SDXL_lora_xander.safetensors;

