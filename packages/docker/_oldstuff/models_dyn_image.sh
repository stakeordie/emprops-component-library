#!/bin/bash

# Default values
ROOT="/home/ubuntu/ComfyUI"
CONFIG_FILE=""
MAX_PARALLEL=5

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            ROOT="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --parallel)
            MAX_PARALLEL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --path <root_path> --config <config_file> [--parallel <max_parallel>]"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$CONFIG_FILE" ]; then
    echo "Error: Config file is required"
    echo "Usage: $0 --path <root_path> --config <config_file> [--parallel <max_parallel>]"
    exit 1
fi

# Ensure jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "jq could not be found. Installing..."
    apt-get update && apt-get install -y jq
fi

git lfs install

rm -rf ${ROOT}/models/*

# Function to download file with retry mechanism
download_file() {
    local url="$1"
    local output="$2"
    local max_retries=3
    local retry_count=0

    # Ensure output directory exists
    mkdir -p "$(dirname "$output")"

    while [ $retry_count -lt $max_retries ]; do
        wget -O "$output" "$url" && return 0
        retry_count=$((retry_count + 1))
        echo "Download failed for $url. Retry $retry_count of $max_retries"
        sleep 2
    done
    return 1
}

# Function to process download queue with parallel limit
process_downloads() {
    local max_parallel=${1:-5}
    local active_jobs=0
    
    while IFS='|' read -r url path; do
        while [ $active_jobs -ge $max_parallel ]; do
            wait -n
            active_jobs=$((active_jobs - 1))
        done
        
        download_file "$url" "${ROOT}/models/${path}" &
        active_jobs=$((active_jobs + 1))
    done

    wait
}

# Process all model types from JSON and create download queue
(
    # Use jq to extract all model entries regardless of category
    jq -r 'to_entries | .[] | .value[] | [.url, .path] | join("|")' "$CONFIG_FILE" | process_downloads $MAX_PARALLEL
)

# Verify downloaded files
echo "Downloaded files:"
find ${ROOT}/models -type f
