#!/bin/bash

# 環境変数設定
export S3_URL=s3://aws-s3-bucket/sample/scenario
export SOURCE_ID=fukuyama
export AWS_BATCH_JOB_ID=${AWS_BATCH_JOB_ID:-scene01}
export IS_LOCAL=true
export APP_DIR=/workspace/try_bravs/app
export CREATION_DATE_TIME=${CREATION_DATE_TIME:-2024-12-03T10:00:0.0+09:00}
export DYNAMO_DB_NAME=${DYNAMO_DB_NAME:-DYNAMO_DB_JOB_STATUS_TBL}
START_STEP="MAP_SELECT"

USER_CONFIG_FILE="./user_config.sh"
if [ -f "$USER_CONFIG_FILE" ]; then
    echo "Loading user configuration from $USER_CONFIG_FILE"
    source "$USER_CONFIG_FILE"
else
    echo "No user configuratio found. Using default settings."
fi

JOB_ID=${AWS_BATCH_JOB_ID}

WORK_DIR="/mnt/efs/${SOURCE_ID}/${JOB_ID}"
STATUS_FILE="${WORK_DIR}/job_status_${SOURCE_ID}_${JOB_ID}.json"

cd app

# 外部スクリプトを読み込む
source job_status_utils.sh


# 前回のステップを読み込む
load_last_step

# 初回実行時、last_stepが未定義または空
if [ -z "$last_step" ] || [ "$last_step" == "NOT_STARTED" ]; then
    # last_step="NOT_STARTED"
    save_last_step "MAP_SELECT"
fi
# if [ "$last_step" == "EXEC_DIVP" ] || [ "$last_step" == "TERMINATE_PROCESS" ]; then
#     save_last_step "TERMINATE_PROCESS"
# fi

# 開始したいステップから実行
save_last_step $START_STEP

./entrypoint.sh

