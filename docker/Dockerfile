# Builder stage for SSH key
FROM pytorch/pytorch:latest as start

RUN apt update && apt-get install -y \
    git git-lfs rsync nginx wget curl nano ffmpeg libsm6 libxext6 \
    cron sudo ssh zstd jq build-essential cmake ninja-build \
    gcc g++ openssh-client aria2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM start AS middle

ENV ROOT=/workspace
ENV PATH="${ROOT}/.local/bin:${PATH}"
ENV CONFIG_DIR=${ROOT}/config
ENV COMFY_DIR=${ROOT}/ComfyUI

WORKDIR ${ROOT}

RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFY_DIR} && \
    cd ${COMFY_DIR} && \
    pip install --upgrade pip && \
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
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

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
CMD ["/start.sh"]