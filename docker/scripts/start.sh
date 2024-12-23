#!/bin/bash
# Only enable debug mode if DEBUG is set
if [ "${DEBUG:-}" = "true" ]; then
    set -x
fi

ROOT="${ROOT:-/workspace}"
CONFIG_DIR="${CONFIG_DIR:-${ROOT}/config}"
COMFY_DIR="${COMFY_DIR:-${ROOT}/ComfyUI}"
CONFIG_FILE="$CONFIG_DIR/config.json"
LOG_DIR="${ROOT}/logs"
START_LOG="${LOG_DIR}/start.log"


echo "BEFORE PATH: $PATH"

PATH=/usr/local/bin:$PATH

echo "AFTER PATH: $PATH"

# Add at the top of the file with other env vars
COMFY_AUTH=""

# Ensure base directories exist
mkdir -p "$LOG_DIR" "${ROOT}/shared"
chmod 755 "$LOG_DIR" "${ROOT}/shared"
touch "$START_LOG"
chmod 644 "$START_LOG"

log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    # Only write to log file, don't duplicate to stdout unless DEBUG is set
    if [ "${DEBUG:-}" = "true" ]; then
        echo "[$timestamp] $*" | tee -a "$START_LOG"
    else
        echo "[$timestamp] $*" >> "$START_LOG"
        # For non-debug mode, only show important messages on screen
        case "$*" in
            *ERROR*|*FAIL*|*SUCCESS*|*READY*)
                echo "[$timestamp] $*"
                ;;
        esac
    fi
}

main() {
    log ""
    log "====================================="
    log "      Starting ComfyUI Setup         "
    log "====================================="
    log ""
    log "=============== Steps ================"
    log "1. Check environment variables"
    log "2. Setup SSH access"
    log "3. Setup pre-installed nodes"
    log "4. Install nodes from config"
    log "5. Download models"
    log "6. Setup NGINX"
    log "7. Setup shared directories"
    log "8. Setup ComfyUI instances"
    log "9. Setup service scripts"
    log "10. Start NGINX"
    log "11. Start ComfyUI services"
    log "12. Verify all services"
    log "====================================="
    log ""
    
    # Phase 1: Check environment variables
    log_phase "1" "Checking environment variables"
    if ! setup_env_vars; then
        log "ERROR: Environment check failed"
        return 1
    fi
    
    # Phase 2: Setup SSH access
    log_phase "2" "Setting up SSH access"
    if ! setup_ssh_access; then
        log "ERROR: SSH setup failed"
        return 1
    fi
    
    # Phase 3: Setup pre-installed nodes
    log_phase "3" "Setting up custom nodes"
    setup_preinstalled_nodes

    log_phase "4&5" "aws sync"
    if ! s3_sync; then
        log "ERROR: AWS sync failed"
        return 1
    fi
    
    # # Phase 4: Install custom nodes from config
    # log_phase "4" "Installing nodes from config"
    # install_nodes

    # # Phase 5: Download models if specified in config
    # log_phase "5" "Downloading models"
    # download_models
    
    # Phase 6: Setup NGINX
    log_phase "6" "Setting up NGINX"
    if ! setup_nginx; then
        log "ERROR: NGINX setup failed"
        return 1
    fi
    
    # # Phase 7: Setup shared directories
    # log_phase "7" "Setting up shared directories"
    # setup_shared_dirs
    
    # Phase 8: Setup ComfyUI instances
    log_phase "8" "Setting up ComfyUI instances"
    setup_comfyui
    
    # Phase 9: Setup service scripts
    log_phase "9" "Setting up service scripts"
    setup_service_scripts
    
    # Phase 10: Start NGINX
    log_phase "10" "Starting NGINX"
    start_nginx
    
    # Phase 11: Start ComfyUI services
    log_phase "11" "Starting ComfyUI services"
    start_comfyui
    
    # Phase 12: Verify all services
    log_phase "12" "Verifying all services"
    if ! verify_and_report; then
        log "ERROR: Service verification failed"
        # Don't exit - keep container running for debugging
    fi
}

