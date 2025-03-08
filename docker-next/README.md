# Docker Setup Guide

This guide explains how to set up and run the ComfyUI environment both locally and on a remote server, with support for both GPU and mock (CPU) modes.

## Prerequisites

- Docker and Docker Compose installed
- AWS credentials (for S3 sync features)
- HuggingFace token
- OpenAI API key (optional)
- SSH key for NGINX repository access

## Local Development Setup

### 1. Environment Configuration

1. Copy the sample environment file:
   ```bash
   cp .env.sample .env.local
   ```

2. Configure your environment variables in `.env.local`:
   - `HF_TOKEN`: Your HuggingFace token
   - `OPENAI_API_KEY`: Your OpenAI API key (if needed)
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY_ENCODED`: encoded with _SLASH_ replacing `/`: hd/d/df -> hd_SLASH_d_SLASH_df
   - `AWS_DEFAULT_REGION`: "us-east-1"
   - `SERVER_CREDS`: HTTP Basic Auth for NGINX. Provide only the password.
   - `TEST_GPUS`: Number of GPUs to mock in test mode
   - `AWS_TEST_MODE`: Set to `true` for test mode

3. Set up SSH key parts (for repository access):
   ```bash
   # Generate the CUT_PK parts from your SSH key
   openssl base64 -in ~/.ssh/id_ed25519 | tr -d '\n' | cut -c-250 > cut1
   openssl base64 -in ~/.ssh/id_ed25519 | tr -d '\n' | cut -c251-500 > cut2
   openssl base64 -in ~/.ssh/id_ed25519 | tr -d '\n' | cut -c501- > cut3
   ```
   Add these values to your `.env.local` as `CUT_PK_1`, `CUT_PK_2`, and `CUT_PK_3`.

### 2. Building and Running

#### 2.1. Build Types

Test and Mock GPU setups are defined in the .env.local file:
- `AWS_TEST_MODE`: Set to `true` for test mode, `false` or unset for production
- `TEST_GPUS`: Number of GPUs to mock in test mode (0 or unset for script to determine GPUs 

#### AWS_TEST_MODE

Bucket Sync: When AWS_TEST_MODE is set to true will use the AWS bucket emprops-share-test for model and config sync. This is useful for testing and debugging in a controlled environment. The production bucket is 100 + GB so it will take a while. The test bucket only has the defualt ComryUI model SD1.5.

Config_nodes_test will also be used which limits the to EmProps Nodes.

#### TEST_GPUS

Mock GPU: When TEST_GPUS is set to a number it will mock that many GPUs in test mode, this results in MOCK_GPU being set to 1 or true and the number of TEST_GPUS being set will run all with the --cpu flag in the comfyui service start command.  This is useful for testing and debugging in a controlled environment. 
If you don't set TEST_GPUS the system will still check for GPU support and if it can't find any it set the number of GPUs to 1 but will also set MOCK_GPU=1.

#### 2.2. Docker Compose


Run `cd docker` to enter the Docker Directory.

Run `docker compose build comfyui` to build the Docker images.
Run `docker compose up comfyui` to start the container.
or
Run `docker compose up --build comfyui` to build and start the container.

Run `docker compose down` to stop and remove the container.

Run `docker exec -it comfy /bin/bash` to enter the container.

Run `docker push emprops/docker:latest` to push the latest image to Docker Hub.


### mgpu CLI usage

Commands:
   - start   [gpu_id]       Start ComfyUI service for GPU
   - stop    [gpu_id]       Stop ComfyUI service for GPU
   - restart [gpu_id]       Restart ComfyUI service for GPU
   - status  [gpu_id]       Show status of ComfyUI service for GPU
   - logs    [gpu_id]       Show logs for GPU
   - setup   [gpu_id]       Setup ComfyUI for GPU
   - count                  Show number of available GPUs

#### Logs
mgpu uses multitail for consolidated logging.
   - "b" to scroll | up down pageup pagedown
   - "/" to search
   - "q" to quite

logs accepts multiple gpu_ids. so mgpu `logs 1 3 4` will work.\5