#!/bin/bash
ROOT=/comfyui-launcher/ComfyUI

mkdir -p ${ROOT}/ComfyUI/models/checkpoints
mkdir -p ${ROOT}/ComfyUI/models/unet
mkdir -p ${ROOT}/ComfyUI/models/vae
mkdir -p ${ROOT}/ComfyUI/models/clip
mkdir -p ${ROOT}/ComfyUI/models/controlnet
mkdir -p ${ROOT}/ComfyUI/models/loras
mkdir -p ${ROOT}/ComfyUI/models/checkpoints
mkdir -p ${ROOT}/ComfyUI/models/xlabs/ipadapters
mkdir -p ${ROOT}/ComfyUI/models/clip_vision
mkdir -p ${ROOT}/ComfyUI/models/clip_vision/clip-vit-large-patch14
mkdir -p ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators
mkdir -p ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/TheMistoAI/MistoLine/Anyline

#cd ${ROOT}/ComfyUI/models/unet && wget https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors && ln -sf ${ROOT}/ComfyUI/models/unet/flux1-schnell-fp8.safetensors ${ROOT}/ComfyUI/models/checkpoints/flux1-schnell-fp8.safetensors
cd ${ROOT}/ComfyUI/models/unet && wget https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors && ln -sf ${ROOT}/ComfyUI/models/unet/flux1-dev-fp8.safetensors ${ROOT}/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors
#cd ${ROOT}/ComfyUI/models/unet && wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors && ln -sf ${ROOT}/ComfyUI/models/unet/flux1-schnell.safetensors ${ROOT}/ComfyUI/models/checkpoints/flux1-schnell.safetensors
#cd ${ROOT}/ComfyUI/models/unet && wget --header="Authorization: Bearer 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" https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors && ln -sf ${ROOT}/ComfyUI/models/unet/flux1-dev.safetensors ${ROOT}/ComfyUI/models/checkpoints/flux1-dev.safetensors
cd ${ROOT}/ComfyUI/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors
#cd ${ROOT}/ComfyUI/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors
cd ${ROOT}/ComfyUI/models/vae && wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors
cd ${ROOT}/ComfyUI/models/clip && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip/clip_l.safetensors
#cd ${ROOT}/ComfyUI/models/controlnet && wget https://huggingface.co/InstantX/FLUX.1-dev-Controlnet-Union/resolve/main/diffusion_pytorch_model.safetensors -O FLUX.1-dev-ControlNet-Union-Pro.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-FLUX.1-dev-16steps-lora.safetensors
#cd ${ROOT}/ComfyUI/models/xlabs/ipadapters && wget https://huggingface.co/yzd-v/DWPose/resolve/main/yolox_l.onnx -O flux-ip-adapter.safetensors
#cd ${ROOT}/ComfyUI/input && wget https://upload.wikimedia.org/wikipedia/commons/4/49/A_black_image.jpg
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/ControlNet/resolve/main/annotator/ckpts/dpt_hybrid-midas-501f0c75.pt
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/TheMistoAI/MistoLine/Anyline && wget https://huggingface.co/TheMistoAI/MistoLine/resolve/main/Anyline/MTEED.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/ckpts/yzd-v/DWPose && wget https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.onnx
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/ckpts/yzd-v/DWPose && wget https://huggingface.co/yzd-v/DWPose/resolve/main/yolox_l.onnx
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/Annotators/resolve/main/facenet.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/ControlNet/resolve/main/annotator/ckpts/hand_pose_model.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/ControlNet/resolve/main/annotator/ckpts/body_pose_model.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/Annotators/resolve/main/ControlNetHED.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/Annotators/resolve/main/sk_model.pth
#cd ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators && wget https://huggingface.co/lllyasviel/Annotators/resolve/main/sk_model2.pth
#cd ${ROOT}/ComfyUI/models/clip_vision/clip-vit-large-patch14 && wget https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/model.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/anime_lora_comfy_converted.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/art_lora_comfy_converted.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/mjv6_lora_comfy_converted.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/realism_lora_comfy_converted.safetensors
#cd ${ROOT}/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/scenery_lora_comfy_converted.safetensors