from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from psycopg2 import errors
from datetime import datetime
import random
import uvicorn
import hashlib
import urllib.parse
import os
import psycopg2
import bcrypt
import psycopg2.extras
import jwt

load_dotenv()
app = FastAPI()

# JWT 設定
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 從環境變數讀取密鑰
JWT_ALGORITHM = "HS256"

#Basic Auth 設定
security = HTTPBasic()
def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    print("🟡 username:", repr(credentials.username))
    print("🟡 password:", repr(credentials.password))
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM admin_users WHERE username=%s", (credentials.username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        print("🛑 找不到使用者")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    hashed_password = row[0]
    print("🟡 hashed_password:", hashed_password)
    
    if not bcrypt.checkpw(credentials.password.strip().encode('utf-8'), hashed_password.encode('utf-8')):
        print("🛑 密碼驗證失敗")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    print("✅ 密碼驗證成功")
    return True


#CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.wvwwcw.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#綠界測試環境設定
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
ECPAY_API_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

#PostgreSQL 連線參數
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = "5432"

#共用資料庫連線
def get_db_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# 產生 CheckMacValue
def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&" + '&'.join([f"{k}={v}" for k, v in sorted_params]) + f"&HashIV={hash_iv}"
    encode_str = urllib.parse.quote_plus(encode_str).lower()
    sha256 = hashlib.sha256()
    sha256.update(encode_str.encode('utf-8'))
    return sha256.hexdigest().upper()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/pay")
async def pay(request: Request):
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
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, amount, item_names, status, created_at, customer_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, amount, item_names, 'pending', trade_date, customer_id))
        conn.commit()
        cursor.close()
        conn.close()
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
async def ecpay_notify(request: Request):
    try:
        data = await request.form()
        print("✅ 收到綠界通知：", data)

        order_id = data.get("MerchantTradeNo")
        rtn_code = data.get("RtnCode")
        payment_date = data.get("PaymentDate", None)
        status_ = "success" if rtn_code == "1" else "fail"

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status=%s, paid_at=%s WHERE order_id=%s", (status_, payment_date, order_id))
        conn.commit()

        # 🟢 新增出貨資料（如果訂單是成功付款）
        if status_ == "success":
            # 這裡假設收件人與地址等資料先隨便填，等人工在後台編輯，或者可以自己決定要不要從客戶資料表撈
            cursor.execute("""
                INSERT INTO shipments (order_id, recipient_name, address, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (order_id, '待填寫', '待填寫', 'pending'))
            conn.commit()
            print(f"✅ 出貨單已自動建立，order_id: {order_id}")

        cursor.close()
        conn.close()
        print(f"✅ 訂單 {order_id} 狀態已更新為：{status_}")

        return HTMLResponse("1|OK")
    except Exception as e:
        print("❌ /ecpay/notify 發生錯誤：", str(e))
        return HTMLResponse("0|Error")

@app.get("/orders/{order_id}/status")
async def get_order_status(order_id: str):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return JSONResponse({"order_id": order_id, "status": row[0]})
        else:
            return JSONResponse({"error": "Order not found"}, status_code=404)

    except Exception as e:
        print("❌ 後端查詢訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.get("/admin/orders")
async def admin_get_orders(auth=Depends(verify_basic_auth)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_id, item_names, amount, status, created_at, paid_at FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    orders = [{"id": r[0], "order_id": r[1], "item_names": r[2], "amount": r[3], "status": r[4], "created_at": str(r[5]), "paid_at": str(r[6]) if r[6] else None} for r in rows]
    return JSONResponse(orders)

@app.post("/admin/update_order_status")
async def update_order_status(request: Request, auth=Depends(verify_basic_auth)):
    try:
        data = await request.json()
        order_id = data.get("order_id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return JSONResponse({"error": "缺少必要參數"}, status_code=400)

        if new_status not in ["pending", "success", "fail"]:
            return JSONResponse({"error": "無效的訂單狀態"}, status_code=400)

        conn = get_db_conn()
        cursor = conn.cursor()
        
        # 檢查訂單是否存在
        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            return JSONResponse({"error": "找不到訂單"}, status_code=404)

        # 更新訂單狀態
        cursor.execute("""
            UPDATE orders 
            SET status=%s, 
                paid_at=CASE 
                    WHEN %s='success' THEN CURRENT_TIMESTAMP 
                    ELSE paid_at 
                END 
            WHERE order_id=%s
        """, (new_status, new_status, order_id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse({"message": "訂單狀態更新成功"})

    except Exception as e:
        print("❌ 更新訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "更新訂單狀態失敗"}, status_code=500)

# 取得所有商品
@app.get("/products")
async def get_products(query: str = ""):
    conn = get_db_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if query:
        # 模糊搜尋
        cursor.execute("""
            SELECT id, name, price, description, image_url, created_at, category
            FROM products
            WHERE name ILIKE %s
        """, (f"%{query}%",))
    else:
        # 回傳所有商品
        cursor.execute("""
            SELECT id, name, price, description, image_url, created_at, category
            FROM products
        """)
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

#後台新增商品
@app.post("/admin/products")
async def admin_add_product(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url", "")
    category = data.get("category", "")

    if not name or not price:
        return JSONResponse({"error": "❌ 商品名稱與價格為必填！"}, status_code=400)

    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, price, description, image_url, category)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, price, description, image_url, category))
        conn.commit()
        return JSONResponse({"message": "✅ 商品已新增"})
    except errors.StringDataRightTruncation as e:
        # 資料過長
        return JSONResponse({"error": "❌ 文字長度超過限制，請修改再送出！"}, status_code=400)
    except Exception as e:
        print("❌ 新增商品時出錯：", e)
        return JSONResponse({"error": "❌ 新增商品失敗，請稍後再試！"}, status_code=500)
    finally:
        cursor.close()
        conn.close()

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

#後台編輯商品
@app.put("/admin/products/{id}")
async def admin_update_product(id: int, request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url", "")
    category = data.get("category", "")

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name=%s, price=%s, description=%s, image_url=%s, category=%s
        WHERE id=%s
    """, (name, price, description, image_url, category, id))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "商品已更新"})

