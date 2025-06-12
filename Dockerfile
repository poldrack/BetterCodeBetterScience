# Dockefile for shell example

FROM ubuntu
RUN apt-get update && apt-get install -y wget curl
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh \
    && bash Miniconda3-latest-Linux-aarch64.sh -b -p /root/miniconda3 \
    && rm -f Miniconda3-latest-Linux-aarch64.sh \
    && echo PATH="/root/miniconda3/bin":$PATH >> /root/.bashrc
RUN curl -LsSf https://astral.sh/uv/install.sh | sh