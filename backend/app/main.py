from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from psycopg2 import errors
from datetime import datetime, timedelta
import random
import uvicorn
import hashlib
import urllib.parse
import os
import psycopg2
import bcrypt
import psycopg2.extras
import jwt
import pytz
from psycopg2.pool import SimpleConnectionPool
import smtplib
import ssl
from email.mime.text import MIMEText
import uuid
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel

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
from routers import customers
app.include_router(customers.router)


# JWT 設定
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 從環境變數讀取密鑰
if not JWT_SECRET_KEY:
    print("⚠️ JWT_SECRET_KEY 環境變數未設定，將使用預設值。請在生產環境中設定安全的密鑰！")
    JWT_SECRET_KEY = "super-secret-jwt-key-for-development"

JWT_ALGORITHM = "HS256"

# 新增 Email 設定
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173") # 前端網址，用於 Email 驗證連結

# 檢查 Email 設定是否完整
if not all([EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD, FRONTEND_URL]):
    print("⚠️ Email 設定不完整！請檢查 .env 中的 EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD, FRONTEND_URL。")

# PostgreSQL 連線參數
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = "5432"


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

#綠界測試環境設定
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
ECPAY_API_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

# 產生 CheckMacValue
def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&" + '&'.join([f"{k}={v}" for k, v in sorted_params]) + f"&HashIV={hash_iv}"
    encode_str = urllib.parse.quote_plus(encode_str).lower()
    sha256 = hashlib.sha256()
    sha256.update(encode_str.encode('utf-8'))
    return sha256.hexdigest().upper()

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

