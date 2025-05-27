from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import requests, hmac, hashlib, base64, time, json
import os

load_dotenv() 
app = FastAPI()

# CORS 設定（如果你前端跑在不同來源要允許）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.wvwwcw.xyz"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LINE Pay 設定
LINE_PAY_CHANNEL_ID = os.getenv("LINE_PAY_CHANNEL_ID")
LINE_PAY_CHANNEL_SECRET = os.getenv("LINE_PAY_CHANNEL_SECRET")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN")
LINE_PAY_BASE_URL = os.getenv("LINE_PAY_BASE_URL")

@app.post("/pay")
async def pay():
    nonce = str(int(time.time()))
    headers = {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": LINE_PAY_CHANNEL_ID,
        "X-LINE-Authorization-Nonce": nonce,
    }

    order_id = f"ORDER-{int(time.time())}"
    body = {
        "amount": 100,
        "currency": "TWD",
        "orderId": order_id,
        "packages": [{
            "id": "package-1",
            "amount": 100,
            "name": "代購商品",
            "products": [{"name": "UNIQLO 外套", "quantity": 1, "price": 100}]
        }],
        "redirectUrls": {
            "confirmUrl": f"{YOUR_DOMAIN}/pay/confirm",
            "cancelUrl": f"{YOUR_DOMAIN}/pay/cancel"
        }
    }

    signature = hmac.new(
        LINE_PAY_CHANNEL_SECRET.encode('utf-8'),
        json.dumps(body, separators=(',', ':')).encode('utf-8'),
        hashlib.sha256
    ).digest()
    headers['X-LINE-Authorization'] = base64.b64encode(signature).decode('utf-8')

    res = requests.post(f"{LINE_PAY_BASE_URL}/v3/payments/request", headers=headers, json=body)
    res_data = res.json()

    if "info" in res_data:
        return JSONResponse({"url": res_data["info"]["paymentUrl"]["web"]})
    else:
        return JSONResponse({"error": res_data}, status_code=400)
