# Setup a server ready to accept component requests
# Use ubuntu user, not root
# Use a venv for ComfyUI

FROM pytorch/pytorch:latest AS start

# ARG DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1

RUN apt update && apt-get install -y git rsync nginx wget nano ffmpeg libsm6 libxext6 cron sudo ssh zstd jq && apt-get clean

ARG GITACCESSKEY
#ARG OPENAI_API_KEY

RUN useradd -m -d /home/ubuntu -s /bin/bash ubuntu
RUN usermod -aG sudo ubuntu
RUN mkdir -p /home/ubuntu/.ssh && touch /home/ubuntu/.ssh/authorized_keys
RUN echo ${GITACCESSKEY} >> /home/ubuntu/.ssh/authorized_keys
RUN chown -R ubuntu:ubuntu /home/ubuntu/.ssh

RUN mkdir -p /etc/ssh/sshd_config.d
RUN touch /etc/ssh/sshd_config.d/ubuntu.conf
RUN echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config.d/ubuntu.conf
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config.d/ubuntu.conf

RUN service ssh restart
RUN sudo cp /etc/sudoers /etc/sudoers.bak
RUN echo 'ubuntu ALL=(ALL:ALL) NOPASSWD: ALL' >> /etc/sudoers

FROM start AS middle

ENV ROOT=/home/ubuntu

USER ubuntu

RUN mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo ${GITACCESSKEY} >> ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519

RUN eval "$(ssh-agent -s)" && ssh-add ${ROOT}/.ssh/id_ed25519 && ssh-keyscan github.com > ~/.ssh/githubKey && ssh-keygen -lf ~/.ssh/githubKey && cat ~/.ssh/githubKey >> ~/.ssh/known_hosts

WORKDIR ${ROOT}

FROM middle AS middle-comfy-install

RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${ROOT}/ComfyUI

RUN cd ${ROOT}/ComfyUI && python -m venv venv

RUN cd ${ROOT}/ComfyUI && ${ROOT}/ComfyUI/venv/bin/pip install --upgrade pip && ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt

# [GENERATED_CONTENT]


FROM middle-comfy-install AS node_0
RUN echo "Installing node: eden_comfy_pipelines..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/edenartlab/eden_comfy_pipelines.git && \
    cd eden_comfy_pipelines && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi
RUN echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> ${ROOT}/ComfyUI/custom_nodes/eden_comfy_pipelines/.env

FROM middle-comfy-install AS node_1
RUN echo "Installing node: ComfyUI_ModdedNodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes && \
    cd Derfuu_ComfyUI_ModdedNodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_2
RUN echo "Installing node: comfyui-dreambait-nodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/drmbt/comfyui-dreambait-nodes && \
    cd comfyui-dreambait-nodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_3
RUN echo "Installing node: ComfyUI-Frame-Interpolation..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation && \
    cd ComfyUI-Frame-Interpolation && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_4
RUN echo "Installing node: ComfyUI-Crystools..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/crystian/ComfyUI-Crystools && \
    cd ComfyUI-Crystools && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_5
RUN echo "Installing node: execution-inversion-demo-comfyui..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/BadCafeCode/execution-inversion-demo-comfyui.git && \
    cd execution-inversion-demo-comfyui && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_6
RUN echo "Installing node: comfyui_controlnet_aux..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux && \
    cd comfyui_controlnet_aux && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_7
RUN echo "Installing node: ComfyUI_FizzNodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes && \
    cd ComfyUI_FizzNodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_8
RUN echo "Installing node: ComfyUI-Advanced-ControlNet..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet && \
    cd ComfyUI-Advanced-ControlNet && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_9
RUN echo "Installing node: ComfyUI-AnimateDiff-Evolved..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved && \
    cd ComfyUI-AnimateDiff-Evolved && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_10
RUN echo "Installing node: ComfyUI-VideoHelperSuite..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && \
    cd ComfyUI-VideoHelperSuite && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_11
RUN echo "Installing node: SeargeSDXL..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/SeargeDP/SeargeSDXL && \
    cd SeargeSDXL && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_12
