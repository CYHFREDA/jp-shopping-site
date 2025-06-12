import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

global_pool = None  # 初始化為 None

# 全局連線池 minconn 建議根據應用程式的預期併發量設定，maxconn 避免耗盡資料庫資源
# 可以根據實際情況調整這些值
# 初始化連線池
def init_pool():
    global global_pool
    if not global_pool:
        global_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port="5432"
        )

# 從連線池中獲取連線
def get_db_conn():
    if not global_pool:
        init_pool()
    return global_pool.getconn()

# FastAPI 依賴項：獲取游標並確保連線被歸還
async def get_db_cursor():
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield cursor
    finally:
        if cursor:
            cursor.close()
        if conn:
            global_pool.putconn(conn)