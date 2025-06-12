from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from db.db import get_db_cursor
from datetime import datetime
import random
import hashlib
import urllib.parse
import os
import jwt

router = APIRouter()

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

# 建立訂單並取得綠界付款參數
@router.post("/pay")
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

# 接收綠界付款結果
@router.post("/ecpay/notify")
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
