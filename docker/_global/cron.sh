#!/bin/bash

# Specify the folder path
FOLDER_PATH="/comfyui-launcher/ComfyUI/output"

# Define the cron job schedule and command
CRON_JOB="0 * * * * rm -f $FOLDER_PATH/*"

# Check if the cron job already exists
(crontab -l | grep -q "$CRON_JOB") || (crontab -l; echo "$CRON_JOB") | crontab -
