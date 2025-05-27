#!/bin/bash

# 產生日期時間標籤（格式：YYYYMMDDHHMM）
DATE_TAG=$(date +"%Y%m%d%H%M")
IMAGE_NAME="inulifgogo/backend-api:$DATE_TAG"

echo "========= 建立映像檔: $IMAGE_NAME ========="
docker build -t $IMAGE_NAME .

echo "========= 推送映像檔到 Docker Hub ========="
docker push $IMAGE_NAME

echo "========= 更新 Kubernetes Deployment 新映像檔 ========="
kubectl set image deployment/backend-api backend-api=$IMAGE_NAME
#kubectl set image 這個指令就已經會自動觸發「滾動更新」（rolling update），相當於自動重啟 Pod。
echo "========= 新的映像檔：$IMAGE_NAME ========="

echo "========= 清理 Docker 映像檔 ========="
docker image prune -a -f

echo "=========  等待 10 秒 ========="
sleep 10

echo "========= Deployment 映像檔 =========="
kubectl get deployment backend-api -o jsonpath="{.spec.template.spec.containers[*].image}"
echo "========= Pod 狀態 =========="
kubectl get pods -l app=backend-api -o wide
