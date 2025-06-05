FROM postgres:15

RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y postgresql-15-cron && \
    rm -rf /var/lib/apt/lists/*

CMD ["postgres", "-c", "shared_preload_libraries=pg_cron", "-c", "cron.database_name=shopping"]