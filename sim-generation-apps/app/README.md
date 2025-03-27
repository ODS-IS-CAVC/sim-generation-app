# シナリオ生成用コンテナ
## ファイル構成
| ファイル、フォルダ名 | 概要|
| --- | ---|
| app/camera_distance | 測距アルゴリズム |
| app/map_tools | 地図選択関連コード |
| app/scenario | シナリオ生成用コード|
| app/tool | ツール類|
| app/xodr_tool | OpenDRIVE関連 |
| app/entrypoint.sh | シナリオ生成実行スクリプト |
| Dockerfile | シナリオ生成用コンテナDockerfile |
| requirements.txt | python 依存関係 |
| readme.md | このファイル |

## コンテナのビルド
```
docker build -t scenario-generator:latest .
```

## 環境変数

| 環境変数 |	概要|
| --- | --- |
|S3_URL | S3コピー先 |
|SOURCE_ID | 取得元のID（UUIDが入る）|
|JOB_ID | バッチジョブのID|
|CREATION_DATE_TIME | バッチジョブ起動時の時間|
|AWS_ROLE_ARN	AWS | 他のアカウントからデータを取得するロール|
|ROLE_SESSION_NAME | Role セッション名|
|S3_DESTINATION_NAME | S3出力先を指定|
|DYNAMO_DB_NAME | 処理ステータス管理|
|IS_LOCAL | AWS接続する(TRUE)/しない(FALSE)|


# Python スクリプト一覧
## download_osm.py GPS情報を元にOpenStreetMap（OSM）ファイルをダウンロードする。
```bash
python app/tool/download_osm.py
```
```bash
usage: download_osm.py [-h] --input_path INPUT_PATH --output_path OUTPUT_PATH --col-lat LATITUDE --col-lon LONGITUDE -m

GPS情報を元にOpenStreetMap（OSM）ファイルをダウンロードする機能

options:
  --input_path  INPUT_PATH    Gセンサ、GPSファイルパス（タイプ：string）
  --output_path OSM_FILE_PATH OSMファイルパス
  --col-lat     LATITUDE      Latitudeのヘッダー名
  --col-lon     LONGITUDE     Longitudeのヘッダー名
  -m                          高速道路を指定
```

## video2image.py 動画から画像を抽出
```bash
python app/camera_distance/tools/video2image.py --input_path ./input.mp4 --output_path ./output
```

```bash
usage: video2image.py [-h] --input_path INPUT_PATH --output_path OUTPUT_PATH [--frame_skip FRAME_SKIP] [--start_time START_TIME] [--end_time END_TIME] [--gps_coord_file GPS_COORD_FILE]

動画からの画像切り出し機能

options:
  -h, --help            show this help message and exit
  --input_path INPUT_PATH
                        動画ファイルパス（タイプ：string）
  --output_path OUTPUT_PATH
                        出力フォルダパス（タイプ：string）
  --frame_skip FRAME_SKIP
                        frame-skipは任意（タイプ：int; default=0）
  --start_time START_TIME
                        動画からの画像抽出開始時間（タイプ：float; default=0.0）
  --end_time END_TIME   動画からの画像抽出終了時間（タイプ：float; default=-1）
  --gps_coord_file GPS_COORD_FILE
                        GPSデータファイルパス

```


## calc_camera_elevation_angle.py カメラの仰角を計算する
```bash
python app/camera_distance/tools/calc_camera_elevation_angle.py
```

```bash
usage: calc_camera_elevation_angle.py [-h] --input_image_path INPUT_IMAGE_PATH [--theta THETA] [--proj_mode PROJ_MODE]

カメラの仰角を計算する

options:
  -h, --help            show this help message and exit
  --input_image_path INPUT_IMAGE_PATH
                        入力画像ファイルパス
  --theta THETA         水平視野角θの値（degrees）
  --proj_mode PROJ_MODE
                        射影方式（0: 中心射影方式、1: 等距離射影方式）
```


## infer_distance_to_car.py 対象の相対座標を計算する
```bash
python app/camera_distance/infer_distance_to_car.py
```