setup_env_vars() {
    log "Setting up environment variables..."

    check_env_vars
    set_gpu_env
    
    # Clean up PATH to avoid duplicates
    clean_path="/opt/conda/bin:/workspace/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"   
    AWS_SECRET_ACCESS_KEY=$(echo "${AWS_SECRET_ACCESS_KEY_ENCODED}" | sed 's/_SLASH_/\//g')
    export AWS_SECRET_ACCESS_KEY
    
    # Persist environment variables for SSH sessions
    log "Persisting environment variables..."
    {
        echo "ROOT=${ROOT}"
        echo "NUM_GPUS=${NUM_GPUS}"
        echo "MOCK_GPU=${MOCK_GPU}"
        echo "TEST_GPUS=${TEST_GPUS:-}"
        echo "SERVER_CREDS=${SERVER_CREDS}"
        echo "COMFY_AUTH=${COMFY_AUTH}"
        echo "PATH=${clean_path}"
        echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
        echo "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
        echo "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}"
    } >> /etc/environment
    
    # Also add to profile for interactive sessions
    {
        echo "export ROOT=${ROOT}"
        echo "export NUM_GPUS=${NUM_GPUS}"
        echo "export MOCK_GPU=${MOCK_GPU}"
        echo "export TEST_GPUS=${TEST_GPUS:-}"
        echo "export SERVER_CREDS=${SERVER_CREDS}"
        echo "export COMFY_AUTH=${COMFY_AUTH}"
        echo "export PATH=${clean_path}"
        echo "export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
        echo "export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
        echo "export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}"
    } > /etc/profile.d/comfyui-env.sh
    
    # Set for current session
    export PATH="${clean_path}"
    
    log "Environment variables persisted"
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

    if [ -z "$TEST_GPUS" ]; then
        log "TEST_GPUS is not set"
    else
        log "TEST_GPUS is set"
    fi   
}

set_gpu_env() {
    log "=== GPU Environment Debug ==="
    
    # Check for test mode
    if [ -n "$TEST_GPUS" ] && [[ "$TEST_GPUS" =~ ^[0-9]+$ ]]; then
        log "Test mode: Mocking $TEST_GPUS GPUs"
        NUM_GPUS=$TEST_GPUS
        export NUM_GPUS
        export MOCK_GPU=1  # Flag to indicate we're in test mode
        return 0
    fi
    
    if command -v nvidia-smi &> /dev/null; then
        log "nvidia-smi is available"
        nvidia-smi 2>&1 | while read -r line; do log "  $line"; done
        
        # Get number of GPUs
        NUM_GPUS=$(nvidia-smi --list-gpus | wc -l)
        log "Found $NUM_GPUS GPUs"
        export NUM_GPUS
        export MOCK_GPU=0
    else
        log "nvidia-smi not found, assuming CPU mode"
        NUM_GPUS=0
        export NUM_GPUS
        export MOCK_GPU=0
    fi
    
    log "GPU Environment: NUM_GPUS=$NUM_GPUS MOCK_GPU=$MOCK_GPU"
}

