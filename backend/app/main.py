from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from psycopg2 import errors
from datetime import datetime, timedelta
from routers import customers, verify, pay, orders, admin
from pydantic import BaseModel
from config import verify_customer_jwt, verify_admin_jwt,JWT_SECRET_KEY, JWT_ALGORITHM
import jwt
import random
import hashlib
import urllib.parse
import os
import bcrypt
import pytz 

# FastAPI 實例宣告
app = FastAPI()

#DB
from db.db import get_db_cursor

#CORS 設定
from middleware import setup_cors
setup_cors(app)

# .env 載入
from dotenv import load_dotenv
load_dotenv()

# 引入顧客 API 路由（如註冊、登入、查看自己資訊等）
app.include_router(customers.router)

# 引入 Email 驗證路由
app.include_router(verify.router, prefix="/api")

# 引入綠界支付路由
app.include_router(pay.router)

# 引入訂單 API 路由
app.include_router(orders.router)

# 引入後台 API 路由
app.include_router(admin.router)

#測試API是否正常
@app.get("/health")
async def health():
    return {"status": "ok"}

# ⭐️ 改善全域例外處理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ 全域例外錯誤: {exc}")
    # 若為 psycopg2 的特定資料庫錯誤，給前端更明確提示
    if isinstance(exc, errors.StringDataRightTruncation):
        return JSONResponse({"error": "❌ 文字長度超過限制！"}, status_code=400)
    if isinstance(exc, errors.UniqueViolation):
        return JSONResponse({"error": "❌ 資料重複，請確認再送出！"}, status_code=400)
    # 其他未知錯誤
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "❌ 伺服器錯誤，請稍後再試！"}
    )

# 取得所有商品
@app.get("/api/products")
async def get_products(query: str = "", category: str = "", cursor=Depends(get_db_cursor)):
    sql_query = "SELECT id, name, price, description, image_url, created_at, category FROM products"
    params = []
    conditions = []

    if query:
        conditions.append("(name ILIKE %s OR description ILIKE %s)")
        params.extend([f"%{query}%", f"%{query}%"])

    if category:
        conditions.append("category ILIKE %s")
        params.append(f"%{category}%")

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)
    
    sql_query += " ORDER BY created_at DESC"

    cursor.execute(sql_query, tuple(params))
    
    products = cursor.fetchall()
    return products

# 取得單一商品 (根據 ID)
@app.get("/api/products/{product_id}")
async def get_product_by_id(product_id: int, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute(
            """
            SELECT id, name, price, description, image_url, created_at, category
            FROM products
            WHERE id = %s
            """,
            (product_id,)
        )
        product = cursor.fetchone()

        if product:
            # 將查詢結果轉換為字典以便 JSON 序列化
            product_dict = {
                "id": product[0],
                "name": product[1],
                "price": float(product[2]), # 確保價格是數字類型
                "description": product[3],
                "image_url": product[4],
                "created_at": product[5].isoformat() if product[5] else None, # 轉換日期時間格式
                "category": product[6]
            }
            return JSONResponse(product_dict)
        else:
            raise HTTPException(status_code=404, detail="Product not found")

    except Exception as e:
        print(f"❌ 後端查詢單一商品錯誤 (ID: {product_id})：{str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")