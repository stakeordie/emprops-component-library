# Docker Installation Guide

This guide provides detailed instructions for building and running our Docker containers.

## Prerequisites

- Docker installed on your system
- NVIDIA GPU with appropriate drivers
- NVIDIA Container Toolkit installed

## Building the Containers

### Standard ComfyUI Container

```bash
cd docker
docker build -t emprops-comfyui -f Dockerfile .
```

### Hybrid ComfyUI + A1111 Container

```bash
cd docker
docker build -t emprops-hybrid -f Dockerfile.hybrid .
```

## Running the Containers

### ComfyUI Container

```bash
docker run -p 3188:3188 --gpus all \
  -v /path/to/your/models:/workspace/shared \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=your_region \
  emprops-comfyui
```

### Hybrid Container

```bash
docker run -p 3188:3188 -p 3130:3130 --gpus all \
  -v /path/to/your/models:/workspace/shared \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=your_region \
  emprops-hybrid
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROOT` | Root directory | `/workspace` |
| `ROOT_COMFY` | ComfyUI installation directory | `/workspace/ComfyUI` |
| `ROOT_A1111` | A1111 installation directory | `/stable-diffusion-webui` |
| `SHARED_DIR` | Shared models directory | `/workspace/shared` |
| `AWS_S3_BUCKET` | S3 bucket for models | - |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `AWS_DEFAULT_REGION` | AWS region | - |

## Accessing the Services

- ComfyUI: http://localhost:3188
- A1111 (hybrid container only): http://localhost:3130

## Troubleshooting

### Common Issues

- **GPU not detected**: Ensure NVIDIA drivers and Container Toolkit are properly installed
- **Models not found**: Verify AWS credentials and S3 bucket configuration
- **Container crashes**: Check the logs for specific error messages:
  ```bash
  docker logs container_name
  ```

### Logs

Container logs are stored in `/workspace/logs/` and can be viewed from within the container or by mounting the directory to your host system.
