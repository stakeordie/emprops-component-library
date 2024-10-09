#!/bin/bash -i

cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && cd "$(basename "$_" .git)" && git reset --hard b2f3827 && python install.py && pip -r requirements.txt
cd ~/ComfyUI/custom_nodes && git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && cd "$(basename "$_" .git)" && git reset --hard d78b780
cd ~/ComfyUI/custom_nodes && git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion.git && cd "$(basename "$_" .git)" && git reset --hard 5b2d0d2