```bash
usage: infer_distance_to_car.py [-h] --input_dir INPUT_DIR --output_dir OUTPUT_DIR [--pos_est_setting_file POS_EST_SETTING_FILE]

対象の相対座標を計算する

options:
  -h, --help            show this help message and exit
  --input_dir INPUT_DIR
                        入力画像フォルダパス
  --output_dir OUTPUT_DIR
                        出力結果フォルダパス
  --pos_est_setting_file POS_EST_SETTING_FILE
                        距離推定の設定ファイル
```

* 距離推定の設定ファイル  
  `(input/position_estimation_setting.json)`  
  |No.|キー|説明|例|
  |:-|:-|:-|:-|
  |1|theta|水平視野角θの値(degrees)|120|
  |2|proj_mode|射影方式 (0: 中心射影方式、1: 等距離射影方式)|0|
  |3|camera_elevation_angle|カメラの仰角(degrees)|30.4001872036101|
  |4|max_distance|フレーム間で同一オブジェクトと見なす距離(ピクセル距離)|200|
  |5|max_dissappear_frame_num|検知が途切れた場合に保持し続けるフレーム数。<br>一時的に検知が途切れても、このフレーム数以内に復活する場合はトラッキングが途切れない。（同一IDが振られる）|20|

## calc_detect_car_abs_pos.pyを実行して、自車の絶対座標から検出車の絶対座標計算する
```bash
python app/camera_distance/calc_detect_car_abs_pos.py
```

```bash
usage: calc_detect_car_abs_pos.py [-h] --rel_coord_file REL_COORD_FILE --gps_coord_file GPS_COORD_FILE [--acc_data_file ACC_DATA_FILE]
                                  [--epsg_code EPSG_CODE] [--fps FPS]

対象の相対座標の計算

options:
  -h, --help            show this help message and exit
  --rel_coord_file REL_COORD_FILE
                        相対距離推定結果jsonファイルパス
  --gps_coord_file GPS_COORD_FILE
                        GPSデータファイルパス
  --acc_data_file ACC_DATA_FILE
                        加速度データcsvファイルパス
  --epsg_code EPSG_CODE
                        EPSGコード（6669~6687）
  --fps FPS             FPS
```


## visualize_absolute_coord.py 推定値の可視化する
```bash
python app/camera_distance/tools/visualize_absolute_coord.py
```

```bash
usage: visualize_absolute_coord.py [-h] --output_path OUTPUT_PATH --abs_coord_file ABS_COORD_FILE [--mperp MPERP]

推定によって計算した、自車の座標と検出車の座標を簡単に可視化する

options:
  -h, --help            show this help message and exit
  --output_path OUTPUT_PATH
                        出力フォルダパス（タイプ：string）
  --abs_coord_file ABS_COORD_FILE
                        自車と検出車の絶対座標のjsonファイルパス（タイプ：string）
  --mperp MPERP         1ピクセルあたりの距離（meter）（タイプ：float）
```


## summary_video_result.py 相対座標の推定結果をエクセルとしてまとめる
```bash
python app/camera_distance/summary_video_result.py
```

```bash
usage: summary_video_result.py [-h] --rel_coord_file REL_COORD_FILE --output_dir OUTPUT_DIR

相対座標の推定結果をエクセルとしてまとめる

options:
  -h, --help            show this help message and exit
  --rel_coord_file REL_COORD_FILE
                        自車の相対座標と検出車の相対座標のjsonファイルパス（infer_distance_to_car.pyの出力json）
  --output_dir OUTPUT_DIR
                        出力エクセルのフォルダーパス
```


## coordinate_converter.py 元の座標系から基準座標系に座標を変換し、制限された軽度・緯度の範囲に絞り込む
```bash
python app/camera_distance/tools/coordinate_converter.py
```

```bash
usage: tools/coordinate_converter.py [-h] --input_path INPUT_FILE [--output_path OUTPUT_FILE]

"元の座標系から基準座標系に座標を変換し、制限された軽度・緯度の範囲に絞り込む"

options:
  -h, --help            show this help message and exit
  --input_path INPUT_LANE_FILE
                        レーン座標情報のjsonファイルパス             
  --output_path OUTPUT_FILE
                        結果のjsonファイルパス
```