setup_ssh_access() {
    log "Starting SSH agent"
    eval "$(ssh-agent -s)"

    log "Setting up SSH access..."
    
    # Verify SSH directory exists and has correct permissions
    if [ ! -d "/root/.ssh" ]; then
        log "Creating /root/.ssh directory"
        mkdir -p /root/.ssh
        chmod 700 /root/.ssh
    fi
    
    # Verify directory permissions
    if [ "$(stat -c %a /root/.ssh)" != "700" ]; then
        log "Fixing /root/.ssh directory permissions"
        chmod 700 /root/.ssh
    fi

    # Check if all key parts are present
    if [ -n "$CUT_PK_1" ] && [ -n "$CUT_PK_2" ] && [ -n "$CUT_PK_3" ]; then
        # Combine the key parts
        full_base64_key="${CUT_PK_1}${CUT_PK_2}${CUT_PK_3}"
        
        # Decode the base64 key
        if ! full_key=$(echo "$full_base64_key" | base64 -d); then
            log "ERROR: Failed to decode base64 key"
            return 1
        fi
        
        # Write the key to file
        if ! echo "$full_key" > /root/.ssh/id_ed25519; then
            log "ERROR: Failed to write SSH key to file"
            return 1
        fi
        
        # Set correct permissions
        chmod 400 /root/.ssh/id_ed25519
        
        # Verify key file exists and has correct permissions
        if [ ! -f "/root/.ssh/id_ed25519" ]; then
            log "ERROR: SSH key file not found after creation"
            return 1
        fi
        
        if [ "$(stat -c %a /root/.ssh/id_ed25519)" != "400" ]; then
            log "ERROR: SSH key file has incorrect permissions"
            chmod 400 /root/.ssh/id_ed25519
        fi
        
        # Try to add the key
        if ! ssh-add /root/.ssh/id_ed25519; then
            log "ERROR: Failed to add SSH key to agent"
            return 1
        fi
        
        # Verbose key validation
        log "Validating SSH key..."
        if ! ssh-keygen -y -f /root/.ssh/id_ed25519; then
            log "ERROR: SSH key validation failed"
            return 1
        fi
        
        # Test SSH connection to GitHub with retries
        log "Testing GitHub SSH connection..."
        local max_attempts=3
        local attempt=1
        local success=false
        
        while [ $attempt -le $max_attempts ]; do
            log "SSH connection attempt $attempt of $max_attempts"
            if ssh -T git@github.com -o StrictHostKeyChecking=no 2>&1 | grep -q "successfully authenticated"; then
                success=true
                break
            else
                log "SSH attempt $attempt failed with exit code $?"
            fi
            attempt=$((attempt + 1))
            if [ $attempt -le $max_attempts ]; then
                log "Waiting 10 seconds before next attempt..."
                sleep 10
                log "Resuming after wait"
            fi
        done
        
        if [ "$success" != "true" ]; then
            log "ERROR: Failed to connect to GitHub after $max_attempts attempts"
            return 1
        fi
        
        log "SSH key successfully set up and verified"
    else
        # Detailed logging if key parts are missing
        [ -z "$CUT_PK_1" ] && log "Missing CUT_PK_1"
        [ -z "$CUT_PK_2" ] && log "Missing CUT_PK_2"
        [ -z "$CUT_PK_3" ] && log "Missing CUT_PK_3"

        log "ERROR: SSH key parts are missing"
        return 1
    fi

    # Add GitHub to known hosts if not present
    touch /root/.ssh/known_hosts
    chmod 644 /root/.ssh/known_hosts
    if ! grep -q "github.com" /root/.ssh/known_hosts; then
        ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
    fi
    
    # Final verification
    log "Final SSH setup verification:"
    log "- SSH directory: $(ls -ld /root/.ssh)"
    log "- SSH key file: $(ls -l /root/.ssh/id_ed25519)"
    log "- Known hosts: $(ls -l /root/.ssh/known_hosts)"
}

setup_preinstalled_nodes() {
    log "Setting up pre-installed custom nodes..."
    if [ -d "/workspace/shared_custom_nodes" ]; then
        log "Found pre-installed nodes, moving to shared directory"
        mv /workspace/shared_custom_nodes "${ROOT}/shared/custom_nodes"
        log "Contents of shared custom_nodes directory:"
        ls -la "${ROOT}/shared/custom_nodes" | while read -r line; do log "  $line"; done
    else
        log "No pre-installed nodes found at /workspace/shared_custom_nodes"
    fi
}

# install_nodes() {
#     log "Processing custom nodes from config..."
    
#     if [ ! -f "$CONFIG_FILE" ]; then
#         log "Config not found: $CONFIG_FILE"
#         return
#     fi

