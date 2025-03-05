#!/bin/bash
# direct.sh - Environment setup and initialization script for running containers
# This script checks the current environment, sets up dependencies, and runs start.sh

# Enable debug mode if DEBUG is set
if [ "${DEBUG:-}" = "true" ]; then
    set -x
fi

# Directory setup
ROOT="${ROOT:-/workspace}"
LOG_DIR="${ROOT}/logs"
REPORT_DIR="${ROOT}/reports"
ENV_REPORT="${REPORT_DIR}/environment_report.txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

# Create necessary directories
mkdir -p "$LOG_DIR" "$REPORT_DIR"
chmod 755 "$LOG_DIR" "$REPORT_DIR"

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp]${NC} $*" | tee -a "${LOG_DIR}/direct.log"
}

log_success() {
    log "${GREEN}SUCCESS:${NC} $*"
}

log_warning() {
    log "${YELLOW}WARNING:${NC} $*"
}

log_error() {
    log "${RED}ERROR:${NC} $*"
}

# Function to check if package is installed
is_package_installed() {
    dpkg -l "$1" &> /dev/null
}

# Function to check if Python package is installed
is_python_package_installed() {
    python -c "import $1" &> /dev/null
}

# Function to load environment files
load_env_files() {
    log "Loading environment files..."
    
    # Load .env file if it exists
    if [ -f "${DOCKER_DIR}/.env" ]; then
        log "Loading ${DOCKER_DIR}/.env"
        set -o allexport
        source "${DOCKER_DIR}/.env"
        set +o allexport
    else
        log_warning "No .env file found at ${DOCKER_DIR}/.env"
    fi
    
    # Load .env.local file if it exists
    if [ -f "${DOCKER_DIR}/.env.local" ]; then
        log "Loading ${DOCKER_DIR}/.env.local"
        set -o allexport
        source "${DOCKER_DIR}/.env.local"
        set +o allexport
    else
        log_warning "No .env.local file found at ${DOCKER_DIR}/.env.local"
    fi
    
    log_success "Environment files loaded"
}

# Function to check system environment
check_system_env() {
    log "Checking system environment..."
    
    {
        echo "======= SYSTEM INFORMATION ======="
        echo "Date: $(date)"
        echo "Hostname: $(hostname)"
        echo "Kernel: $(uname -a)"
        echo "Distribution: $(cat /etc/*release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
        echo "CPU: $(grep "model name" /proc/cpuinfo | head -n1 | cut -d: -f2 | tr -d ' ')"
        echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
        echo ""
    } > "$ENV_REPORT"
    
    log_success "System environment checked"
}

# Function to check Python environment
check_python_env() {
    log "Checking Python environment..."
    
    {
        echo "======= PYTHON ENVIRONMENT ======="
        echo "Python version: $(python --version 2>&1)"
        echo "Pip version: $(pip --version 2>&1)"
        echo "Python path: $(which python)"
        echo "Pip path: $(which pip)"
        echo ""
        echo "Installed Python packages:"
        pip list
        echo ""
    } >> "$ENV_REPORT"
    
    log_success "Python environment checked"
}

# Function to check GPU availability
check_gpu() {
    log "Checking GPU availability..."
    
    {
        echo "======= GPU INFORMATION ======="
        if command -v nvidia-smi &> /dev/null; then
            echo "NVIDIA driver installed"
            echo "GPU information:"
            nvidia-smi
        else
            echo "NVIDIA driver not found"
        fi
        
        if [ -e /proc/driver/nvidia/version ]; then
            echo "NVIDIA driver version: $(cat /proc/driver/nvidia/version | head -n1)"
        fi
        
        echo "CUDA version: $(nvcc --version 2>/dev/null || echo 'CUDA not found')"
        echo ""
        
        # Check PyTorch GPU availability
        echo "PyTorch GPU availability:"
        python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('Number of GPUs:', torch.cuda.device_count())" 2>/dev/null || echo "PyTorch not installed or error checking GPU"
        echo ""
    } >> "$ENV_REPORT"
    
    log_success "GPU check completed"
}

# Function to check directory structure
check_directory_structure() {
    log "Checking directory structure..."
    
    {
        echo "======= DIRECTORY STRUCTURE ======="
        echo "ROOT directory: $ROOT"
        if [ -d "$ROOT" ]; then
            echo "ROOT exists: Yes"
            echo "ROOT contents:"
            ls -la "$ROOT" | sed 's/^/  /'
        else
            echo "ROOT exists: No"
        fi
        
        echo ""
        echo "COMFY_DIR: ${COMFY_DIR:-${ROOT}/ComfyUI}"
        if [ -d "${COMFY_DIR:-${ROOT}/ComfyUI}" ]; then
            echo "COMFY_DIR exists: Yes"
        else
            echo "COMFY_DIR exists: No"
        fi
        
        echo ""
        echo "Other important directories:"
        for dir in "${ROOT}/shared" "${ROOT}/shared_custom_nodes" "${ROOT}/config"; do
            echo "  $dir: $([ -d "$dir" ] && echo "Exists" || echo "Does not exist")"
        done
        echo ""
    } >> "$ENV_REPORT"
    
    log_success "Directory structure checked"
}

