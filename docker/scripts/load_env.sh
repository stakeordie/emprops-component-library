#!/bin/bash
# load_env.sh
# Securely loads environment variables in the Docker container

set -e

ENV_FILE="${1:-/workspace/.env}"
LOG_FILE="/workspace/logs/env_load.log"

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Logging function
log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log "Starting environment variable loading"

# Function to mask sensitive values when logging
mask_value() {
    local value="$1"
    local masked=""
    
    if [[ ${#value} -le 8 ]]; then
        masked="********"
    else
        masked="${value:0:4}...${value: -4}"
    fi
    
    echo "$masked"
}

# Check if the env file exists
if [[ -f "$ENV_FILE" ]]; then
    log "Loading environment variables from $ENV_FILE"
    
    # Read each line from the env file
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        if [[ -z "$line" || "$line" =~ ^\s*# ]]; then
            continue
        fi
        
        # Extract variable name and value
        if [[ "$line" =~ ^([A-Za-z0-9_-]+)=(.*)$ ]]; then
            var_name="${BASH_REMATCH[1]}"
            var_value="${BASH_REMATCH[2]}"
            
            # Remove quotes if present
            var_value="${var_value%\"}"
            var_value="${var_value#\"}"
            var_value="${var_value%\'}"
            var_value="${var_value#\'}"
            
            # Set the environment variable
            export "$var_name"="$var_value"
            
            # Log masked values for sensitive variables
            if [[ "$var_name" == *"KEY"* || "$var_name" == *"SECRET"* || "$var_name" == *"PASSWORD"* || "$var_name" == *"TOKEN"* ]]; then
                log "Set $var_name=$(mask_value "$var_value")"
            else
                log "Set $var_name=$var_value"
            fi
        fi
    done < "$ENV_FILE"
    
    log "Environment variables loaded successfully"
else
    log "WARNING: Environment file $ENV_FILE not found"
fi

# Verify critical environment variables
check_env_var() {
    local var_name="$1"
    local required="$2"
    
    if [[ -z "${!var_name}" ]]; then
        if [[ "$required" == "true" ]]; then
            log "ERROR: Required environment variable $var_name is not set"
            return 1
        else
            log "WARNING: Optional environment variable $var_name is not set"
        fi
    else
        if [[ "$var_name" == *"KEY"* || "$var_name" == *"SECRET"* || "$var_name" == *"PASSWORD"* || "$var_name" == *"TOKEN"* ]]; then
            log "Verified $var_name=$(mask_value "${!var_name}")"
        else
            log "Verified $var_name=${!var_name}"
        fi
    fi
    
    return 0
}

# AWS credentials are required for S3 model syncing
if check_env_var "AWS_ACCESS_KEY_ID" "true" && \
   check_env_var "AWS_SECRET_ACCESS_KEY" "true" && \
   check_env_var "AWS_DEFAULT_REGION" "true"; then
    log "AWS credentials verified"
else
    log "WARNING: AWS credentials incomplete, S3 model syncing may not work"
fi

# Check optional API keys
check_env_var "OPENAI_API_KEY" "false"
check_env_var "HF_TOKEN" "false"

log "Environment verification complete"