#     # Use shared custom_nodes directory
#     cd "${ROOT}/shared/custom_nodes"
    
    # while IFS= read -r node; do
    #     name=$(echo "$node" | jq -r '.name')
    #     url=$(echo "$node" | jq -r '.url')
    #     commit=$(echo "$node" | jq -r '.commit // empty')
    #     install_reqs=$(echo "$node" | jq -r '.requirements')
        
    #     if [ "$name" != "null" ] && [ "$url" != "null" ]; then
    #         log "Processing node: $name"
            
    #         # Handle environment variables if present
    #         env_vars=$(echo "$node" | jq -r '.env // empty')
    #         if [ ! -z "$env_vars" ]; then
    #             log "Setting environment variables for $name"
    #             while IFS="=" read -r key value; do
    #                 if [ ! -z "$key" ]; then
    #                     # Expand any environment variables in the value
    #                     expanded_value=$(eval echo "$value")
    #                     export "$key"="$expanded_value"
    #                     log "Set $key"
    #                 fi
    #             done < <(echo "$env_vars" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"')
    #         fi
            
    #         if [ ! -d "$name" ]; then
    #             log "Installing node: $name"
    #             git clone "$url" "$name"
                
    #             if [ ! -z "$commit" ]; then
    #                 cd "$name"
    #                 git reset --hard "$commit"
    #                 cd ..
    #             fi
    #         else
    #             log "Node directory exists: $name"
    #             # Update existing repository
    #             cd "$name"
    #             git remote set-url origin "$url"
    #             git fetch
    #             if [ ! -z "$commit" ]; then
    #                 git reset --hard "$commit"
    #             else
    #                 git pull
    #             fi
    #             cd ..
    #         fi
            
    #         # Install requirements if specified as true
    #         if [ "$install_reqs" = "true" ] && [ -f "$name/requirements.txt" ]; then
    #             log "Installing requirements for $name"
    #             pip install -r "$name/requirements.txt"
    #         fi
    #     fi
    # done < <(jq -c '.nodes[]' "$CONFIG_FILE")
# }

# download_model() {
#     local url="$1"
#     local path="$2"
#     local filename="$3"
    
#     log "Downloading model: $filename"
    
#     # Create full path in shared directory, remove any double slashes
#     local full_path="${ROOT}/shared/${path%/}"
    
#     # Create directory if it doesn't exist
#     mkdir -p "$full_path"
    
#     # Update comfy_dir_config.yaml
#     update_comfy_config "$path"
    
#     log "Saving to: $full_path/$filename"
    
#     # Use wget with progress bar, suppress verbose output
#     if ! wget --quiet --show-progress --progress=bar:force:noscroll -O "$full_path/$filename" "$url" >> "$START_LOG" 2>&1; then
#         log "Failed to download $url"
#         return 1
#     fi

#     # Verify file was downloaded and has size
#     if [ ! -s "$full_path/$filename" ]; then
#         log "Download failed - file is empty"
#         return 1
#     fi
    
#     log "Successfully downloaded $filename"
#     return 0
# }

# update_comfy_config() {
#     local path="$1"
#     local config_file="${ROOT}/shared/comfy_dir_config.yaml"
    
#     # Create config file if it doesn't exist
#     if [ ! -f "$config_file" ]; then
#         log "Creating new comfy_dir_config.yaml"
#         cat > "$config_file" << EOL
# comfyui:
#     base_path: /workspace/shared
#     custom_nodes: custom_nodes/
# EOL
#     fi
    
#     # Extract the directory type from path (e.g., "checkpoints" from "models/checkpoints/")
#     local dir_type=$(echo "$path" | sed -n 's|^models/\([^/]*\)/.*$|\1|p')
#     if [ -n "$dir_type" ]; then
#         # Check if this type already exists in config
#         if ! grep -q "^[[:space:]]*${dir_type}:" "$config_file"; then
#             log "Adding $dir_type path to comfy_dir_config.yaml"
#             # Create temp file for sed (macOS requires this)
#             local temp_file=$(mktemp)
#             sed "/^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:/i\\    ${dir_type}: models/${dir_type}/" "$config_file" > "$temp_file"
#             mv "$temp_file" "$config_file"
#         fi
#     fi
# }