# Function to check environment variables
check_env_variables() {
    log "Checking environment variables..."
    
    {
        echo "======= ENVIRONMENT VARIABLES ======="
        echo "Important environment variables:"
        
        # Check common environment variables used in start.sh
        for var in ROOT NUM_GPUS MOCK_GPU TEST_GPUS SERVER_CREDS COMFY_AUTH HF_TOKEN OPENAI_API_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION COMFY_REPO_URL LANGFLOW_AUTO_LOGIN LANGFLOW_SUPERUSER LANGFLOW_SUPERUSER_PASSWORD; do
            echo "  $var: ${!var:+set (✓)}"
            if [ -z "${!var}" ]; then
                echo "  $var: not set (✗)"
            fi
        done
        
        echo ""
        echo "PATH: $PATH"
        echo ""
    } >> "$ENV_REPORT"
    
    log_success "Environment variables checked"
}

# Function to check installed packages
check_installed_packages() {
    log "Checking installed packages..."
    
    {
        echo "======= INSTALLED PACKAGES ======="
        echo "Checking for required system packages:"
        
        # List from Dockerfile
        packages=(
            "git" "git-lfs" "rsync" "nginx" "wget" "curl" "nano" "net-tools" "lsof" 
            "ffmpeg" "libsm6" "libxext6" "cron" "sudo" "ssh" "zstd" "jq" "build-essential" 
            "cmake" "ninja-build" "gcc" "g++" "openssh-client" "libx11-dev" "libxrandr-dev" 
            "libxinerama-dev" "libxcursor-dev" "libxi-dev" "libgl1-mesa-dev" "libglfw3-dev"
        )
        
        for pkg in "${packages[@]}"; do
            if is_package_installed "$pkg"; then
                echo "  $pkg: installed (✓)"
            else
                echo "  $pkg: not installed (✗)"
            fi
        done
        
        echo ""
    } >> "$ENV_REPORT"
    
    log_success "Package check completed"
}

# Function to install missing dependencies
install_missing_dependencies() {
    log "Installing missing dependencies..."
    
    # Update package lists
    apt update
    
    # Install basic packages from Dockerfile
    apt-get install -y \
        git git-lfs rsync nginx wget curl nano net-tools lsof nvtop multitail ffmpeg libsm6 libxext6\
        cron sudo ssh zstd jq build-essential cmake ninja-build \
        gcc g++ openssh-client libx11-dev libxrandr-dev libxinerama-dev \
        libxcursor-dev libxi-dev libgl1-mesa-dev libglfw3-dev software-properties-common
    
    # Install additional GCC packages
    apt update && add-apt-repository ppa:ubuntu-toolchain-r/test -y \
        && apt install -y gcc-11 g++-11 libstdc++6 \
        && apt-get install -y locales
    
    # Clean up
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
    log_success "Dependencies installed"
}

# Function to install newer libstdc++
install_libstdcxx() {
    log "Installing newer libstdc++..."
    
    cd /tmp && \
        wget http://security.ubuntu.com/ubuntu/pool/main/g/gcc-12/libstdc++6_12.3.0-1ubuntu1~22.04_amd64.deb && \
        dpkg -x libstdc++6_12.3.0-1ubuntu1~22.04_amd64.deb . && \
        cp -v usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30 /usr/lib/x86_64-linux-gnu/ && \
        cp -v usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30 /opt/conda/lib/ && \
        cd /usr/lib/x86_64-linux-gnu && \
        ln -sf libstdc++.so.6.0.30 libstdc++.so.6 && \
        cd /opt/conda/lib && \
        ln -sf libstdc++.so.6.0.30 libstdc++.so.6
    
    log_success "Installed newer libstdc++"
}

# Function to update Python packages
update_python_packages() {
    log "Updating Python packages..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install PyTorch
    pip install --upgrade torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
    
    # Install other requirements mentioned in the Dockerfile
    pip install --upgrade mmengine opencv-python imgui-bundle pyav boto3 awscli librosa uv
    
    log_success "Python packages updated"
}

# Function to clone ComfyUI if needed
setup_comfyui() {
    log "Setting up ComfyUI..."
    
    COMFY_DIR="${COMFY_DIR:-${ROOT}/ComfyUI}"
    
    if [ ! -d "$COMFY_DIR" ]; then
        log "Cloning ComfyUI repository..."
        git clone "${COMFY_REPO_URL:-https://github.com/comfyanonymous/ComfyUI.git}" "$COMFY_DIR"
        
        # Install requirements
        cd "$COMFY_DIR" && \
            pip uninstall -y onnxruntime && \
            pip install --upgrade pip && \
            pip install --upgrade mmengine opencv-python imgui-bundle pyav boto3 awscli librosa && \
            pip install -r requirements.txt && \
            pip uninstall -y onnxruntime-gpu && \
            pip install onnxruntime-gpu==1.20.1
    else
        log "ComfyUI directory already exists at $COMFY_DIR"
    fi
    
    log_success "ComfyUI setup completed"
}

