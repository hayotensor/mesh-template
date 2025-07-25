FROM nvcr.io/nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
LABEL maintainer="Hypertensor@home"
LABEL repository="mesh"

WORKDIR /home
# Set en_US.UTF-8 locale by default
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends --force-yes \
  build-essential \
  curl \
  wget \
  git \
  vim \
  && apt-get clean autoclean && rm -rf /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O install_miniconda.sh && \
  bash install_miniconda.sh -b -p /opt/conda && rm install_miniconda.sh
ENV PATH="/opt/conda/bin:${PATH}"

RUN conda install python~=3.11.0 pip && \
    pip install --no-cache-dir torch torchvision torchaudio && \
    conda clean --all

COPY requirements.txt mesh/requirements.txt
COPY requirements-dev.txt mesh/requirements-dev.txt
RUN pip install --no-cache-dir -r mesh/requirements.txt && \
    pip install --no-cache-dir -r mesh/requirements-dev.txt && \
    rm -rf ~/.cache/pip

COPY . mesh/
RUN cd mesh && \
    pip install --no-cache-dir .[dev] && \
    conda clean --all && rm -rf ~/.cache/pip

CMD bash