# download_models() {
#     if [ ! -f "$CONFIG_FILE" ]; then
#         log "No config file found at $CONFIG_FILE"
#         return 0
#     fi

#     # Process each model in the configuration
#     local models
#     models=$(jq -c '.models[] | select(.url != null)' "$CONFIG_FILE")
    
#     # Check if models is empty
#     if [ -z "$models" ]; then
#         log "No models found in configuration to download"
#         return 0
#     fi

#     # Process models using a while loop
#     echo "$models" | while read -r model; do
#         # Extract model details
#         local url name path
#         url=$(echo "$model" | jq -r '.url')
#         name=$(echo "$model" | jq -r '.name')
#         path=$(echo "$model" | jq -r '.path // "models/checkpoints/"')
        
#         # log "Processing model: $name"
#         # log "  URL: $url"
#         # log "  Path: $path"
        
#         # Download the model
#         download_model "$url" "$path" "$name"
#     done

#     return 0
# }


s3_sync() {
    # Sync models and configs from S3
    log "Syncing from S3..."
    echo "Syncing from S3..."
    echo $AWS_ACCESS_KEY_ID
    echo $AWS_SECRET_ACCESS_KEY
    aws s3 sync s3://emprops-share /workspace/shared

    # Install custom nodes from config
    log "Installing custom nodes..."
    if [ -f "/workspace/shared/custom_nodes/config_nodes.json" ]; then
        cd /workspace/shared/custom_nodes
        for node in $(jq -r '.custom_nodes[] | @base64' config_nodes.json); do
            _jq() {
                echo ${node} | base64 --decode | jq -r ${1}
            }
            
            name=$(_jq '.name')
            url=$(_jq '.url')
            commit=$(_jq '.commit // empty')
            install_reqs=$(_jq '.requirements')
            
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
                        git reset --hard "$commit"
                        cd ..
                    fi
                else
                    log "Node directory exists: $name"
                    # Update existing repository
                    cd "$name"
                    git remote set-url origin "$url"
                    git fetch
                    if [ ! -z "$commit" ]; then
                        git reset --hard "$commit"
                    else
                        git pull
                    fi
                    cd ..
                fi
                
                # Install requirements if specified as true
                if [ "$install_reqs" = "true" ] && [ -f "$name/requirements.txt" ]; then
                    log "Installing requirements for $name"
                    pip install -r "$name/requirements.txt"
                fi
            fi
        done
    fi
}

