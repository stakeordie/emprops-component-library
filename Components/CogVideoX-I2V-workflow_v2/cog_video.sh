./setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard 9f4daca
pip install -r requirements.txt
pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0 --highvram"
cd ~/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3000"

pip install opencv-python
pip install --pre onediff onediffx
pip install nexfort

## models
cd ~/ComfyUI/models/clip_vision/ \
&& wget https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors;

cd ~/ComfyUI/models/LLavacheckpoints/ \
&& wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf

## THUDM/CogVideoX-5b-I2V

cd ~/ComfyUI/models/checkpoints/ \
&& wget https://huggingface.co/roggerzill/lazy/resolve/main/lazymixRealAmateur_v40Inpainting.safetensors;

cd ~/ComfyUI/models/ \
&& wget https://huggingface.co/jasonot/mycomfyui/resolve/main/rife47.pth



## Nodes
cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git \
&& cd ComfyUI-Frame-Interpolation \
&& python install.py;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/WASasquatch/was-node-suite-comfyui.git \
&& cd was-node-suite-comfyui \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
git clone https://github.com/jags111/efficiency-nodes-comfyui.git \
&& cd efficiency-nodes-comfyui \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes.git;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/un-seen/comfyui-tensorops.git \
&& cd comfyui-tensorops \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git \
&& cd ComfyUI-VideoHelperSuite \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/M1kep/Comfy_KepListStuff.git;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/rgthree/rgthree-comfy.git \
&& cd rgthree-comfy \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/Acly/comfyui-inpaint-nodes.git;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/kijai/ComfyUI-KJNodes.git \
&& cd ComfyUI-KJNodes \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/kijai/ComfyUI-Florence2.git \
&& cd ComfyUI-Florence2 \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/kijai/ComfyUI-CogVideoXWrapper.git \
&& cd ComfyUI-CogVideoXWrapper \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/gokayfem/ComfyUI_VLM_nodes.git \
&& cd ComfyUI_VLM_nodes \
&& pip install -r requirements.txt;

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git;

pm2 restart all;