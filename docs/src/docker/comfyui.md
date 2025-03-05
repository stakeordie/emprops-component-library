# ComfyUI Container

This page documents the standalone ComfyUI Docker container.

## Overview

The ComfyUI container provides a complete, self-contained environment for running ComfyUI with all necessary dependencies pre-installed.

## Architecture

```mermaid
graph TD
    subgraph "Docker Container"
        subgraph "File System"
            rootDir["/workspace"] --> comfyDir["/workspace/ComfyUI"]
            rootDir --> configDir["/workspace/config"]
            rootDir --> logsDir["/workspace/logs"]
            rootDir --> sharedDir["/workspace/shared"]
            rootDir --> scriptsDir["/workspace/scripts"]
        end
        
        subgraph "Services"
            comfyUI["ComfyUI\n(Port 3188)"]
            nginx["NGINX\nProxy"]
        end
        
        subgraph "Resources"
            models["Model Repository\n/workspace/shared"]
            customNodes["Custom Nodes\n/workspace/shared_custom_nodes"]
        end
        
        comfyDir --> comfyUI
        comfyUI --> nginx
        sharedDir --> models
        models --> comfyUI
        customNodes --> comfyUI
    end
    
    externalS3["AWS S3\nModel Repository"] -->|Sync| models
    
    user["User"] -->|Port 3188| nginx
```

## Container Components

- **PyTorch Base**: `pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime`
- **ComfyUI**: Latest version from GitHub
- **NGINX**: For serving web interface
- **Model Management**: AWS S3 integration for model syncing

## Directory Structure

- `/workspace`: Root directory
  - `/workspace/ComfyUI`: ComfyUI installation
  - `/workspace/config`: Configuration files
  - `/workspace/logs`: Log files
  - `/workspace/shared`: Shared model repository
  - `/workspace/shared_custom_nodes`: Custom ComfyUI nodes

## Startup Process

```mermaid
sequenceDiagram
    participant Container as Docker Container
    participant Script as start.sh
    participant ComfyUI as ComfyUI Service
    participant NGINX as NGINX
    participant AWS as AWS S3
    
    Container->>Script: Run entrypoint
    
    Script->>Script: Setup environment
    Script->>Script: Check environment variables
    
    Script->>AWS: Sync models from S3
    AWS-->>Script: Models synced
    
    Script->>NGINX: Configure and start
    NGINX-->>Script: NGINX ready
    
    Script->>ComfyUI: Start ComfyUI
    ComfyUI-->>Script: ComfyUI running
    
    Script->>Script: Verify services
    Script->>Container: Keep container running
```

## Key Scripts

- `start.sh`: Main entry point
- `s3_sync.sh`: AWS S3 model synchronization
- `setup_nginx.sh`: NGINX configuration

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ROOT` | Root directory | No |
| `AWS_S3_BUCKET` | S3 bucket for models | Yes (for S3 sync) |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes (for S3 sync) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes (for S3 sync) |
| `AWS_DEFAULT_REGION` | AWS region | Yes (for S3 sync) |

For a complete list of environment variables, see the [Installation Guide](/docker/installation).

## Building and Running

See the [Installation Guide](/docker/installation) for detailed instructions on building and running the container.
