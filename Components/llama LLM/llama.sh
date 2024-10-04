#!/bin/bash -i
apt update
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install stable && npm install -g pm2
apt-get update && apt-get install nano ffmpeg libsm6 libxext6 -y
pip install --ignore-installed websocket-client flask gdown
## llama
curl -fsSL https://ollama.com/install.sh | sh
source ~/.bashrc
pm2 start --name ollama "OLLAMA_HOST=0.0.0.0 ollama serve"
ollama pull llama3.1:latest
ollama pull llava-llama3:latest
gdown https://drive.google.com/uc?id=1Vx4kqcpPKfUpYSFpK_0XRZ7h64nosraW
gdown https://drive.google.com/uc?id=1d3wPbtjFcgCkWAMVFQalOuQHdiNmfc5i

pm2 restart all;
