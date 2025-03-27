# ベースイメージ (Ubuntu 最新版)
FROM ubuntu:latest

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    && apt-get clean

# 作業ディレクトリを設定
WORKDIR /usr/src

# libOpenDRIVE をクローンしてビルド
RUN git clone https://github.com/pageldev/libOpenDRIVE.git && \
    cd libOpenDRIVE && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# C++ コードをコンパイル
COPY convert_xodr_to_obj.cpp .
RUN g++ -std=c++17 convert_xodr_to_obj.cpp -o convert_xodr_to_obj \
    -I/usr/local/include \
    /usr/local/lib/libOpenDrive.a

# 実行用エントリーポイント
ENTRYPOINT ["/usr/src/convert_xodr_to_obj"]

