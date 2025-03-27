FROM ubuntu:22.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-venv \
    libproj-dev proj-bin \
    && rm -rf /var/lib/apt/lists/*

# projの環境変数をセット
ENV PROJ_LIB=/usr/share/proj/

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonパッケージをインストール
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# スクリプトをコピー
COPY osm_to_xodr.py ./

# コンテナ起動時にスクリプトを実行
CMD ["python3", "osm_to_xodr.py"]
