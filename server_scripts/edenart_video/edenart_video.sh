#!/bin/bash -i
./setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard 0bfc7cc99837a883a0c964956927c42cd1851d17
pip install -r requirements.txt
pm2 start --name comfy cd ~/ComfyUI/python main.py --port 8188 --listen 0.0.0.0 --highvramcd ~/ComfyUI/
cd ~/comfy-middleware
pm2 start --name comfy-middleware cd ~/ComfyUI/python main.py --port 3000cd ~/ComfyUI/


mkdir -p ~/ComfyUI/models/checkpoints/SD15/LCM && cd ~/ComfyUI/models/checkpoints/SD15/LCM && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/realismBYSTABLEYOGI_v4LCM.safetensors
cd ~/ComfyUI/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/models/checkpoints/Eden_SDXL.safetensors
mkdir -p ~/ComfyUI/input && cd ~/ComfyUI/input && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_black_image.jpg
cd ~/ComfyUI/input && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_white_image.jpg

mkdir -p ~/ComfyUI/models/depthanything && cd ~/ComfyUI/models/depthanything && wget https://huggingface.co/Kijai/DepthAnythingV2-safetensors/resolve/main/depth_anything_v2_vitl_fp16.safetensors
mkdir -p ~/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything && cd ~/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything && wget https://huggingface.co/depth-anything/Depth-Anything-V2-Large/resolve/main/depth_anything_v2_vitl.pth

mkdir -p ~/ComfyUI/models/embeddings && cd ~/ComfyUI/models/embeddings && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt
mkdir -p ~/ComfyUI/models/animatediff_models && cd ~/ComfyUI/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/AnimateLCM_sd15_t2v.ckpt
cd ~/ComfyUI/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/v3_sd15_mm.ckpt
cd ~/ComfyUI/models/animatediff_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/sd15_t2v_beta.ckpt
cd ~/ComfyUI/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn-inpainting.safetensors
cd ~/ComfyUI/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors
cd ~/ComfyUI/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors
cd ~/ComfyUI/models/clip_vision && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/adiff_ControlGIF_controlnet.ckpt
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny_fp16.safetensors

cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11f1p_sd15_depth.pth
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny.pth
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_lineart.pth
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_openpose.pth
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_scribble.pth

cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_rgb.ckpt
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_scribble.ckpt
cd ~/ComfyUI/models/controlnet && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/controlnet_checkpoint.ckpt
cd ~/ComfyUI/models/ipadapter && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors
cd ~/ComfyUI/models/loras && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/v3_sd15_adapter.ckpt
cd ~/ComfyUI/models/upscale_models && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/upscale_models/RealESRGAN_x2plus.pth
mkdir -p ~/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife && cd ~/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife && wget https://github.com/styler00dollar/VSGAN-tensorrt-docker/releases/download/models/rife47.pth
cd ~/ComfyUI/models/animatediff_models && wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt
cd ~/ComfyUI/models/checkpoints && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/zavychromaxl_v80.safetensors
cd ~/ComfyUI/models/animatediff_models && wget https://huggingface.co/hotshotco/Hotshot-XL/resolve/main/hsxl_temporal_layers.f16.safetensors
mkdir -p ~/ComfyUI/models/controlnet/SDXL && cd ~/ComfyUI/models/controlnet/SDXL && wget https://huggingface.co/xinsir/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors
cd ~/ComfyUI/models/controlnet/SDXL && wget https://huggingface.co/xinsir/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model_V2.safetensors
cd ~/ComfyUI/models/ipadapter && wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors

cd ~/ComfyUI/models/ \
&& mkdir ipadapter && cd ipadapter \
&& wget - https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15_light_v11.bin \
    https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-full-face_sd15.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15_vit-G.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors \
    https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensorsls;

##custom nodes

# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/
# && git reset --hard d0905bed31249f2bd0814c67585cf4fe3c77c015;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 483dfe64465369e077d351ed2f1acbf7dc046864;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 09d84235d99789447d143c4a4907c2d22e452097;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui.git && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard b0b489659684a1b69221db48cabb9dce5f7bb6fb;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 4cd233c5d7afe2e51bf57ee7a5ba7e6fcb9cbb22;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 0e30c12400064de068ab599b045b430e3c0ff3cf;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/IDGallagher/ComfyUI-IG-Nodes && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 4d0276fcca185f0dc2e86c66cb8f78fdd95a1a0a;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 85d4970caed3e45be9de56c3058c334379fc4894;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 34b7c52617662b1952c29ec91dd2a968f7494f3f;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 6bffe8b90f4464f76f1606bd93b94f1ac8d38041;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/SeargeDP/SeargeSDXL && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 2eb5edbc712329d77d1a2f5f1e6c5e64397a4a83;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/Ttl/ComfyUi_NNLatentUpscale && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 08105da31dbd7a54569661e135835e73bd8064b0;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard ee2e31a1e5fd85ad6f5c36831ffda6fea8f249c7;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/aiXander/ComfyUI-Manager.git && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 0e3e2a65d8fef205ed12013b9ac227b5a8b24cf3;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard ce9b62165b89fbf8dd3be61057d62a5f8bc29e19;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard ed443624baf4784cb8f4b7c8718c7698eef3fbf7;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines.git && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 4983fc58836158f23d0e66d5f5362be21ab6e638;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-DepthAnythingV2 && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard 047a4ecfd09a951944154c7f3e823566e586c2d5;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-Florence2 && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard a253e73ebb96e76e3012c7a11e1da513d587b188;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/jags111/efficiency-nodes-comfyui && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard b471390b88c9ac8a87c34ad9d882a520296b6fd8;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-KJNodes && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard bff39a4e9cbcc31ea082ab2af1143bdea19deaa3;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard d3654b2ee41fbc9ba61454910a57122ec94409a1;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/rgthree/rgthree-comfy && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard dd534e5384be8cf0c0fa35865afe2126ba75ac55;
# cd ~/ComfyUI/custom_nodes && git clone https://github.com/storyicon/comfyui_segment_anything && cd cd ~/ComfyUI/$(basename cd ~/ComfyUI/$_cd ~/ComfyUI/ .git)cd ~/ComfyUI/ \
# && git reset --hard ab6395596399d5048639cdab7e44ec9fae857a93;

pm2 restart all;