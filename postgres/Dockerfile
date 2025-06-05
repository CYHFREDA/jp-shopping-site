FROM postgres:15

# 加入 PostgreSQL 官方 apt repository
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y postgresql-15-cron && \
    rm -rf /var/lib/apt/lists/*

# 啟動時帶入 cron 設定
CMD ["postgres", "-c", "cron.database_name=shopping"]