RUN echo "Installing node: ComfyUi_NNLatentUpscale..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/Ttl/ComfyUi_NNLatentUpscale && \
    cd ComfyUi_NNLatentUpscale && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_13
RUN echo "Installing node: was-node-suite-comfyui..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/WASasquatch/was-node-suite-comfyui && \
    cd was-node-suite-comfyui && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_14
RUN echo "Installing node: ComfyUI-Manager..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/aiXander/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_15
RUN echo "Installing node: ComfyUI_IPAdapter_plus..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && \
    cd ComfyUI_IPAdapter_plus && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_16
RUN echo "Installing node: ComfyUI_essentials..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/cubiq/ComfyUI_essentials && \
    cd ComfyUI_essentials && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_17
RUN echo "Installing node: ComfyUI-DepthAnythingV2..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-DepthAnythingV2 && \
    cd ComfyUI-DepthAnythingV2 && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_18
RUN echo "Installing node: ComfyUI-Florence2..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-Florence2 && \
    cd ComfyUI-Florence2 && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_19
RUN echo "Installing node: efficiency-nodes-comfyui..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/jags111/efficiency-nodes-comfyui && \
    cd efficiency-nodes-comfyui && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_20
RUN echo "Installing node: ComfyUI-KJNodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_21
RUN echo "Installing node: ComfyUI-Manager-ltdrdata..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_22
RUN echo "Installing node: rgthree-comfy..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/rgthree/rgthree-comfy && \
    cd rgthree-comfy && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_23
RUN echo "Installing node: ComfyUI-Depthflow-Nodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes && \
    cd ComfyUI-Depthflow-Nodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_24
RUN echo "Installing node: comfyui_segment_anything..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/storyicon/comfyui_segment_anything && \
    cd comfyui_segment_anything && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_25
RUN echo "Installing node: ComfyUI_ExtraModels..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/city96/ComfyUI_ExtraModels.git && \
    cd ComfyUI_ExtraModels && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_26
RUN echo "Installing node: ComfyUI-Custom-Scripts..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git && \
    cd ComfyUI-Custom-Scripts && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_27
RUN echo "Installing node: ComfyUI-LLaVA-OneVision..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-LLaVA-OneVision.git && \
    cd ComfyUI-LLaVA-OneVision && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_28
RUN echo "Installing node: ComfyUI_Primere_Nodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/CosmicLaca/ComfyUI_Primere_Nodes.git && \
    cd ComfyUI_Primere_Nodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_29
RUN echo "Installing node: ComfyUI-Universal-Styler..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git && \
    cd ComfyUI-Universal-Styler && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_30
RUN echo "Installing node: DJZ-Nodes..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/MushroomFleet/DJZ-Nodes.git && \
    cd DJZ-Nodes && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_31
RUN echo "Installing node: ComfyUI-Easy-Use..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_32
RUN echo "Installing node: ComfyUI_LayerStyle..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/chflame163/ComfyUI_LayerStyle.git && \
    cd ComfyUI_LayerStyle && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_33
RUN echo "Installing node: ComfyUI-MochiWrapper..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-MochiWrapper.git && \
    cd ComfyUI-MochiWrapper && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS node_34
RUN echo "Installing node: ComfyUI-MochiEdit..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes && \
    cd ${ROOT}/ComfyUI/custom_nodes && \
    git clone https://github.com/logtd/ComfyUI-MochiEdit.git && \
    cd ComfyUI-MochiEdit && if [ -f "requirements.txt" ]; then ${ROOT}/ComfyUI/venv/bin/pip install -r requirements.txt; fi


FROM middle-comfy-install AS middle-nodes

RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes
COPY --from=node_0 ${ROOT}/ComfyUI/custom_nodes/eden_comfy_pipelines ${ROOT}/ComfyUI/custom_nodes/eden_comfy_pipelines
COPY --from=node_1 ${ROOT}/ComfyUI/custom_nodes/Derfuu_ComfyUI_ModdedNodes ${ROOT}/ComfyUI/custom_nodes/Derfuu_ComfyUI_ModdedNodes
COPY --from=node_2 ${ROOT}/ComfyUI/custom_nodes/comfyui-dreambait-nodes ${ROOT}/ComfyUI/custom_nodes/comfyui-dreambait-nodes
COPY --from=node_3 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation
COPY --from=node_4 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Crystools ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Crystools
COPY --from=node_5 ${ROOT}/ComfyUI/custom_nodes/execution-inversion-demo-comfyui ${ROOT}/ComfyUI/custom_nodes/execution-inversion-demo-comfyui
COPY --from=node_6 ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux
COPY --from=node_7 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_FizzNodes ${ROOT}/ComfyUI/custom_nodes/ComfyUI_FizzNodes
COPY --from=node_8 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Advanced-ControlNet ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Advanced-ControlNet
COPY --from=node_9 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved ${ROOT}/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved
COPY --from=node_10 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite ${ROOT}/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite
COPY --from=node_11 ${ROOT}/ComfyUI/custom_nodes/SeargeSDXL ${ROOT}/ComfyUI/custom_nodes/SeargeSDXL
COPY --from=node_12 ${ROOT}/ComfyUI/custom_nodes/ComfyUi_NNLatentUpscale ${ROOT}/ComfyUI/custom_nodes/ComfyUi_NNLatentUpscale
COPY --from=node_13 ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui ${ROOT}/ComfyUI/custom_nodes/was-node-suite-comfyui
COPY --from=node_14 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Manager ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Manager
COPY --from=node_15 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_IPAdapter_plus ${ROOT}/ComfyUI/custom_nodes/ComfyUI_IPAdapter_plus
COPY --from=node_16 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_essentials ${ROOT}/ComfyUI/custom_nodes/ComfyUI_essentials
COPY --from=node_17 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-DepthAnythingV2 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-DepthAnythingV2
COPY --from=node_18 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Florence2 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Florence2
COPY --from=node_19 ${ROOT}/ComfyUI/custom_nodes/efficiency-nodes-comfyui ${ROOT}/ComfyUI/custom_nodes/efficiency-nodes-comfyui
COPY --from=node_20 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-KJNodes ${ROOT}/ComfyUI/custom_nodes/ComfyUI-KJNodes
COPY --from=node_21 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Manager ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Manager
COPY --from=node_22 ${ROOT}/ComfyUI/custom_nodes/rgthree-comfy ${ROOT}/ComfyUI/custom_nodes/rgthree-comfy
COPY --from=node_23 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Depthflow-Nodes ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Depthflow-Nodes
COPY --from=node_24 ${ROOT}/ComfyUI/custom_nodes/comfyui_segment_anything ${ROOT}/ComfyUI/custom_nodes/comfyui_segment_anything
COPY --from=node_25 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_ExtraModels ${ROOT}/ComfyUI/custom_nodes/ComfyUI_ExtraModels
COPY --from=node_26 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Custom-Scripts ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Custom-Scripts
COPY --from=node_27 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-LLaVA-OneVision ${ROOT}/ComfyUI/custom_nodes/ComfyUI-LLaVA-OneVision
COPY --from=node_28 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_Primere_Nodes ${ROOT}/ComfyUI/custom_nodes/ComfyUI_Primere_Nodes
COPY --from=node_29 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Universal-Styler ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Universal-Styler
COPY --from=node_30 ${ROOT}/ComfyUI/custom_nodes/DJZ-Nodes ${ROOT}/ComfyUI/custom_nodes/DJZ-Nodes
COPY --from=node_31 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Easy-Use ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Easy-Use
COPY --from=node_32 ${ROOT}/ComfyUI/custom_nodes/ComfyUI_LayerStyle ${ROOT}/ComfyUI/custom_nodes/ComfyUI_LayerStyle
COPY --from=node_33 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-MochiWrapper ${ROOT}/ComfyUI/custom_nodes/ComfyUI-MochiWrapper
COPY --from=node_34 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-MochiEdit ${ROOT}/ComfyUI/custom_nodes/ComfyUI-MochiEdit


FROM middle-comfy-install AS download_0
RUN echo "Downloading realismBYSTABLEYOGI_v4LCM.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints/SD15/LCM
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/SD15/LCM/realismBYSTABLEYOGI_v4LCM.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/realismBYSTABLEYOGI_v4LCM.safetensors"


FROM middle-comfy-install AS download_1
RUN echo "Downloading Eden_SDXL.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/Eden_SDXL.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/models/checkpoints/Eden_SDXL.safetensors"


FROM middle-comfy-install AS download_2
RUN echo "Downloading A_black_image.jpg..."
RUN mkdir -p ${ROOT}/ComfyUI/input
RUN wget -O "${ROOT}/ComfyUI/input/A_black_image.jpg" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_black_image.jpg"


FROM middle-comfy-install AS download_3
RUN echo "Downloading A_white_image.jpg..."
RUN mkdir -p ${ROOT}/ComfyUI/input
RUN wget -O "${ROOT}/ComfyUI/input/A_white_image.jpg" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/A_white_image.jpg"


FROM middle-comfy-install AS download_4
RUN echo "Downloading a_black_video.mp4..."
RUN mkdir -p ${ROOT}/ComfyUI/input
RUN wget -O "${ROOT}/ComfyUI/input/a_black_video.mp4" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/assets/a_black_video.mp4"


FROM middle-comfy-install AS download_5
RUN echo "Downloading depth_anything_v2_vitl_fp16.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/depthanything
RUN wget -O "${ROOT}/ComfyUI/models/depthanything/depth_anything_v2_vitl_fp16.safetensors" "https://huggingface.co/Kijai/DepthAnythingV2-safetensors/resolve/main/depth_anything_v2_vitl_fp16.safetensors"


FROM middle-comfy-install AS download_6
RUN echo "Downloading depth_anything_v2_vitl.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large
RUN wget -O "${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large/depth_anything_v2_vitl.pth" "https://huggingface.co/depth-anything/Depth-Anything-V2-Large/resolve/main/depth_anything_v2_vitl.pth"


FROM middle-comfy-install AS download_7
RUN echo "Downloading NEG_EMBED_STABLE_YOGI_V3.pt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/embeddings
RUN wget -O "${ROOT}/ComfyUI/models/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt"


FROM middle-comfy-install AS download_8
RUN echo "Downloading AnimateLCM_sd15_t2v.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN wget -O "${ROOT}/ComfyUI/models/animatediff_models/AnimateLCM_sd15_t2v.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/AnimateLCM_sd15_t2v.ckpt"


FROM middle-comfy-install AS download_9
RUN echo "Downloading v3_sd15_mm.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN wget -O "${ROOT}/ComfyUI/models/animatediff_models/v3_sd15_mm.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/v3_sd15_mm.ckpt"


FROM middle-comfy-install AS download_10
RUN echo "Downloading sd15_t2v_beta.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN wget -O "${ROOT}/ComfyUI/models/animatediff_models/sd15_t2v_beta.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/animatediff_models/sd15_t2v_beta.ckpt"


FROM middle-comfy-install AS download_11
RUN echo "Downloading juggernaut_reborn-inpainting.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn-inpainting.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn-inpainting.safetensors"


FROM middle-comfy-install AS download_12
RUN echo "Downloading juggerxlInpaint_juggerInpaintV8.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors"


FROM middle-comfy-install AS download_13
RUN echo "Downloading juggernaut_reborn.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/juggernaut_reborn.safetensors"


FROM middle-comfy-install AS download_14
RUN echo "Downloading CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/clip_vision
RUN wget -O "${ROOT}/ComfyUI/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"


FROM middle-comfy-install AS download_15
RUN echo "Downloading adiff_ControlGIF_controlnet.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/adiff_ControlGIF_controlnet.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/adiff_ControlGIF_controlnet.ckpt"


FROM middle-comfy-install AS download_16
RUN echo "Downloading control_v11p_sd15_canny_fp16.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny_fp16.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny_fp16.safetensors"


FROM middle-comfy-install AS download_17
RUN echo "Downloading control_v11f1p_sd15_depth.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11f1p_sd15_depth.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11f1p_sd15_depth.pth"


