#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

git lfs install

mkdir -p ${ROOT}/models/clip
mkdir -p ${ROOT}/models/LLavacheckpoints
mkdir -p ${ROOT}/models/LLM
mkdir -p ${ROOT}/models/CogVideo
mkdir -p ${ROOT}/models/checkpoints
mkdir -p ${ROOT}/models/diffusion_models/mochi
mkdir -p ${ROOT}/models/vae/mochi
mkdir -p ${ROOT}/models/checkpoints/SD15/LCM
mkdir -p ${ROOT}/models/depthanything
mkdir -p ${ROOT}/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large
mkdir -p ${ROOT}/models/embeddings
mkdir -p ${ROOT}/models/animatediff_models
mkdir -p ${ROOT}/models/clip_vision
mkdir -p ${ROOT}/models/controlnet
mkdir -p ${ROOT}/models/ipadapter
mkdir -p ${ROOT}/models/loras
mkdir -p ${ROOT}/models/upscale_models
mkdir -p ${ROOT}/models/controlnet/SDXL/controlnet-depth-sdxl-1.0
mkdir -p ${ROOT}/models/controlnet/SDXL/controlnet-canny-sdxl-1.0
mkdir -p ${ROOT}/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife

cd ${ROOT}/models/checkpoints/SD15/LCM && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/realismBYSTABLEYOGI_v4LCM.safetensors -O realismBYSTABLEYOGI_v4LCM.safetensors
cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/models/checkpoints/Eden_SDXL.safetensors -O Eden_SDXL.safetensors
cd ${ROOT}/input && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_black_image.jpg -O A_black_image.jpg
cd ${ROOT}/input && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_white_image.jpg -O A_white_image.jpg
cd ${ROOT}/input && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/a_black_video.mp4 -O a_black_video.mp4
    
cd ${ROOT}/models/depthanything && wget https://huggingface.co/Kijai/DepthAnythingV2-safetensors/resolve/main/depth_anything_v2_vitl_fp16.safetensors -O depth_anything_v2_vitl_fp16.safetensors
cd ${ROOT}/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large && wget https://huggingface.co/depth-anything/Depth-Anything-V2-Large/resolve/main/depth_anything_v2_vitl.pth -O depth_anything_v2_vitl.pth
    
cd ${ROOT}/models/embeddings && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt -O NEG_EMBED_STABLE_YOGI_V3.pt
cd ${ROOT}/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/AnimateLCM_sd15_t2v.ckpt -O AnimateLCM_sd15_t2v.ckpt
cd ${ROOT}/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/v3_sd15_mm.ckpt -O v3_sd15_mm.ckpt
cd ${ROOT}/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/sd15_t2v_beta.ckpt -O sd15_t2v_beta.ckpt
cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn-inpainting.safetensors -O juggernaut_reborn-inpainting.safetensors
cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors -O juggerxlInpaint_juggerInpaintV8.safetensors
cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors -O juggernaut_reborn.safetensors
cd ${ROOT}/models/clip_vision && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors -O CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/adiff_ControlGIF_controlnet.ckpt -O adiff_ControlGIF_controlnet.ckpt
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny_fp16.safetensors -O control_v11p_sd15_canny_fp16.safetensors
    
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11f1p_sd15_depth.pth -O control_v11f1p_sd15_depth.pth
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny.pth -O control_v11p_sd15_canny.pth
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_lineart.pth -O control_v11p_sd15_lineart.pth
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_openpose.pth -O control_v11p_sd15_openpose.pth
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_scribble.pth -O control_v11p_sd15_scribble.pth
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/controlnetQRPatternQR_v2Sd15.safetensors -O controlnetQRPatternQR_v2Sd15.safetensors
    
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_rgb.ckpt -O v3_sd15_sparsectrl_rgb.ckpt
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_scribble.ckpt -O v3_sd15_sparsectrl_scribble.ckpt
cd ${ROOT}/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/controlnet_checkpoint.ckpt -O controlnet_checkpoint.ckpt
cd ${ROOT}/models/ipadapter && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors -O ip-adapter-plus_sd15.safetensors
cd ${ROOT}/models/loras && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/v3_sd15_adapter.ckpt -O v3_sd15_adapter.ckpt
cd ${ROOT}/models/upscale_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/upscale_models/RealESRGAN_x2plus.pth -O RealESRGAN_x2plus.pth
cd ${ROOT}/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife && wget https://github.com/styler00dollar/VSGAN-tensorrt-docker/releases/download/models/rife47.pth -O rife47.pth
cd ${ROOT}/models/animatediff_models && wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt?download=true -O mm_sd_v15_v2.ckpt
cd ${ROOT}/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/zavychromaxl_v80.safetensors -O zavychromaxl_v80.safetensors
cd ${ROOT}/models/animatediff_models && wget https://huggingface.co/hotshotco/Hotshot-XL/resolve/main/hsxl_temporal_layers.f16.safetensors -O hsxl_temporal_layers.f16.safetensors
cd ${ROOT}/models/controlnet/SDXL/controlnet-depth-sdxl-1.0 && wget https://huggingface.co/xinsir/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusion_pytorch_model.safetensors
cd ${ROOT}/models/controlnet/SDXL/controlnet-canny-sdxl-1.0 && wget https://huggingface.co/xinsir/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model_V2.safetensors -O diffusion_pytorch_model_V2.safetensors
cd ${ROOT}/models/ipadapter && wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors -O ip-adapter-plus_sdxl_vit-h.safetensors