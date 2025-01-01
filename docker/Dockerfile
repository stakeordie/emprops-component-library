# Builder stage for SSH key
FROM pytorch/pytorch:latest AS start

RUN apt update && apt-get install -y \
    git git-lfs rsync nginx wget curl nano net-tools lsof nvtop multitail ffmpeg libsm6 libxext6 \
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
    ln -sf libstdc++.so.6.0.30 libstdc++.so.6

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
    pip uninstall onnxruntime && \
    pip install --upgrade pip && \
    pip install --upgrade onnxruntime-gpu mmengine opencv-python imgui-bundle pyav boto3 awscli && \
    pip install -r requirements.txt

FROM middle AS shared

RUN cd ${ROOT} && rm -rf ${COMFY_DIR}

COPY config/shared ${ROOT}/shared_custom_nodes

RUN find ${ROOT}/shared_custom_nodes -name "requirements.txt" -execdir pip install -r {} \;

FROM shared AS end

# Copy init.d script
COPY scripts/comfyui /etc/init.d/comfyui

RUN chmod +x /etc/init.d/comfyui && \
    update-rc.d comfyui defaults

COPY ./scripts/mgpu /usr/local/bin/mgpu
RUN chmod +x /usr/local/bin/mgpu

# Copy startup script
COPY scripts/start.sh /scripts/start.sh
RUN chmod +x /scripts/start.sh

# Add build argument for cache busting
ARG CACHEBUST=1

RUN --mount=type=cache,target=/root/.cache/pip mkdir -p ${ROOT}/shared && \
    CACHEBUST=${CACHEBUST} git clone https://github.com/stakeordie/emprops_shared.git ${ROOT}/shared

# RUN usermod -aG crontab ubuntu
# Create cron pid directory with correct permissions
RUN mkdir -p /var/run/cron \
    && touch /var/run/cron/crond.pid \
    && chmod 644 /var/run/cron/crond.pid
RUN sed -i 's/touch $PIDFILE/# touch $PIDFILE/g' /etc/init.d/cron

RUN cd ${ROOT} && git-lfs install 

# Copy cleanup script and setup cron
COPY scripts/cleanup_outputs.sh /usr/local/bin/cleanup_outputs.sh
RUN chmod +x /usr/local/bin/cleanup_outputs.sh && \
    echo "*/15 * * * * /usr/local/bin/cleanup_outputs.sh >> /var/log/cleanup.log 2>&1" > /etc/cron.d/cleanup && \
    chmod 0644 /etc/cron.d/cleanup && \
    mkdir -p /var/run/cron && \
    touch /var/run/cron/crond.pid && \
    chmod 644 /var/run/cron/crond.pid && \
    sed -i 's/touch $PIDFILE/# touch $PIDFILE/g' /etc/init.d/cron
    
# Start services and application
CMD ["/scripts/start.sh"]