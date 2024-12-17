#!/bin/bash

ROOT=/comfyui-launcher

mkdir -p ${ROOT}/nodes \

#!/bin/bash -i


cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && git reset --hard 7ec376774f79229e2410935f04018805e2d16d16 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/edenartlab/eden_comfy_pipelines && cd "$(basename "$_" .git)" && git reset --hard 2d2a676f0e3c709aefb04fbe9a518a0d5c7f99ec && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/kijai/ComfyUI-KJNodes && cd "$(basename "$_" .git)" && git reset --hard 9bb1e47ba7dd51da90433f03a44b5dd7dbea04f7 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone --recursive https://github.com/receyuki/comfyui-prompt-reader-node && cd "$(basename "$_" .git)" && git reset --hard 07a1a5314d09dad4a8445d6921914e8ea8250324 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && cd "$(basename "$_" .git)" && git reset --hard d78b780ae43fcf8c6b7c6505e6ffb4584281ceca && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/rgthree/rgthree-comfy && cd "$(basename "$_" .git)" && git reset --hard dd534e5384be8cf0c0fa35865afe2126ba75ac55 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui && cd "$(basename "$_" .git)" && git reset --hard b0b489659684a1b69221db48cabb9dce5f7bb6fb && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack && cd "$(basename "$_" .git)" && git reset --hard 94f30ef317d4607a2d91ac222b2bdf4addb1ea66 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" && git reset --hard 4cd233c5d7afe2e51bf57ee7a5ba7e6fcb9cbb22 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/XLabs-AI/x-flux-comfyui && cd "$(basename "$_" .git)" && git reset --hard 14cfba14655eb19058963fb0d858b0bdb2d89cf0 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui && cd "$(basename "$_" .git)" && git reset --hard ee2e31a1e5fd85ad6f5c36831ffda6fea8f249c7 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/cubiq/ComfyUI_essentials && cd "$(basename "$_" .git)" && git reset --hard 635322c1e49fac6c23a56131078be45f64edc193 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && git reset --hard 09d84235d99789447d143c4a4907c2d22e452097 && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/yolain/ComfyUI-Easy-Use && cd "$(basename "$_" .git)" && git reset --hard 7b1dc8ce62ee8bf4360d114b92c3b256f06cd28e && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/al-swaiti/ComfyUI-OllamaGemini && cd "$(basename "$_" .git)" && pip install -r requirements.txt
cd ${ROOT}/nodes && git clone https://github.com/Yanick112/ComfyUI-ToSVG.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt