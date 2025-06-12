from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from db.db import get_db_cursor
from datetime import datetime, timedelta
from utils.email import send_verification_email
from config import JWT_SECRET_KEY, JWT_ALGORITHM, FRONTEND_URL
import psycopg2.extras
import bcrypt
import uuid
import jwt

router = APIRouter(prefix="/api/customers")

#客戶註冊
@router.post("/register")
async def customer_register(request: Request, background_tasks: BackgroundTasks, cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    address = data.get("address")

    print(f"[註冊] 收到註冊請求 - Username: {username}, Email: {email}")

    try:
        if not (username and name and email and phone and address and password):
            print("❌ [註冊] 註冊失敗: 缺少必要欄位")
            return JSONResponse({"error": "缺少必要欄位"}, status_code=400)

        # 檢查 Email 是否已存在
        cursor.execute("SELECT customer_id, username, is_verified, token_expiry FROM customers WHERE email = %s", (email,))
        existing_email_record = cursor.fetchone()
        if existing_email_record:
            customer_id, _, is_verified, token_expiry = existing_email_record
            if is_verified:
                return JSONResponse({"error": "Email 已被使用"}, status_code=400)
            elif token_expiry and datetime.utcnow() > token_expiry.replace(tzinfo=None):
                cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
                cursor.connection.commit()
            else:
                remaining_seconds = max(0, int((token_expiry.replace(tzinfo=None) - datetime.utcnow()).total_seconds()))
                return JSONResponse({"error": "Email 已被使用且尚待驗證", "retry_after_seconds": remaining_seconds}, status_code=400)

        # 檢查 Username 是否已存在
        cursor.execute("SELECT customer_id, email, is_verified, token_expiry FROM customers WHERE username = %s", (username,))
        existing_username_record = cursor.fetchone()
        if existing_username_record:
            customer_id_un, _, is_verified_un, token_expiry_un = existing_username_record
            if is_verified_un:
                return JSONResponse({"error": "使用者名稱已被使用"}, status_code=400)
            elif token_expiry_un and datetime.utcnow() > token_expiry_un.replace(tzinfo=None):
                cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id_un,))
                cursor.connection.commit()
            else:
                remaining_seconds = max(0, int((token_expiry_un.replace(tzinfo=None) - datetime.utcnow()).total_seconds()))
                return JSONResponse({"error": "使用者名稱已被使用且尚待驗證", "retry_after_seconds": remaining_seconds}, status_code=400)

        # 註冊流程
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        verification_token = str(uuid.uuid4())
        token_expiry = datetime.utcnow() + timedelta(minutes=5)

        cursor.execute(
            """
            INSERT INTO customers (username, email, password, name, phone, address,
                                   is_verified, verification_token, token_expiry, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """,
            (username, email, hashed_password, name, phone, address, False, verification_token, token_expiry)
        )
        cursor.connection.commit()

        # 發送驗證信
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        background_tasks.add_task(send_verification_email, email, username, verification_link)

        print(f"✅ [註冊] 使用者 '{username}' 註冊成功")
        return JSONResponse({"message": "註冊成功，請檢查您的 Email"})
    
    except Exception as e:
        print(f"❌ [註冊] 錯誤：{e}")
        return JSONResponse({"error": "註冊失敗，請稍後再試"}, status_code=500)

#客戶登入（前台用）
@router.post("/login")
async def customer_login(request: Request, cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JSONResponse({"error": "帳號或密碼為必填！"}, status_code=400)

    cursor.execute("""
        SELECT customer_id, username, name, email, phone, address, password, is_verified 
        FROM customers 
        WHERE username=%s
    """, (username,))
    row = cursor.fetchone()
    
    if not row:
        return JSONResponse({"error": "帳號或密碼錯誤"}, status_code=401)
    
    if not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return JSONResponse({"error": "帳號或密碼錯誤"}, status_code=401)
        
    if not row["is_verified"]:
        return JSONResponse({"error": "請先驗證您的 Email"}, status_code=401)

    customer_id = row["customer_id"]
    token = jwt.encode({
        "customer_id": customer_id, 
        "username": username,  # 添加用户名到 token
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # 更新 current_token 實現後踢前機制
    cursor.execute("UPDATE customers SET current_token=%s WHERE customer_id=%s", (token, customer_id))
    cursor.connection.commit()

    # 構建用戶資料（不包含密碼）
    customer_data = {
        "customer_id": row["customer_id"],
        "username": row["username"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"]
    }

    return JSONResponse({
        "token": token,
        "customer": customer_data,
        "expire_at": (datetime.utcnow() + timedelta(minutes=30)).timestamp() * 1000  # 轉換為毫秒
    })

#驗證 token
@router.post("/verify-token")
async def verify_token(request: Request, cursor=Depends(get_db_cursor)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"error": "未提供有效的認證令牌"}, status_code=401)
    
    token = auth_header.split(" ")[1]
    try:
        # 解碼 token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        customer_id = payload.get("customer_id")
        username = payload.get("username")
        
        # 檢查 token 是否與資料庫中的相符
        cursor.execute("""
            SELECT customer_id, username, name, email, phone, address, current_token
            FROM customers 
            WHERE customer_id=%s AND username=%s
        """, (customer_id, username))
        row = cursor.fetchone()
        
        if not row:
            return JSONResponse({"error": "找不到用戶"}, status_code=401)
            
        # 如果是支付過程中的 token 驗證，不檢查 current_token
        is_payment = request.headers.get("X-Payment-Process") == "true"
        if not is_payment and row["current_token"] != token:
            return JSONResponse({"error": "Token 不符"}, status_code=401)
            
        # 構建用戶資料
        customer_data = {
            "customer_id": row["customer_id"],
            "username": row["username"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "address": row["address"]
        }
        
        return JSONResponse({
            "message": "Token 驗證成功",
            "customer": customer_data
        })
        
    except jwt.ExpiredSignatureError:
        return JSONResponse({"error": "認證令牌已過期"}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse({"error": "無效的認證令牌"}, status_code=401)
    except Exception as e:
        print(f"❌ [Token 驗證] 發生錯誤：{str(e)}")
        return JSONResponse({"error": "驗證過程發生錯誤"}, status_code=500)