# Function to setup shared directories
setup_shared_directories() {
    log "Setting up shared directories..."
    
    if [ ! -d "${ROOT}/shared" ]; then
        mkdir -p "${ROOT}/shared"
        git clone https://github.com/stakeordie/emprops_shared.git "${ROOT}/shared"
    fi
    
    if [ ! -d "${ROOT}/shared_custom_nodes" ] && [ -d "${DOCKER_DIR}/config/shared" ]; then
        mkdir -p "${ROOT}/shared_custom_nodes"
        cp -r "${DOCKER_DIR}/config/shared"/* "${ROOT}/shared_custom_nodes/"
        
        # Install requirements for custom nodes
        find "${ROOT}/shared_custom_nodes" -name "requirements.txt" -execdir pip install -r {} \;
    fi
    
    log_success "Shared directories setup completed"
}

# Function to configure services
setup_services() {
    log "Setting up services..."
    
    # Copy service scripts if they exist
    if [ -f "${DOCKER_DIR}/scripts/comfyui" ]; then
        cp "${DOCKER_DIR}/scripts/comfyui" /etc/init.d/comfyui
        chmod +x /etc/init.d/comfyui
        update-rc.d comfyui defaults
    fi
    
    if [ -f "${DOCKER_DIR}/scripts/langflow" ]; then
        cp "${DOCKER_DIR}/scripts/langflow" /etc/init.d/langflow
        chmod +x /etc/init.d/langflow
        update-rc.d langflow defaults
    fi
    
    # Setup utility scripts
    if [ -f "${DOCKER_DIR}/scripts/mgpu" ]; then
        cp "${DOCKER_DIR}/scripts/mgpu" /usr/local/bin/mgpu
        chmod +x /usr/local/bin/mgpu
    fi
    
    if [ -f "${DOCKER_DIR}/scripts/mcomfy" ]; then
        mkdir -p /usr/local/lib/mcomfy
        cp "${DOCKER_DIR}/scripts/mcomfy" /usr/local/bin/mcomfy
        chmod +x /usr/local/bin/mcomfy
    fi
    
    if [ -f "${DOCKER_DIR}/scripts/update_nodes.sh" ]; then
        cp "${DOCKER_DIR}/scripts/update_nodes.sh" /usr/local/lib/mcomfy/update_nodes.sh
        chmod +x /usr/local/lib/mcomfy/update_nodes.sh
    fi
    
    # Setup cleanup script
    if [ -f "${DOCKER_DIR}/scripts/cleanup_outputs.sh" ]; then
        cp "${DOCKER_DIR}/scripts/cleanup_outputs.sh" /usr/local/bin/cleanup_outputs.sh
        chmod +x /usr/local/bin/cleanup_outputs.sh
        echo "*/15 * * * * /usr/local/bin/cleanup_outputs.sh >> /var/log/cleanup.log 2>&1" > /etc/cron.d/cleanup
        chmod 0644 /etc/cron.d/cleanup
    fi
    
    # Setup cron
    mkdir -p /var/run/cron
    touch /var/run/cron/crond.pid
    chmod 644 /var/run/cron/crond.pid
    sed -i 's/touch $PIDFILE/# touch $PIDFILE/g' /etc/init.d/cron
    
    log_success "Services setup completed"
}

# Main function
main() {
    log ""
    log "=============================================="
    log "      Direct Environment Setup Script         "
    log "=============================================="
    log ""
    
    # Load environment variables
    load_env_files
    
    # Check current environment and generate report
    log "Generating environment report..."
    check_system_env
    check_python_env
    check_gpu
    check_directory_structure
    check_env_variables
    check_installed_packages
    
    log_success "Environment report generated at $ENV_REPORT"
    log "Report summary:"
    head -n 10 "$ENV_REPORT"
    log "..."
    
    # Ask for confirmation before proceeding
    read -p "Do you want to proceed with the setup? (y/n): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log "Setup aborted by user."
        exit 0
    fi
    
    # Install and configure everything needed
    install_missing_dependencies
    install_libstdcxx
    update_python_packages
    setup_comfyui
    setup_shared_directories
    setup_services
    
    # Run start.sh if it exists
    if [ -f "${DOCKER_DIR}/scripts/start.sh" ]; then
        log "Running start.sh..."
        chmod +x "${DOCKER_DIR}/scripts/start.sh"
        "${DOCKER_DIR}/scripts/start.sh"
    else
        log_error "start.sh not found at ${DOCKER_DIR}/scripts/start.sh"
    fi
    
    log_success "Setup completed successfully"
}

# Execute main function
main
