#!/bin/bash
set -o pipefail  # Capture errors in pipe chains

# Setup logging
LOG_FILE="/home/ubuntu/start.log"
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

CONFIG_DIR="/home/ubuntu/config"
COMFY_DIR="/home/ubuntu/ComfyUI"
CONFIG_FILE="$CONFIG_DIR/config.json"
VENV_DIR="$COMFY_DIR/venv"
COMFY_COMMIT="main"

# Function to download models
download_models() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "No config file found at $CONFIG_FILE"
        return 0
    fi

    # Use the virtual environment's Python and Hugging Face CLI
    VENV_PYTHON="$VENV_DIR/bin/python"
    HUGGINGFACE_CLI="$VENV_DIR/bin/huggingface-cli"

    # Check if Hugging Face CLI is available
    if [ ! -x "$HUGGINGFACE_CLI" ]; then
        log "Hugging Face CLI not found at $HUGGINGFACE_CLI"
        return 1
    fi

    # Try to import huggingface_hub
    if "$VENV_PYTHON" -c "import huggingface_hub" 2>/dev/null; then
        # Login to Hugging Face using environment variable
        if [ -n "$HF_TOKEN" ]; then
            log "Logging into Hugging Face"
            "$VENV_PYTHON" -c "from huggingface_hub import login; login(token='$HF_TOKEN')"
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

    # Create a Python script for downloading with progress
    download_script=$(mktemp)
    cat > "$download_script" << 'EOL'
import sys
import os
import logging
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('/home/ubuntu/start.log', mode='a'),
                              logging.StreamHandler(sys.stderr)])
logger = logging.getLogger(__name__)

def download_with_progress(repo_id, filename, local_dir):
    try:
        # Ensure local directory exists
        os.makedirs(local_dir, exist_ok=True)
        
        # Import huggingface_hub dynamically
        import huggingface_hub
        
        # Log download start
        logger.info(f"Starting download: {filename} from {repo_id}")
        
        # Determine download method based on library version
        if hasattr(huggingface_hub, 'hf_hub_download'):
            # Newer versions of the library
            try:
                path = huggingface_hub.hf_hub_download(
                    repo_id=repo_id, 
                    filename=filename, 
                    local_dir=local_dir,
                    with_tqdm=True
                )
                logger.info(f"Successfully downloaded: {path}")
                print(f"SUCCESS: {path}")
                return 0
            except TypeError:
                # Fallback if with_tqdm is not supported
                path = huggingface_hub.hf_hub_download(
                    repo_id=repo_id, 
                    filename=filename, 
                    local_dir=local_dir,
                    resume_download=True
                )
                logger.info(f"Successfully downloaded: {path}")
                print(f"SUCCESS: {path}")
                return 0
        else:
            # Older versions of the library
            logger.warning("Using older download method")
            path = huggingface_hub.download_file(
                repo_id=repo_id, 
                filename=filename, 
                local_dir=local_dir
            )
            logger.info(f"Successfully downloaded: {path}")
            print(f"SUCCESS: {path}")
            return 0
    
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    repo_id = sys.argv[1]
    filename = sys.argv[2]
    local_dir = sys.argv[3]
    sys.exit(download_with_progress(repo_id, filename, local_dir))
EOL

    # Download each model
    echo "$models" | jq -r '.url' | while read -r url; do
        # Extract model repo and filename from URL
        repo=$(echo "$url" | sed -n 's|https://huggingface.co/\([^/]*/[^/]*\)/.*|\1|p')
        filename=$(basename "$url")
        
        log "Downloading model: $filename from $repo"
        
        # Export HF_HUB_ENABLE_HF_TRANSFER to enable faster downloads
        export HF_HUB_ENABLE_HF_TRANSFER=0

        # Try Hugging Face download with Python script
        "$VENV_PYTHON" "$download_script" "$repo" "$filename" "$models_dir" 2>&1 | while read -r line; do
            if [[ "$line" == SUCCESS:* ]]; then
                log "Successfully downloaded $filename"
            elif [[ "$line" == ERROR:* ]]; then
                log "Failed to download $filename: ${line#ERROR: }"
                
                # Fallback to wget
                log "Attempting wget download for $filename"
                wget -c "$url" -O "$models_dir/$filename" \
                    --progress=dot:giga \
                    2>&1 | while read -r wget_line; do
                        # Parse and log wget progress
                        if [[ "$wget_line" =~ ^[[:space:]]*([0-9]+)% ]]; then
                            progress="${BASH_REMATCH[1]}"
                            log "Download Progress: |$(printf "%0.s=" $(seq 1 $((progress/10))))>$(printf "%0.s " $(seq 1 $((10-progress/10))))| $progress%"
                        fi
                    done

                # Check wget download status
                if [ $? -eq 0 ]; then
                    log "Successfully downloaded $filename using wget"
                else
                    log "CRITICAL: Failed to download $filename"
                    return 1
                fi
            fi
        done
    done

    # Clean up temporary download script
    rm "$download_script"

    return 0
}

# Function to install custom nodes
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
                    source "$VENV_DIR/bin/activate"
                    pip install -r "$name/requirements.txt"
                    deactivate
                fi
            else
                log "Node already exists: $name"
            fi
        fi
    done < <(jq -c '.nodes[]' "$CONFIG_FILE")
}

