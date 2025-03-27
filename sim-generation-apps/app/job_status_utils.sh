#!/bin/bash
if [ -z "$DYNAMO_DB_NAME" ]; then
    echo "環境変数 DYNAMO_DB_NAME が設定されていません。"
    exit 1
fi

# DynamoDBまたはローカルJSONから前回の処理ステップを読み込む関数
load_last_step() {
    if [ "$IS_LOCAL" = true ]; then
        # ローカルJSONからステップを読み込む
        if [ -f "$STATUS_FILE" ]; then
            last_step=$(jq -r '.last_step' "$STATUS_FILE")
        else
            last_step="NOT_STARTED"
        fi
    else
        # DynamoDBからステップを読み込む
        last_step=$(aws dynamodb get-item \
            --table-name $DYNAMO_DB_NAME \
            --key '{"source_id": {"S": "'"$SOURCE_ID"'"}, "creation_date_time": {"S": "'"$CREATION_DATE_TIME"'"}}' \
            --query 'Item.last_step.S' --output text 2>/dev/null || echo "NOT_STARTED")
    fi
}

# DynamoDBまたはローカルJSONにステップを保存する関数
save_last_step() {
    local step=$1
    if [ "$IS_LOCAL" = true ]; then
        # ローカルJSONにステップを保存する
        echo "{\"source_id\": \"$SOURCE_ID\", \"job_id\": \"$JOB_ID\", \"last_step\": \"$step\"}" > "$STATUS_FILE"
    else
        # DynamoDBにステップを保存する
        aws dynamodb update-item \
            --table-name $DYNAMO_DB_NAME \
            --key '{"source_id": {"S": "'"$SOURCE_ID"'"}, "creation_date_time": {"S": "'"$CREATION_DATE_TIME"'"}}' \
            --update-expression "SET last_step = :step" \
            --expression-attribute-values '{":step": {"S": "'"$step"'"}}'
    fi
    # 保存したステップを反映
    last_step=$step
}
