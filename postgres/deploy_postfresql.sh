#!/bin/bash

# 記錄 deploy_backend.sh 檔案所在目錄
SCRIPT_DIR=$(cd $(dirname $0) && pwd)

# 變數設定
IMAGE_NAME="inulifgogo/postgresql"
DATE_TAG=$(date +"%Y%m%d%H%M")
FULL_IMAGE_NAME="$IMAGE_NAME:$DATE_TAG"

echo "🔨 開始 Build PostgreSQL Docker 映像檔：$FULL_IMAGE_NAME"
docker build -t $FULL_IMAGE_NAME $SCRIPT_DIR

echo "📦 推送映像檔到 Docker Hub：$FULL_IMAGE_NAME"
docker push $FULL_IMAGE_NAME

echo "🚀 使用 kubectl set image 更新 Deployment"
kubectl set image deployment postgres postgres=$FULL_IMAGE_NAME

echo "========= 清理 Docker 映像檔 ========="
docker image prune -a -f