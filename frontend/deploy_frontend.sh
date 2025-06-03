#!/bin/bash

# 記錄 deploy_frontend.sh 檔案所在目錄
SCRIPT_DIR=$(cd $(dirname $0) && pwd)
# Vue 專案目錄相對於腳本目錄的路徑
VUE_PROJECT_DIR="$SCRIPT_DIR/../clevora-vue"

# 變數設定
# 更改映像檔名稱以區分 Vue 前端
IMAGE_NAME="inulifgogo/clevora-vue-frontend"
DATE_TAG=$(date +"%Y%m%d%H%M")
FULL_IMAGE_NAME="$IMAGE_NAME:$DATE_TAG"

echo "➡️ 進入 Vue 專案目錄：$VUE_PROJECT_DIR"
cd $VUE_PROJECT_DIR

echo "📦 安裝 Vue 專案依賴..."
npm install

echo "🔨 建置 Vue 前端應用程式 (npm run build)..."
npm run build

echo "🐳 開始 Build 前端 Docker 映像檔：$FULL_IMAGE_NAME"
# 在 Vue 專案目錄下執行 docker build
docker build -t $FULL_IMAGE_NAME .

echo "⬆️ 推送映像檔到 Docker Hub：$FULL_IMAGE_NAME"
docker push $FULL_IMAGE_NAME

echo "🚀 使用 kubectl set image 更新 Deployment"
# 這裡需要確認您的前端 Deployment 的名稱是否還是 "frontend"
# 以及容器的名稱是否也是 "frontend"
# 如果您的 K8s 設定檔在 clevora-vue/k8s 下，可能需要調整 kubectl apply 的路徑
# 假設您的 Deployment 名稱是 clevora-vue-frontend
kubectl set image deployment clevora-vue-frontend clevora-vue-frontend=$FULL_IMAGE_NAME

echo "🧹 清理 Docker 映像檔..."
docker image prune -a -f

echo "✅ Vue 前端部署腳本執行完成！"

# 這裡可以選擇性地加上等待和檢查 Pod 狀態的命令
# echo "⏳ 等待 20 秒讓 Pod 滾動更新..."
# sleep 20
#
# echo "✅ 目前使用的映像檔："
# kubectl get deployment clevora-vue-frontend -o jsonpath='{.spec.template.spec.containers[*].image}'; echo
#
# echo "✅ 目前 Pod 狀態："
# kubectl get pods -l app=clevora-vue-frontend -o wide
#
# echo "🎉 Vue 前端部署完成！使用的新映像檔：$FULL_IMAGE_NAME"