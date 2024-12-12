#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/config/monitor.config.cjs"

# Load configuration using node
load_config() {
    node --no-warnings << EOF
        const config = require('${CONFIG_FILE}').test;
        console.log(JSON.stringify({
            logsDir: config.paths.logsDir,
            logFile: config.paths.logs.generator,
            interval: config.timing.generatorInterval
        }));
EOF
}

# Parse configuration
CONFIG=$(load_config)
LOGSDIR=$(echo "$CONFIG" | node --no-warnings -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf-8')).logsDir)")
LOGFILE=$(echo "$CONFIG" | node --no-warnings -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf-8')).logFile)")
INTERVAL=$(echo "$CONFIG" | node --no-warnings -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf-8')).interval)")

# Ensure logs directory exists
mkdir -p "$LOGSDIR"
OUTPUT="$LOGSDIR/$LOGFILE"
MODE_FILE="$LOGSDIR/generator.mode"
echo "normal" > "$MODE_FILE"

# Function to write log with timestamp
write_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$OUTPUT"
}

# Function to get current mode
get_mode() {
    cat "$MODE_FILE" 2>/dev/null || echo "normal"
}

# Function to simulate a generation cycle
simulate_generation() {
    local gen_id="$1"
    local current_mode=$(get_mode)
    
    case "$current_mode" in
        "normal")
            write_log "Process completed successfully - Job ID: $gen_id"
            sleep 1
            ;;
        "stalled")
            write_log "Starting long-running operation - Job ID: $gen_id"
            sleep 30
            write_log "Long-running operation complete - Job ID: $gen_id"
            ;;
        "concurrent")
            for i in {1..5}; do
                write_log "Concurrent operation $i in progress - Job ID: $gen_id"
                sleep 1
            done
            ;;
        *)
            write_log "Standard operation completed - Job ID: $gen_id"
            sleep 1
            ;;
    esac
}

# Function to change mode
change_mode() {
    echo "${1:-normal}" > "$MODE_FILE"
}

# Trap signals to change modes
trap 'change_mode "normal"' SIGUSR1
trap 'change_mode "stalled"' SIGUSR2
trap 'change_mode "concurrent"' SIGHUP

# Main loop
if [ "$1" = "start" ]; then
    generation=0
    while true; do
        simulate_generation "$generation"
        generation=$((generation + 1))
        sleep "$INTERVAL"
    done
fi