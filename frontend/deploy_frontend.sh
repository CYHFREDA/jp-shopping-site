#!/bin/bash

# 記錄 deploy_backend.sh 檔案所在目錄
SCRIPT_DIR=$(cd $(dirname $0) && pwd)

# 變數設定
IMAGE_NAME="inulifgogo/frontend-shop"
DATE_TAG=$(date +"%Y%m%d%H%M")
FULL_IMAGE_NAME="$IMAGE_NAME:$DATE_TAG"

echo "🔨 開始 Build 前端 Docker 映像檔：$FULL_IMAGE_NAME"
docker build -t $FULL_IMAGE_NAME $SCRIPT_DIR

echo "📦 推送映像檔到 Docker Hub：$FULL_IMAGE_NAME"
docker push $FULL_IMAGE_NAME

echo "🚀 使用 kubectl set image 更新 Deployment"
kubectl set image deployment frontend frontend=$FULL_IMAGE_NAME

echo "========= 清理 Docker 映像檔 ========="
docker image prune -a -f

echo "⏳ 等待 20 秒讓 Pod 滾動更新..."
sleep 20

echo "✅ 目前使用的映像檔："
kubectl get deployment frontend -o jsonpath="{.spec.template.spec.containers[*].image}"; echo

echo "✅ 目前 Pod 狀態："
kubectl get pods -l app=frontend -o wide

echo "🎉 前端部署完成！使用的新映像檔：$FULL_IMAGE_NAME"

