#!/bin/bash

# Get the script's directory path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/config/monitor.config.cjs"

# Load configuration using node
load_config() {
    node --no-warnings -e "
        const config = require('$CONFIG_FILE').test;
        console.log(JSON.stringify({
            logsDir: config.paths.logsDir,
            logFile: config.paths.logs.monitor
        }));
    "
}

# Parse configuration
CONFIG=$(load_config)
LOGS_DIR=$(echo "$CONFIG" | node --no-warnings -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf-8')).logsDir)")
LOG_FILE=$(echo "$CONFIG" | node --no-warnings -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf-8')).logFile)")

# Arguments from PM2
LOG_PATH="${1}"          # Monitor log path
TIMEOUT="${2:-30}"       # Timeout in seconds
SERVICE_NAME="${3:-generator}"  # Service to monitor, default to 'generator'
MONITOR_LOG="$LOGS_DIR/$LOG_FILE"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

echo "Starting monitor for service: $SERVICE_NAME"
echo "Timeout set to: $TIMEOUT seconds"
echo "Monitor log: $MONITOR_LOG"

# Initialize variables
last_activity=$(date +%s)
current_generation=false

log_monitor_status() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MONITOR_LOG"
}

check_timeout() {
    current_time=$(date +%s)
    time_diff=$((current_time - last_activity))
    
    if [ $time_diff -gt $TIMEOUT ]; then
        log_monitor_status "No activity detected for $TIMEOUT seconds. Restarting service..."
        pm2 restart "$SERVICE_NAME"
        last_activity=$(date +%s)
    fi
}

# Main monitoring loop
log_monitor_status "Monitor started"

# Use PM2 log streaming
pm2 logs "$SERVICE_NAME" --raw | while IFS= read -r line; do
    # Reset timeout on any activity
    last_activity=$(date +%s)
    
    # Process the log line
    if echo "$line" | grep -q "\[START\]"; then
        if [ "$current_generation" = true ]; then
            log_monitor_status "Warning: New generation started while another was in progress"
        fi
        current_generation=true
        log_monitor_status "Generation started"
        
    elif echo "$line" | grep -q "\[WEBSOCKET:status\]"; then
        if [ "$current_generation" = true ]; then
            log_monitor_status "Status update received"
        fi
        
    elif echo "$line" | grep -q "\[WEBSOCKET:progress\]"; then
        if [ "$current_generation" = true ]; then
            progress=$(echo "$line" | grep -o '[0-9]\+')
            log_monitor_status "Progress update: $progress%"
        fi
        
    elif echo "$line" | grep -q "\[WEBSOCKET:complete\]"; then
        if [ "$current_generation" = true ]; then
            current_generation=false
            log_monitor_status "Generation completed successfully"
        fi
    fi
    
    # Check for timeout
    check_timeout
done

log_monitor_status "Monitor stopped"