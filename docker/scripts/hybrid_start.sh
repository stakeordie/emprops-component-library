#!/bin/bash
# hybrid_start.sh - Combined startup script for ComfyUI and A1111
# This script starts both services in the same container

# Only enable debug mode if DEBUG is set
if [ "${DEBUG:-}" = "true" ]; then
    set -x
fi

ROOT="${ROOT:-/workspace}"
LOG_DIR="${ROOT}/logs"
START_LOG="${LOG_DIR}/hybrid_start.log"

# Create log directory
mkdir -p "$LOG_DIR"
touch "$START_LOG"
chmod 644 "$START_LOG"

# Logging function
log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $*" | tee -a "$START_LOG"
}

log_phase() {
    local phase="$1"
    local description="$2"
    log ""
    log "==== PHASE ${phase}: ${description} ===="
}

# Main function for hybrid container startup
main() {
    log ""
    log "=========================================="
    log "     Hybrid ComfyUI + A1111 Container     "
    log "=========================================="
    log ""
    
    log_phase "1" "Setting up environment"
    # Run ComfyUI's environment setup
    if [ -f "${ROOT}/scripts/start.sh" ]; then
        log "Running ComfyUI environment setup..."
        # Source the start.sh file but skip the main function to just get the env vars and functions
        source "${ROOT}/scripts/start.sh" skip_main
        
        # Run selected functions from ComfyUI's start.sh
        setup_env_vars
        check_env_vars
        set_gpu_env
        setup_ssh_access
        
        log "ComfyUI environment setup complete"
    else
        log "WARNING: ComfyUI start.sh not found at ${ROOT}/scripts/start.sh"
    fi
    
    log_phase "2" "Syncing models from AWS"
    # Run model sync from AWS to shared directory
    if type s3_sync &>/dev/null; then
        s3_sync
    else
        log "WARNING: s3_sync function not available, skipping model sync"
    fi
    
    log_phase "3" "Setting up NGINX"
    # Setup NGINX for both services
    if type setup_nginx &>/dev/null; then
        setup_nginx
    else
        log "WARNING: setup_nginx function not available, skipping NGINX setup"
    fi
    
    log_phase "4" "Initializing A1111"
    # Run A1111 setup
    if [ -f "${ROOT}/scripts/a1111/hybrid_build.sh" ]; then
        log "Running A1111 hybrid build script..."
        bash "${ROOT}/scripts/a1111/hybrid_build.sh"
    else
        log "WARNING: A1111 hybrid build script not found at ${ROOT}/scripts/a1111/hybrid_build.sh"
    fi
    
    log_phase "5" "Starting ComfyUI"
    # Setup and start ComfyUI
    if type setup_comfyui &>/dev/null && type start_comfyui &>/dev/null; then
        setup_comfyui
        start_comfyui
    else
        log "WARNING: ComfyUI setup/start functions not available"
    fi
    
    log_phase "6" "Verifying services"
    # Verify all services
    if type verify_and_report &>/dev/null; then
        verify_and_report
    else
        log "WARNING: verify_and_report function not available, skipping service verification"
    fi
    
    log "Hybrid container setup completed successfully"
    log "ComfyUI available at port 3188"
    log "A1111 available at port 3130"
}

# Check if we are being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ "$1" != "skip_main" ]]; then
        main
        
        # Keep container running
        log "Container initialization complete. Keeping container running..."
        tail -f /dev/null
    fi
else
    # Being sourced, not executing main
    log "Being sourced, not executing main function"
fi
