#FROM nvidia/cuda:11.4.3-devel-ubuntu20.04
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# https://qiita.com/mochi_yu2/items/af80a3adc7ff70e58807
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 必要なパッケージをインストール
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get install -y g++-11 \
    && apt-get -y install --no-install-recommends \
    curl \
    wget \
    zip \
    unzip \
    software-properties-common \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libdb5.3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    uuid-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    gpg \
    netcat \
    iputils-ping \
    net-tools \
    jq \
    && rm -rf /var/lib/apt/lists/*

# AWS CLI のインストール
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -r awscliv2.zip aws

# ------------------------------------------------------------
# Python 3.11.3
# ------------------------------------------------------------
ARG PYTHON="3.11.3"
# ダウンロード
RUN wget -q "https://www.python.org/ftp/python/${PYTHON}/Python-${PYTHON}.tar.xz" \
    && tar xvf Python-${PYTHON}.tar.xz
# ビルドしてインストール
WORKDIR /Python-${PYTHON}
RUN ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall
# ビルドに使用したファイルを削除
WORKDIR /
RUN rm -rf /Python-${PYTHON} Python-${PYTHON}.tar.xz

RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1 \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# 作業ディレクトリを作成
WORKDIR /app

# Python のパッケージをインストール
COPY requirements.txt /app/requirements.txt

# CPU バージョンの PyTorch をインストール
# RUN pip install --no-cache-dir torch==2.1.1+cpu torchvision==0.16.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir -r /app/requirements.txt

# Pythonスクリプトをコンテナにコピー
COPY app /app/

# 実行権限付与
RUN chmod +x /app/entrypoint.sh

# 実行時のエントリーポイントを設定
ENTRYPOINT ["/app/entrypoint.sh"]
