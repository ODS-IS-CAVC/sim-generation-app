#!/bin/bash

ENV_CONTAINER=scenario-generator
ENV_TAG=latest

S3_URL=s3://aws-s3-bucket-url/uuid/
export SOURCE_ID=${SOURCE_ID:-SOURCE_ID}
export AWS_BATCH_JOB_ID=${AWS_BATCH_JOB_ID:-JOB_ID}
export CREATION_DATE_TIME=2024-12-03T10:00:0.0+09:00

ENV_IS_LOCAL=true
MNT_SRC=/mnt/efs
MNT_TRG=/mnt/efs

USER_CONFIG_FILE="./user_config.sh"
if [ -f "$USER_CONFIG_FILE" ]; then
    echo "Loading user configuration from $USER_CONFIG_FILE"
    source "$USER_CONFIG_FILE"
else
    echo "No user configuratio found. Using default settings."
fi

docker run -it \
    -e S3_URL=${S3_URL} \
    -e SOURCE_ID=${SOURCE_ID} \
    -e AWS_BATCH_JOB_ID=${AWS_BATCH_JOB_ID} \
    -e IS_LOCAL=${ENV_IS_LOCAL} \
    -e CREATION_DATE_TIME=${CREATION_DATE_TIME} \
    -v ${MNT_SRC}:${MNT_TRG} \
    ${ENV_CONTAINER}:${ENV_TAG}