#後台刪除商品
@app.delete("/admin/products/{id}")
async def admin_delete_product(id: int, auth=Depends(verify_basic_auth)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "商品已刪除"})

#出貨管理（後台）
@app.get("/admin/shipments")
async def admin_get_shipments(auth=Depends(verify_basic_auth)):
    print("🚚 準備查詢出貨資料")
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT shipment_id, order_id, recipient_name, address, status, created_at FROM shipments ORDER BY created_at DESC")
        rows = cursor.fetchall()
        print("✅ 查詢結果：", rows)
    except Exception as e:
        print("❌ 出錯：", e)
    finally:
        cursor.close()
        conn.close()
    shipments = [{"shipment_id": r[0], "order_id": r[1], "recipient_name": r[2], "address": r[3], "status": r[4], "created_at": str(r[5])} for r in rows]
    return JSONResponse(shipments)

# 出貨管理（更新出貨單資料）
@app.post("/admin/update_shipment")
async def admin_update_shipment(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    shipment_id = data.get("shipment_id")
    recipient_name = data.get("recipient_name")
    address = data.get("address")
    status_ = data.get("status")

    if not shipment_id or not recipient_name or not address or not status_:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE shipments SET recipient_name=%s, address=%s, status=%s
        WHERE shipment_id=%s
    """, (recipient_name, address, status_, shipment_id))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "✅ 出貨資料已更新！"})

#客戶管理（後台）
@app.get("/admin/customers")
async def admin_get_customers(auth=Depends(verify_basic_auth)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, name, email, phone, address, created_at FROM customers ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
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

#客戶註冊（前台用）
@app.post("/customers/register")
async def customer_register(request: Request):
    data = await request.json()
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    if not (username and name and password):
        return JSONResponse({"error": "缺少必要欄位"}, status_code=400)

    # bcrypt 雜湊密碼
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (username, name, email, phone, password, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                      (username, name, email, phone, hashed_password))
        conn.commit()
        return JSONResponse({"message": "註冊成功"})
    except psycopg2.IntegrityError:
        return JSONResponse({"error": "使用者名稱已被使用"}, status_code=400)
    finally:
        cursor.close()
        conn.close()

#客戶登入（前台用）
@app.post("/customers/login")
async def customer_login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    conn = get_db_conn()
    cursor = conn.cursor()
    # 先撈出該 username 的 bcrypt 雜湊密碼
    cursor.execute("SELECT customer_id, name, password FROM customers WHERE username=%s", (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        hashed_password = row[2]
        # 用 bcrypt 驗證密碼是否相符
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return JSONResponse({"message": "登入成功", "customer_id": row[0], "name": row[1]})
    return JSONResponse({"error": "帳號或密碼錯誤"}, status_code=401)

#客戶重置密碼
@app.post("/admin/reset_customer_password")
async def admin_reset_customer_password(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    customer_id = data.get("customer_id")
    new_password = data.get("new_password")

    if not customer_id or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    # bcrypt 雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET password=%s WHERE customer_id=%s", (hashed_password, customer_id))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "✅ 密碼已重置（bcrypt 加密）"})

#編輯客戶資料
@app.post("/admin/update_customer")
async def admin_update_customer(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    customer_id = data.get("customer_id")
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address", "")
    if not customer_id or not name or not phone:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name=%s, phone=%s, address=%s
        WHERE customer_id=%s
    """, (name, phone, address, customer_id))

    conn.commit()
    cursor.close()
    conn.close()

    return JSONResponse({"message": "✅ 客戶資料已更新！"})

#新增管理員
@app.post("/admin/create_admin")
async def create_admin(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return JSONResponse({"message": "✅ 管理員已新增"})
    except psycopg2.IntegrityError:
        return JSONResponse({"error": "❌ 帳號已存在"}, status_code=400)
    finally:
        cursor.close()
        conn.close()

#顯示後台使用者
@app.get("/admin/admin_users")
async def admin_get_admin_users(auth=Depends(verify_basic_auth)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username, created_at FROM admin_users ORDER BY created_at")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"username": r[0], "created_at": str(r[1])} for r in rows]

#修改使用者密碼
@app.post("/admin/update_admin_password")
async def update_admin_password(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    username = data.get("username")
    new_password = data.get("new_password")
    if not username or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    
    # bcrypt 重新產生雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin_users SET password=%s WHERE username=%s", (hashed_password, username))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "✅ 密碼已更新！"})

@app.get("/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: int, request: Request):
    try:
        # 從請求頭中獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse({"error": "未授權訪問"}, status_code=401)
        
        token = auth_header.split(' ')[1]
        # 驗證 token 並獲取客戶 ID
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            token_customer_id = payload.get('customer_id')
            if not token_customer_id or int(token_customer_id) != customer_id:
                return JSONResponse({"error": "無權訪問此客戶的訂單"}, status_code=403)
        except jwt.InvalidTokenError:
            return JSONResponse({"error": "無效的認證令牌"}, status_code=401)

        conn = get_db_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at 
            FROM orders 
            WHERE customer_id=%s 
            ORDER BY created_at DESC
        """, (customer_id,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return JSONResponse(orders)

    except Exception as e:
        print(f"❌ 後端查詢客戶 {customer_id} 訂單錯誤：", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)