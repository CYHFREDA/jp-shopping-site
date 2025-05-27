#!/bin/bash

# 你的 Docker Hub 帳號 & 密碼（建議改用環境變數避免硬編在檔案裡）
DOCKERHUB_USERNAME="inulifgogo"
DOCKERHUB_PASSWORD="cahKev-miknik-tespe8"

# 要清理的 repo 名稱陣列
REPOS=("inulifgogo/backend-api" "inulifgogo/frontend-shop")

# 只保留最新的 N 個 tags
KEEP_NUM=5

# 取得 JWT token
echo "取得登入 token..."
TOKEN=$(curl -s -H "Content-Type: application/json" -X POST \
  -d "{\"username\": \"$DOCKERHUB_USERNAME\", \"password\": \"$DOCKERHUB_PASSWORD\"}" \
  https://hub.docker.com/v2/users/login/ | jq -r .token)

# 逐一處理每個 repo
for REPO in "${REPOS[@]}"; do
  echo "----------------------"
  echo "開始清理 $REPO"

  # 取得 tag 列表
  tags=$(curl -s -H "Authorization: JWT $TOKEN" \
    "https://hub.docker.com/v2/repositories/$REPO/tags?page_size=100" | jq -r '.results[].name')

  # 排除最新的 N 個 tags
  tags_to_delete=$(echo "$tags" | tail -n +$((KEEP_NUM + 1)))

  if [ -z "$tags_to_delete" ]; then
    echo "沒有需要刪除的 tags，已跳過。"
  else
    # 逐一刪除
    for tag in $tags_to_delete; do
      echo "刪除 tag: $tag"
      curl -s -X DELETE -H "Authorization: JWT $TOKEN" \
        "https://hub.docker.com/v2/repositories/$REPO/tags/$tag/"
    done
    echo "已完成 $REPO tags 清理！"
  fi
done

echo "全部完成！"

