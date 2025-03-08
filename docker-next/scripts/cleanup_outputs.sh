#!/bin/bash

ROOT="${ROOT:-/workspace}"
NUM_GPUS="${NUM_GPUS:-1}"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Clean up outputs for all GPU instances
for gpu in $(seq 0 $((NUM_GPUS-1))); do
    OUTPUT_DIR="${ROOT}/comfyui_gpu${gpu}/output"
    
    if [ -d "$OUTPUT_DIR" ]; then
        log "Cleaning output directory for GPU $gpu: $OUTPUT_DIR"
        find "$OUTPUT_DIR" -type f -mmin +60 -delete
        find "$OUTPUT_DIR" -type d -empty -delete
    else
        log "Output directory for GPU $gpu does not exist: $OUTPUT_DIR"
    fi
done

log "Cleanup complete"
