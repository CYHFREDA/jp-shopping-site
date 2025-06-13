from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from db.db import get_db_cursor, get_sync_db_cursor_and_conn, global_pool
from datetime import datetime, timedelta
import random
import hashlib
import urllib.parse
import os
import jwt
from apscheduler.schedulers.background import BackgroundScheduler

router = APIRouter()
scheduler = BackgroundScheduler()
scheduler.start()

#綠界測試環境設定
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
ECPAY_API_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

# 檢查未收到回覆的訂單
def check_pending_orders():
    conn = None
    cursor = None
    try:
        conn, cursor = get_sync_db_cursor_and_conn()
        # 查找建立超過 20 分鐘但仍為 pending 的訂單
        cursor.execute("""
            UPDATE orders 
            SET status = 'fail',
                payment_message = '付款逾時，未收到付款結果'
            WHERE status = 'pending'
            AND created_at < NOW() - INTERVAL '20 minutes'
            RETURNING order_id
        """)
        updated_orders = cursor.fetchall()
        conn.commit()
        
        if updated_orders:
            print(f"✅ 已將以下逾時訂單更新為失敗狀態：{[order['order_id'] for order in updated_orders]}")
    except Exception as e:
        print(f"❌ 檢查逾時訂單時發生錯誤：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            global_pool.putconn(conn)

# 每 5 分鐘執行一次檢查
scheduler.add_job(check_pending_orders, 'interval', minutes=5)

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
            "OrderResultURL": f"{YOUR_DOMAIN}/pay/result",  # 新增此參數
            "PlatformID": ECPAY_MERCHANT_ID
        }
        params["CheckMacValue"] = generate_check_mac_value(params, ECPAY_HASH_KEY, ECPAY_HASH_IV)
        print("✅ 送出的參數：", params)

        return JSONResponse({"ecpay_url": ECPAY_API_URL, "params": params, "order_id": order_id})

    except Exception as e:
        print("❌ 後端錯誤：", str(e))
        return JSONResponse({"error": "後端發生錯誤"}, status_code=500)

# 處理綠界回調通知
@router.post("/ecpay/notify")
async def handle_ecpay_notification(request: Request, cursor=Depends(get_db_cursor)):
    try:
        # 接收綠界的回調資料
        form_data = await request.form()
        print("✅ 收到綠界回調：", dict(form_data))

        # 取得必要參數
        merchant_trade_no = form_data.get("MerchantTradeNo")
        rtn_code = form_data.get("RtnCode")
        rtn_msg = form_data.get("RtnMsg")
        check_mac_value = form_data.get("CheckMacValue")
        payment_date = form_data.get("PaymentDate")

        # 驗證資料完整性
        if not all([merchant_trade_no, rtn_code, rtn_msg, check_mac_value]):
            print("❌ 回調資料不完整")
            return JSONResponse({"error": "回調資料不完整"}, status_code=400)

        # 更新訂單狀態
        if rtn_code == "1":  # 付款成功
            new_status = "success"
        elif rtn_code in ["10300066", "385"]:  # 付款等待中
            new_status = "pending"
            rtn_msg = "交易處理中，等待銀行回覆"
        elif rtn_code in ["10100248", "10100252", "10100254", "10100251"]:  # 信用卡常見錯誤
            new_status = "fail"
            error_messages = {
                "10100248": "信用卡交易被拒絕",
                "10100252": "信用卡額度不足",
                "10100254": "信用卡交易失敗，請確認交易限制",
                "10100251": "信用卡過期"
            }
            rtn_msg = error_messages.get(rtn_code, rtn_msg)
        else:  # 其他所有錯誤
            new_status = "fail"

        cursor.execute("""
            UPDATE orders
            SET status = %s,
                payment_message = %s,
                paid_at = CASE WHEN %s = 'success' THEN %s::timestamp ELSE NULL END,
                updated_at = NOW()
            WHERE order_id = %s
            RETURNING order_id, status
        """, (new_status, rtn_msg, new_status, payment_date, merchant_trade_no))
        
        updated_order = cursor.fetchone()
        cursor.connection.commit()

        if not updated_order:
            print(f"❌ 找不到訂單：{merchant_trade_no}")
            return JSONResponse({"error": "找不到訂單"}, status_code=404)

        print(f"✅ 訂單 {merchant_trade_no} 已更新為 {new_status}，原因：{rtn_msg}")

        # 如果付款成功，建立出貨單
        if new_status == "success":
            try:
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
                    SELECT 
                        order_id,
                        recipient_name,
                        delivery_type,
                        store_id,
                        store_name,
                        cvs_type,
                        address,
                        'pending',
                        NOW()
                    FROM orders
                    WHERE order_id = %s
                """, (merchant_trade_no,))
                cursor.connection.commit()
                print(f"✅ 已為訂單 {merchant_trade_no} 建立出貨單")
            except Exception as e:
                print(f"❌ 建立出貨單時發生錯誤：{str(e)}")
                # 不中斷處理，因為訂單狀態已更新成功

        return "1|OK"

    except Exception as e:
        print(f"❌ 處理綠界回調時發生錯誤：{str(e)}")
        return JSONResponse({"error": "處理回調時發生錯誤"}, status_code=500)