# 支付區
@app.post("/pay")
async def pay(request: Request, cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        print("✅ 收到前端資料：", data)

        products = data.get("products")
        customer_id = data.get("customer_id")

        if not products:
            return JSONResponse({"error": "❌ 缺少商品資料"}, status_code=400)
            
        if not customer_id:
            print("⚠️ 未收到 customer_id，訂單將不會關聯到客戶。")

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d%H%M%S")
        serial_number = f"{random.randint(0, 999999):06d}"
        order_id = f"{date_time_str}{serial_number}"

        amount = sum(item["price"] * item["quantity"] for item in products)
        item_names = "#".join([f"{item['name']} x {item['quantity']}" for item in products])
        trade_date = now.strftime("%Y/%m/%d %H:%M:%S")

        #寫入資料庫
        cursor.execute("""
            INSERT INTO orders (order_id, amount, item_names, status, created_at, customer_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, amount, item_names, 'pending', trade_date, customer_id))
        cursor.connection.commit()
        print("✅ 訂單已寫入資料庫！")

        # 綠界參數
        params = {
            "MerchantID": ECPAY_MERCHANT_ID,
            "MerchantTradeNo": order_id,
            "MerchantTradeDate": trade_date,
            "PaymentType": "aio",
            "TotalAmount": amount,
            "TradeDesc": "綠界平台商測試",
            "ItemName": item_names,
            "ReturnURL": f"{YOUR_DOMAIN}/ecpay/notify",
            "ChoosePayment": "Credit",
            "ClientBackURL": f"{YOUR_DOMAIN}/pay/return",
            "PlatformID": ECPAY_MERCHANT_ID
        }
        params["CheckMacValue"] = generate_check_mac_value(params, ECPAY_HASH_KEY, ECPAY_HASH_IV)
        print("✅ 送出的參數：", params)

        return JSONResponse({"ecpay_url": ECPAY_API_URL, "params": params, "order_id": order_id})

    except Exception as e:
        print("❌ 後端錯誤：", str(e))
        return JSONResponse({"error": "後端發生錯誤"}, status_code=500)

@app.post("/ecpay/notify")
async def ecpay_notify(request: Request, cursor=Depends(get_db_cursor)):
    try:
        data = await request.form()
        print("✅ 收到綠界通知：", data)

        order_id = data.get("MerchantTradeNo")
        rtn_code = data.get("RtnCode")
        payment_date = data.get("PaymentDate", None)
        status_ = "success" if rtn_code == "1" else "fail"

        cursor.execute("UPDATE orders SET status=%s, paid_at=%s WHERE order_id=%s", (status_, payment_date, order_id))
        cursor.connection.commit()

        # 🟢 新增出貨資料（如果訂單是成功付款）
        if status_ == "success":
            # 先查訂單的 customer_id
            cursor.execute("SELECT customer_id FROM orders WHERE order_id = %s", (order_id,))
            row = cursor.fetchone()
            customer_id = row[0] if row else None

            recipient_name = '待填寫'
            address = '待填寫'
            if customer_id:
                cursor.execute("SELECT name, address FROM customers WHERE customer_id = %s", (customer_id,))
                customer = cursor.fetchone()
                if customer:
                    recipient_name, address = customer

            cursor.execute("""
                INSERT INTO shipments (order_id, recipient_name, address, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (order_id, recipient_name, address, 'pending'))
            cursor.connection.commit()
            print(f"✅ 出貨單已自動建立，order_id: {order_id}, recipient: {recipient_name}, address: {address}")

        print(f"✅ 訂單 {order_id} 狀態已更新為：{status_}")

        return HTMLResponse("1|OK")
    except Exception as e:
        print("❌ /ecpay/notify 發生錯誤：", str(e))
        return HTMLResponse("0|Error")

#前端
@app.get("/api/orders/{order_id}/status")
async def get_order_status(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        row = cursor.fetchone()

        if row:
            return JSONResponse({"order_id": order_id, "status": row[0]})
        else:
            return JSONResponse({"error": "Order not found"}, status_code=404)

    except Exception as e:
        print("❌ 後端查詢訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

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

# 後台：取得所有商品 (需要管理員權限)
@app.get("/api/admin/products")
async def admin_get_products(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT id, name, price, description, image_url, created_at, category
            FROM products
            ORDER BY created_at DESC
        """)

        products = []
        for row in cursor.fetchall():
             products.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "description": row[3],
                "image_url": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "category": row[6]
            })
        
        return JSONResponse(products)

    except Exception as e:
        print("❌ 後台載入商品資料錯誤：", str(e))
        return JSONResponse({"error": "無法載入商品資料"}, status_code=500)

#客戶登入（前台用）
@app.post("/api/customers/login")
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

@app.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: int, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        # 验证 token 中的 customer_id 是否匹配
        if auth.get("customer_id") != customer_id:
            return JSONResponse({"error": "無權訪問此客戶的訂單"}, status_code=403)

        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at
            FROM orders
            WHERE customer_id=%s
            ORDER BY created_at DESC
        """, (customer_id,))
        orders = cursor.fetchall()
        
        # 將 datetime 物件轉換為字串以便 JSON 序列化
        formatted_orders = []
        for order_row in orders:
            # 將 DictRow 轉換為標準 Python 字典
            order_dict = dict(order_row)
            # 格式化 datetime 物件為字串以便 JSON 序列化
            if order_dict.get('created_at'):
                order_dict['created_at'] = order_dict['created_at'].isoformat()
            if order_dict.get('paid_at'):
                order_dict['paid_at'] = order_dict['paid_at'].isoformat()
            formatted_orders.append(order_dict)

        return JSONResponse(formatted_orders)

    except Exception as e:
        print(f"❌ 後端查詢客戶 {customer_id} 訂單錯誤： {e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)
    
# 後端
@app.get("/api/admin/orders")
async def admin_get_orders(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT id, order_id, amount, item_names, status, created_at, paid_at FROM orders ORDER BY created_at DESC")
        rows = cursor.fetchall()

        # 手動構建字典列表並格式化 datetime 欄位
        formatted_orders = []
        for row in rows:
            order_dict = {
                "id": row[0],
                "order_id": row[1],
                "amount": row[2],
                "item_names": row[3],
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None, # 格式化 datetime
                "paid_at": row[6].isoformat() if row[6] else None    # 格式化 datetime
            }
            formatted_orders.append(order_dict)

        return JSONResponse(formatted_orders)

    except Exception as e:
        print(f"❌ 後端查詢訂單錯誤： {e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)

@app.post("/api/admin/update_order_status")
async def update_order_status(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        order_id = data.get("order_id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return JSONResponse({"error": "缺少必要參數"}, status_code=400)

        if new_status not in ["pending", "success", "fail"]:
            return JSONResponse({"error": "無效的訂單狀態"}, status_code=400)

        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return JSONResponse({"error": "找不到訂單"}, status_code=404)

        cursor.execute("""
            UPDATE orders 
            SET status=%s, 
                paid_at=CASE 
                    WHEN %s='success' THEN CURRENT_TIMESTAMP 
                    ELSE paid_at 
                END 
            WHERE order_id=%s
        """, (new_status, new_status, order_id))
        
        cursor.connection.commit()

        return JSONResponse({"message": "訂單狀態更新成功"})

    except Exception as e:
        print("❌ 更新訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "更新訂單狀態失敗"}, status_code=500)

#後台新增商品
@app.post("/api/admin/products")
async def admin_add_product(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url")
    if not image_url:
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqqmt7zkmd-lRuFm44YueFePaZjxllx12CfQ&s"
    category = data.get("category", "")

    if not name or not price:
        return JSONResponse({"error": "❌ 商品名稱與價格為必填！"}, status_code=400)

    try:
        cursor.execute("""
            INSERT INTO products (name, price, description, image_url, category)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, price, description, image_url, category))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 商品已新增"})
    except errors.StringDataRightTruncation as e:
        # 資料過長
        return JSONResponse({"error": "❌ 文字長度超過限制，請修改再送出！"}, status_code=400)
    except Exception as e:
        print("❌ 新增商品時出錯：", e)
        return JSONResponse({"error": "❌ 新增商品失敗，請稍後再試！"}, status_code=500)

#後台編輯商品
@app.put("/api/admin/products/{id}")
async def admin_update_product(id: int, request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url", "")
    category = data.get("category", "")

    cursor.execute("""
        UPDATE products
        SET name=%s, price=%s, description=%s, image_url=%s, category=%s
        WHERE id=%s
    """, (name, price, description, image_url, category, id))
    cursor.connection.commit()
    return JSONResponse({"message": "商品已更新"})

#後台刪除商品
@app.delete("/api/admin/products/{id}")
async def admin_delete_product(id: int, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    cursor.connection.commit()
    return JSONResponse({"message": "商品已刪除"})

#後台出貨管理
@app.get("/api/admin/shipments")
async def admin_get_shipments(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    print("🚚 準備查詢出貨資料")
    try:
        cursor.execute("SELECT shipment_id, order_id, recipient_name, address, status, created_at, return_store_name, return_tracking_number FROM shipments ORDER BY created_at DESC")
        rows = cursor.fetchall()
        print("✅ 查詢結果：", rows)
    except Exception as e:
        print("❌ 出錯：", e)
    shipments = [{"shipment_id": r[0], "order_id": r[1], "recipient_name": r[2], "address": r[3], "status": r[4], "created_at": str(r[5]), "return_store_name": r[6], "return_tracking_number": r[7]} for r in rows]
    return JSONResponse(shipments)

# 後台出貨管理更新出貨單資料
@app.post("/api/admin/update_shipment")
async def admin_update_shipment(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    shipment_id = data.get("shipment_id")
    recipient_name = data.get("recipient_name")
    address = data.get("address")
    status_ = data.get("status")

    if not shipment_id or not recipient_name or not address or not status_:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    cursor.execute("""
        UPDATE shipments SET recipient_name=%s, address=%s, status=%s
        WHERE shipment_id=%s
    """, (recipient_name, address, status_, shipment_id))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 出貨資料已更新！"})

#後台客戶管理
@app.get("/api/admin/customers")
async def admin_get_customers(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    cursor.execute("SELECT customer_id, name, email, phone, address, created_at FROM customers ORDER BY created_at DESC")
    rows = cursor.fetchall()
    customers = [
        {
            "customer_id": r[0],
            "name": r[1],
            "email": r[2],
            "phone": r[3],
            "address": r[4],
            "created_at": str(r[5])
        }
        for r in rows
    ]
    return JSONResponse(customers)

#後台客戶重置密碼
@app.post("/api/admin/reset_customer_password")
async def admin_reset_customer_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    customer_id = data.get("customer_id")
    new_password = data.get("new_password")

    if not customer_id or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    # bcrypt 雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # conn = get_db_conn()
    # cursor = conn.cursor()
    cursor.execute("UPDATE customers SET password=%s WHERE customer_id=%s", (hashed_password, customer_id))
    cursor.connection.commit()
    # cursor.close()
    # conn.close()
    return JSONResponse({"message": "✅ 密碼已重置（bcrypt 加密）"})

#後台編輯客戶資料
@app.post("/api/admin/update_customer")
async def admin_update_customer(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    customer_id = data.get("customer_id")
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address", "")
    if not customer_id or not name or not phone:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    # conn = get_db_conn()
    # cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name=%s, phone=%s, address=%s
        WHERE customer_id=%s
    """, (name, phone, address, customer_id))

    cursor.connection.commit()
    # cursor.close()
    # conn.close()

    return JSONResponse({"message": "✅ 客戶資料已更新！"})

#後台新增管理員
@app.post("/api/admin/create_admin")
async def create_admin(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (username, hashed_password))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 管理員已新增"})
    except psycopg2.IntegrityError:
        return JSONResponse({"error": "❌ 帳號已存在"}, status_code=400)
    finally:
        pass # 連線由依賴項管理，不需要手動關閉

#顯示後台使用者
@app.get("/api/admin/admin_users")
async def admin_get_admin_users(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    # 讀取 id, username, created_at 和 notes 欄位
    cursor.execute("SELECT id, username, created_at, notes FROM admin_users ORDER BY created_at")
    rows = cursor.fetchall()
    # 返回包含 id 和 notes 的使用者列表
    return [{"id": r[0], "username": r[1], "created_at": str(r[2]), "notes": r[3]} for r in rows]

# 刪除管理員
@app.delete("/api/admin/admin_users/{admin_id}")
async def admin_delete_admin(admin_id: int, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        # 執行刪除操作
        cursor.execute("DELETE FROM admin_users WHERE id=%s", (admin_id,))
        cursor.connection.commit()

        # 檢查是否有行被刪除
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="❌ 找不到該管理員或已刪除！")

        return JSONResponse({"message": "✅ 管理員已成功刪除！"})
    except HTTPException as e:
        raise e # 重新拋出 HTTPException
    except Exception as e:
        print(f"❌ 刪除管理員時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 刪除管理員失敗，請稍後再試！")

# 獲取系統設定
@app.get("/api/admin/settings")
async def get_admin_settings(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT site_title, contact_email, items_per_page FROM settings LIMIT 1")
        settings = cursor.fetchone()
        if settings:
            return JSONResponse(dict(settings))
        else:
            # 如果資料庫中沒有設定，返回預設值或空物件
            return JSONResponse({"site_title": "", "contact_email": "", "items_per_page": 10})
    except Exception as e:
        print(f"❌ 獲取系統設定時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 獲取系統設定失敗！")

# 更新系統設定
@app.post("/api/admin/settings")
async def update_admin_settings(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        site_title = data.get("site_title")
        contact_email = data.get("contact_email")
        items_per_page = data.get("items_per_page")

        # 檢查設定是否存在，如果不存在則插入，否則更新
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]

        if count == 0:
            # 插入新設定
            cursor.execute("INSERT INTO settings (site_title, contact_email, items_per_page) VALUES (%s, %s, %s)",
                           (site_title, contact_email, items_per_page))
        else:
            # 更新現有設定
            cursor.execute("UPDATE settings SET site_title=%s, contact_email=%s, items_per_page=%s",
                           (site_title, contact_email, items_per_page))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 設定已成功保存！"})
    except Exception as e:
        print(f"❌ 保存系統設定時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 保存設定失敗！")

# 修改管理員資訊 (例如備註)
@app.post("/api/admin/update_admin")
async def admin_update_admin(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    admin_id = data.get("id") # 從前端傳入管理員 ID
    notes = data.get("notes")

    if not admin_id:
        raise HTTPException(status_code=400, detail="❌ 缺少管理員 ID")
    
    # 注意：這裡只允許更新 notes 欄位，如果需要更新其他欄位，需要修改這裡的 SQL 語句
    cursor.execute("UPDATE admin_users SET notes=%s WHERE id=%s", (notes, admin_id))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 管理員資料已更新！"})

#修改使用者密碼
@app.post("/api/admin/update_admin_password")
async def update_admin_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    new_password = data.get("new_password")
    if not username or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    
    # bcrypt 重新產生雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("UPDATE admin_users SET password=%s WHERE username=%s", (hashed_password, username))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 密碼已更新！"})

# 後台管理員重置密碼
@app.post("/api/admin/reset_admin_password")
async def admin_reset_admin_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="❌ 缺少使用者名稱")

    # 生成一個新的隨機密碼 (例如 8 個字元的英數字混合)
    new_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))

    # bcrypt 雜湊新密碼
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # 更新資料庫中的密碼
        cursor.execute("UPDATE admin_users SET password=%s WHERE username=%s", (hashed_password, username))
        cursor.connection.commit()
        # 返回新生成的明文密碼給前端 (請注意安全性)
        return JSONResponse({"message": "✅ 密碼已重置！", "new_password": new_password})
    except Exception as e:
        print(f"❌ 重置管理員密碼時出錯: {e}")
        raise HTTPException(status_code=500, detail="❌ 重置密碼失敗，請稍後再試！")

@app.post("/api/admin/login")
async def admin_login(request: Request, cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"error": "帳號或密碼為必填！"}, status_code=400)
    cursor.execute("SELECT id, password FROM admin_users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if not row or not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return JSONResponse({"error": "帳號或密碼錯誤"}, status_code=401)
    admin_id = row["id"]
    token = jwt.encode({
        "admin_id": admin_id,
        "username": username, # 添加用户名到 token
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # 更新 current_token 實現後踢前機制
    cursor.execute("UPDATE admin_users SET current_token=%s WHERE id=%s", (token, admin_id))
    cursor.connection.commit()

    return JSONResponse({
        "message": "登入成功",
        "token": token,
        "admin_id": admin_id,
        "expire_at": (datetime.utcnow() + timedelta(minutes=30)).timestamp() * 1000 # 轉換為毫秒
    })

# 發送驗證 Email 的輔助函式
async def send_verification_email(recipient_email: str, username: str, verification_link: str):
    if not all([EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD]):
        print("❌ 無法發送 Email：Email 服務設定不完整。")
        return False

    sender_email = EMAIL_USERNAME
    sender_password = EMAIL_PASSWORD

    if not sender_email or not sender_password:
        print("❌ [Email服務] 錯誤：SMTP 環境變數未完整設定。")
        raise ValueError("SMTP environment variables are not fully set.")

    # 使用 MIMEMultipart 來同時包含純文字和 HTML 內容
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "歡迎加入！請驗證您的 Email 以啟用帳戶"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # Email 的純文字內容 (重新加入)
    text = f"""
        哈囉 {username},
        感謝您註冊我們的服務！
        請點擊以下連結驗證您的 Email：
        {verification_link}
        此連結將於 5 分鐘內過期。
        如果您沒有註冊，請忽略此 Email。
        """

    # Email 的 HTML 內容 (Notion 風格卡片)
    html = f"""
        <!DOCTYPE html>
        <html lang=\"zh-TW\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>CleVora 帳戶驗證通知</title>
        </head>
        <body style=\"background:#f8f9fa;padding:32px 0;\">
          <div style=\"max-width:480px;margin:0 auto;font-family:'Segoe UI','Arial','Microsoft JhengHei',sans-serif;\">
            <h2 style=\"color:#38302e;text-align:center;margin-bottom:8px;\">驗證您的信箱</h2>
            <p style=\"text-align:center;color:#555;margin-bottom:24px;\">感謝您註冊 Clevora 日本代購，請確認以下資訊並完成驗證：</p>
            <div style=\"background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);padding:24px 20px 16px 20px;margin-bottom:24px;\">
              <div style=\"display:flex;align-items:center;margin-bottom:12px;\">
                <span style=\"font-size:20px;margin-right:10px;\">📧</span>
                <span style=\"color:#a18a7b;font-weight:bold;width:80px;display:inline-block;\">信箱</span>
                <span style=\"color:#38302e;\">{recipient_email}</span>
              </div>
              <div style=\"display:flex;align-items:center;margin-bottom:12px;\">
                <span style=\"font-size:20px;margin-right:10px;\">⏰</span>
                <span style=\"color:#a18a7b;font-weight:bold;width:80px;display:inline-block;\">有效時間</span>
                <span style=\"color:#38302e;\">5 分鐘內</span>
              </div>
              <div style="display:flex;align-items:center;margin-bottom:12px;">
                <span style="font-size:20px;margin-right:10px;">🔗</span>
                <span style="color:#a18a7b;font-weight:bold;width:80px;display:inline-block;">驗證連結</span>
                <span style="color:#a18a7b;">點此下方連結完成驗證</span>
              </div>
            </div>
            <a href="{verification_link}" style="display:block;width:100%;max-width:320px;margin:0 auto 24px auto;background:#a18a7b;color:#fff;text-align:center;padding:14px 0;border-radius:8px;font-size:1.15rem;font-weight:bold;text-decoration:none;">立即驗證信箱</a>
            <p style="color:#888;font-size:0.95rem;text-align:center;margin-bottom:8px;">如果你沒有註冊 Clevora，請忽略此信件。</p>
            <p style="color:#bbb;font-size:0.85rem;text-align:center;">Clevora 日本代購 &nbsp;|&nbsp; <a href="mailto:wvwwcw99@gmail.com" style="color:#bbb;">客服信箱</a></p>
          </div>
        </body>
        </html>
        """

    # 將純文字和 HTML 內容附加到 MIMEMultipart 物件 (純文字在前，HTML 在後)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    msg.attach(part1)
    msg.attach(part2)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"✅ [Email服務] 驗證信成功寄送給 {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ [Email服務] 寄送驗證信失敗：{e}")
        return False

# Email 驗證端點
@app.get("/api/verify-email")
async def verify_email(token: str, cursor=Depends(get_db_cursor)):
    print(f"[Email 驗證] 收到 Email 驗證請求，Token: {token}")
    try:
        cursor.execute("SELECT customer_id, username, is_verified, token_expiry FROM customers WHERE verification_token = %s", (token,))
        customer = cursor.fetchone()

        if not customer:
            print(f"❌ [Email 驗證] 驗證失敗: 無效或找不到 token: {token}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="無效或已使用的驗證連結。")

        customer_id, username, is_verified, token_expiry = customer
        print(f"[Email 驗證] 找到客戶 '{username}', 已驗證狀態: {is_verified}, 過期時間: {token_expiry}")

        if is_verified:
            print(f"✅ [Email 驗證] 客戶 '{username}' 已驗證成功，無需重複驗證。")
            return JSONResponse({"message": "您的 Email 已驗證成功，無需重複驗證。"})

        if token_expiry and datetime.utcnow() > token_expiry.replace(tzinfo=None):
            print(f"❌ [Email 驗證] 驗證失敗: 客戶 '{username}' 的 token 已過期。")
            # 清除過期的 token 和過期時間
            cursor.execute("UPDATE customers SET verification_token = NULL, token_expiry = NULL WHERE customer_id = %s", (customer_id,))
            cursor.connection.commit()
            print(f"✅ [Email 驗證] 客戶 '{username}' 的過期 token 已被清除。")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已過期，請重新註冊或申請新連結。")

        print(f"[Email 驗證] 嘗試更新客戶 '{username}' 為已驗證狀態。")
        cursor.execute("UPDATE customers SET is_verified = TRUE, verification_token = NULL, token_expiry = NULL WHERE customer_id = %s", (customer_id,))
        cursor.connection.commit()
        print(f"✅ [Email 驗證] 客戶 '{username}' Email 已驗證成功並更新資料庫！")

        return JSONResponse({"message": "✅ Email 驗證成功！您現在可以登入。"})

    except HTTPException as e:
        print(f"❌ [Email 驗證] 發生 HTTP 錯誤：{e.detail}")
        raise e
    except Exception as e:
        print(f"❌ [Email 驗證] 發生未知錯誤：{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email 驗證失敗，請稍後再試！")

# 重新發送驗證 Email 端點
@app.post("/api/customers/resend-verification-email")
async def resend_verification_email_endpoint(request: Request, cursor=Depends(get_db_cursor)):
    data = await request.json()
    email = data.get("email")

    if not email:
        print("❌ [重新發送驗證信] 請求缺少 Email。")
        return JSONResponse({"error": "缺少 Email 地址"}, status_code=400)

    try:
        print(f"[重新發送驗證信] 收到重新發送請求，Email: {email}")
        cursor.execute("SELECT customer_id, username, is_verified FROM customers WHERE email = %s", (email,))
        customer = cursor.fetchone()

        if not customer:
            print(f"❌ [重新發送驗證信] Email '{email}' 未註冊或不存在。")
            return JSONResponse({"error": "此 Email 地址未註冊。"}, status_code=404)

        customer_id, username, is_verified = customer

        if is_verified:
            print(f"✅ [重新發送驗證信] Email '{email}' 已驗證，無需重新發送。")
            return JSONResponse({"message": "您的 Email 已驗證成功，無需重新發送。"}, status_code=200)

        # 生成新的驗證 token 和過期時間
        verification_token = str(uuid.uuid4())
        token_expiry = datetime.utcnow() + timedelta(minutes=5) # 5 分鐘過期

        print(f"[重新發送驗證信] 為 Email '{email}' 生成新 token: {verification_token}, 過期時間: {token_expiry}")

        # 更新資料庫中的 token 和過期時間
        cursor.execute(
            "UPDATE customers SET verification_token = %s, token_expiry = %s WHERE customer_id = %s",
            (verification_token, token_expiry, customer_id)
        )
        cursor.connection.commit()
        print(f"✅ [重新發送驗證信] 資料庫已更新 Email '{email}' 的驗證 token。")

        # 重新發送驗證 Email
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        email_sent = await send_verification_email(email, username, verification_link)

        if email_sent:
            print(f"✅ [重新發送驗證信] 驗證信已成功重新發送給 {email}。")
            return JSONResponse({"message": "✅ 驗證信已成功重新發送，請檢查您的 Email 收件箱。"}, status_code=200)
        else:
            print(f"❌ [重新發送驗證信] 重新發送驗證信給 {email} 失敗。")
            return JSONResponse({"error": "重新發送驗證信失敗，請稍後再試。"}, status_code=500)

    except Exception as e:
        print(f"❌ [重新發送驗證信] 發生錯誤：{e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)

# 儀表板統計 API
@app.get("/api/admin/dashboard_summary")
async def admin_dashboard_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    auth=Depends(verify_admin_jwt),
    cursor=Depends(get_db_cursor)
):
    try:
        # 今日訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURRENT_DATE
        """)
        today_order = cursor.fetchone()[0]

        # 未付款訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM orders WHERE status = 'pending'
        """)
        unpaid_order = cursor.fetchone()[0]

        # 未出貨訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM shipments WHERE status = 'pending'
        """)
        unshipped_order = cursor.fetchone()[0]

        # 總營業額（已付款訂單）
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'success'
        """)
        total_sales = float(cursor.fetchone()[0])

        # 處理日期區間
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if not start_date or not end_date:
            end_date = today.strftime('%Y-%m-%d')
            start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        # 查詢區間訂單數
        cursor.execute("""
            SELECT TO_CHAR(created_at, 'MM/DD') as day, COUNT(*)
            FROM orders
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY day
            ORDER BY day
        """, (start_date, end_date))
        rows = cursor.fetchall()
        date_map = {r[0]: r[1] for r in rows}
        # 產生區間所有日期
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        dates = [(start_dt + timedelta(days=i)).strftime('%m/%d') for i in range((end_dt - start_dt).days + 1)]
        counts = [date_map.get(d, 0) for d in dates]

        return JSONResponse({
            "todayOrder": today_order,
            "unpaidOrder": unpaid_order,
            "unshippedOrder": unshipped_order,
            "totalSales": total_sales,
            "orderChart": {
                "dates": dates,
                "counts": counts
            }
        })
    except Exception as e:
        print("❌ 儀表板統計 API 錯誤：", e)
        return JSONResponse({"error": "無法取得儀表板統計資料"}, status_code=500)

@app.get("/api/orders/{order_id}")
async def get_order_by_id(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at
            FROM orders WHERE order_id=%s
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到訂單"}, status_code=404)
        order = {
            "order_id": row[0],
            "amount": row[1],
            "item_names": row[2],
            "status": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "paid_at": row[5].isoformat() if row[5] else None
        }
        return JSONResponse(order)
    except Exception as e:
        print(f"❌ 查詢單一訂單錯誤：{e}")
        return JSONResponse({"error": "查詢訂單失敗"}, status_code=500)

@app.get("/api/orders/{order_id}/shipment")
async def get_order_shipment(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT shipment_id, order_id, recipient_name, address, status, created_at
            FROM shipments WHERE order_id=%s
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({})
        shipment = {
            "shipment_id": row[0],
            "order_id": row[1],
            "recipient_name": row[2],
            "address": row[3],
            "status": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        }
        return JSONResponse(shipment)
    except Exception as e:
        print(f"❌ 查詢出貨單錯誤：{e}")
        return JSONResponse({"error": "查詢出貨單失敗"}, status_code=500)

@app.post("/api/orders/{order_id}/mark-picked-up")
async def mark_picked_up(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        # 先檢查出貨單狀態是否為已到店，並確認是否為該客戶的訂單
        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'arrived':
            return JSONResponse({"error": "只有已到店狀態才能確認取貨"}, status_code=400)
        
        # 更新狀態為 'picked_up' 並記錄取貨時間
        cursor.execute("UPDATE shipments SET status='picked_up', picked_up_at = NOW() WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "狀態已更新為已取貨"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 確認取貨錯誤：{e}")
        return JSONResponse({"error": "狀態更新失敗"}, status_code=500)

@app.post("/api/orders/{order_id}/complete")
async def complete_order(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'picked_up':
            return JSONResponse({"error": "只有已取貨狀態才能完成訂單"}, status_code=400)
        
        cursor.execute("UPDATE shipments SET status='completed' WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "訂單已完成"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 完成訂單錯誤：{e}")
        return JSONResponse({"error": "訂單完成失敗"}, status_code=500)

@app.post("/api/orders/{order_id}/return")
async def request_return(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'picked_up':
            return JSONResponse({"error": "只有已取貨狀態才能申請退貨"}, status_code=400)
        
        # 更新狀態為 'returned_pending'，表示退貨申請中
        cursor.execute("UPDATE shipments SET status='returned_pending' WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "已成功申請退貨，等待管理員處理。"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 申請退貨錯誤：{e}")
        return JSONResponse({"error": "申請退貨失敗"}, status_code=500)

@app.post("/api/admin/auto_complete_shipments")
async def auto_complete_shipments(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            UPDATE shipments
            SET status = 'completed'
            WHERE status = 'shipped'
              AND delivered_at IS NOT NULL
              AND delivered_at < NOW() - INTERVAL '7 days'
            RETURNING order_id;
        """)
        updated = cursor.fetchall()
        cursor.connection.commit()
        return {"message": f"自動完成 {len(updated)} 筆出貨單", "order_ids": [row[0] for row in updated]}
    except Exception as e:
        print(f"❌ 自動完成出貨單錯誤：{e}")
        return {"error": "自動完成失敗"}

class OrderIdRequest(BaseModel):
    order_id: str

@app.post("/api/admin/mock_delivered")
async def mock_delivered(
    req: OrderIdRequest,
    auth=Depends(verify_admin_jwt),
    cursor=Depends(get_db_cursor)
):
    order_id = req.order_id
    try:
        # 先檢查訂單狀態是否為已出貨
        cursor.execute("SELECT status FROM shipments WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": "找不到出貨單"}
        if row[0] != 'shipped':
            return {"error": "只有已出貨狀態才能模擬到店"}
        # 同時更新 delivered_at 與 status
        cursor.execute("""
            UPDATE shipments 
            SET delivered_at = NOW(), status = 'arrived'
            WHERE order_id = %s
        """, (order_id,))
        cursor.connection.commit()
        return {"message": f"已模擬到店，order_id: {order_id}"}
    except Exception as e:
        print(f"❌ 模擬到店錯誤：{e}")
        return {"error": "模擬到店失敗"}

@app.post("/api/orders/{order_id}/set-return-logistics")
async def set_return_logistics(order_id: str, request: Request, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        data = await request.json()
        return_store_name = data.get("return_store_name")

        if not return_store_name:
            return JSONResponse({"error": "請提供 7-11 門市名稱！"}, status_code=400)

        # 檢查出貨單狀態是否為 'returned_pending'，並確認是否為該客戶的訂單
        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'returned_pending':
            return JSONResponse({"error": "只有退貨申請中的訂單才能設定退貨物流"}, status_code=400)

        # 生成一個模擬的退貨物流編號
        return_tracking_number = f"711-{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

        # 更新出貨單資料，新增 7-11 門市名稱和物流編號
        cursor.execute("""
            UPDATE shipments
            SET return_store_name = %s, return_tracking_number = %s
            WHERE order_id = %s
        """, (return_store_name, return_tracking_number, order_id))
        cursor.connection.commit()

        return JSONResponse({"message": "7-11 退貨物流已設定成功！", "tracking_number": return_tracking_number})

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 設定 7-11 退貨物流錯誤：{e}")
        return JSONResponse({"error": "設定 7-11 退貨物流失敗！"}, status_code=500)