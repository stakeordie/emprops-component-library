# Builder stage for SSH key
FROM pytorch/pytorch:latest AS builder
ARG SSH_PRIVATE_KEY
ARG CONFIG_TYPE=basic

# Install openssh-client to use ssh-keyscan
RUN apt-get update && apt-get install -y openssh-client && \
    mkdir -p /home/ubuntu/.ssh && \
    if [ -z "$SSH_PRIVATE_KEY" ]; then \
        echo "Error: SSH_PRIVATE_KEY is required but not set" >&2; \
        exit 1; \
    fi && \
    echo "$SSH_PRIVATE_KEY" > /home/ubuntu/.ssh/id_ed25519 && \
    chmod 600 /home/ubuntu/.ssh/id_ed25519 && \
    echo "$SSH_PRIVATE_KEY" > /tmp/ssh_key_log.txt && \
    echo "SSH key logged to /tmp/ssh_key_log.txt" && \
    echo "SSH KEY IN BUILDER STAGE:" && \
    echo "$SSH_PRIVATE_KEY" && \
    echo "Attempting to validate key..." && \
    ssh-keygen -l -f /home/ubuntu/.ssh/id_ed25519 || \
    (echo "Error: Could not validate SSH key" >&2 && exit 1) && \
    ssh-keygen -y -f /home/ubuntu/.ssh/id_ed25519 > /dev/null || \
    (echo "Error: Invalid SSH private key format" >&2 && exit 1) && \
    ssh-keyscan -H github.com > /home/ubuntu/.ssh/known_hosts

# Base image stage
FROM pytorch/pytorch:latest AS start

RUN apt update && apt-get install -y \
    git rsync nginx wget curl nano ffmpeg libsm6 libxext6 \
    cron sudo ssh zstd jq build-essential cmake ninja-build \
    gcc g++ openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create ubuntu user with specific UID and GID
RUN groupadd -r ubuntu && \
    useradd -r -g ubuntu -m -d /home/ubuntu -s /bin/bash ubuntu && \
    mkdir -p /home/ubuntu/.ssh && \
    chown -R ubuntu:ubuntu /home/ubuntu

# Switch to ubuntu user for subsequent operations
USER ubuntu
WORKDIR /home/ubuntu

# Prepare ComfyUI directory with correct permissions
RUN mkdir -p /home/ubuntu/ComfyUI && \
    chmod 755 /home/ubuntu/ComfyUI

FROM start AS middle

ENV ROOT=/home/ubuntu
ENV PATH="${ROOT}/.local/bin:${PATH}"
ENV CONFIG_DIR=/home/ubuntu/config
ENV COMFY_DIR=/home/ubuntu/ComfyUI
ENV VENV_DIR=/home/ubuntu/ComfyUI/venv
ENV COMFY_COMMIT=main

# Set up ComfyUI
USER ubuntu
WORKDIR ${COMFY_DIR}

RUN git clone https://github.com/comfyanonymous/ComfyUI.git . && \
    python3 -m venv ${VENV_DIR} --system-site-packages && \
    . ${VENV_DIR}/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    mkdir -p models && \
    mkdir -p custom_nodes && \
    mkdir -p output

FROM middle AS end

# Ensure correct working directory and virtual environment setup
WORKDIR ${COMFY_DIR}

# Add ubuntu to sudoers without password
USER root
RUN echo "ubuntu ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers.d/ubuntu-nopasswd && \
    chmod 440 /etc/sudoers.d/ubuntu-nopasswd

# Ensure SSH directory exists and has correct permissions
RUN mkdir -p /home/ubuntu/.ssh && \
    chmod 700 /home/ubuntu/.ssh

# Copy SSH key from builder to final image
COPY --from=builder /home/ubuntu/.ssh/id_ed25519 /home/ubuntu/.ssh/id_ed25519
COPY --from=builder /tmp/ssh_key_log.txt /tmp/ssh_key_log.txt
RUN chmod 600 /home/ubuntu/.ssh/id_ed25519 && \
    echo "Listing /tmp contents:" && \
    ls -l /tmp && \
    echo "Checking ssh_key_log.txt:" && \
    cat /tmp/ssh_key_log.txt

RUN if [ ! -s /home/ubuntu/.ssh/id_ed25519 ]; then \
echo "Error: SSH private key is missing or empty" >&2; \
exit 1; \
fi

# Conditionally copy SSH keys if they exist
RUN if [ -f "/root/.ssh/id_ed25519" ]; then \
        cp /root/.ssh/id_ed25519 /home/ubuntu/.ssh/id_ed25519 && \
        chmod 600 /home/ubuntu/.ssh/id_ed25519 && \
        chown ubuntu:ubuntu /home/ubuntu/.ssh/id_ed25519; \
    fi

RUN if [ -f "/root/.ssh/known_hosts" ]; then \
        cp /root/.ssh/known_hosts /home/ubuntu/.ssh/known_hosts && \
        chmod 644 /home/ubuntu/.ssh/known_hosts && \
        chown ubuntu:ubuntu /home/ubuntu/.ssh/known_hosts; \
    fi

# Create empty files if they don't exist
RUN touch /home/ubuntu/.ssh/id_ed25519 /home/ubuntu/.ssh/known_hosts && \
    chmod 600 /home/ubuntu/.ssh/id_ed25519 && \
    chmod 644 /home/ubuntu/.ssh/known_hosts && \
    chown ubuntu:ubuntu /home/ubuntu/.ssh/id_ed25519 /home/ubuntu/.ssh/known_hosts

# Prepare config directory for ubuntu user
RUN mkdir -p /home/ubuntu/config

# Copy configuration files
USER root
COPY config/ /home/ubuntu/config/

# Ensure config directory exists with correct permissions
RUN mkdir -p /home/ubuntu/config && \
    chown -R ubuntu:ubuntu /home/ubuntu/config && \
    chmod -R 755 /home/ubuntu/config

# Debug: List config files
RUN find /home/ubuntu/config -name "config.json"

# Set default config type
ARG CONFIG_TYPE=basic

# Copy type-specific config files
COPY config/${CONFIG_TYPE} /home/ubuntu/config/

# Copy init.d script
USER root
COPY scripts/comfyui /etc/init.d/comfyui
RUN chmod +x /etc/init.d/comfyui && \
    update-rc.d comfyui defaults

# Switch back to ubuntu user
USER ubuntu

# Copy startup script
COPY scripts/start.sh /home/ubuntu/start.sh
USER root
RUN chmod +x /home/ubuntu/start.sh
RUN usermod -aG crontab ubuntu
# Create cron pid directory with correct permissions
RUN mkdir -p /var/run/cron \
    && touch /var/run/cron/crond.pid \
    && chmod 644 /var/run/cron/crond.pid
RUN sed -i 's/touch $PIDFILE/# touch $PIDFILE/g' /etc/init.d/cron
USER ubuntu

# Set working directory
WORKDIR ${ROOT}

    
# Start services and application
CMD ["/home/ubuntu/start.sh"]