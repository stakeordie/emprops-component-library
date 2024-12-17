#!/bin/bash
set -x  # Print commands and their arguments as they are executed
set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Capture errors in pipe chains

echo "DEBUG: Script starting" > /tmp/debug.log
date >> /tmp/debug.log

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Ensure ROOT is set
: "${ROOT:=/home/ubuntu}"
log "Using ROOT directory: $ROOT"

error_exit() {
    log "ERROR: $1" >&2
    exit 1
}

setup_nginx() {
  log "Setting up Nginx configuration..."
  sudo rm -rf /etc/nginx
  sudo git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo
  sudo ln -s /etc/nginx-repo/node /etc/nginx
}

extract_models() {
  if [ -f "${ROOT}/tmp/models.tar.zst" ]; then
    cd /home/ubuntu/
    tar -I zstd -xvf ${ROOT}/tmp/models.tar.zst
    rm ${ROOT}/tmp/models.tar.zst
    cp -rn /home/ubuntu/models/* /home/ubuntu/ComfyUI/models
    rm -rf /home/ubuntu/models
  fi
}

setup_comfyui() {
  local comfyui_path="${ROOT}/ComfyUI"
  local comfyui_commit="915fdb57454c094391d830cefb4ffdd24ed8088c"

  cd "$comfyui_path"
  # Activate virtual environment
  # shellcheck disable=SC1091
  source venv/bin/activate

  git reset --hard "$comfyui_commit"
  # pip install -r requirements.txt
  
  pip install "numpy < 2"

  deactivate
}

setup_env_files() {
  log "Setting up environment files..."
  cd "${ROOT}/env_files" || return
  
  # Loop through all env files and move them to their destinations
  for env_file in ComfyUI_custom_nodes_*_env; do
    if [ -f "$env_file" ]; then
      # Extract repo name from file name
      repo_name=${env_file#ComfyUI_custom_nodes_}
      repo_name=${repo_name%_env}
      
      # Create destination directory and move file
      target_dir="${ROOT}/ComfyUI/custom_nodes/${repo_name}"
      mkdir -p "$target_dir"
      cp "$env_file" "${target_dir}/.env"
      chown ubuntu:ubuntu "${target_dir}/.env"
      
      log "Moved $env_file to ${target_dir}/.env"
    fi
  done
}

install_models() {
  # Process models from config and download them directly to ComfyUI/models
  python3 -c '
import json
import os
import urllib.request
import sys
from tqdm import tqdm

def download_file(url, path, name):
    # If path ends with /, treat it as a directory and append the name
    if path.endswith("/"):
        path = os.path.join(path, name)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"\nDownloading model: {name}")
    print(f"URL: {url}")
    print(f"To: {path}")
    
    try:
        response = urllib.request.urlopen(url)
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
        
        with open(path, "wb") as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                size = f.write(buffer)
                progress_bar.update(size)
        
        progress_bar.close()
        print(f"✓ Download complete: {name}\n")
        
    except Exception as e:
        print(f"✗ Error downloading {name}: {str(e)}", file=sys.stderr)
        raise

def process_config():
    config_path = "/home/ubuntu/scripts/models_config_container.json"
    comfy_dir = "/home/ubuntu/ComfyUI"
    
    print("\n=== Starting Model Downloads ===\n")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    total_models = len(config["models"])
    print(f"Found {total_models} models to download\n")
    
    for i, model in enumerate(config["models"], 1):
        url = model["url"]
        name = model["name"]  # name is now required
        path = os.path.join(comfy_dir, model["path"])
        print(f"\n[{i}/{total_models}] Processing model: {name}")
        try:
            download_file(url, path, name)
        except Exception as e:
            print(f"Failed to download model {name} ({i}/{total_models})")
            continue
    
    print("\n=== Model Downloads Complete ===\n")

process_config()
'
}

key_share() {
  echo -e "\n$(cat /root/.ssh/authorized_keys)" >> /home/ubuntu/.ssh/authorized_keys
}

main() {
  log "Starting initialization process..."
  
  setup_nginx
  setup_comfyui
  setup_env_files
  install_models
  key_share
  
  log "Initialization complete."
  
  # Start ComfyUI or any other required services

  mv $ROOT/scripts/comfyui /etc/init.d/

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