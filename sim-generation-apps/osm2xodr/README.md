# OSM to XODR Converter

このリポジトリは、OpenStreetMap(OSM)データをOpenDRIVE(XODR)フォーマットに変換するためのDocker環境を提供します。

## ファイル構成

```
.
├── Dockerfile
├── osm2xodr.py
├── requirements.txt
├── README.md  # このファイル
```

## 環境構築と実行手順

### 1. Docker イメージのビルド
```sh
docker build -t osm2xodr .
```

## 2. コンテナを実行
```bash
docker run --rm -v $(pwd)/data:/data osm2xodr python3 osm_to_xodr.py -i /data/input.osm -o /data/output.xodr --lane-width 3.7 --epsg-code 6677 --center-map
```
- input.osm から output.xodr を生成し、マウントした data/ ディレクトリに output.xodr を保存。
```
options:
  --input-path  入力ファイルパス（OpenStreetMap/XML形式）
  --output-path 出力ファイルパス（XODR）
  --lane-width  車線の幅
  --center-map  マップ中心を設定する
  --epsg-code   投影先のEPSGコード（default:6677）
```


## 必要な依存パッケージ

このプロジェクトでは以下の Python ライブラリが必要です。
- carla
- pyproj

これらは `requirements.txt` に記載されており、Dockerfile 内で自動的にインストールされます。