setup_nginx() {
    log "Setting up NGINX..."
    
    # Setup auth first
    if ! setup_nginx_auth; then
        log "ERROR: Failed to setup NGINX authentication"
        return 1
    fi
    
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

setup_nginx_auth() {
    log "Setting up NGINX authentication..."
    
    # Create nginx directory if it doesn't exist
    if [ ! -d "/etc/nginx" ]; then
        log "Creating /etc/nginx directory"
        mkdir -p /etc/nginx
        chmod 755 /etc/nginx
    fi
    
    # Check if auth credentials are available
    if [ -n "$SERVER_CREDS" ]; then
        # Write credentials to .sd file
        if ! echo "$SERVER_CREDS" > /etc/nginx/.sd; then
            log "ERROR: Failed to write auth credentials to file"
            return 1
        fi
        
        # Set correct permissions
        chmod 600 /etc/nginx/.sd
        
        # Verify file exists and has correct permissions
        if [ ! -f "/etc/nginx/.sd" ]; then
            log "ERROR: Auth file not found after creation"
            return 1
        fi
        
        if [ "$(stat -c %a /etc/nginx/.sd)" != "600" ]; then
            log "ERROR: Auth file has incorrect permissions"
            chmod 600 /etc/nginx/.sd
        fi
        
        log "NGINX authentication setup complete"
    else
        log "ERROR: SERVER_CREDS not set"
        return 1
    fi
}

# setup_shared_dirs() {
#     log "Creating shared directories..."
#     mkdir -p "${ROOT}/shared/models"
#     mkdir -p "${ROOT}/shared/custom_nodes"
#     log "Shared directories created at ${ROOT}/shared/"
# }

setup_comfyui() {
    log "Setting up ComfyUI..."
    
    if [ "$NUM_GPUS" -eq 0 ]; then
        # CPU mode
        log "Setting up CPU mode..."
        if ! mgpu setup cpu; then
            log "ERROR: Failed to setup CPU instance"
            return 1
        fi
    else
        # GPU mode
        log "Setting up GPU mode with $NUM_GPUS GPUs"
        
        # Add --cpu flag in test mode
        if [ "${MOCK_GPU:-0}" -eq 1 ]; then
            log "Test mode: Adding --cpu flag to all instances"
            export COMFY_ARGS="--cpu"
        fi
        
        # Setup GPU instances
        log "Setting up GPU instances..."
        if ! mgpu setup all; then
            log "ERROR: Failed to set up GPU instances"
            return 1
        fi
        
        # Start services
        log "Starting GPU services..."
        if ! mgpu start all; then
            log "ERROR: Failed to start GPU services"
            return 1
        fi
        
        # Quick status check
        log "Verifying services..."
        mgpu status all >/dev/null || {
            log "ERROR: Service verification failed"
            return 1
        }
    fi
    
    log "ComfyUI setup complete"
    return 0
}

setup_service_scripts() {
    log "Setting up service scripts"
    
    # Verify mgpu script is available
    if ! command -v mgpu >/dev/null 2>&1; then
        log "ERROR: MGPU command not found in PATH"
        return 1
    fi
    
    # Update service defaults if needed
    if ! update-rc.d comfyui defaults; then
        log "WARNING: Failed to update ComfyUI service defaults"
    fi
    
    log "Service scripts initialized"
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
    log "Starting NGINX..."
    
    # Stop nginx if it's already running
    if service nginx status >/dev/null 2>&1; then
        log "NGINX is already running, stopping it first..."
        service nginx stop
    fi
    
    # Start nginx
    log "Starting NGINX service..."
    if ! service nginx start; then
        log "ERROR: Failed to start NGINX"
        return 1
    fi
    
    # Verify it's running
    sleep 2
    if ! service nginx status >/dev/null 2>&1; then
        log "ERROR: NGINX failed to start"
        service nginx status | while read -r line; do log "  $line"; done
        return 1
    fi
    
    log "NGINX started successfully"
}

start_comfyui() {
    log "Starting ComfyUI services..."
    
    if [ "$NUM_GPUS" -eq 0 ]; then
        # CPU mode - start single instance through mgpu
        log "Starting ComfyUI in CPU mode"
        if ! mgpu start 0; then
            log "ERROR: Failed to start ComfyUI CPU service"
            mgpu status 2>&1 | tail -n 3 | while read -r line; do log "  $line"; done
            return 1
        fi
        
        # Wait for service to be ready
        log "Checking ComfyUI service..."
            
        # Check service status and ports
        if ! mgpu status | grep -q "running"; then
            log "ERROR: Service not running"
            mgpu logs 2>&1
            return 1
        fi

        if ! netstat -tuln | grep -q ":8188 "; then
            log "ERROR: Direct port 8188 not listening"
            netstat -tuln | grep -E ':3188|:8188'
            return 1
        fi

        if ! netstat -tuln | grep -q ":3188 "; then
            log "ERROR: Proxy port 3188 not listening"
            netstat -tuln | grep -E ':3188|:8188'
            return 1
        fi

        log "ComfyUI service ready"
    else
        # GPU mode - start all instances using mgpu
        log "Starting ComfyUI in GPU mode with $NUM_GPUS GPUs"
        
        # Add --cpu flag in test mode
        if [ "${MOCK_GPU:-0}" -eq 1 ]; then
            log "Test mode: Adding --cpu flag to all instances"
            export COMFY_ARGS="--cpu"
        fi
        
        if ! mgpu start all; then
            log "ERROR: Failed to start ComfyUI GPU services"
            mgpu status all 2>&1 | tail -n 5 | while read -r line; do log "  $line"; done
            return 1
        fi
    fi
    
    log "All ComfyUI services started successfully"
}

log_phase() {
    local phase_num=$1
    local phase_name=$2
    log ""
    log "===================================="
    log "Phase $phase_num: $phase_name"
    log "===================================="
}

verify_and_report() {
    log ""
    log "===================================="
    log "Starting Service Verification"
    log "===================================="
    
    # Give services a moment to start if they just started
    sleep 2
    
    # Run comprehensive verification
    verify_services
    
    # Final user instructions
    if [ "$all_services_ok" = true ]; then
        log ""
        log "===================================="
        log "All services are running correctly"
        log "Use 'mgpu logs-all' to monitor all services"
        log "===================================="
        return 0
    else
        log ""
        log "===================================="
        log "WARNING: Some services are not functioning correctly"
        log "Check the logs above for specific errors"
        log "Use 'mgpu logs-all' to monitor services for errors"
        log "===================================="
        return 1
    fi
}

verify_services() {
    # Setup auth first
    setup_auth
    
    log "Phase 12: Verifying all services..."
    all_services_ok=true
    
    # 1. Verify NGINX
    log "=== Verifying NGINX ==="
    if ! service nginx status >/dev/null 2>&1; then
        log "ERROR: NGINX is not running"
        all_services_ok=false
    else
        log "NGINX is running"
        # Check nginx config
        if ! nginx -t >/dev/null 2>&1; then
            log "ERROR: NGINX configuration test failed"
            nginx -t 2>&1 | while read -r line; do log "  $line"; done
            all_services_ok=false
        fi
        
        # Check proxy port
        if ! netstat -tuln | grep -q ":3188 "; then
            log "ERROR: NGINX proxy port 3188 is not listening"
            log "Current listening ports:"
            netstat -tuln | while read -r line; do log "  $line"; done
            all_services_ok=false
        else
            log "NGINX proxy port 3188 is listening"
        fi
        
        # Test NGINX auth separately from service
        log "Testing NGINX auth on port 3188..."
        if ! make_auth_request "http://localhost:3188/system_stats"; then
            log "ERROR: NGINX auth test failed"
            log "Curl verbose output:"
            curl -v -I -u "$COMFY_AUTH" "http://localhost:3188/" 2>&1 | while read -r line; do log "  $line"; done
            all_services_ok=false
        else
            log "NGINX auth test passed"
        fi
    fi
    
    # 2. Verify ComfyUI Services
    log "=== Verifying ComfyUI Services ==="
    log "How many GPUs: $NUM_GPUS"
    if [ "$NUM_GPUS" -eq 0 ]; then
        # CPU mode
        log "Checking CPU mode..."
        if ! mgpu status | grep -q "running"; then
            log "ERROR: ComfyUI CPU service is not running"
            mgpu status 2>&1 | while read -r line; do log "  $line"; done
            all_services_ok=false
        else
            log "ComfyUI CPU service is running"
        fi
        
        # Check logs
        if [ ! -f "${ROOT}/comfyui_cpu/logs/output.log" ]; then
            log "ERROR: Missing log file: ${ROOT}/comfyui_cpu/logs/output.log"
            all_services_ok=false
        else
            log "Log file exists"
            # Show last few lines of log
            log "=== Last 5 lines of output.log ==="
            tail -n 5 "${ROOT}/comfyui_cpu/logs/output.log" | while read -r line; do log "  $line"; done
        fi
        
        # Try a test request to ComfyUI service
        log "Testing ComfyUI service on port 3188..."
        if ! make_auth_request "http://localhost:3188/system_stats"; then
            log "ERROR: ComfyUI service is not responding"
            log "Curl verbose output:"
            make_auth_request "http://localhost:3188/system_stats" "verbose" 2>&1 | while read -r line; do log "  $line"; done
            all_services_ok=false
        else
            log "ComfyUI service test passed"
        fi
    else
        # GPU mode
        log "Checking GPU mode ($NUM_GPUS GPUs)..."
        for gpu in $(seq 0 $((NUM_GPUS-1))); do
            log "Checking GPU $gpu..."
            
            # Check service
            if ! mgpu status "$gpu" | grep -q "running"; then
                log "ERROR: ComfyUI service for GPU $gpu is not running"
                mgpu status "$gpu" 2>&1 | while read -r line; do log "  $line"; done
                all_services_ok=false
                continue
            fi
            
            # Check proxy port
            local proxy_port=$((3188 + gpu))
            if ! netstat -tuln | grep -q ":$proxy_port "; then
                log "ERROR: NGINX proxy port $proxy_port is not listening"
                log "Current listening ports:"
                netstat -tuln | while read -r line; do log "  $line"; done
                all_services_ok=false
            fi
            
            # Check logs
            if [ ! -f "${ROOT}/comfyui_gpu${gpu}/logs/output.log" ]; then
                log "ERROR: Missing log file: ${ROOT}/comfyui_gpu${gpu}/logs/output.log"
                all_services_ok=false
            fi
            
            # Try a test request
            if ! make_auth_request "http://localhost:$proxy_port/system_stats"; then
                log "ERROR: ComfyUI GPU $gpu is not responding to requests"
                log "Curl verbose output:"
                make_auth_request "http://localhost:$proxy_port/system_stats" "verbose" 2>&1 | while read -r line; do log "  $line"; done
                all_services_ok=false
            fi
        done
    fi
    
    # 3. Final Summary
    log "=== Service Status Summary ==="
    log "NGINX: $(service nginx status >/dev/null 2>&1 && echo "RUNNING" || echo "NOT RUNNING")"
    
    if [ "$NUM_GPUS" -eq 0 ]; then
        # CPU mode summary
        local service_status=$(mgpu status | grep -q "running" && echo "RUNNING" || echo "NOT RUNNING")
        local proxy_status=$(netstat -tuln | grep -q ":3188 " && echo "LISTENING" || echo "NOT LISTENING")
        local api_status=$(make_auth_request "http://localhost:3188/system_stats" && echo "RESPONDING" || echo "NOT RESPONDING")
        log "ComfyUI CPU: Service: $service_status, Proxy: $proxy_status, API: $api_status"
    else
        # GPU mode summary
        for gpu in $(seq 0 $((NUM_GPUS-1))); do
            local proxy_port=$((3188 + gpu))
            local service_status=$(mgpu status "$gpu" | grep -q "running" && echo "RUNNING" || echo "NOT RUNNING")
            local proxy_status=$(netstat -tuln | grep -q ":$proxy_port " && echo "LISTENING" || echo "NOT LISTENING")
            local api_status=$(make_auth_request "http://localhost:$proxy_port/system_stats" && echo "RESPONDING" || echo "NOT RESPONDING")
            log "ComfyUI GPU $gpu: Service: $service_status, Proxy: $proxy_status, API: $api_status"
        done
    fi
    
    if [ "$all_services_ok" = false ]; then
        log "ERROR: Some services are not functioning correctly"
        return 1
    fi
    
    log "All services verified successfully"
}

setup_auth() {
    if [ -n "$SERVER_CREDS" ]; then
        # Add "sd:" prefix and base64 encode
        COMFY_AUTH=$(echo -n "sd:$SERVER_CREDS" | base64)
    else
        log "WARNING: SERVER_CREDS not set, authentication may fail"
    fi
}

make_auth_request() {
    local url=$1
    local auth_opts=""
    
    if [ -n "$COMFY_AUTH" ]; then
        # Decode base64 credentials for curl
        local decoded_creds=$(echo "$COMFY_AUTH" | base64 -d)
        auth_opts="-u '$decoded_creds'"
    fi
    
    if [ "$2" = "verbose" ]; then
        eval "curl -v $auth_opts '$url'"
    else
        eval "curl -s $auth_opts '$url'"
    fi
}

all_services_ok=true
main

tail -f /dev/null