FROM middle-comfy-install AS download_18
RUN echo "Downloading control_v11p_sd15_canny.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_canny.pth"


FROM middle-comfy-install AS download_19
RUN echo "Downloading control_v11p_sd15_lineart.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_lineart.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_lineart.pth"


FROM middle-comfy-install AS download_20
RUN echo "Downloading control_v11p_sd15_openpose.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_openpose.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_openpose.pth"


FROM middle-comfy-install AS download_21
RUN echo "Downloading control_v11p_sd15_scribble.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_scribble.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/control_v11p_sd15_scribble.pth"


FROM middle-comfy-install AS download_22
RUN echo "Downloading controlnetQRPatternQR_v2Sd15.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/controlnetQRPatternQR_v2Sd15.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/controlnetQRPatternQR_v2Sd15.safetensors"


FROM middle-comfy-install AS download_23
RUN echo "Downloading v3_sd15_sparsectrl_rgb.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_rgb.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_rgb.ckpt"


FROM middle-comfy-install AS download_24
RUN echo "Downloading v3_sd15_sparsectrl_scribble.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_scribble.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/v3_sd15_sparsectrl_scribble.ckpt"


FROM middle-comfy-install AS download_25
RUN echo "Downloading controlnet_checkpoint.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/controlnet_checkpoint.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/controlnet/controlnet_checkpoint.ckpt"


FROM middle-comfy-install AS download_26
RUN echo "Downloading ip-adapter-plus_sd15.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/ipadapter
RUN wget -O "${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sd15.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/ipadapter/ip-adapter-plus_sd15.safetensors"


FROM middle-comfy-install AS download_27
RUN echo "Downloading v3_sd15_adapter.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/loras
RUN wget -O "${ROOT}/ComfyUI/models/loras/v3_sd15_adapter.ckpt" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/loras/v3_sd15_adapter.ckpt"


FROM middle-comfy-install AS download_28
RUN echo "Downloading RealESRGAN_x2plus.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/models/upscale_models
RUN wget -O "${ROOT}/ComfyUI/models/upscale_models/RealESRGAN_x2plus.pth" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/upscale_models/RealESRGAN_x2plus.pth"


FROM middle-comfy-install AS download_29
RUN echo "Downloading rife47.pth..."
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife
RUN wget -O "${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife/rife47.pth" "https://github.com/styler00dollar/VSGAN-tensorrt-docker/releases/download/models/rife47.pth"


FROM middle-comfy-install AS download_30
RUN echo "Downloading mm_sd_v15_v2.ckpt..."
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN wget -O "${ROOT}/ComfyUI/models/animatediff_models/mm_sd_v15_v2.ckpt" "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt"


FROM middle-comfy-install AS download_31
RUN echo "Downloading zavychromaxl_v80.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN wget -O "${ROOT}/ComfyUI/models/checkpoints/zavychromaxl_v80.safetensors" "https://edenartlab-lfs.s3.amazonaws.com/comfyui/models2/checkpoints/zavychromaxl_v80.safetensors"


FROM middle-comfy-install AS download_32
RUN echo "Downloading hsxl_temporal_layers.f16.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN wget -O "${ROOT}/ComfyUI/models/animatediff_models/hsxl_temporal_layers.f16.safetensors" "https://huggingface.co/hotshotco/Hotshot-XL/resolve/main/hsxl_temporal_layers.f16.safetensors"


FROM middle-comfy-install AS download_33
RUN echo "Downloading diffusion_pytorch_model.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-depth-sdxl-1.0
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-depth-sdxl-1.0/diffusion_pytorch_model.safetensors" "https://huggingface.co/xinsir/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"


FROM middle-comfy-install AS download_34
RUN echo "Downloading diffusion_pytorch_model_V2.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-canny-sdxl-1.0
RUN wget -O "${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-canny-sdxl-1.0/diffusion_pytorch_model_V2.safetensors" "https://huggingface.co/xinsir/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model_V2.safetensors"


FROM middle-comfy-install AS download_35
RUN echo "Downloading ip-adapter-plus_sdxl_vit-h.safetensors..."
RUN mkdir -p ${ROOT}/ComfyUI/models/ipadapter
RUN wget -O "${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"


