# 使用一個 Node.js 映像檔來建置 Vue 應用
FROM node:lts-alpine as builder

# 設定工作目錄
WORKDIR /app

# 將 package.json 和 package-lock.json 複製到工作目錄
COPY package*.json ./

# 安裝項目依賴
RUN npm install

# 將所有原始碼複製到工作目錄
COPY . .

# 建置 Vue 應用程式
RUN npm run build

# 使用一個輕量級的 Nginx 映像檔來提供靜態檔案
FROM nginx:alpine

# 複製 Nginx 設定檔 (如果需要自訂)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 將建置好的靜態檔案從 builder 階段複製到 Nginx 的靜態檔案目錄
COPY --from=builder /app/dist /usr/share/nginx/html

# 啟動 Nginx 伺服器
CMD ["nginx", "-g", "daemon off;"] 