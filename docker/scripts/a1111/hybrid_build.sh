#!/bin/bash

set -Eeuo pipefail

# Log file setup
LOG_DIR="/workspace/logs"
mkdir -p "$LOG_DIR"
BUILD_LOG="$LOG_DIR/hybrid_build.log"
touch "$BUILD_LOG"

# Logging function
log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $*" | tee -a "$BUILD_LOG"
}

log "Starting hybrid ComfyUI + A1111 setup..."

# Create necessary directories
mkdir -p /data/config/auto/scripts/

ROOT_COMFY="/workspace/ComfyUI"
ROOT_A1111="/stable-diffusion-webui"
SHARED_DIR="/workspace/shared"

log "ComfyUI root: $ROOT_COMFY"
log "A1111 root: $ROOT_A1111"
log "Shared models directory: $SHARED_DIR"

# Mount scripts for A1111
find "${ROOT_A1111}/scripts/" -maxdepth 1 -type l -delete
if [ -d "/data/config/auto/scripts/" ]; then
    cp -vrfTs /data/config/auto/scripts/ "${ROOT_A1111}/scripts/"
fi

# Install git-lfs if not already installed
if ! command -v git-lfs &> /dev/null; then
    log "Installing git-lfs..."
    apt-get install -y git-lfs
    git lfs install
fi

# Function to check if a model exists in shared directory
model_exists_in_shared() {
    local model_name=$1
    
    # Check various potential locations
    for path in "${SHARED_DIR}/models/stable-diffusion/${model_name}" \
                "${SHARED_DIR}/models/checkpoints/${model_name}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # Try matching partial filenames (without extensions)
    local base_name=$(basename "$model_name" .safetensors)
    base_name=$(basename "$base_name" .ckpt)
    
    for file in "${SHARED_DIR}/models/stable-diffusion/"*; do
        local file_base=$(basename "$file" .safetensors)
        file_base=$(basename "$file_base" .ckpt)
        
        if [ "$file_base" = "$base_name" ]; then
            echo "$file"
            return 0
        fi
    done
    
    return 1
}

