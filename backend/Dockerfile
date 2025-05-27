FROM python:3.10-slim

# 安裝 Linux 套件：更新 + 安裝 postgresql-client
RUN apt update && \
    apt install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY app/requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY app/ ./app/

# 啟動 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

