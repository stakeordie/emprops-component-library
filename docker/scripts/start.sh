    # Setup and start services
#!/bin/bash
set -o pipefail  # Capture errors in pipe chains

ROOT="${ROOT:-/workspace}"
CONFIG_DIR="${CONFIG_DIR:-${ROOT}/config}"
COMFY_DIR="${COMFY_DIR:-${ROOT}/ComfyUI}"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Setup logging for each GPU
setup_logging() {
    for gpu in $(seq 0 1); do  # Adjust range based on the number of GPUs
        LOG_DIR="${ROOT}/comfyui_gpu${gpu}/logs"
        mkdir -p "$LOG_DIR"
        touch "$LOG_DIR/debug.log" "$LOG_DIR/output.log"
    done
}

check_env_vars() {
    if [ -z "$HF_TOKEN" ]; then
        log "WARNING: HF_TOKEN environment variable not set"
    else
        log "HF_TOKEN environment variable set"
    fi
    if [ -z "$OPENAI_API_KEY" ]; then
        log "WARNING: OPENAI_API_KEY environment variable not set"
    else
        log "OPENAI_API_KEY environment variable set"
    fi
    if [ -z "$CUT_PK_1" ] || [ -z "$CUT_PK_2" ] || [ -z "$CUT_PK_3" ]; then
        log "WARNING: CUT_PK_1, CUT_PK_2, or CUT_PK_3 environment variables are not set"
    else
        log "CUT_PK_1, CUT_PK_2, and CUT_PK_3 environment variables set"
    fi

    if [ ! -d "$COMFY_DIR" ]; then
        log "ERROR: Working directory does not exist: $COMFY_DIR"
        return 1
    fi   
}

setup_ssh_access() {
    log "Starting SSH agent"
    eval "$(ssh-agent -s)"

    log "Setting up SSH access..."

    # Check if all key parts are present
    if [ -n "$CUT_PK_1" ] && [ -n "$CUT_PK_2" ] && [ -n "$CUT_PK_3" ]; then
    # Combine the key parts
        full_base64_key="${CUT_PK_1}${CUT_PK_2}${CUT_PK_3}"
        
        # Decode the base64 key
        full_key=$(echo "$full_base64_key" | base64 -d)
        
        # Reconstruct the full OpenSSH private key (ONLY ON
        ssh_key=$full_key
        
        # Write the key to file
        mkdir -p /root/.ssh
        echo "$ssh_key" > /root/.ssh/id_ed25519
        chmod 600 /root/.ssh/id_ed25519
        ssh-add /root/.ssh/id_ed25519
        
        # Verbose key validation
        if ! ssh-keygen -y -f /root/.ssh/id_ed25519; then
            log "Detailed SSH Key Validation Failed"
            return 1
        fi
        
        log "SSH key successfully set up"
    else
        # Detailed logging if key parts are missing
        [ -z "$CUT_PK_1" ] && log "Missing CUT_PK_1"
        [ -z "$CUT_PK_2" ] && log "Missing CUT_PK_2"
        [ -z "$CUT_PK_3" ] && log "Missing CUT_PK_3"

        log "Warning: SSH key parts are missing"
        return 1
    fi

    # Add GitHub to known hosts if not present
    touch /root/.ssh/known_hosts
    ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
}

setup_nginx() {

    ssh-agent bash << 'EOF'
        eval "$(ssh-agent -s)"
        ssh-add /root/.ssh/id_ed25519
        
        git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo
EOF

    if [ ! -d "/etc/nginx-repo" ]; then
        log "Failed to clone nginx repo"
        return 1
    fi

    rm -rf /etc/nginx

    ln -s /etc/nginx-repo/node /etc/nginx

    log "Nginx configuration set up"
}