# Function to create symbolic links for A1111
setup_model_symlinks() {
    log "Setting up model symbolic links for A1111..."
    
    # Create A1111 model directories if they don't exist
    mkdir -p "${ROOT_A1111}/models/Stable-diffusion"
    mkdir -p "${ROOT_A1111}/models/VAE"
    mkdir -p "${ROOT_A1111}/models/Lora"
    mkdir -p "${ROOT_A1111}/models/ControlNet"
    mkdir -p "${ROOT_A1111}/models/ESRGAN"
    mkdir -p "${ROOT_A1111}/embeddings"
    
    # Link main model directories
    if [ -d "${SHARED_DIR}/models/stable-diffusion" ]; then
        log "Linking stable diffusion models..."
        find "${SHARED_DIR}/models/stable-diffusion" -type f \( -name "*.safetensors" -o -name "*.ckpt" \) | while read -r model; do
            model_name=$(basename "$model")
            if [ ! -e "${ROOT_A1111}/models/Stable-diffusion/${model_name}" ]; then
                ln -sf "$model" "${ROOT_A1111}/models/Stable-diffusion/${model_name}"
                log "Linked: ${model_name}"
            fi
        done
    fi
    
    # Link VAE models
    if [ -d "${SHARED_DIR}/models/vae" ]; then
        log "Linking VAE models..."
        find "${SHARED_DIR}/models/vae" -type f \( -name "*.safetensors" -o -name "*.ckpt" -o -name "*.pt" \) | while read -r model; do
            model_name=$(basename "$model")
            if [ ! -e "${ROOT_A1111}/models/VAE/${model_name}" ]; then
                ln -sf "$model" "${ROOT_A1111}/models/VAE/${model_name}"
                log "Linked VAE: ${model_name}"
            fi
        done
    fi
    
    # Link LoRA models
    if [ -d "${SHARED_DIR}/models/lora" ]; then
        log "Linking LoRA models..."
        find "${SHARED_DIR}/models/lora" -type f \( -name "*.safetensors" -o -name "*.ckpt" -o -name "*.pt" \) | while read -r model; do
            model_name=$(basename "$model")
            if [ ! -e "${ROOT_A1111}/models/Lora/${model_name}" ]; then
                ln -sf "$model" "${ROOT_A1111}/models/Lora/${model_name}"
                log "Linked LoRA: ${model_name}"
            fi
        done
    fi
    
    # Link ControlNet models
    if [ -d "${SHARED_DIR}/models/controlnet" ]; then
        log "Linking ControlNet models..."
        find "${SHARED_DIR}/models/controlnet" -type f \( -name "*.safetensors" -o -name "*.ckpt" -o -name "*.pt" -o -name "*.pth" \) | while read -r model; do
            model_name=$(basename "$model")
            if [ ! -e "${ROOT_A1111}/models/ControlNet/${model_name}" ]; then
                ln -sf "$model" "${ROOT_A1111}/models/ControlNet/${model_name}"
                log "Linked ControlNet: ${model_name}"
            fi
        done
    fi
    
    # Link ESRGAN upscalers
    if [ -d "${SHARED_DIR}/models/upscale" ]; then
        log "Linking upscaler models..."
        find "${SHARED_DIR}/models/upscale" -type f -name "*.pth" | while read -r model; do
            model_name=$(basename "$model")
            if [ ! -e "${ROOT_A1111}/models/ESRGAN/${model_name}" ]; then
                ln -sf "$model" "${ROOT_A1111}/models/ESRGAN/${model_name}"
                log "Linked Upscaler: ${model_name}"
            fi
        done
    fi
    
    # Link embeddings/textual inversions
    if [ -d "${SHARED_DIR}/embeddings" ]; then
        log "Linking embeddings..."
        find "${SHARED_DIR}/embeddings" -type f \( -name "*.pt" -o -name "*.bin" -o -name "*.safetensors" \) | while read -r embedding; do
            embedding_name=$(basename "$embedding")
            if [ ! -e "${ROOT_A1111}/embeddings/${embedding_name}" ]; then
                ln -sf "$embedding" "${ROOT_A1111}/embeddings/${embedding_name}"
                log "Linked Embedding: ${embedding_name}"
            fi
        done
    fi
    
    log "Model linking complete"
}

# Download a model only if it doesn't exist in shared directory
download_if_needed() {
    local model_name=$1
    local download_url=$2
    local target_dir="${ROOT_A1111}/models/Stable-diffusion"
    
    # Check if model exists in shared directory
    local existing_path=$(model_exists_in_shared "$model_name")
    if [ -n "$existing_path" ]; then
        log "Model $model_name already exists at $existing_path"
        # Create symbolic link if it doesn't exist
        if [ ! -e "${target_dir}/${model_name}" ]; then
            ln -sf "$existing_path" "${target_dir}/${model_name}"
            log "Created symlink for $model_name"
        fi
    else
        log "Downloading $model_name from $download_url"
        wget --no-verbose --show-progress --progress=bar:force:noscroll "$download_url" -O "${target_dir}/${model_name}"
        log "Downloaded $model_name"
    fi
}

# Install PM2 for process management
if ! command -v pm2 &> /dev/null; then
    log "Installing PM2..."
    apt-get install -y ca-certificates curl gnupg
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
    apt-get update
    apt-get install -y nodejs
    npm install -g npm@9.8.0
    npm install -g pm2@latest
fi

log "PM2 status:"
pm2 status || true

# Copy error catching script
cp /docker/error_catch_all.sh ~/.pm2/logs/error_catch_all.sh 2>/dev/null || true

# Set up config file
if [ -f "/docker/config.py" ]; then
    python /docker/config.py /data/config/auto/config.json
fi

# Setup basic config files
if [ ! -f /data/config/auto/ui-config.json ]; then
    echo '{}' > /data/config/auto/ui-config.json
