from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import requests, hmac, hashlib, base64, time, json
import os
import uuid

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

LINE_PAY_CHANNEL_ID = os.getenv("LINE_PAY_CHANNEL_ID")
LINE_PAY_CHANNEL_SECRET = os.getenv("LINE_PAY_CHANNEL_SECRET")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
LINE_PAY_BASE_URL = os.getenv("LINE_PAY_BASE_URL")

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
            print("❌ 缺少商品資料！")
            return JSONResponse({"error": "缺少商品資料"}, status_code=400)

        print("收到的商品列表：", products)

        # 計算總金額
        amount = sum(item["price"] * item["quantity"] for item in products)
        print("計算總金額：", amount)

        nonce = str(uuid.uuid4())
        order_id = f"ORDER-{int(time.time())}"
        body_dict = {
            "amount": amount,
            "currency": "TWD",
            "orderId": order_id,
            "packages": [{
                "id": "package-1",
                "amount": amount,
                "name": "代購商品",
                "products": products
            }],
            "redirectUrls": {
                "confirmUrl": f"{YOUR_DOMAIN}/pay/confirm",
                "cancelUrl": f"{YOUR_DOMAIN}/pay/cancel"
            }
        }

        # ✅ 產生沒有多餘空白的 JSON
        body_str = json.dumps(body_dict, separators=(',', ':'))

        # ✅ LINE Pay 文件要求簽名串接方式
        message = nonce + body_str + LINE_PAY_CHANNEL_ID

        signature = hmac.new(
            LINE_PAY_CHANNEL_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()

        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": LINE_PAY_CHANNEL_ID,
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": base64.b64encode(signature).decode('utf-8')
        }

        # ✅ 送出
        res = requests.post(
            f"{LINE_PAY_BASE_URL}/v3/payments/request",
            headers=headers,
            data=body_str
        )

        res_data = res.json()
        print("LINE Pay 回應：", res_data)

        if "info" in res_data:
            return JSONResponse({"url": res_data["info"]["paymentUrl"]["web"]})
        else:
            return JSONResponse({"error": res_data}, status_code=400)

    except Exception as e:
        print("❌ 後端錯誤：", str(e))
        return JSONResponse({"error": "後端發生錯誤"}, status_code=500)