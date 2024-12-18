FROM pytorch/pytorch:latest

# ARG DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1

RUN apt update && apt-get install -y git rsync nginx wget nano ffmpeg libsm6 libxext6 cron sudo && apt-get clean

ARG GITACCESSKEY

RUN useradd -m -d /home/ubuntu -s /bin/bash ubuntu
RUN usermod -aG sudo ubuntu
RUN mkdir -p /home/ubuntu/.ssh && touch /home/ubuntu/.ssh/authorized_keys
RUN echo ${GITACCESSKEY} >> /home/ubuntu/.ssh/authorized_keys
RUN chown -R ubuntu:ubuntu /home/ubuntu/.ssh
RUN touch /etc/ssh/sshd_config.d/ubuntu.conf && echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config.d/ubuntu.conf && echo "PasswordAuthentication no" >> /etc/ssh/sshd_config.d/ubuntu.conf
RUN service ssh restart
RUN sudo cp /etc/sudoers /etc/sudoers.bak
RUN echo 'ubuntu ALL=(ALL:ALL) NOPASSWD: ALL' >> /etc/sudoers

RUN su - ubuntu

RUN mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo ${GITACCESSKEY} >> ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519

ENV ROOT=/comfyui-launcher

# COPY ./models.sh /scripts/models.sh
# RUN /scripts/models.sh

COPY ./nodes.sh /scripts/nodes.sh
RUN /scripts/nodes.sh

RUN eval "$(ssh-agent -s)" && ssh-add /root/.ssh/id_ed25519 && ssh-keyscan github.com > ~/.ssh/githubKey && ssh-keygen -lf ~/.ssh/githubKey && cat ~/.ssh/githubKey >> ~/.ssh/known_hosts

WORKDIR ${ROOT}

COPY ./build.sh /scripts/build.sh

RUN /scripts/build.sh

COPY ./models.sh /scripts/models.sh

COPY ./start.sh /scripts/start.sh

COPY ./cron.sh /scripts/cron.sh

CMD  ["/scripts/start.sh"]