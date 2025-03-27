#!/bin/bash

if [ -z "$AWS_ROLE_ARN" ]; then
    echo "環境変数 AWS_ROLE_ARN が設定されていません。"
    exit 1
fi
if [ -z "$ROLE_SESSION_NAME" ]; then
    echo "環境変数 AWS_ROLE_ARN が設定されていません。"
    exit 1
fi
if [ -z "$S3_DESTINATION_NAME" ]; then
    echo "環境変数 S3_DESTINATION_NAME が設定されていません。"
    exit 1
fi

# AWS / ファイルダウンロード処理
aws_download() {
    # コピー先ディレクトリを作成
    mkdir -p "$INPUT_DIR"

    if [ "$IS_LOCAL" = true ]; then
        echo "S3_URL = $S3_URL"
        echo "SOURCE_ID = $SOURCE_ID"
        echo "INPUT_DIR = $INPUT_DIR"
    else
        echo "Assume Roleを開始します。"
        Credentials=$(aws sts assume-role --role-arn "$AWS_ROLE_ARN" --role-session-name $ROLE_SESSION_NAME)
        export AWS_ACCESS_KEY_ID=$(echo $Credentials | \jq -r '.Credentials.AccessKeyId')
        export AWS_SECRET_ACCESS_KEY=$(echo $Credentials | \jq -r '.Credentials.SecretAccessKey')
        export AWS_SESSION_TOKEN=$(echo $Credentials | \jq -r '.Credentials.SessionToken')
        echo "S3_CHECK: ファイル数チェックを開始します。"

        # S3内のファイルをカウント
        file_count=$(aws s3 ls "$S3_URL" --recursive | wc -l)

        if [ "$file_count" -eq 0 ]; then
            echo "S3バケットにファイルが存在しません。"
            exit 1
        elif [ "$file_count" -gt 1000 ]; then
            echo "S3バケット内のファイル数が1000件を超えています。"
            exit 1
        fi

        echo "S3バケット内のファイル数: $file_count"
        echo "S3_COPY: 検証アカウントのs3からデータをコピーします。"

        # copy s3 bucket
        echo "ファイルコピー処理を実行"
        aws s3 cp "$S3_URL" s3://"$S3_DESTINATION_NAME"/"$SOURCE_ID"/ --recursive

        # sync s3 bucket
        echo "ファイル同期処理を実行"
        aws s3 sync "$S3_URL" s3://"$S3_DESTINATION_NAME"/"$SOURCE_ID"/

        echo "検証アカウントからデータをコピーしました。"

        echo "S3_DL: S3からファイルをダウンロードします。"
        # S3からすべてのファイルを指定ディレクトリにダウンロード
        aws s3 cp s3://"$S3_DESTINATION_NAME"/"$SOURCE_ID"/ "$INPUT_DIR" --recursive
        echo "S3から$INPUT_DIRにすべてのファイルをダウンロードしました。"

        echo "Assume Roleを終了します"
        unset AWS_ACCESS_KEY_ID
        unset AWS_SECRET_ACCESS_KEY
        unset AWS_SESSION_TOKEN
    fi
}
