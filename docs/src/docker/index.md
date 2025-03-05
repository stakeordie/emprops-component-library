# Docker Containers

This section covers the Docker container setup for ComfyUI and related services.

## Overview

We provide several Docker configurations:

1. **ComfyUI Container**: Standard container for running ComfyUI
2. **Hybrid Container**: Combined ComfyUI and A1111 Stable Diffusion WebUI container with shared models

## Container Types

| Container Type | Description | Use Case |
|---------------|-------------|----------|
| [ComfyUI](/docker/comfyui) | Standard ComfyUI container | When you only need ComfyUI functionality |
| [Hybrid Container](/docker/hybrid) | Combined ComfyUI + A1111 container | When you need both A1111 and ComfyUI with shared models |

## Key Features

- AWS S3 integration for model management
- Shared model repository to minimize duplication
- Efficient resource usage across services
- Comprehensive environment configuration

## Getting Started

See the [Installation Guide](/docker/installation) for detailed instructions on building and running our containers.
