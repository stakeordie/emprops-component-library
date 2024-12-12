#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Capture errors in pipe chains

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Error handling function
error_exit() {
    log "ERROR: $1" >&2
    exit 1
}

# Ensure ROOT is set
: "${ROOT:=/comfyui-launcher}"
log "Using ROOT directory: $ROOT"


setup_nginx() {
  log "Setting up Nginx configuration..."
  sudo rm -rf /etc/nginx
  sudo git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo
  sudo ln -s /etc/nginx-repo/node /etc/nginx
}

setup_comfyui() {
  local comfyui_path="${ROOT}/ComfyUI"

  if [ ! -d "$comfyui_path" ]; then
    log "Cloning ComfyUI repository..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "$comfyui_path"
  else
    log "ComfyUI directory already exists"
  fi

  cd "$comfyui_path"

  # Create virtual environment if not exists
  if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv
  fi

  # Activate virtual environment
  # shellcheck disable=SC1091
  source venv/bin/activate

  pip install --upgrade pip

  # Install main requirements
  log "Installing ComfyUI requirements..."
  cd "$comfyui_path" && ls
  pip install -r requirements.txt
}

install_custom_node_requirements() {
    local custom_nodes_path="${ROOT}/ComfyUI/custom_nodes"
    
    mkdir -p "$custom_nodes_path"
    
    # Move contents of ~/nodes into custom_nodes if ~/nodes exists and is not empty
    if [ -d ${ROOT}/nodes ] && [ "$(ls -A ${ROOT}/nodes)" ]; then
        log "Moving contents of ${ROOT}/nodes into ${custom_nodes_path}..."
        mv ${ROOT}/nodes/* "$custom_nodes_path/"
        
        # Optional: Remove the now-empty ~/nodes directory
        rmdir ${ROOT}/nodes 2>/dev/null || true
    fi

    # Find and install requirements for each custom node
    log "Installing custom node requirements..."

    cd $custom_nodes_path
    find . -name "requirements.txt" | while read -r req_file; do
        log "Installing requirements from $req_file"
        pip install -r "$req_file"
    done

    pip install "numpy < 2"
}

install_models() {
  /scripts/models.sh
}

main() {
    setup_nginx
    setup_comfyui
    install_custom_node_requirements
    install_models

    # Deactivate virtual environment
    deactivate

    # Start ComfyUI or any other required services

    mv /scripts/comfyui /etc/init.d/

    sudo chmod +x /etc/init.d/comfyui
    sudo update-rc.d comfyui defaults

    /etc/init.d/nginx start

    /scripts/cron.sh

    service comfyui start
}

if [ ! -f "/etc/nginx-repo" ]; then
  main || error_exit "Failed to complete startup process"
else
  log "Nginx configuration already exists"
fi

sleep infinity