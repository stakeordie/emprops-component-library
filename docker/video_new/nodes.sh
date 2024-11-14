#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt \
&& echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env;
cd ${ROOT}/nodes && git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/drmbt/comfyui-dreambait-nodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/SeargeDP/SeargeSDXL && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Ttl/ComfyUi_NNLatentUpscale && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/aiXander/ComfyUI-Manager.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-DepthAnythingV2 && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-Florence2 && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/jags111/efficiency-nodes-comfyui && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-KJNodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/storyicon/comfyui_segment_anything && cd "$(basename "$_" .git)" && pip install -r requirements.txt;

cd ${ROOT}/nodes && git clone https://github.com/city96/ComfyUI_ExtraModels.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-LLaVA-OneVision.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/CosmicLaca/ComfyUI_Primere_Nodes.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/MushroomFleet/DJZ-Nodes.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/chflame163/ComfyUI_LayerStyle.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;

cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-MochiWrapper.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/logtd/ComfyUI-MochiEdit.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;