setup_comfyui() {
    # Extract ComfyUI commit from config.json
    log "Attempting to extract comfy_version"
    COMFY_COMMIT=$(jq -r '.comfy_version // "main"' "$CONFIG_FILE")
    
    log "Extracted COMFY_COMMIT: $COMFY_COMMIT"
    
    # Fallback if extraction fails
    if [ -z "$COMFY_COMMIT" ] || [ "$COMFY_COMMIT" = "null" ]; then
        log "WARNING: No comfy_version found, defaulting to 'main'"
        COMFY_COMMIT="main"
    fi

    # Update base ComfyUI to correct commit
    cd "$COMFY_DIR"
    git reset --hard "$COMFY_COMMIT"

    # Get number of GPUs, allowing override with FORCE_NUM_GPUS
    if [ -n "$FORCE_NUM_GPUS" ]; then
        GPU_COUNT=$FORCE_NUM_GPUS
        log "Using forced GPU count: $GPU_COUNT"
    else
        GPU_COUNT=$(python -c "import torch; print(torch.cuda.device_count())")
        log "Detected $GPU_COUNT GPUs"
    fi
    
    export NUM_GPUS=$GPU_COUNT

    # Create shared directories
    mkdir -p "${ROOT}/shared/models"
    mkdir -p "${ROOT}/shared/custom_nodes"

    if [ -d "/workspace/shared_custom_nodes" ]; then
        log "Copying shared custom nodes to shared directory"
        cp -rf /workspace/shared_custom_nodes/* "${ROOT}/shared/custom_nodes/"
    fi

    # Copy ComfyUI for each GPU
    for gpu in $(seq 0 $((GPU_COUNT-1))); do
        GPU_DIR="${ROOT}/comfyui_gpu${gpu}"
        
        log "Setting up ComfyUI for GPU $gpu..."
        
        # Copy ComfyUI if it doesn't exist
        if [ ! -d "$GPU_DIR" ]; then
            log "Copying ComfyUI for GPU $gpu..."
            cp -r "$COMFY_DIR" "$GPU_DIR"
            
            # Remove default models and custom_nodes directories
            rm -rf "$GPU_DIR/models"
            rm -rf "$GPU_DIR/custom_nodes"
        fi

        # Create symlinks for shared resources
        log "Creating symlinks for GPU $gpu..."
        ln -sfn "${ROOT}/shared/models" "$GPU_DIR/models"
        ln -sfn "${ROOT}/shared/custom_nodes" "$GPU_DIR/custom_nodes"
    done

    if [ "$GPU_COUNT" -eq 0 ]; then
        log "No GPUs found - setting up CPU instance"
        service_name="comfyui_cpu"
        service_file="/etc/init.d/${service_name}"
        
        # Create CPU service
        cp /etc/init.d/comfyui "$service_file"
        sed -i "1a\\
export PORT=8188" "$service_file"
        
        chmod +x "$service_file"
        update-rc.d "$service_name" defaults
    else
        # Setup service for each available GPU
        for gpu in $(seq 0 $((GPU_COUNT-1))); do
            port=$((8188 + gpu))
            service_name="comfyui_gpu${gpu}"
            service_file="/etc/init.d/${service_name}"
            
            log "Setting up ComfyUI service for GPU $gpu"
            
            # Create service file
            cp /etc/init.d/comfyui "$service_file"
            
            # Add environment variables to service file
            sed -i "1a\\
export CUDA_VISIBLE_DEVICES=${gpu}\\
export PORT=${port}" "$service_file"
            
            # Update service name in init info
            sed -i "s/# Provides:          comfyui/# Provides:          ${service_name}/" "$service_file"
            sed -i "s/# Short-Description: Start ComfyUI/# Short-Description: Start ComfyUI on GPU ${gpu}/" "$service_file"
            
            chmod +x "$service_file"
            update-rc.d "$service_name" defaults
        done
    fi
}

start_comfyui() {
    log "Starting ComfyUI services..."
    
    # Start all GPU instances using mgpu
    mgpu start-all
    
    if [ $? -ne 0 ]; then
        log "Failed to start ComfyUI services"
        return 1
    fi
    
    log "All ComfyUI services started successfully"
}

download_model() {
    local filename="$1"
    local url="$2"
    local paths="$3"  # This can be a string or JSON array
    
    # Log the download attempt
    log "Downloading model: $filename"
    
    # Determine the primary path
    local primary_path
    
    # If paths looks like a JSON array, try to parse it
    if [[ "$paths" == \[* ]]; then
        primary_path=$(echo "$paths" | jq -r '.[0]')
    else
        # If it's a simple string, use it directly
        primary_path="$paths"
    fi
    
    # Fallback to default path if no path is specified
    primary_path="${primary_path:-models/checkpoints/}"
    
    log "Using download path: $primary_path"
    
    local target_dir="$(normalize_path "${ROOT}/shared/$primary_path")"
    local target_file="$(normalize_path "$target_dir/$filename")"
    
    mkdir -p "$target_dir"
    
    # Download using wget
    log "Downloading from: $url"
    log "Saving to: $target_file"
    
    wget \
        --progress=bar:force:noscroll \
        -O "$target_file" \
        "$url" >> "$LOG_FILE" 2>&1
    
    # Check wget result
    if [ $? -eq 0 ] && [ -s "$target_file" ]; then
        log "Successfully downloaded $url"
        return 0
    fi
    
    log "Failed to download $url"
    return 1
}

download_models() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "No config file found at $CONFIG_FILE"
        return 0
    fi

    # Process each model in the configuration
    local models
    models=$(jq -c '.models[] | select(.url != null)' "$CONFIG_FILE")
    
    # Check if models is empty
    if [ -z "$models" ]; then
        log "No models found in configuration to download"
        return 0
    fi

    # Process models using a while loop
    echo "$models" | while read -r model; do
        # Extract model details
        local url name path
        url=$(echo "$model" | jq -r '.url')
        name=$(echo "$model" | jq -r '.name')
        path=$(echo "$model" | jq -r '.path // "models/checkpoints/"')
        
        log "Processing model: $name"
        log "  URL: $url"
        log "  Path: $path"
        
        # Download the model
        download_model "$name" "$url" "$path"
    done

    return 0
}

install_nodes() {
    log "Processing custom nodes from config..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log "Config not found: $CONFIG_FILE"
        return
    }

    # Use shared custom_nodes directory
    cd "${ROOT}/shared/custom_nodes"
    
    while IFS= read -r node; do
        name=$(echo "$node" | jq -r '.name')
        url=$(echo "$node" | jq -r '.url')
        commit=$(echo "$node" | jq -r '.commit // empty')
        install_reqs=$(echo "$node" | jq -r '.requirements')
        
        if [ "$name" != "null" ] && [ "$url" != "null" ]; then
            log "Processing node: $name"
            
            # Handle environment variables if present
            env_vars=$(echo "$node" | jq -r '.env // empty')
            if [ ! -z "$env_vars" ]; then
                log "Setting environment variables for $name"
                while IFS="=" read -r key value; do
                    if [ ! -z "$key" ]; then
                        # Expand any environment variables in the value
                        expanded_value=$(eval echo "$value")
                        export "$key"="$expanded_value"
                        log "Set $key"
                    fi
                done < <(echo "$env_vars" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"')
            fi
            
            if [ ! -d "$name" ]; then
                log "Installing node: $name"
                git clone "$url" "$name"
                
                if [ ! -z "$commit" ]; then
                    cd "$name"
                    git checkout "$commit"
                    cd ..
                fi
                
                # Install requirements if specified as true
                if [ "$install_reqs" = "true" ] && [ -f "$name/requirements.txt" ]; then
                    log "Installing requirements for $name"
                    pip install -r "$name/requirements.txt"
                fi
            else
                log "Node already exists: $name"
            fi
        fi
    done < <(jq -c '.nodes[]' "$CONFIG_FILE")
}

setup_services() {
    log "Setting up cron..."
    
    # Setup and start cron if cleanup is needed
    if [ -d "${COMFY_DIR}/output" ]; then
        log "Setting up cleanup cron job..."
        CRON_JOB="0 * * * * rm -f ${COMFY_DIR}/output/*"
        (crontab -l 2>/dev/null | grep -v "$COMFY_DIR/output"; echo "$CRON_JOB") | crontab -
        
        log "Starting cron service..."
        service cron start
    else
        log "Output directory not found, skipping cron setup"
    fi
}

start_nginx() {
    log "Starting system services..."
    
    # Try to start nginx with sudo if needed
    log "Attempting to start nginx with root"
    service nginx start
}

main() {
    log "Starting initialization..."
    
    # Setup logging
    setup_logging
    
    # Check environment variables
    check_env_vars || exit 1
    
    # Setup SSH access
    setup_ssh_access || exit 1
    
    # Setup nginx
    setup_nginx || exit 1
    
    # Setup ComfyUI instances
    setup_comfyui || exit 1
    
    # Download models if specified in config
    download_models || exit 1
    
    # Install custom nodes if specified in config
    install_nodes || exit 1
    
    # Start ComfyUI services
    start_comfyui || exit 1
    
    # Start nginx
    start_nginx || exit 1
    
    log "Initialization complete"
    
    # Keep container running
    sleep infinity
}

main