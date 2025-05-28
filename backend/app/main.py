from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv
from datetime import datetime
import random
import uvicorn
import hashlib
import urllib.parse
import os
import uuid
import time
import psycopg2

load_dotenv()
app = FastAPI()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.wvwwcw.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 綠界測試環境設定
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID") 
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY")        
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
ECPAY_API_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

# PostgreSQL 連線參數
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = "5432"

# 產生 CheckMacValue
def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&"
    encode_str += '&'.join([f"{k}={v}" for k, v in sorted_params])
    encode_str += f"&HashIV={hash_iv}"
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
        if not products:
            return JSONResponse({"error": "❌ 缺少商品資料"}, status_code=400)

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d%H%M%S")
        serial_number = f"{random.randint(0, 999999):06d}"
        order_id = f"{date_time_str}{serial_number}"
        #print(order_id)

        amount = sum(item["price"] * item["quantity"] for item in products)
        item_names = "#".join([f"{item['name']} x {item['quantity']}" for item in products])
        trade_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # ✅ 寫入資料庫，狀態為 pending
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, amount, item_names, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, amount, item_names, 'pending', trade_date))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 訂單已寫入資料庫！")

        # ✅ 組合綠界參數
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

        return JSONResponse({
            "ecpay_url": ECPAY_API_URL,
            "params": params
        })

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

        status = "success" if rtn_code == "1" else "fail"

        # ✅ 更新資料庫訂單狀態與付款時間
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders SET status=%s, paid_at=%s WHERE order_id=%s
        """, (status, payment_date, order_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ 訂單 {order_id} 狀態已更新為：{status}")

        # 綠界要求一定要回傳 "1|OK"
        return HTMLResponse("1|OK")

    except Exception as e:
        print("❌ /ecpay/notify 發生錯誤：", str(e))
        return HTMLResponse("0|Error")

@app.get("/admin/orders")
async def admin_get_orders(auth=Depends(verify_basic_auth)):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_id, item_names, amount, status, created_at, paid_at FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    orders = [{"id": r[0], "order_id": r[1], "item_names": r[2], "amount": r[3], "status": r[4], "created_at": str(r[5]), "paid_at": str(r[6]) if r[6] else None} for r in rows]
    return JSONResponse(orders)

@app.post("/admin/update_order_status")
async def admin_update_status(request: Request, auth=Depends(verify_basic_auth)):
    data = await request.json()
    order_id = data.get("order_id")
    new_status = data.get("status")
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return JSONResponse({"message": "狀態已更新！"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
