import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from db.db import get_db_cursor

load_dotenv()

# JWT 設定
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# JWT 認證依賴項 (取代 Basic Auth)
async def verify_admin_jwt(request: Request, cursor=Depends(get_db_cursor)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的認證令牌")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("admin_id")
        username = payload.get("username")  # 从 token 中获取用户名
        
        # 检查 token 是否与数据库中的相符（只检查同一用户名的 token）
        cursor.execute("""
            SELECT current_token 
            FROM admin_users 
            WHERE id=%s AND username=%s
        """, (admin_id, username))
        row = cursor.fetchone()
        
        if not row or row["current_token"] != token:
            print(f"❌ [管理員驗證] 管理員 {username} (ID: {admin_id}) 的 token 不符或已在其他地方登入")
            raise HTTPException(status_code=401, detail="KICKED")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="認證令牌已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的認證令牌")

async def verify_customer_jwt(request: Request, cursor=Depends(get_db_cursor)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的認證令牌")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        customer_id = payload.get("customer_id")
        username = payload.get("username")  # 从 token 中获取用户名
        
        # 检查 token 是否与数据库中的相符（只检查同一用户名的 token）
        cursor.execute("""
            SELECT current_token 
            FROM customers 
            WHERE customer_id=%s AND username=%s
        """, (customer_id, username))
        row = cursor.fetchone()
        
        if not row or row["current_token"] != token:
            print(f"❌ [會員驗證] 會員 {username} (ID: {customer_id}) 的 token 不符或已在其他地方登入")
            raise HTTPException(status_code=401, detail="KICKED")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="認證令牌已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的認證令牌")

# Email 設定
FRONTEND_URL = os.getenv("FRONTEND_URL")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# 檢查 Email 設定是否完整
if not all([EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD, FRONTEND_URL]):
    print("⚠️ Email 設定不完整！請檢查 .env 中的 EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD, FRONTEND_URL。")