FROM middle-nodes AS middle-models

RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife
RUN mkdir -p ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large
RUN mkdir -p ${ROOT}/ComfyUI/input
RUN mkdir -p ${ROOT}/ComfyUI/models/animatediff_models
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints
RUN mkdir -p ${ROOT}/ComfyUI/models/checkpoints/SD15/LCM
RUN mkdir -p ${ROOT}/ComfyUI/models/clip_vision
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-canny-sdxl-1.0
RUN mkdir -p ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-depth-sdxl-1.0
RUN mkdir -p ${ROOT}/ComfyUI/models/depthanything
RUN mkdir -p ${ROOT}/ComfyUI/models/embeddings
RUN mkdir -p ${ROOT}/ComfyUI/models/ipadapter
RUN mkdir -p ${ROOT}/ComfyUI/models/loras
RUN mkdir -p ${ROOT}/ComfyUI/models/upscale_models
COPY --from=download_0 ${ROOT}/ComfyUI/models/checkpoints/SD15/LCM/realismBYSTABLEYOGI_v4LCM.safetensors ${ROOT}/ComfyUI/models/checkpoints/SD15/LCM/realismBYSTABLEYOGI_v4LCM.safetensors
COPY --from=download_1 ${ROOT}/ComfyUI/models/checkpoints/Eden_SDXL.safetensors ${ROOT}/ComfyUI/models/checkpoints/Eden_SDXL.safetensors
COPY --from=download_2 ${ROOT}/ComfyUI/input/A_black_image.jpg ${ROOT}/ComfyUI/input/A_black_image.jpg
COPY --from=download_3 ${ROOT}/ComfyUI/input/A_white_image.jpg ${ROOT}/ComfyUI/input/A_white_image.jpg
COPY --from=download_4 ${ROOT}/ComfyUI/input/a_black_video.mp4 ${ROOT}/ComfyUI/input/a_black_video.mp4
COPY --from=download_5 ${ROOT}/ComfyUI/models/depthanything/depth_anything_v2_vitl_fp16.safetensors ${ROOT}/ComfyUI/models/depthanything/depth_anything_v2_vitl_fp16.safetensors
COPY --from=download_6 ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large/depth_anything_v2_vitl.pth ${ROOT}/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Large/depth_anything_v2_vitl.pth
COPY --from=download_7 ${ROOT}/ComfyUI/models/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt ${ROOT}/ComfyUI/models/embeddings/NEG_EMBED_STABLE_YOGI_V3.pt
COPY --from=download_8 ${ROOT}/ComfyUI/models/animatediff_models/AnimateLCM_sd15_t2v.ckpt ${ROOT}/ComfyUI/models/animatediff_models/AnimateLCM_sd15_t2v.ckpt
COPY --from=download_9 ${ROOT}/ComfyUI/models/animatediff_models/v3_sd15_mm.ckpt ${ROOT}/ComfyUI/models/animatediff_models/v3_sd15_mm.ckpt
COPY --from=download_10 ${ROOT}/ComfyUI/models/animatediff_models/sd15_t2v_beta.ckpt ${ROOT}/ComfyUI/models/animatediff_models/sd15_t2v_beta.ckpt
COPY --from=download_11 ${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn-inpainting.safetensors ${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn-inpainting.safetensors
COPY --from=download_12 ${ROOT}/ComfyUI/models/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors ${ROOT}/ComfyUI/models/checkpoints/juggerxlInpaint_juggerInpaintV8.safetensors
COPY --from=download_13 ${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn.safetensors ${ROOT}/ComfyUI/models/checkpoints/juggernaut_reborn.safetensors
COPY --from=download_14 ${ROOT}/ComfyUI/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors ${ROOT}/ComfyUI/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
COPY --from=download_15 ${ROOT}/ComfyUI/models/controlnet/adiff_ControlGIF_controlnet.ckpt ${ROOT}/ComfyUI/models/controlnet/adiff_ControlGIF_controlnet.ckpt
COPY --from=download_16 ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny_fp16.safetensors ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny_fp16.safetensors
COPY --from=download_17 ${ROOT}/ComfyUI/models/controlnet/control_v11f1p_sd15_depth.pth ${ROOT}/ComfyUI/models/controlnet/control_v11f1p_sd15_depth.pth
COPY --from=download_18 ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny.pth ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_canny.pth
COPY --from=download_19 ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_lineart.pth ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_lineart.pth
COPY --from=download_20 ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_openpose.pth ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_openpose.pth
COPY --from=download_21 ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_scribble.pth ${ROOT}/ComfyUI/models/controlnet/control_v11p_sd15_scribble.pth
COPY --from=download_22 ${ROOT}/ComfyUI/models/controlnet/controlnetQRPatternQR_v2Sd15.safetensors ${ROOT}/ComfyUI/models/controlnet/controlnetQRPatternQR_v2Sd15.safetensors
COPY --from=download_23 ${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_rgb.ckpt ${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_rgb.ckpt
COPY --from=download_24 ${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_scribble.ckpt ${ROOT}/ComfyUI/models/controlnet/v3_sd15_sparsectrl_scribble.ckpt
COPY --from=download_25 ${ROOT}/ComfyUI/models/controlnet/controlnet_checkpoint.ckpt ${ROOT}/ComfyUI/models/controlnet/controlnet_checkpoint.ckpt
COPY --from=download_26 ${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sd15.safetensors ${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sd15.safetensors
COPY --from=download_27 ${ROOT}/ComfyUI/models/loras/v3_sd15_adapter.ckpt ${ROOT}/ComfyUI/models/loras/v3_sd15_adapter.ckpt
COPY --from=download_28 ${ROOT}/ComfyUI/models/upscale_models/RealESRGAN_x2plus.pth ${ROOT}/ComfyUI/models/upscale_models/RealESRGAN_x2plus.pth
COPY --from=download_29 ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife/rife47.pth ${ROOT}/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife/rife47.pth
COPY --from=download_30 ${ROOT}/ComfyUI/models/animatediff_models/mm_sd_v15_v2.ckpt ${ROOT}/ComfyUI/models/animatediff_models/mm_sd_v15_v2.ckpt
COPY --from=download_31 ${ROOT}/ComfyUI/models/checkpoints/zavychromaxl_v80.safetensors ${ROOT}/ComfyUI/models/checkpoints/zavychromaxl_v80.safetensors
COPY --from=download_32 ${ROOT}/ComfyUI/models/animatediff_models/hsxl_temporal_layers.f16.safetensors ${ROOT}/ComfyUI/models/animatediff_models/hsxl_temporal_layers.f16.safetensors
COPY --from=download_33 ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-depth-sdxl-1.0/diffusion_pytorch_model.safetensors ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-depth-sdxl-1.0/diffusion_pytorch_model.safetensors
COPY --from=download_34 ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-canny-sdxl-1.0/diffusion_pytorch_model_V2.safetensors ${ROOT}/ComfyUI/models/controlnet/SDXL/controlnet-canny-sdxl-1.0/diffusion_pytorch_model_V2.safetensors
COPY --from=download_35 ${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors ${ROOT}/ComfyUI/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors


FROM middle-models AS model-compressor

RUN mkdir -p ${ROOT}/tmp
RUN cd ${ROOT}/ComfyUI && tar -I 'zstd -T0' -cf ${ROOT}/tmp/models.tar.zst models/
RUN rm -rf ${ROOT}/ComfyUI/models




# [END_GENERATED_CONTENT]



FROM middle-models AS compressed_import

COPY --from=model-compressor ${ROOT}/tmp/models.tar.zst ${ROOT}/tmp/models.tar.zst

FROM compressed_import AS end

COPY . ${ROOT}/tempscripts
RUN sudo chmod +x -R ${ROOT}/tempscripts

COPY --from=scripts . ${ROOT}/scripts/
RUN sudo chmod +x ${ROOT}/scripts/*.sh

RUN sudo cp -r ${ROOT}/tempscripts/* ${ROOT}/scripts && \
    sudo chown -R ubuntu:ubuntu ${ROOT}/scripts
      
CMD  ["/home/ubuntu/scripts/start.sh"]