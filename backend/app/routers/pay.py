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
    check_mac = hashlib.md5(encode_str.encode('utf-8')).hexdigest().upper()
    return check_mac

# 建立訂單並取得綠界付款參數
@router.post("/pay")
async def pay(request: Request, cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        print("✅ 收到前端資料：", data)

        products = data.get("products")
        customer_id = data.get("customer_id")
        delivery_type = data.get("delivery_type", "home")  # 預設為宅配
        store_id = data.get("store_id")      # 門市代號
        store_name = data.get("store_name")  # 門市名稱
        cvs_type = data.get("cvs_type")      # 超商類型
        address = data.get("address")         # 地址
        recipient_name = data.get("recipient_name")  # 收件人姓名
        recipient_phone = data.get("recipient_phone")  # 收件人電話

        if not products:
            return JSONResponse({"error": "❌ 缺少商品資料"}, status_code=400)
            
        if not customer_id:
            print("⚠️ 未收到 customer_id，訂單將不會關聯到客戶。")

        # 驗證配送資訊
        if delivery_type == "cvs":
            if not all([store_id, store_name, cvs_type]):
                return JSONResponse({"error": "❌ 請選擇取貨門市"}, status_code=400)
        else:  # delivery_type == "home"
            if not address:
                return JSONResponse({"error": "❌ 請填寫配送地址"}, status_code=400)

        if not recipient_name or not recipient_phone:
            return JSONResponse({"error": "❌ 請填寫收件人資訊"}, status_code=400)

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d%H%M%S")
        serial_number = f"{random.randint(0, 999999):06d}"
        order_id = f"{date_time_str}{serial_number}"

        amount = sum(item["price"] * item["quantity"] for item in products)
        item_names = "#".join([f"{item['name']} x {item['quantity']}" for item in products])
        trade_date = now.strftime("%Y/%m/%d %H:%M:%S")

        # 超商類型代碼轉換
        cvs_type_mapping = {
            "全家": "FAMI",
            "7-11": "UNIMART",
            "萊爾富": "HILIFE",
            "OK": "OKMART",
            # 如果前端直接傳綠界代碼，保持原樣
            "FAMI": "FAMI",
            "UNIMART": "UNIMART",
            "HILIFE": "HILIFE",
            "OKMART": "OKMART"
        }
        
        # 轉換超商類型代碼（如果是超商取貨）
        ecpay_cvs_type = None
        if delivery_type == "cvs":
            ecpay_cvs_type = cvs_type_mapping.get(cvs_type)
            if not ecpay_cvs_type:
                return JSONResponse({"error": f"不支援的超商類型：{cvs_type}"}, status_code=400)

        #寫入資料庫
        cursor.execute("""
            INSERT INTO orders (
                order_id, amount, item_names, status, created_at, customer_id,
                delivery_type, store_id, store_name, cvs_type, address,
                recipient_name, recipient_phone
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id, amount, item_names, 'pending', trade_date, customer_id,
            delivery_type, store_id, store_name, ecpay_cvs_type, address,
            recipient_name, recipient_phone
        ))
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
            # 先查訂單的資訊
            cursor.execute("""
                SELECT customer_id, delivery_type, store_id, store_name, cvs_type,
                       address, recipient_name, recipient_phone
                FROM orders 
                WHERE order_id = %s
            """, (order_id,))
            row = cursor.fetchone()
            if not row:
                print(f"❌ 找不到訂單資訊：{order_id}")
                return HTMLResponse("0|Error")

            delivery_type = row["delivery_type"]
            store_id = row["store_id"]
            store_name = row["store_name"]
            cvs_type = row["cvs_type"]
            address = row["address"]
            recipient_name = row["recipient_name"]

            cursor.execute("""
                INSERT INTO shipments (
                    order_id, 
                    recipient_name,
                    delivery_type,
                    store_id,
                    store_name,
                    cvs_type,
                    address,
                    status, 
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                order_id, 
                recipient_name,
                delivery_type,
                store_id,
                store_name,
                cvs_type,
                address,
                'pending'
            ))
            cursor.connection.commit()
            print(f"✅ 出貨單已自動建立，order_id: {order_id}, recipient: {recipient_name}, delivery_type: {delivery_type}")

        print(f"✅ 訂單 {order_id} 狀態已更新為：{status_}")

        return HTMLResponse("1|OK")
    except Exception as e:
        print("❌ /ecpay/notify 發生錯誤：", str(e))
        return HTMLResponse("0|Error")