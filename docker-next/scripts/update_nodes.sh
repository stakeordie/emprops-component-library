#!/bin/bash

# Set up environment
ROOT="${ROOT:-/workspace}"
LOG_DIR="${ROOT}/logs"
UPDATE_LOG="${LOG_DIR}/update.log"
NODE_STATE_FILE="${ROOT}/shared/node_state.json"

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Enable debug mode if DEBUG is set, but don't show command execution
if [ "${DEBUG:-}" = "true" ]; then
    export PS4='+ ${BASH_SOURCE##*/}:${LINENO}: '
    set -x
fi

# Ensure log directory exists
mkdir -p "$LOG_DIR"
touch "$UPDATE_LOG"

log() {
    local msg_type="${1:-INFO}"
    shift
    local color="$BLUE"
    
    case "$msg_type" in
        "ERROR") color="$RED" ;;
        "WARNING") color="$YELLOW" ;;
        "SUCCESS") color="$GREEN" ;;
        *) msg_type="INFO" ;;
    esac
    
    printf "${color}%s${NC} %s\n" "$msg_type:" "$*" | tee -a "$UPDATE_LOG"
}

# Shorthand logging functions
info() { log "INFO" "$@"; }
error() { log "ERROR" "$@"; }
warning() { log "WARNING" "$@"; }
success() { log "SUCCESS" "$@"; }

sync_from_s3() {
    info "=== Starting S3 sync ==="
    
    # Determine which bucket to use based on AWS_TEST_MODE
    local bucket="emprops-share"
    if [ "${AWS_TEST_MODE:-false}" = "true" ]; then
        info "Using test bucket: emprops-share-test"
        bucket="emprops-share-test"
    else
        info "Using production bucket: emprops-share"
    fi

    # Sync only config files from S3, exclude models and custom_nodes
    info "Syncing config files from s3://$bucket..."
    if [ "${SKIP_AWS_SYNC:-false}" = "true" ]; then
        info "Skipping AWS S3 sync (SKIP_AWS_SYNC=true)"
    else
        info "Running AWS S3 sync for config files..."
        aws s3 sync "s3://$bucket" /workspace/shared \
            --exclude "*" \
            --include "config_nodes*.json" \
            --size-only 2>&1 | tee -a "${UPDATE_LOG}"
        
        local sync_status=$?
        if [ $sync_status -eq 0 ]; then
            success "Config files sync completed"
        else
            error "Config files sync failed with status $sync_status"
            return 1
        fi
    fi
    
    info "=== S3 sync complete ==="
}

get_node_state() {
    local name=$1
    local dir="/workspace/shared/custom_nodes/$name"
    
    if [ ! -d "$dir" ]; then
        echo "not_installed"
        return
    fi
    
    if [ ! -d "$dir/.git" ]; then
        echo "invalid"
        return
    fi
    
    cd "$dir" || return
    
    local current_commit
    current_commit=$(git rev-parse HEAD 2>/dev/null)
    local current_url
    current_url=$(git config --get remote.origin.url 2>/dev/null)
    
    echo "{\"commit\": \"$current_commit\", \"url\": \"$current_url\"}"
}

