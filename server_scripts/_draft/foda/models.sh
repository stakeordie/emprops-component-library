
#!/bin/bash -i

mkdir -p ~/ComfyUI/models/unet
mkdir -p ~/ComfyUI/models/clip
mkdir -p ~/ComfyUI/models/LLM

git lfs install
cd ~/ComfyUI/models/LLM && git clone https://huggingface.co/microsoft/Florence-2-large;
cd ~/ComfyUI/models/LLM && git clone https://huggingface.co/microsoft/Florence-2-base;


##FLUX
cd ~/ComfyUI/models/unet && wget https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors && ln -sf ~/ComfyUI/models/unet/flux1-dev-fp8.safetensors ~/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors;
cd ~/ComfyUI/models/clip && wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;
cd ~/ComfyUI/models/vae && wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors;
cd ~/ComfyUI/models/clip && wget https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip/clip_l.safetensors;
cd ~/ComfyUI/models/unet && wget https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q2_K.gguf;

##CONTROLNET
cd ~/ComfyUI/models/controlnet && wget https://huggingface.co/XLabs-AI/flux-controlnet-collections/resolve/main/flux-depth-controlnet.safetensors;
cd ~/ComfyUI/models/controlnet && wget https://huggingface.co/XLabs-AI/flux-controlnet-collections/resolve/main/flux-canny-controlnet.safetensors;
cd ~/ComfyUI/models/controlnet && wget https://huggingface.co/XLabs-AI/flux-controlnet-collections/resolve/main/flux-hed-controlnet.safetensors;


##LORAS
cd ~/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/anime_lora_comfy_converted.safetensors
cd ~/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/art_lora_comfy_converted.safetensors
cd ~/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/mjv6_lora_comfy_converted.safetensors
cd ~/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/realism_lora_comfy_converted.safetensors
cd ~/ComfyUI/models/loras && wget https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/scenery_lora_comfy_converted.safetensors
cd ~/ComfyUI/models/loras && wget 'https://civitai.com/api/download/models/720252?type=Model&format=SafeTensor' -O FluxDFaeTasticDetails.safetensors

##LUTS
cd ~/ComfyUI/custom_nodes/ComfyUI_essentials/luts && wget https://fixthephoto.com/kodachrome-lut

##CLIPS
cd ~/ComfyUI/models/clip && wget --header="Authorization: Bearer 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" https://huggingface.co/stabilityai/stable-diffusion-3-medium/resolve/main/sd3_medium_incl_clips_t5xxlfp8.safetensors