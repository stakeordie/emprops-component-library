FROM pytorch/pytorch:latest

# ARG DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1

RUN apt update && apt-get install -y git rsync nginx wget nano ffmpeg libsm6 libxext6 && apt-get clean

ARG GITACCESSKEY

RUN mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo ${GITACCESSKEY} >> ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519

ENV ROOT=/comfyui-launcher

# COPY ./models.sh /scripts/models.sh
# RUN /scripts/models.sh

COPY ./nodes.sh /scripts/nodes.sh
RUN /scripts/nodes.sh

RUN eval "$(ssh-agent -s)" && ssh-add /root/.ssh/id_ed25519 && ssh-keyscan github.com > ~/.ssh/githubKey && ssh-keygen -lf ~/.ssh/githubKey && cat ~/.ssh/githubKey >> ~/.ssh/known_hosts
RUN rm -rf /etc/nginx && git clone git@github.com:stakeordie/emprops-nginx-conf.git /etc/nginx-repo && ln -s nginx-repo/node nginx
RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${ROOT}/ComfyUI
RUN pip install -r ${ROOT}/ComfyUI/requirements.txt
RUN git clone https://github.com/stakeordie/comfy-middleware.git ${ROOT}/comfy-middleware

WORKDIR ${ROOT}

COPY ./build.sh /scripts/build.sh

RUN /scripts/build.sh

COPY ./models.sh /scripts/models.sh

COPY ./start.sh /scripts/start.sh

ENTRYPOINT /scripts/start.sh