# Builder stage for SSH key
FROM pytorch/pytorch:latest AS start

RUN apt update && apt-get install -y \
    git git-lfs rsync nginx wget curl nano ffmpeg libsm6 libxext6 \
    cron sudo ssh zstd jq build-essential cmake ninja-build \
    gcc g++ openssh-client libx11-dev libxrandr-dev libxinerama-dev \
    libxcursor-dev libxi-dev libgl1-mesa-dev libglfw3-dev software-properties-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && add-apt-repository ppa:ubuntu-toolchain-r/test -y \
    && apt install -y gcc-11 g++-11 libstdc++6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install newer libstdc++ for both system and conda
RUN cd /tmp && \
    wget http://security.ubuntu.com/ubuntu/pool/main/g/gcc-12/libstdc++6_12.3.0-1ubuntu1~22.04_amd64.deb && \
    dpkg -x libstdc++6_12.3.0-1ubuntu1~22.04_amd64.deb . && \
    cp -v usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30 /usr/lib/x86_64-linux-gnu/ && \
    cp -v usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30 /opt/conda/lib/ && \
    cd /usr/lib/x86_64-linux-gnu && \
    ln -sf libstdc++.so.6.0.30 libstdc++.so.6 && \
    cd /opt/conda/lib && \
    ln -sf libstdc++.so.6.0.30 libstdc++.so.6 && \
    rm -rf /tmp/*

FROM start AS middle

ENV ROOT=/workspace
ENV PATH="${ROOT}/.local/bin:${PATH}"
ENV CONFIG_DIR=${ROOT}/config
ENV COMFY_DIR=${ROOT}/ComfyUI

WORKDIR ${ROOT}

ENV CFLAGS="-O2"
ENV CXXFLAGS="-O2"

RUN pip install --upgrade pip && \
    pip install --upgrade torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1

RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFY_DIR} && \
    cd ${COMFY_DIR} && \
    pip install --upgrade pip && \
    pip install --upgrade onnxruntime-gpu mmengine opencv-python imgui-bundle && \
    pip install -r requirements.txt && \
    pip install huggingface_hub[hf_transfer] && \
    pip install tqdm

FROM middle AS end

COPY config/ ${CONFIG_DIR}/

# Debug: List config files
RUN find ${CONFIG_DIR} -name "config.json"

# Set default config type
ARG CONFIG_TYPE

# Copy type-specific config files
COPY config/${CONFIG_TYPE} ${CONFIG_DIR}/

# Copy init.d script
COPY scripts/comfyui /etc/init.d/comfyui
RUN chmod +x /etc/init.d/comfyui && \
    update-rc.d comfyui defaults

# Copy startup script
COPY scripts/start.sh /scripts/start.sh
RUN chmod +x /scripts/start.sh

COPY scripts ${ROOT}/scripts

RUN rm -rf ${ROOT}/scripts/start.sh && rm -rf ${ROOT}/scripts/comfyui


# RUN usermod -aG crontab ubuntu
# Create cron pid directory with correct permissions
RUN mkdir -p /var/run/cron \
    && touch /var/run/cron/crond.pid \
    && chmod 644 /var/run/cron/crond.pid
RUN sed -i 's/touch $PIDFILE/# touch $PIDFILE/g' /etc/init.d/cron

RUN cd ${ROOT} && git-lfs install 

# Start services and application
CMD ["/scripts/start.sh"]