from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import requests
import hashlib
import urllib.parse
import os
import uuid
import datetime
import time

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

# 產生檢查碼
def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&"
    encode_str += '&'.join([f"{k}={v}" for k, v in sorted_params])
    encode_str += f"&HashIV={hash_iv}"

    # URL encode 並轉成小寫
    encode_str = urllib.parse.quote_plus(encode_str).lower()

    # SHA256 加密
    sha256 = hashlib.sha256()
    sha256.update(encode_str.encode('utf-8'))
    check_mac_value = sha256.hexdigest().upper()

    return check_mac_value

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/pay")
async def pay(request: Request):
    try:
        data = await request.json()
        print("收到前端資料：", data)

        products = data.get("products")
        if not products:
            return JSONResponse({"error": "缺少商品資料"}, status_code=400)

        # 產生訂單編號
        order_id = f"ORDER{int(time.time())}"
        print("訂單編號：", order_id)

        # 計算總金額
        amount = sum(item["price"] * item["quantity"] for item in products)
        print("總金額：", amount)

        # 商品名稱
        item_names = "#".join([f"{item['name']} x {item['quantity']}" for item in products])

        # 付款時間
        trade_date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # 綠界必填參數
        params = {
            "MerchantID": ECPAY_MERCHANT_ID,
            "MerchantTradeNo": order_id,
            "MerchantTradeDate": trade_date,
            "PaymentType": "aio",
            "TotalAmount": amount,
            "TradeDesc": "綠界平台商測試",
            "ItemName": item_names,
            "ReturnURL": f"{YOUR_DOMAIN}/ecpay/notify",   # 綠界會呼叫此 URL 通知付款結果
            "ChoosePayment": "Credit",
            "ClientBackURL": f"{YOUR_DOMAIN}/pay/return",
            "PlatformID": ECPAY_MERCHANT_ID   # 平台商模式必填：填入「特店編號」
        }

        # 產生檢查碼
        params["CheckMacValue"] = generate_check_mac_value(params, ECPAY_HASH_KEY, ECPAY_HASH_IV)

        print("送出的參數：", params)

        # 這邊後端直接回傳參數，讓前端產生 <form> 並自動 submit
        return JSONResponse({
            "ecpay_url": ECPAY_API_URL,
            "params": params
        })

    except Exception as e:
        print("❌ 後端錯誤：", str(e))
        return JSONResponse({"error": "後端發生錯誤"}, status_code=500)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)