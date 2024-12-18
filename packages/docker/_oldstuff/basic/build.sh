#!/bin/bash

set -Eeuo pipefail

ROOT=/comfyui-launcher

echo $ROOT
ls -lha $ROOT
ls -lha / 

echo "Installing pm2..."
apt-get install -y ca-certificates curl gnupg ufw
mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y nodejs git-lfs
npm install -g npm@9.8.0
npm install -g pm2@latest
pip install --ignore-installed websocket-client flask gdown

cd ${ROOT}

apt install -y nvtop

echo "~~READY~~"