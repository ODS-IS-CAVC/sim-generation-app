# シナリオ生成アプリ
## 1.アプリの概要

本アプリは、NEDO（New Energy and Industrial Technology Development Organization）の公募案件にて、実証実験に向けて作成したものです。 
また、ドライブレコーダー映像、Gセンサ、GPS情報をもとにシナリオを生成するためのアプリケーションです。

## 2.動作要件
 このアプリケーションは、Dockerコンテナ内で実行されることを前提としています。
 以下の環境で動作確認をしています。
 
 - Docker version 27.3.1, build ce12230


## 3.アプリケーションの簡易説明

- [**シナリオ生成アプリ**](./app/) を参照ください。
- [**OSMtoXODR**](./osm2xodr/) を参照ください。
- [**XODRtoOBJ**](./xodr2obj/) を参照ください。

## 4. 免責事項

本ソフトウェアは「現状のまま」提供され、明示または黙示を問わず、商品性、特定目的への適合性、および権利非侵害を含む、いかなる保証も行いません。  
作者または著作権者は、本ソフトウェアの使用によって生じるいかなる損害についても、契約上の行為、過失またはその他の不法行為にかかわらず責任を負いません。  

## 5.ライセンス

[**3.アプリケーション構成**](./#3.アプリケーション構成)に記載のシナリオ生成アプリ、OSMtoXODR、XODRtoOBJのリポジトリのソースコードに、GNU Affero General Public License v3 or later (AGPLv3+)のライセンスを付与します。
詳細は [**LICENSE**](./LICENSE) を参照してください。  

app/camera_distance/yolo/配下のプログラムは以下のリポジトリのものを改変して利用しています。
- [**https://github.com/WongKinYiu/yolov7**](https://github.com/WongKinYiu/yolov7)

認識モデルは以下のリポジトリのものを使用しています。
- [**https://github.com/ultralytics/ultralytics**](https://github.com/ultralytics/ultralytics)