save_node_states() {
    info "Saving current node states..."
    echo "{" > "$NODE_STATE_FILE"
    echo "  \"nodes\": {" >> "$NODE_STATE_FILE"
    
    local first=true
    for dir in /workspace/shared/custom_nodes/*/; do
        if [ -d "$dir" ]; then
            local name
            name=$(basename "$dir")
            local state
            state=$(get_node_state "$name")
            
            if [ "$first" = true ]; then
                first=false
            else
                echo "    ," >> "$NODE_STATE_FILE"
            fi
            
            echo "    \"$name\": $state" >> "$NODE_STATE_FILE"
        fi
    done
    
    echo "  }" >> "$NODE_STATE_FILE"
    echo "}" >> "$NODE_STATE_FILE"
    
    info "Node states saved to $NODE_STATE_FILE"
}

setup_node() {
    local name=$1
    local url=$2
    local branch=$3
    local commit=$4
    local install_reqs=$5
    local recursive=$6
    local env_vars=$7
    local action=$8
    
    info "Setting up node: $name (Action: $action)"
    info "  URL: $url"
    info "  Branch: ${branch:-default}"
    info "  Commit: ${commit:-latest}"
    
    cd /workspace/shared/custom_nodes || {
        error "Failed to change to custom_nodes directory"
        return 1
    }
    
    case "$action" in
        "install"|"update")
            if [ "$action" = "update" ] && [ -d "$name" ]; then
                info "  Updating existing repository"
                cd "$name" || return 1
                git fetch origin
                cd ..
            else
                if [ -d "$name" ]; then
                    info "  Removing existing directory for clean install"
                    rm -rf "$name"
                fi
                
                info "  Cloning repository"
                local clone_cmd="git clone"
                if [ "$recursive" = "true" ]; then
                    clone_cmd="$clone_cmd --recursive"
                fi
                
                if [ -n "$branch" ] && [ "$branch" != "null" ]; then
                    info "  Cloning branch: $branch"
                    $clone_cmd -b "$branch" "$url" "$name" || return 1
                else
                    info "  Cloning default branch"
                    $clone_cmd "$url" "$name" || return 1
                fi
            fi
            
            cd "$name" || return 1
            
            if [ -n "$commit" ] && [ "$commit" != "null" ]; then
                info "  Checking out specific commit: $commit"
                git reset --hard "$commit" || return 1
            fi
            
            # Handle environment variables
            if [ -n "$env_vars" ] && [ "$env_vars" != "null" ]; then
                info "  Setting up .env file"
                : > .env
                
                while IFS="=" read -r key value; do
                    if [ -n "$key" ]; then
                        expanded_value=$(eval echo "$value")
                        echo "$key=$expanded_value" >> .env
                        info "    Added env var: $key"
                    fi
                done < <(echo "$env_vars" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"')
            fi
            
            # Install requirements if specified
            if [ "$install_reqs" = "true" ]; then
                if [ -f "requirements.txt" ]; then
                    info "  Installing requirements using uv..."
                    uv pip install --system -r requirements.txt || {
                        warning "uv install failed, falling back to pip..."
                        pip install -r requirements.txt || {
                            error "Failed to install requirements"
                            return 1
                        }
                    }
                    success "Requirements installed successfully"
                else
                    info "  No requirements.txt found"
                fi
            fi
            
            cd ..
            ;;
            
        "remove")
            if [ -d "$name" ]; then
                info "  Removing node directory"
                rm -rf "$name"
            else
                info "  Node directory already removed"
            fi
            ;;
            
        *)
            error "Unknown action: $action"
            return 1
            ;;
    esac
    
    info "Node $name processed successfully"
    return 0
}

update_nodes() {
    info "=== Starting node updates ==="
    
    # Determine which config file to use
    local config_file="/workspace/shared/config_nodes.json"
    
    info "AWS_TEST_MODE=${AWS_TEST_MODE:-false}"
    if [ "${AWS_TEST_MODE:-false}" = "true" ]; then
        info "Using test config: config_nodes_test.json"
        config_file="/workspace/shared/config_nodes_test.json"
    else
        info "Using production config: config_nodes.json"
    fi
    
    info "Using config file: $config_file"
    
    if [ ! -f "$config_file" ]; then
        error "Config file $config_file not found"
        return 1
    fi
    
    # Save current state before making changes
    save_node_states
    
    # Process each node in the config
    info "Processing nodes from config..."
    for node in $(jq -r '.custom_nodes[] | @base64' "$config_file"); do
        _jq() {
            echo "${node}" | base64 --decode | jq -r "${1}"
        }
        
        name=$(_jq '.name')
        url=$(_jq '.url')
        branch=$(_jq '.branch')
        commit=$(_jq '.commit // empty')
        install_reqs=$(_jq '.requirements')
        recursive=$(_jq '.recursive')
        env_vars=$(_jq '.env')
        
        if [ "$name" = "null" ] || [ "$url" = "null" ]; then
            error "Invalid node configuration (missing name or url)"
            continue
        fi
        
        # Get current state
        current_state=$(get_node_state "$name")
        
        # Determine action based on state
        action="install"
        if [ "$current_state" != "not_installed" ] && [ "$current_state" != "invalid" ]; then
            current_url=$(echo "$current_state" | jq -r '.url')
            if [ "$current_url" != "$url" ]; then
                action="install"  # Reinstall if URL changed
            else
                action="update"
            fi
        fi
        
        # Process the node
        if ! setup_node "$name" "$url" "$branch" "$commit" "$install_reqs" "$recursive" "$env_vars" "$action"; then
            error "Failed to process node $name"
            continue
        fi
    done
    
    # Handle removals - check for nodes that exist but aren't in config
    info "Checking for nodes to remove..."
    for dir in /workspace/shared/custom_nodes/*/; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            if ! jq -e ".custom_nodes[] | select(.name == \"$name\")" "$config_file" >/dev/null; then
                info "Found node to remove: $name"
                setup_node "$name" "" "" "" "" "" "" "remove"
            fi
        fi
    done
    
    # Save final state
    save_node_states
    
    info "=== Node updates complete ==="
}

main() {
    info "=== Starting update process ==="
    
    # Parse command line arguments
    NODES_ONLY=false
    MODELS_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --nodes-only)
                NODES_ONLY=true
                shift
                ;;
            --models-only)
                MODELS_ONLY=true
                shift
                ;;
            *)
                error "Unknown argument '$1'"
                return 1
                ;;
        esac
    done
    
    # Validate arguments
    if [ "$NODES_ONLY" = true ] && [ "$MODELS_ONLY" = true ]; then
        error "Cannot specify both --nodes-only and --models-only"
        return 1
    fi
    
    if [ "$MODELS_ONLY" = true ]; then
        info "Running models sync only"
        if ! sync_from_s3; then
            error "S3 sync failed"
            return 1
        fi
    elif [ "$NODES_ONLY" = true ]; then
        info "Running nodes update only"
        if ! update_nodes; then
            error "Node updates failed"
            return 1
        fi
    else
        # Default behavior: run both
        info "Running full update (models and nodes)"
        if ! sync_from_s3; then
            error "S3 sync failed"
            return 1
        fi
        
        if ! update_nodes; then
            error "Node updates failed"
            return 1
        fi
    fi
    
    info "=== Update process complete ==="
}

main "$@"
