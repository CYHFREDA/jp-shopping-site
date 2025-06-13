from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from db.db import get_db_cursor
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
    try:
        with get_db_cursor() as cursor:
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
            cursor.connection.commit()
            
            if updated_orders:
                print(f"✅ 已將以下逾時訂單更新為失敗狀態：{[order['order_id'] for order in updated_orders]}")
    except Exception as e:
        print(f"❌ 檢查逾時訂單時發生錯誤：{str(e)}")

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

# 接收綠界付款結果
@router.post("/ecpay/notify")
async def ecpay_notify(request: Request, cursor=Depends(get_db_cursor)):
    try:
        data = await request.form()
        print("✅ 收到綠界通知：", data)

        order_id = data.get("MerchantTradeNo")
        rtn_code = data.get("RtnCode")
        rtn_msg = data.get("RtnMsg", "")  # 取得交易訊息
        payment_date = data.get("PaymentDate", None)

        # 根據 RtnCode 判斷狀態
        # 成功狀態
        if rtn_code == "1":
            status_ = "success"  # 交易成功
        # 待處理狀態
        elif rtn_code in ["10300066", "385"]:
            status_ = "pending"  # 交易付款結果待確認中
        # 信用卡失敗狀態
        elif rtn_code in [
            "10100248",  # 拒絕交易
            "10100252",  # 額度不足
            "10100254",  # 交易失敗，請確認交易限制
            "10100251",  # 卡片過期
            "10100255",  # 報失卡
            "10100256",  # 被盜用卡
            "500",       # 一般交易失敗
            "501",       # 日期錯誤
            "502",       # 信用卡號錯誤
            "503",       # 新帳戶資訊
            "504",       # 不要重試
            "505",       # 請重試
            "506",       # 檢查帳號錯誤
            "507",       # 新帳戶資訊可用
            "508",       # 稍後重試
            "509",       # 過期卡片，取得新的到期日後重試
            "510",       # 不要重試，安全性違規
            "511",       # 取得新的到期日後重試
            "512",       # 不允許的服務
            "513",       # 不允許的交易
            "514",       # 安全性違規，不要重試
            "515",       # 請重試
            "516",       # 請重試
            "517",       # CVV2 拒絕
            "518",       # 無效的帳戶/日期或銷售日期在未來
            "519",       # 無效的有效日期
            "520",       # 交易被拒絕
            "521",       # 輸入較小的金額
            "522",       # 現金回饋大於交易總金額
            "523",       # 加密盒離線
            "524",       # 轉帳交易無法使用
            "525",       # 無法連接到發卡行
            "526",       # 未定義的卡片
            "527",       # 商店編號/終端機編號無效
            "528",       # 超過提款限額
            "529",       # 重複交易違反頻率限制
            "530",       # 加密問題
            "531",       # 需要 3DS 驗證
            "532",       # PIN 相關錯誤
            "540",       # 編輯錯誤
            "541",       # 無儲蓄帳戶
            "542",       # PIN 處理錯誤
            "550",       # 無效的車輛
            "551",       # 無效的駕駛
            "552",       # 無效的產品
            "553",       # 超過產品類別的交易總額限制
            "554",       # 超過每日限額
            "555",       # 無效的日期/時間
            "556",       # 超過數量
            "557",       # 無效的提示輸入
            "558",       # 無效的磁軌 2 資料
            "559",       # ID 問題
            "560",       # 無效的里程數
            "561",       # 無效的限制代碼
            "562",       # 不允許加油站付款
            "563",       # 超過燃料限額
            "564",       # 超過現金限額
            "565",       # 燃料價格錯誤
            "566",       # 需要 Y 或 N
            "567",       # 超過維修限額
            "568",       # 超過添加劑限額
            "569",       # 無效的使用者
            "721",       # 無效的郵遞區號
            "722",       # 欄位中的值無效
            "723",       # 需要駕照或身分證
            "724",       # 轉介 - 未啟用
            "726",       # 無法找到記錄
            "727",       # 轉介 - 請致電授權
            "728",       # 轉介 - 跳過追蹤資訊
            "729",       # 檔案中有硬性負面資訊
            "731",       # 拒絕遺失/被盜支票
            "771",       # 金額太大
            "772",       # 重複的退款
            "773",       # 交易失敗
            "774",       # 重複的沖正
            "775",       # 子系統無法使用
            "776",       # 重複的完成
            "782",       # 計數超過限制
            "790",       # 請勿重新提交相同的交易
            "791",       # 停止重複付款請求
            "792",       # 請見服務人員
            "801",       # 超過商品限額
            "802",       # 需要壓印卡片
            "803",       # 不在檔案中
            "804",       # 僅限燃料
            "805",       # 速度超過限制
            "806",       # 需要授權 ID
            "807",       # 超過非燃料限額
            "808",       # 無效的位置
            "809",       # 超過卡片速度計數
            "810",       # 超過卡片速度金額
            "811",       # 超過發卡行速度計數
            "812",       # 超過發卡行速度金額
            "813",       # 超過商店每日速度計數
            "814",       # 超過商店每日速度金額
            "815",       # 超過商店每日速度兩者
            "816",       # 超過商店產品速度金額
            "817",       # 超過商店產品速度計數
            "818",       # 超過商店產品速度兩者
            "819",       # 超過連鎖店每日速度計數
            "820",       # 超過連鎖店每日速度金額
            "821",       # 超過連鎖店每日速度兩者
            "822",       # 超過連鎖店產品速度計數
            "823",       # 超過連鎖店產品速度兩者
            "824",       # 超過連鎖店產品速度金額
            "825",       # 連鎖店商店沒有連鎖店 ID
            "826",       # 需要簽名
            "902",       # 無效的交易
            "904",       # 格式錯誤
            "906",       # 系統錯誤
            "907",       # 發卡行或交換機無法運作
            "908",       # 找不到交易目的地
            "909",       # 系統故障
            "911",       # 發卡行超時
            "913",       # 重複的交易
            "914",       # 找不到原始授權
            "915",       # 不支援超時沖正
            "920",       # 安全性硬體/軟體錯誤
            "921",       # 安全性硬體/軟體錯誤
            "923",       # 請求處理中
            "924",       # 限額檢查失敗
            "940",       # 錯誤
            "941",       # 無效的發卡行
            "942",       # 客戶取消
            "944",       # 無效的回應
            "950",       # 違反商業安排
            "954",       # CCV 失敗
            "958",       # CCV2 失敗
            "959",       # CVV 失敗
            "963"        # 收單通道無法使用
        ]:
            status_ = "fail"  # 交易失敗（信用卡相關問題）
        # 系統錯誤狀態
        elif rtn_code in ["920", "921", "923", "924", "940", "906", "907", "908", "909"]:
            status_ = "error"  # 系統錯誤，需要重試
        # 其他所有狀態
        else:
            status_ = "fail"  # 其他失敗情況

        # 更新訂單狀態和訊息
        cursor.execute(
            "UPDATE orders SET status=%s, paid_at=%s, payment_message=%s WHERE order_id=%s", 
            (status_, payment_date, rtn_msg, order_id)
        )
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

        print(f"✅ 訂單 {order_id} 狀態已更新為：{status_}，訊息：{rtn_msg}")

        return HTMLResponse("1|OK")
    except Exception as e:
        print("❌ /ecpay/notify 發生錯誤：", str(e))
        return HTMLResponse("0|Error")