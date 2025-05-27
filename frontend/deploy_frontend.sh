#!/bin/bash

# 變數設定
IMAGE_NAME="inulifgogo/frontend-shop"
DATE_TAG=$(date +"%Y%m%d%H%M")
FULL_IMAGE_NAME="$IMAGE_NAME:$DATE_TAG"

echo "🔨 開始 Build 前端 Docker 映像檔：$FULL_IMAGE_NAME"
docker build -t $FULL_IMAGE_NAME .

echo "📦 推送映像檔到 Docker Hub：$FULL_IMAGE_NAME"
docker push $FULL_IMAGE_NAME

echo "📝 更新 deployment.yaml 使用新映像檔"
# 這邊假設 deployment.yaml 在 frontend/k8s/deployment.yaml
# 且含有 image: inulifgogo/frontend-shop:xxx
# 這樣可以直接做取代
sed -i "s|image: $IMAGE_NAME:.*|image: $FULL_IMAGE_NAME|" ./k8s/deployment.yaml

echo "🚀 套用 Deployment 更新到 Kubernetes"
kubectl apply -f ./k8s/deployment.yaml

echo "⏳ 等待 20 秒讓 Pod 滾動更新..."
sleep 20

echo "✅ 檢查新的 Pod 狀態與使用映像檔："
kubectl get pods -l app=frontend -o wide
kubectl get deployment frontend -o jsonpath="{.spec.template.spec.containers[*].image}"; echo

echo "🎉 前端部署完成！使用的新映像檔：$FULL_IMAGE_NAME"

