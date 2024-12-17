#!/bin/bash

set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Function to handle errors
error_exit() {
    log "ERROR: $1" >&2
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            COMFY_PATH="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL="$2"
            shift 2
            ;;
        *)
            error_exit "Unknown argument: $1"
            ;;
    esac
done

# Validate required arguments
[[ -z "$COMFY_PATH" ]] && error_exit "Missing required argument: --path"
[[ -z "$CONFIG_FILE" ]] && error_exit "Missing required argument: --config"
[[ ! -f "$CONFIG_FILE" ]] && error_exit "Config file not found: $CONFIG_FILE"

# Process nodes configuration using Python
python3 -c '
import json
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def install_node(node):
    name = node.get("name", "")
    url = node.get("url", "")
    path = os.path.join("'$COMFY_PATH'", "custom_nodes")
    requirements = node.get("requirements", True)
    env_vars = node.get("env", {})
    
    print(f"\nInstalling node: {name}")
    print(f"URL: {url}")
    print(f"Path: {path}")
    
    try:
        # Create directory if it doesnt exist
        os.makedirs(path, exist_ok=True)
        
        # Clone repository
        subprocess.run(["git", "clone", url], 
                      cwd=path, 
                      check=True, 
                      capture_output=True)
        
        # Get the directory name from the git URL
        dir_name = url.split("/")[-1].replace(".git", "")
        node_path = os.path.join(path, dir_name)
        
        # Install requirements if they exist
        if requirements and os.path.exists(os.path.join(node_path, "requirements.txt")):
            subprocess.run(["pip", "install", "-r", "requirements.txt"],
                         cwd=node_path,
                         check=True,
                         capture_output=True)
        
        # Write environment variables if specified
        if env_vars:
            with open(os.path.join(node_path, ".env"), "w") as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
        
        print(f" Successfully installed {name}")
        return True
        
    except Exception as e:
        print(f" Failed to install {name}: {str(e)}", file=sys.stderr)
        return False

def process_config():
    with open("'$CONFIG_FILE'", "r") as f:
        config = json.load(f)
    
    nodes = config.get("nodes", [])
    parallel = int("'${PARALLEL:-1}'")
    
    print(f"\n=== Installing {len(nodes)} nodes ===\n")
    
    if parallel > 1:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = [executor.submit(install_node, node) for node in nodes]
            for future in as_completed(futures):
                future.result()
    else:
        for node in nodes:
            install_node(node)
    
    print("\n=== Node installation complete ===\n")

process_config()
'