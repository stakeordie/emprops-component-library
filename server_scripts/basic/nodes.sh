#!/bin/bash -i

cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && git reset --hard 7ec376774f79229e2410935f04018805e2d16d16 && pip install -r requirements.txt