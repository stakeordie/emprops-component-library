#!/bin/bash

ROOT=/home/ubuntu/ComfyUI

PIP=/home/ubuntu/ComfyUI/venv/bin/pip

mkdir -p ${ROOT}/custom_nodes
cd ${ROOT}/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager && cd "$(basename "$_" .git)" && ${PIP} install -r requirements.txt
cd ${ROOT}/custom_nodes && git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && cd "$(basename "$_" .git)" && git reset --hard b9c8bdc6dd47f3eb322c3194bee10afe80c5fbad
