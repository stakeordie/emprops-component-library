#!/bin/bash

set -Eeuo pipefail

# TODO: move all mkdir -p ?
mkdir -p /data/config/auto/scripts/
# mount scripts individually

ROOT=/stable-diffusion-webui

echo $ROOT
ls -lha $ROOT
ls -lha /

find "${ROOT}/scripts/" -maxdepth 1 -type l -delete
cp -vrfTs /data/config/auto/scripts/ "${ROOT}/scripts/"

apt-get install git-lfs
git lfs install
git clone https://github.com/stakeordie/sd_models.git /docker/emprops_models_repo
rm -rf /docker/emprops_models_repo/.git

echo "Installing pm2..."
apt-get install -y ca-certificates curl gnupg
mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y nodejs
apt-get install nodejs -y
npm install -g npm@9.8.0
npm install -g pm2@latest
pm2 status

cp /docker/error_catch_all.sh ~/.pm2/logs/error_catch_all.sh


# Set up config file
python /docker/config.py /data/config/auto/config.json

if [ ! -f /data/config/auto/ui-config.json ]; then
  echo '{}' >/data/config/auto/ui-config.json
fi

if [ ! -f /data/config/auto/styles.csv ]; then
  touch /data/config/auto/styles.csv
fi

# copy models from original models folder
mkdir -p /data/models/VAE-approx/ /data/models/karlo/

rsync -a --info=NAME ${ROOT}/models/VAE-approx/ /data/models/VAE-approx/
rsync -a --info=NAME ${ROOT}/models/karlo/ /data/models/karlo/
#rsync -a --info=NAME /docker/the-models/ /data/models/Stable-diffusion/

declare -A MOUNTS

MOUNTS["/root/.cache"]="/data/.cache"
MOUNTS["${ROOT}/models"]="/data/models"

MOUNTS["${ROOT}/embeddings"]="/data/embeddings"
MOUNTS["${ROOT}/config.json"]="/data/config/auto/config.json"
MOUNTS["${ROOT}/ui-config.json"]="/data/config/auto/ui-config.json"
MOUNTS["${ROOT}/styles.csv"]="/data/config/auto/styles.csv"
MOUNTS["${ROOT}/extensions"]="/data/config/auto/extensions"
MOUNTS["${ROOT}/config_states"]="/data/config/auto/config_states"

# extra hacks
MOUNTS["${ROOT}/repositories/CodeFormer/weights/facelib"]="/data/.cache"

for to_path in "${!MOUNTS[@]}"; do
  set -Eeuo pipefail
  from_path="${MOUNTS[${to_path}]}"
  rm -rf "${to_path}"
  if [ ! -f "$from_path" ]; then
    mkdir -vp "$from_path"
  fi
  mkdir -vp "$(dirname "${to_path}")"
  ln -sT "${from_path}" "${to_path}"
  echo Mounted $(basename "${from_path}")
done

echo "Installing extension dependencies (if any)"

# because we build our container as root:
chown -R root ~/.cache/
chmod 766 ~/.cache/

shopt -s nullglob
# For install.py, please refer to https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Developing-extensions#installpy
list=(./extensions/*/install.py)
for installscript in "${list[@]}"; do
  EXTNAME=$(echo $installscript | cut -d '/' -f 3)
  # Skip installing dependencies if extension is disabled in config
  if $(jq -e ".disabled_extensions|any(. == \"$EXTNAME\")" config.json); then
    echo "Skipping disabled extension ($EXTNAME)"
    continue
  fi
  PYTHONPATH=${ROOT} python "$installscript"
done

if [ -f "/data/config/auto/startup.sh" ]; then
  pushd ${ROOT}
  echo "Running startup script"
  . /data/config/auto/startup.sh
  popd
fi

mkdir ${ROOT}/models/Stable-diffusion && cd ${ROOT}/models/Stable-diffusion


MODELS=""
##JuggernautXL
wget --no-verbose --show-progress --progress=bar:force:noscroll "https://civitai.com/api/download/models/288982?type=Model&format=SafeTensor&size=full&fp=fp16" -O JuggernautXL_v8Rundiffusion.safetensors && MODELS+="JuggernautXL_v8Rundiffusion.safetensors,"
##EpiCPhotoGasm
wget --no-verbose --show-progress --progress=bar:force:noscroll "https://civitai.com/api/download/models/223670?type=Model&format=SafeTensor&size=full&fp=fp16" -O epiCPhotoGasm.safetensors && MODELS+="epiCPhotoGasm.safetensors,"
## 1.5
wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors && MODELS+="v1-5-pruned.safetensors,"
## 2.1
wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors && MODELS+="v2-1_768-ema-pruned.safetensors,"
## SDXL
wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors && MODELS+="sd_xl_base_1.0_0.9vae.safetensors,"
##SDXL Refiner
wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0_0.9vae.safetensors && MODELS+="sd_xl_refiner_1.0_0.9vae.safetensors,"
## OLD 1.5
# wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.ckpt
# ## OLD 2.1
# wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt
# ## OLD SDXL
# wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
# ## OLD SDXL Refiner
# wget --no-verbose --show-progress --progress=bar:force:noscroll https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
# ## OLD JuggerNautXL
# wget --no-verbose --show-progress --progress=bar:force:noscroll "https://civitai.com/api/download/models/288982?type=Model&format=SafeTensor&size=full&fp=fp16" -O juggernautXL_v8Rundiffusion.safetensors

cd ${ROOT}

rsync -avz --progress /docker/emprops_models_repo/ /stable-diffusion-webui/models/

cd ~/.pm2/logs && pm2 start --name error_catch_all "./error_catch_all.sh"

cd ${ROOT} && pm2 start --name webui "python -u webui.py --opt-sdp-no-mem-attention --api --port 3130 --medvram --no-half-vae"

eval "$(ssh-agent -s)"
ssh-add /root/.ssh/id_ed25519
rm -rf /etc/nginx
ssh-keyscan github.com > ~/.ssh/githubKey
ssh-keygen -lf ~/.ssh/githubKey
cat ~/.ssh/githubKey >> ~/.ssh/known_hosts
git clone -b sd-node git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx
service nginx start

# Comma separated string to array
IFS=, read -r -a models <<<"${MODELS}"

# Array to parameter list
echo "WAITING TO START UP BEFORE LOADING MODELS..."

sleep 75

# Array to parameter list
echo "Loading models: ${MODELS}"

for model in "${models[@]}"; do echo $model && python /docker/loader.py -m $model; done

echo "~~READY~~"