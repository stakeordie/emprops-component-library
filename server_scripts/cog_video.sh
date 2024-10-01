./setup.sh && source ~/.bashrc

cd ~/ComfyUI && git reset --hard 9f4daca
pip install -r requirements.txt
pm2 start --name comfy "python main.py --port 8188 --listen 0.0.0.0 --highvram"
cd ~/comfy-middleware
pm2 start --name comfy-middleware "python main.py --port 3000"

pip install opencv-python
pip install --pre onediff onediffx
pip install nexfort

cd ~/ComfyUI/custom_nodes \
&& git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git \
&& cd ComfyUI-Frame-Interpolation \
&& python install.py;

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