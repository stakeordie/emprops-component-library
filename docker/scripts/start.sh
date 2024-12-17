#!/bin/bash
set -o pipefail  # Capture errors in pipe chains

ROOT="${ROOT:-/workspace}"
CONFIG_DIR="${CONFIG_DIR:-${ROOT}/config}"
COMFY_DIR="${COMFY_DIR:-${ROOT}/ComfyUI}"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Setup logging
LOG_FILE="${ROOT}/start.log"
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
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
    else 
        log "Switching ComfyUI to commit: $COMFY_COMMIT"

        # Change to ComfyUI directory and checkout specified commit
        cd "$COMFY_DIR"
        git checkout "$COMFY_COMMIT"
    fi
}
# Function to download models
download_models() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "No config file found at $CONFIG_FILE"
        return 0
    fi

    HF_HUB_ENABLE_HF_TRANSFER=1


    # Try to import huggingface_hub
    if python -c "import huggingface_hub" 2>/dev/null; then
        # Login to Hugging Face using environment variable
        if [ -n "$HF_TOKEN" ]; then
            log "Logging into Hugging Face"
            python -c "from huggingface_hub import login; login(token='$HF_TOKEN')"
        fi

    else
        log "huggingface_hub not found. Falling back to wget downloads."
        return 1
    fi

    local models_dir="/home/ubuntu/ComfyUI/models/checkpoints"
    mkdir -p "$models_dir"

    # Verbose model parsing
    local models=$(jq -c '.models[] | 
        select(.url != null) | 
        {
            url: .url, 
            path: (.path // "models/checkpoints/"),
            name: .name
        }' "$CONFIG_FILE" 2>&1)
    
    log "Parsed Models:"
    echo "$models" >> "$LOG_FILE"

    # Check if models is empty
    if [ -z "$models" ]; then
        log "No models found in configuration to download"
        return 0
    fi

    # Download each model
    echo "$models" | jq -r '.url, .name, .path' | while read -r url; read -r name; read -r paths; do
        download_model "$name" "$url" "$paths"
    done

    return 0
}

download_model() {
    local filename="$1"
    local url="$2"
    local paths="$3"  # This can now be a JSON array
    
    # Log the download attempt
    log "Downloading model: $filename"
    
    # Parse paths array (if it's an array, first path is the download location)
    local primary_path
    local other_paths=()
    
    if [[ $paths == '['* ]]; then
        # It's a JSON array, extract paths
        primary_path=$(echo "$paths" | jq -r '.[0]')
        readarray -t other_paths < <(echo "$paths" | jq -r '.[1:][]')
    else
        # Single path
        primary_path="$paths"
    fi
    
    # Ensure the primary directory exists
    mkdir -p "$COMFY_DIR/$primary_path"
    
    local target_file="$COMFY_DIR/$primary_path$filename"
    
    # First, try using Python script for Hugging Face download
    if [[ "$url" == *"huggingface.co"* ]]; then
        "python" "${ROOT}/scripts/download_model.py" \
            "$url" "$COMFY_DIR/$primary_path" "$filename" >> "$LOG_FILE" 2>&1
        
        # Check download result
        if [ $? -eq 0 ] && [ -s "$target_file" ]; then
            echo "Successfully downloaded $url using Python script" >> "$LOG_FILE"
            # Create symlinks if there are additional paths
            for additional_path in "${other_paths[@]}"; do
                mkdir -p "$COMFY_DIR/$additional_path"
                ln -sf "$target_file" "$COMFY_DIR/$additional_path$filename"
                log "Created symlink at $COMFY_DIR/$additional_path$filename"
            done
            return 0
        fi
    fi

    # If Python script fails or not a HF URL, try wget
    wget \
        --progress=bar:force:noscroll \
        -O "$COMFY_DIR/$primary_path/$filename" \
        "$url" >> "$LOG_FILE" 2>&1
    
    # Check wget result
    if [ $? -eq 0 ] && [ -s "$target_file" ]; then
        echo "Successfully downloaded $url using wget" >> "$LOG_FILE"
        # Create symlinks if there are additional paths
        for additional_path in "${other_paths[@]}"; do
            mkdir -p "$COMFY_DIR/$additional_path"
            ln -sf "$target_file" "$COMFY_DIR/$additional_path$filename"
            log "Created symlink at $COMFY_DIR/$additional_path$filename"
        done
        return 0
    fi

    # If both methods fail
    echo "Failed to download $url" >> "$LOG_FILE"
    return 1
}

install_nodes() {
    log "Processing custom nodes from config..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log "Config not found: $CONFIG_FILE"
        return
    fi

    cd "$COMFY_DIR/custom_nodes"
    
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
    log "Setting up init.d service and cron..."
    
    # Setup init.d service
    update-rc.d comfyui defaults
    
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
    log "Starting setup process..."

    # Check environment variables
    check_env_vars

    # SSH Key Setup
    setup_ssh_access

    # Initial setup
    setup_nginx
    setup_comfyui

    # Process config and install components
    if [ -f "$CONFIG_FILE" ]; then
        install_nodes
        download_models
    else
        log "No config found at: $CONFIG_FILE"
        log "Continuing with default configuration..."
    fi

    # Setup and start services
    setup_services
    start_nginx

    # Start ComfyUI service
    log "Starting ComfyUI service..."
    service comfyui start

    # Monitor service
    RESTART_ATTEMPTS=0
    MAX_RESTART_ATTEMPTS=5
    COMFYUI_DEBUG_LOG="$ROOT/.comfyui/log/debug.log"

    while true; do
        if ! service comfyui status >/dev/null 2>&1; then
            log "ComfyUI service stopped unexpectedly"
            log "=== ComfyUI Debug Log ==="
            tail -n 50 "$COMFYUI_DEBUG_LOG"
            
            if [ $RESTART_ATTEMPTS -lt $MAX_RESTART_ATTEMPTS ]; then
                log "Attempting to restart ComfyUI service (Attempt $((RESTART_ATTEMPTS+1))/$MAX_RESTART_ATTEMPTS)..."
                service comfyui start
                RESTART_ATTEMPTS=$((RESTART_ATTEMPTS+1))
            else
                log "MAX RESTART ATTEMPTS REACHED. Giving up on ComfyUI service."
                break
            fi
        else
            # Reset restart attempts if service is running successfully
            RESTART_ATTEMPTS=0
        fi
        sleep 30
    done
}

main

log "SLEEPING..."

sleep infinity
