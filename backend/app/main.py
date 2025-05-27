from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import requests, hmac, hashlib, base64, time, json
import os

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
        # 從前端拿到 JSON
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

        nonce = str(int(time.time()))
        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": LINE_PAY_CHANNEL_ID,
            "X-LINE-Authorization-Nonce": nonce,
        }

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

        # 🔥 產生 JSON 壓縮字串，確保完全相同
        body_str = json.dumps(body_dict, separators=(',', ':'))

        # 🔥 用 body_str 產生簽名
        signature = hmac.new(
            LINE_PAY_CHANNEL_SECRET.encode('utf-8'),
            body_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        headers['X-LINE-Authorization'] = base64.b64encode(signature).decode('utf-8')

        # 🔥 直接送出這個 body_str，避免 JSON 自動縮排導致簽名不一致
        res = requests.post(
            f"{LINE_PAY_BASE_URL}/v3/payments/request",
            headers=headers,
            data=body_str  # 注意：用 data（不是 json=）
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