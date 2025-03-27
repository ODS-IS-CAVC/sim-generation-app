#!/bin/bash
set -eu

# 環境変数からS3のURL、SOURCE_ID、JOB_IDを受け取る
# JOB_ID:BatchジョブのID
S3_URL=${S3_URL:-}
SOURCE_ID=${SOURCE_ID:-}
JOB_ID=${AWS_BATCH_JOB_ID:-}
APP_DIR=${APP_DIR:-/app}
CREATION_DATE_TIME=${CREATION_DATE_TIME:-}

export LD_LIBRARY_PATH=${APP_DIR}/camera_distance/tracking/dll
export PROJ_LIB=/usr/share/proj/
export AWS_ROLE_ARN=${AWS_ROLE_ARN:-"arn:aws:iam::AWS-ACCOUNT:role/manual-source-role"}
export ROLE_SESSION_NAME=${ROLE_SESSION_NAME:-AWS-ECSTask-role}
export S3_DESTINATION_NAME=${S3_DESTINATION_NAME:-AWS-rawdata-s3}
export DYNAMO_DB_NAME=${DYNAMO_DB_NAME:-AWS_JOB_STATUS_TBL}


# 環境変数が設定されていることを確認
if [ -z "$S3_URL" ]; then
    echo "環境変数 S3_URL が設定されていません。"
    exit 1
fi

if [ -z "$SOURCE_ID" ]; then
    echo "環境変数 SOURCE_ID が設定されていません。"
    exit 1
fi

if [ -z "$JOB_ID" ]; then
    echo "環境変数 JOB_ID が設定されていません。"
    exit 1
fi

if [[ -z "${SOURCE_ID}" || -z "${JOB_ID}" ]]; then
  echo "Error: SOURCE_ID and JOB_ID environment variables must be set"
  exit 1
fi

WORK_DIR="/mnt/efs/${SOURCE_ID}/${JOB_ID}"
# ローカル環境かどうかを判断
IS_LOCAL=${IS_LOCAL:-false}
STATUS_FILE="${WORK_DIR}/job_status_${SOURCE_ID}_${JOB_ID}.json"

# 実行時に使用するファイル、ディレクトリ
INPUT_DIR="${WORK_DIR}/input"
# コピー先ディレクトリを作成
mkdir -p "$INPUT_DIR"

MP4_FRONT=""
IMAGE_SRC=${WORK_DIR}/image_src
IMAGE_DISTORTION=${WORK_DIR}/image_distortion
IMAGE_SEGMENTATION=${WORK_DIR}/image_segmentation
IMAGE_INFER=${WORK_DIR}/image_infer
WORK_JOB_DIR=${WORK_DIR}/job
SIMULATION_DIR=${WORK_JOB_DIR}/scenario
SDMG_EDIT=${WORK_DIR}/sdmg

POS_EST_SETTING_FILE=${APP_DIR}/camera_distance/input/position_estimation_setting.json
LANE_EST_SETTING_FILE=${APP_DIR}/camera_distance/input/lane_estimation_setting.json
if ls ${INPUT_DIR}/position_estimation_setting.json > /dev/null 2>&1; then
    POS_EST_SETTING_FILE=$(ls ${INPUT_DIR}/position_estimation_setting.json)
fi
if ls ${INPUT_DIR}/lane_estimation_setting.json > /dev/null 2>&1; then
    LANE_EST_SETTING_FILE=$(ls ${INPUT_DIR}/lane_estimation_setting.json)
fi
INFER_REL_COORD_FILE=${IMAGE_INFER}/detection_distance_result.json
GPS_COORD_FILE=""
CAR_ABS_RESULT_FILE=${IMAGE_INFER}/car_abs_pos_result.json
BASE_SCENARIO_FILE=${APP_DIR}/scenario/data/base_scenario.xml
CAR_OBJECT_DATA_FILE=${APP_DIR}/scenario/data/car_object_data.xml
SETTING_JSON=${APP_DIR}/scenario/data/setting.json
SCENARIO_XML_FILE=${SDMG_EDIT}/scenario.xml