## correct_car_abs_pos.py レーン情報を元に車の絶対座標を補正する
```bash
python app/camera_distance/correct_car_abs_pos.py
```

```bash
usage: correct_car_abs_pos.py [-h] --lane_coord_file_path LANE_COORD_FILE_PATH --gps_data_file_path GPS_DATA_FILE_PATH --detection_abs_coord_file_path DETECTION_ABS_COORD_FILE_PATH
                              [--road_correct_targets_file_path ROAD_CORRECT_TARGETS_FILE_PATH] --output_path OUTPUT_PATH

レーンのGPS座標から車の位置を求める, GPS座標と最も近いレーン上の点を補正後の車両座標とする

options:
  -h, --help            show this help message and exit
  --lane_coord_file_path LANE_COORD_FILE_PATH
                        レーン座標のjsonファイルパス （タイプ：string）
  --gps_data_file_path GPS_DATA_FILE_PATH
                        車両座標のcsvファイルパス（タイプ：string）
  --detection_abs_coord_file_path DETECTION_ABS_COORD_FILE_PATH
                        車両座標のjsonファイルパス（タイプ：string）
  --road_correct_targets_file_path ROAD_CORRECT_TARGETS_FILE_PATH
                        補正先道路のjsonファイルパス（タイプ：string）
  --output_path OUTPUT_PATH
                        結果フォルダパス （タイプ：string）
```


# xosc_generator.py
車両走行軌跡が記録されているCSVファイルからOpenSCENARIOファイルを生成するスクリプトです。  

## 使い方

```sh
python3 app/scenario/xosc_generator.py --config ./config.json --output ./generated.xosc
```

### --config まはた -c

JSONファイルのパスを指定します。  
ここで指定したJSONファイルから、OpenSCENARIOに登場する車両情報とロードネットワーク設定を読み取ります。  
フォーマットは以下のとおり。  


```json
{
  // 車両情報
  "actors": [
    {
      "csv_file": "divp_Veh_NissanRoox_1.csv", // 車両走行軌跡が記録されているCSVファイルのパス
      "name": "divp_Veh_NissanRoox_1",
      "vehicleCategory": "car",
      "model3d": "asset\\divp_Veh_NissanRoox.fbx",
      "boundingBox": {
        "center": {
          "x": 1.312,
          "y": 0.0,
          "z": 0.728
        },
        "dimensions": {
          "width": 1.8,
          "length": 4.91,
          "height": 1.455
        }
      }
    },
    {
      "csv_file": "divp_Veh_ToyotaCrown_1.csv",
      "name": "divp_Veh_ToyotaCrown_1",
      "vehicleCategory": "car",
      "model3d": "asset\\divp_Veh_ToyotaCrown.fbx"
    }
  ],

  // ロードネットワーク設定
  "roadNetwork": {
    "logicFile": "asset\\E1A_SurugawanNumazuSA_F0.xodr",
    "sceneGraphFile": "asset\\E1A_SurugawanNumazuSA.fbx"
  }
}
```

`boundingBox`が設定されていない場合は、デフォルトで以下の値が設定されます。
```python
{
  'center_x': 1.5,
  'center_y': 0.0,
  'center_z': 0.9,
  'width': 2.0,
  'length': 5.0,
  'height': 1.8
}
```


### --output まはた -o
生成するOpenSCENARIOファイルの出力先のパスを指定します。


### 車両走行軌跡が記録されているCSVファイル
--config で指定したJSONファイルの csv_file でCSVファイルのパスを指定します。  
CSVファイルの形式は以下のとおりです。  

```txt
timestamp,pos_x,pos_y,pos_z,yaw_rad,pitch_rad,roll_rad,vel_x,vel_y,vel_z
0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
5.0,50.0,0.0,0.0,0.0,0.0,0.0,10.0,0.0,0.0
```

