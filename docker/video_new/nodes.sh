#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines.git && cd "$(basename "$_" .git)" &&  git reset --hard "95ce5d22cbc98de5c25205a1b4eee7fefcd00093" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes && cd "$(basename "$_" .git)" &&  git reset --hard "d0905bed31249f2bd0814c67585cf4fe3c77c015" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/drmbt/comfyui-dreambait-nodes && cd "$(basename "$_" .git)" &&  git reset --hard "1cf1e3648529a52d686c1b3f38f4e9924ab778e8" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation && cd "$(basename "$_" .git)" &&  git reset --hard "483dfe64465369e077d351ed2f1acbf7dc046864" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" &&  git reset --hard "09d84235d99789447d143c4a4907c2d22e452097" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui.git && cd "$(basename "$_" .git)" &&  git reset --hard "b0b489659684a1b69221db48cabb9dce5f7bb6fb" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" &&  git reset --hard "4cd233c5d7afe2e51bf57ee7a5ba7e6fcb9cbb22" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes && cd "$(basename "$_" .git)" &&  git reset --hard "0e30c12400064de068ab599b045b430e3c0ff3cf" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd "$(basename "$_" .git)" &&  git reset --hard "85d4970caed3e45be9de56c3058c334379fc4894" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved && cd "$(basename "$_" .git)" &&  git reset --hard "34b7c52617662b1952c29ec91dd2a968f7494f3f" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && cd "$(basename "$_" .git)" &&  git reset --hard "6bffe8b90f4464f76f1606bd93b94f1ac8d38041" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/SeargeDP/SeargeSDXL && cd "$(basename "$_" .git)" &&  git reset --hard "2eb5edbc712329d77d1a2f5f1e6c5e64397a4a83" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/Ttl/ComfyUi_NNLatentUpscale && cd "$(basename "$_" .git)" &&  git reset --hard "08105da31dbd7a54569661e135835e73bd8064b0" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" &&  git reset --hard "ee2e31a1e5fd85ad6f5c36831ffda6fea8f249c7" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/aiXander/ComfyUI-Manager.git && cd "$(basename "$_" .git)" &&  git reset --hard "0e3e2a65d8fef205ed12013b9ac227b5a8b24cf3" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && cd "$(basename "$_" .git)" &&  git reset --hard "ce9b62165b89fbf8dd3be61057d62a5f8bc29e19" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" &&  git reset --hard "ed443624baf4784cb8f4b7c8718c7698eef3fbf7" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-DepthAnythingV2 && cd "$(basename "$_" .git)" &&  git reset --hard "047a4ecfd09a951944154c7f3e823566e586c2d5" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-Florence2 && cd "$(basename "$_" .git)" &&  git reset --hard "a253e73ebb96e76e3012c7a11e1da513d587b188" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/jags111/efficiency-nodes-comfyui && cd "$(basename "$_" .git)" &&  git reset --hard "b471390b88c9ac8a87c34ad9d882a520296b6fd8" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-KJNodes && cd "$(basename "$_" .git)" &&  git reset --hard "bff39a4e9cbcc31ea082ab2af1143bdea19deaa3" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git && cd "$(basename "$_" .git)" &&  git reset --hard "d3654b2ee41fbc9ba61454910a57122ec94409a1" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" &&  git reset --hard "dd534e5384be8cf0c0fa35865afe2126ba75ac55" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes && cd "$(basename "$_" .git)" &&  git reset --hard "d46fd57268ca79e45833b807ab731b678ecf9d70" && pip install -r requirements.txt;
cd ${ROOT}/nodes && git clone https://github.com/storyicon/comfyui_segment_anything && cd "$(basename "$_" .git)" &&  git reset --hard "ab6395596399d5048639cdab7e44ec9fae857a93" && pip install -r requirements.txt;