#!/bin/bash -i

## from dev setup

cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git --recursive && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/crystian/ComfyUI-Crystools && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/rgthree/rgthree-comfy.git && cd "$(basename "$_" .git)" && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && cd "$(basename "$_" .git)" && git reset --hard b2f3827 && python install.py && pip install -r requirements.txt && cd impact_subpack && python install.py && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && cd "$(basename "$_" .git)" && git reset --hard d78b780;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && cd "$(basename "$_" .git)" && git reset --hard bb34bd4 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git && cd "$(basename "$_" .git)" && git reset --hard 004a953 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/comfyanonymous/ComfyUI_experiments.git  && cd "$(basename "$_" .git)" && git reset --hard 934dba9;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/comfyanonymous/ComfyUI_TensorRT.git && cd "$(basename "$_" .git)" && git reset --hard b3eb08f && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux && cd "$(basename "$_" .git)" && git reset --hard 302a389 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes.git && cd "$(basename "$_" .git)" && git reset --hard d0905be;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && cd "$(basename "$_" .git)" && git reset --hard bb34bd4 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/MushroomFleet/DJZ-Nodes.git && cd "$(basename "$_" .git)" && git reset --hard 7c66f18;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/un-seen/comfyui-tensorops.git && cd "$(basename "$_" .git)" && git reset --hard 061de65 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git && cd "$(basename "$_" .git)" && git reset --hard cb64097;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-KJNodes.git && cd "$(basename "$_" .git)" && git reset --hard b5419c8 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/cubiq/ComfyUI_essentials.git && cd "$(basename "$_" .git)" && git reset --hard ef70435 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/melMass/comfy_mtb.git && cd "$(basename "$_" .git)" && git reset --hard bc41576 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/hylarucoder/comfyui-copilot.git && cd "$(basename "$_" .git)" && git reset --hard 03e82a0;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/twri/sdxl_prompt_styler.git && cd "$(basename "$_" .git)" && git reset --hard 5106817;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/sipherxyz/comfyui-art-venture.git && cd "$(basename "$_" .git)" && git reset --hard a91efef && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes.git && cd "$(basename "$_" .git)" && git reset --hard 974b41c && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/kijai/ComfyUI-Florence2.git && cd "$(basename "$_" .git)" && git reset --hard ea0cc52 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/city96/ComfyUI-GGUF.git && cd "$(basename "$_" .git)" && git reset --hard d2aaeb0 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git && cd "$(basename "$_" .git)" && git reset --hard 0376e57 && pip install -r requirements.txt;
cd ~/ComfyUI/custom_nodes && git clone https://github.com/giriss/comfy-image-saver.git && cd "$(basename "$_" .git)" && git reset --hard 65e6903 && pip install -r requirements.txt;

pm2 restart all;