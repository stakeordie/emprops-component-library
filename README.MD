# server setup
## Run

Clone the repo, cd into the directory, and run the following command:

```bash
cd ~
git clone https://github.com/stakeordie/emprops_component_library.git
cd emprops_component_library/server_scripts
./basic.sh && source ~/.bashrc


eval "docker buildx build $(sed 's/^/--build-arg /' ../global/.env) --builder cloud-emprops-comfy-servers --platform linux/amd64 -t emprops/comfy-basic:v1 --output type=cacheonly --push ."

```