fi

if [ ! -f /data/config/auto/styles.csv ]; then
    touch /data/config/auto/styles.csv
fi

# Create mount directories
log "Setting up mount directories..."
mkdir -p /data/.cache /data/models /data/embeddings /data/config/auto

# Setup symbolic links for A1111 models and configs
setup_model_symlinks

# Dictionary of mount points
declare -A MOUNTS

MOUNTS["/root/.cache"]="/data/.cache"
MOUNTS["${ROOT_A1111}/config.json"]="/data/config/auto/config.json"
MOUNTS["${ROOT_A1111}/ui-config.json"]="/data/config/auto/ui-config.json"
MOUNTS["${ROOT_A1111}/styles.csv"]="/data/config/auto/styles.csv"
MOUNTS["${ROOT_A1111}/extensions"]="/data/config/auto/extensions"
MOUNTS["${ROOT_A1111}/config_states"]="/data/config/auto/config_states"

# Set up mount points
for to_path in "${!MOUNTS[@]}"; do
    set -Eeuo pipefail
    from_path="${MOUNTS[${to_path}]}"
    rm -rf "${to_path}" 2>/dev/null || true
    if [ ! -f "$from_path" ] && [ ! -d "$from_path" ]; then
        mkdir -vp "$from_path"
    fi
    mkdir -vp "$(dirname "${to_path}")" 2>/dev/null || true
    ln -sT "${from_path}" "${to_path}" 2>/dev/null || true
    log "Mounted $(basename "${from_path}")"
done

# Check if we need to download specific models
# These will only download if not already in the shared directory
cd "${ROOT_A1111}/models/Stable-diffusion"

MODELS=""

# Download essential models only if they don't exist in shared directory
download_if_needed "JuggernautXL_v8Rundiffusion.safetensors" "https://civitai.com/api/download/models/288982?type=Model&format=SafeTensor&size=full&fp=fp16"
MODELS+="JuggernautXL_v8Rundiffusion.safetensors,"

download_if_needed "epiCPhotoGasm.safetensors" "https://civitai.com/api/download/models/223670?type=Model&format=SafeTensor&size=full&fp=fp16"
MODELS+="epiCPhotoGasm.safetensors,"

download_if_needed "v1-5-pruned.safetensors" "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors"
MODELS+="v1-5-pruned.safetensors,"

download_if_needed "v2-1_768-ema-pruned.safetensors" "https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors"
MODELS+="v2-1_768-ema-pruned.safetensors,"

download_if_needed "sd_xl_base_1.0_0.9vae.safetensors" "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors"
MODELS+="sd_xl_base_1.0_0.9vae.safetensors,"

download_if_needed "sd_xl_refiner_1.0_0.9vae.safetensors" "https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0_0.9vae.safetensors"
MODELS+="sd_xl_refiner_1.0_0.9vae.safetensors,"

# Return to the original directory
cd "${ROOT_A1111}"

# Start the error catcher
cd ~/.pm2/logs && pm2 start --name error_catch_all "./error_catch_all.sh" || true

# Start the A1111 web UI
log "Starting A1111 web UI with PM2..."
cd "${ROOT_A1111}" && pm2 start --name webui "python -u webui.py --opt-sdp-no-mem-attention --api --port 3130 --medvram --no-half-vae"

# Set up NGINX if needed
if [ -d "/etc/nginx" ]; then
    log "Starting NGINX service..."
    service nginx start
else
    log "NGINX directory not found, skipping..."
fi

# Wait for A1111 to start up
log "Waiting for A1111 to start up before loading models..."
sleep 75

# Load models via the API
log "Loading models: ${MODELS}"
IFS=, read -r -a models <<<"${MODELS}"
for model in "${models[@]}"; do 
    if [ -n "$model" ]; then
        echo "$model" 
        python /docker/loader.py -m "$model" || true
    fi
done

log "A1111 setup completed successfully"
echo "~~READY~~"
