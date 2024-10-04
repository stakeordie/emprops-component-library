#!/bin/bash -i

cd ~/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && pip install -r requirements.txt