setup_comfyui() {
    log "Setting up ComfyUI..."

    # Log all environment variables related to configuration
    log "=== Configuration Environment ==="
    log "CONFIG_TYPE: ${CONFIG_TYPE}"
    log "BUILD_CONFIG_TYPE: ${BUILD_CONFIG_TYPE}"
    log "Current Environment Variables:"
    env | grep -E "CONFIG_|BUILD_"

    # Ensure config directory exists with correct permissions
    sudo mkdir -p "$CONFIG_DIR"
    sudo chown ubuntu:ubuntu "$CONFIG_DIR"
    sudo chmod 755 "$CONFIG_DIR"

    # Determine config type, prioritizing environment variable
    CONFIG_TYPE="${CONFIG_TYPE}"
    
    log "Final determined CONFIG_TYPE: $CONFIG_TYPE"
    SERVICE_CONFIG_PATH="/home/ubuntu/config/${CONFIG_TYPE}/config.json"

    # Log the config type and path being used
    log "Checking for config at: $SERVICE_CONFIG_PATH"

    # Strictly check for the specified config type
    if [ ! -f "$SERVICE_CONFIG_PATH" ]; then
        log "ERROR: No config file found for type $CONFIG_TYPE at $SERVICE_CONFIG_PATH"
        log "Listing available config directories:"
        ls -l /home/ubuntu/config/
        exit 1
    fi

    # Copy the config file
    log "Found config file at: $SERVICE_CONFIG_PATH"
    log "Config file contents:"
    cat "$SERVICE_CONFIG_PATH"
    sudo cp "$SERVICE_CONFIG_PATH" "$CONFIG_FILE"

    # Ensure correct permissions
    sudo chown ubuntu:ubuntu "$CONFIG_FILE"
    sudo chmod 644 "$CONFIG_FILE"

    # Ensure ubuntu user owns the ComfyUI directory
    sudo chown -R ubuntu:ubuntu "$COMFY_DIR"
}

setup_nginx() {
    log "Setting up Nginx configuration..."

    if [ -d "/etc/nginx" ]; then
        log "Removing existing nginx config..."
        sudo rm -rf /etc/nginx
    fi

    log "Cloning nginx configuration..."
    if ! sudo git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo; then
        log "Error: Could not clone nginx config repository"
        return 1
    fi

    log "Creating nginx symlink..."
    if ! sudo ln -s /etc/nginx-repo/node /etc/nginx; then
        log "Error: Failed to create nginx symlink"
        return 1
    fi
    
    log "Nginx setup completed successfully"
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
        sudo service cron start
    else
        log "Output directory not found, skipping cron setup"
    fi
}

start_services() {
    log "Starting system services..."
    
    # Try to start nginx with sudo if needed
    log "Attempting to start nginx with root"
    sudo service nginx start
}

setup_ssh_access() {
    log "Setting up SSH access..."
    
    # Ensure SSH directory exists
    mkdir -p /home/ubuntu/.ssh
    chmod 700 /home/ubuntu/.ssh

    # Check and copy SSH keys from root
    if [ -f "/root/.ssh/id_ed25519" ]; then
        cp /root/.ssh/id_ed25519 /home/ubuntu/.ssh/
        chmod 600 /home/ubuntu/.ssh/id_ed25519
        chown ubuntu:ubuntu /home/ubuntu/.ssh/id_ed25519
    else
        log "Warning: No SSH private key found in /root/.ssh/id_ed25519"
    fi

    if [ -f "/root/.ssh/known_hosts" ]; then
        cp /root/.ssh/known_hosts /home/ubuntu/.ssh/
        chmod 644 /home/ubuntu/.ssh/known_hosts
        chown ubuntu:ubuntu /home/ubuntu/.ssh/known_hosts
    else
        log "Warning: No known_hosts file found in /root/.ssh/known_hosts"
    fi

    # Ensure SSH config exists
    touch /home/ubuntu/.ssh/config
    chmod 600 /home/ubuntu/.ssh/config
    chown ubuntu:ubuntu /home/ubuntu/.ssh/config

    # Add GitHub to known hosts if not present
    if ! grep -q "github.com" /home/ubuntu/.ssh/known_hosts; then
        ssh-keyscan github.com >> /home/ubuntu/.ssh/known_hosts 2>/dev/null
    fi
}

main() {
    log "Starting setup process..."

    # SSH Key Setup
    setup_ssh_access

    # Initial setup
    setup_nginx
    setup_comfyui

    # Process config and install components
    if [ -f "$CONFIG_FILE" ]; then
        download_models
        install_nodes
    else
        log "No config found at: $CONFIG_FILE"
        log "Continuing with default configuration..."
    fi

    # Ensure proper permissions
    chown -R ubuntu:ubuntu "$COMFY_DIR"

    # Setup and start services
    setup_services
    start_services

    # Start ComfyUI service
    log "Starting ComfyUI service..."
    service comfyui start

    # Monitor service
    RESTART_ATTEMPTS=0
    MAX_RESTART_ATTEMPTS=5
    COMFYUI_DEBUG_LOG="/home/ubuntu/.comfyui/log/debug.log"

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