MAP_SELECT_FILE=""
XODR_ROAD_COORDINATE_FILE=""
EPSG_CODE=""
if ls ${INPUT_DIR}/*.json 2>/dev/null | grep MapSelectResult > /dev/null 2>&1; then
    MAP_SELECT_FILE=$(ls ${INPUT_DIR}/*.json | grep MapSelectResult)
    XODR_ROAD_COORDINATE_FILE=$(jq -r '.road_coordinates_path' "$MAP_SELECT_FILE")
    EPSG_CODE=$(jq -r '.epsg' "$MAP_SELECT_FILE")
fi
ROAD_CORRECT_TARGET_FILE=""
if ls ${INPUT_DIR}/*.json 2>/dev/null | grep self > /dev/null 2>&1; then
    ROAD_CORRECT_TARGET_FILE=$(ls ${INPUT_DIR}/*.json | grep self)
fi
G_SENSOR_DATA_FILE=""
if ls ${INPUT_DIR}/*.txt > /dev/null 2>&1; then
    G_SENSOR_DATA_FILE=$(ls ${INPUT_DIR}/*.txt)
fi
LANE_ID="-100"
if ls ${INPUT_DIR}/*.json 2>/dev/null | grep NearMiss > /dev/null 2>&1; then
    NEAR_MISS_INFO_FILE=$(ls ${INPUT_DIR}/*.json | grep NearMiss)
    LANE_ID=$(jq -r '.lane_id' "$NEAR_MISS_INFO_FILE")
else
    touch ${INPUT_DIR}/NearMiss_Info.json
    cat <<'EOF' >> ${INPUT_DIR}/NearMiss_Info.json
{
    "lane_id": "-100"
}
EOF
fi

# 外部スクリプトを読み込む
source job_status_utils.sh
source aws_s3_copy.sh

# 前回のステップを読み込む
load_last_step

# 初回実行時、last_stepが未定義または空であれば"NOT_STARTED"として扱う
if [ -z "$last_step" ] || [ "$last_step" == "NOT_STARTED" ]; then
    last_step="NOT_STARTED"
    if [ "$IS_LOCAL" = true ]; then
        last_step="MAP_SELECT"
    fi
fi

echo "前回のステップ: $last_step"

# S3_COPY: 検証環境のロールにスイッチし、ファイルカウントとチェックしダウンロード
if [ "$last_step" == "NOT_STARTED" ] || [ "$last_step" == "S3_COPY" ]; then
    aws_download

    # ステップを保存
    save_last_step "S3_COPY"
    echo "完了: $last_step"
fi

# S3_DL後
if ls ${INPUT_DIR}/*.mp4 2>/dev/null | grep Front > /dev/null 2>&1; then
    MP4_FRONT=$(ls ${INPUT_DIR}/*.mp4 | grep Front)
else
    MP4_FRONT=$(ls ${INPUT_DIR}/*.mp4)
fi
GPS_COORD_FILE=$(ls ${INPUT_DIR}/*.csv)

# MAP_SELECT: マップ選択
if [ "$last_step" == "S3_COPY" ] || [ "$last_step" == "MAP_SELECT" ]; then
    echo "GPS情報を基に、MAPを選択します。"

    # マップ選択処理
    python ${APP_DIR}/map_tools/map_select.py \
        --route_data_path ${GPS_COORD_FILE} \
        --map_data_path ${APP_DIR}/map_tools/map_data/ \
        --lane_id ${LANE_ID}

    # マップ選択情報ファイルが存在するかどうかを確認
    if ! ls ${INPUT_DIR}/*.json 2>/dev/null | grep MapSelectResult > /dev/null 2>&1; then
        echo "対象のマップが見つかりませんでした。: $GPS_COORD_FILE"
        echo "異常終了: $last_step"
        # 処理終了
        save_last_step "TERMINATE_PROCESS"
    else
        MAP_SELECT_FILE=$(ls ${INPUT_DIR}/*.json | grep MapSelectResult)
        XODR_ROAD_COORDINATE_FILE=$(jq -r '.road_coordinates_path' "$MAP_SELECT_FILE")
        EPSG_CODE=$(jq -r '.epsg' "$MAP_SELECT_FILE")
        ROAD_CORRECT_TARGET_FILE=$(ls ${INPUT_DIR}/*.json | grep self)
        # ステップを保存
        save_last_step "MAP_SELECT"
        echo "完了: $last_step"
    fi
fi

# VIDEO_TO_IMAGE: 動画から画像を抽出
if [ "$last_step" == "MAP_SELECT" ] || [ "$last_step" == "VIDEO_TO_IMAGE" ]; then
    echo "動画から画像を抽出"

    python ${APP_DIR}/camera_distance/tools/video2image.py \
        --input_path ${MP4_FRONT} \
        --output_path ${IMAGE_SRC} \
        --frame_skip 1

    # ステップを保存
    save_last_step "VIDEO_TO_IMAGE"
    echo "完了: $last_step"
fi

# DISTORTION: 画像補正
if [ "$last_step" == "VIDEO_TO_IMAGE" ] || [ "$last_step" == "DISTORTION" ]; then
    echo "画像補正"

    python ${APP_DIR}/camera_distance/tools/distortion_correction/distortion_correction.py \
        --input_dir ${IMAGE_SRC} \
        --output_dir ${IMAGE_DISTORTION} \
        --intrinsic_camera_matrix_path ${APP_DIR}/camera_distance/tools/distortion_correction/intrinsic_camera_matrix.npy \
        --calibration_matrix_P2_path ${APP_DIR}/camera_distance/tools/distortion_correction/calibration_matrix_P2.npy \
        --dist_coeffs_path ${APP_DIR}/camera_distance/tools/distortion_correction/dist_coeffs.npy

    # ステップを保存
    save_last_step "DISTORTION"
    echo "完了: $last_step"
fi

# INFER_DISTANCE: 他車両相対距離推定
if [ "$last_step" == "DISTORTION" ] || [ "$last_step" == "INFER_DISTANCE" ]; then
    echo "他車両の相対距離を推定"

    python ${APP_DIR}/camera_distance/infer_distance_to_car.py \
        --input_dir ${IMAGE_DISTORTION} \
        --output_dir ${IMAGE_INFER} \
        --pos_est_setting_file ${POS_EST_SETTING_FILE}

    # ステップを保存
    save_last_step "INFER_DISTANCE"
    echo "完了: $last_step"
fi

# DETECT_CSV: 測距結果CSV出力
if [ "$last_step" == "INFER_DISTANCE" ] || [ "$last_step" == "DETECT_CSV" ]; then
    echo "測距した結果を検出した車両ごとにCSV出力"

    python ${APP_DIR}/tool/detect2csv.py \
        --rel_coord_file ${INFER_REL_COORD_FILE}

    # ステップを保存
    save_last_step "DETECT_CSV"
    echo "完了: $last_step"
fi

# ABS_POS_SELF: 絶対座標算出（自車）
if [ "$last_step" == "INFER_DISTANCE" ] || [ "$last_step" == "DETECT_CSV" ] || [ "$last_step" == "ABS_POS_SELF" ]; then
    echo "自車両の軌跡データを生成"

    # 処理
    if [ -z "$G_SENSOR_DATA_FILE" ]; then
        python ${APP_DIR}/camera_distance/calc_car_abs_pos_self.py \
            --rel_coord_file ${INFER_REL_COORD_FILE} \
            --gps_coord_file ${GPS_COORD_FILE} \
            --epsg_code ${EPSG_CODE} \
            --fps 30
    else
        # 仮：acc_data_fileはcsvデータの必要があるため、txtデータだとエラー。
        python ${APP_DIR}/camera_distance/calc_car_abs_pos_self.py \
            --rel_coord_file ${INFER_REL_COORD_FILE} \
            --gps_coord_file ${GPS_COORD_FILE} \
            --acc_data_file "" \
            --epsg_code ${EPSG_CODE} \
            --fps 30
    fi

    # ステップを保存
    save_last_step "ABS_POS_SELF"
    echo "完了: $last_step"
fi

# CORRECT_CAR: レーン座標補正
if [ "$last_step" == "ABS_POS_SELF" ] || [ "$last_step" == "CORRECT_CAR" ]; then
    echo "レーン情報を元に自車の絶対座標を補正"

    # 処理
    python ${APP_DIR}/camera_distance/correct_car_abs_pos_self.py \
        --lane_coord_file_path ${XODR_ROAD_COORDINATE_FILE} \
        --car_abs_coord_file_path ${CAR_ABS_RESULT_FILE} \
        --road_correct_targets_file_path ${ROAD_CORRECT_TARGET_FILE} \
        # --no_overwrite

    # ステップを保存
    save_last_step "CORRECT_CAR"
    echo "完了: $last_step"
fi

# ABS_POS_DETECT: 絶対座標算出（他車）
if [ "$last_step" == "CORRECT_CAR" ] || [ "$last_step" == "ABS_POS_DETECT" ]; then
    echo "他車両の軌跡データを生成"
    
    # 処理
    python ${APP_DIR}/camera_distance/calc_car_abs_pos_detect.py \
        --car_abs_coord_file_path ${CAR_ABS_RESULT_FILE} \
        --epsg_code ${EPSG_CODE} \
        --fps 30

    # ステップを保存
    save_last_step "ABS_POS_DETECT"
    echo "完了: $last_step"
fi

# CORRECT_CAR: レーン座標補正
if [ "$last_step" == "ABS_POS_DETECT" ] || [ "$last_step" == "CORRECT_CAR_DETECT" ]; then
    echo "レーン情報を元に他車の絶対座標を補正"

    # 処理
    python ${APP_DIR}/camera_distance/correct_car_abs_pos_detect.py \
        --lane_coord_file_path ${XODR_ROAD_COORDINATE_FILE} \
        --car_abs_coord_file_path ${CAR_ABS_RESULT_FILE} \
        --target_option "beforeIn" \
        # --no_overwrite

    # ステップを保存
    save_last_step "CORRECT_CAR_DETECT"
    echo "完了: $last_step"
fi

# SMOOTH_ABS_POS: 速度平均化
if [ "$last_step" == "CORRECT_CAR_DETECT" ] || [ "$last_step" == "SMOOTH_ABS_POS" ]; then
    echo "他車の速度を平均化"

    # 処理
    python ${APP_DIR}/camera_distance/smooth_abs_pos_detect.py \
        --car_abs_coord_file_path ${CAR_ABS_RESULT_FILE} \
        --repeat 3 

    # ステップを保存
    save_last_step "SMOOTH_ABS_POS"
    echo "完了: $last_step"
fi

# CALC_VEL_YAW: 速度角度計算
if [ "$last_step" == "SMOOTH_ABS_POS" ] || [ "$last_step" == "CALC_VEL_YAW" ]; then
    echo "補正した座標での速度角度の再計算"

    # 処理
    python ${APP_DIR}/camera_distance/calc_car_velocity_yaw.py \
        --car_abs_coord_file_path ${CAR_ABS_RESULT_FILE} \
        --fps 30

    # ステップを保存
    save_last_step "CALC_VEL_YAW"
    echo "完了: $last_step"
fi

# MAKE_CAR_ROUTE: 車の経路csv作成
if [ "$last_step" == "CALC_VEL_YAW" ] || [ "$last_step" == "MAKE_CAR_ROUTE" ]; then
    echo "自車・他車の走行経路csvファイルを作成"

    # 処理
    python ${APP_DIR}/tool/make_car_route_csv.py \
        --xodr_road_json ${XODR_ROAD_COORDINATE_FILE} \
        --abs_coord_file ${CAR_ABS_RESULT_FILE}

    # ステップを保存
    save_last_step "MAKE_CAR_ROUTE"
    echo "完了: $last_step"
fi

# GENERATE_SCENARIO: シナリオ生成
if [ "$last_step" == "MAKE_CAR_ROUTE" ] || [ "$last_step" == "GENERATE_SCENARIO" ]; then
    echo "シナリオ生成"

    # 処理
    echo "シナリオINIT"
    python ${APP_DIR}/scenario/scenario_xml_initialize.py \
        --abs_coord_file ${CAR_ABS_RESULT_FILE} \
        --base_scenario_xml ${BASE_SCENARIO_FILE} \
        --car_data_xml ${CAR_OBJECT_DATA_FILE} \
        --output_dir ${SDMG_EDIT}
    
    echo "マップ設定"
    python ${APP_DIR}/scenario/set_map_to_scenario.py \
        --scenario_xml_file ${SCENARIO_XML_FILE} \
        --xosc_config_json ${SDMG_EDIT}/xosc_config.json \
        --map_info_file ${MAP_SELECT_FILE}

    echo "経路をdivp経路に変換"
    python ${APP_DIR}/scenario/route2divp_route.py \
        --car_routes_dir ${IMAGE_INFER} \
        --output_dir ${SIMULATION_DIR}

    echo "generate divp scenario"
    python ${APP_DIR}/scenario/divp_scenario.py \
        --scenario_xml_file ${SCENARIO_XML_FILE} \
        --xosc_config_json ${SDMG_EDIT}/xosc_config.json \
        --car_routes_dir ${SIMULATION_DIR} \
        --output_dir ${SIMULATION_DIR}

    # ROS実行用のsetting.json作成
    echo "generate setting json"
    DIVP_ROUTE_CSV_FILE=$(ls ${SIMULATION_DIR}/*.csv 2> /dev/null | head -n 1)
    python ${APP_DIR}/scenario/generate_ros_setting_json.py \
        --divp_route_csv_file ${DIVP_ROUTE_CSV_FILE} \
        --base_setting_json ${SETTING_JSON} \
        --output_path ${WORK_JOB_DIR} \
        --camera_fps 3

    # ステップを保存
    save_last_step "GENERATE_SCENARIO"
    echo "完了: $last_step"
fi
