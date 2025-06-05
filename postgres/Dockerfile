FROM postgres:15

RUN apt-get update && \
    apt-get install -y postgresql-15-cron && \
    rm -rf /var/lib/apt/lists/*

# 用 command-line 方式指定設定值
CMD ["postgres", "-c", "cron.database_name=shopping"]