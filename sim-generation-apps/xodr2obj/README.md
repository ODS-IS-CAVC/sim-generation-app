# XODR to OBJ Converter
このリポジトリは、OpenDRIVE (XODR) の道路ネットワークファイルを 3D モデル（OBJ 形式）に変換するツールを提供します。

## 特徴
- OpenDRIVE (XODR) ファイルの解析
- 3D の道路ネットワークメッシュを生成
- OBJ 形式でモデルを出力
- Docker コンテナ内で実行可能

## 必要な環境
- Docker（ビルド・実行用）
- 入力ファイルとしての OpenDRIVE (.xodr) ファイル

## Docker イメージのビルド

以下のコマンドを実行して、Docker イメージをビルドします。

```sh
docker build -t xodr2obj .
```

## 使い方

XODR ファイルを OBJ ファイルに変換するには、入力ファイルを含むディレクトリをマウントし、以下のコマンドを実行します。

```sh
docker run --rm -v $(pwd)/data:/data xodr2obj /data/input.xodr /data/output.obj
```

### 使用例
`data` フォルダ内に `test.xodr` という OpenDRIVE ファイルがある場合、次のコマンドを実行します。

```sh
docker run --rm -v $(pwd)/data:/data xodr2obj /data/test.xodr /data/output.obj
```

変換後の `output.obj` ファイルは `data` ディレクトリ内に保存されます。

## デバッグ方法
ファイルのマウントや解析エラーが発生した場合、コンテナを対話的に実行して確認できます。

```sh
docker run --rm -it -v $(pwd)/data:/data xodr2obj bash
```

その後、コンテナ内でファイルが正しく存在するか確認してください。

```sh
ls -l /data
```
