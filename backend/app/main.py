# backend/app/main.py
from fastapi import FastAPI, Request
from flask import Flask, render_template_string, request as flask_request
from threading import Thread
import uvicorn
import requests, hmac, hashlib, base64, time, json

# 建立 FastAPI 與 Flask app
fastapi_app = FastAPI()
flask_app = Flask(__name__)

# === LINE Pay 設定 ===
LINE_PAY_CHANNEL_ID = "2006462420"
LINE_PAY_CHANNEL_SECRET = "8c832c018d09a8be1738b32a3be1ee0a"
LINE_PAY_BASE_URL = "https://sandbox-api-pay.line.me"
YOUR_DOMAIN = "https://shop.wvwwcw.xyz"
# === FastAPI API ===
@fastapi_app.get("/api/health")
def health_check():
    return {"status": "ok"}

@fastapi_app.get("/api/products")
def get_products():
    return [{"id": 1, "name": "UNIQLO 外套", "price": 2990}]

# === Flask 前台頁面 ===
@flask_app.route("/")
def index():
    return render_template_string("""
        <h1>歡迎來到日本代購</h1>
        <p>UNIQLO 外套 - ¥2990</p>
        <a href="/pay"><button style='background-color:#00c300;color:white;padding:10px 20px;'>LINE Pay 支付</button></a>
    """)

@flask_app.route("/pay")
def pay():
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

    # 簽名
    signature = hmac.new(
        LINE_PAY_CHANNEL_SECRET.encode('utf-8'),
        json.dumps(body, separators=(',', ':')).encode('utf-8'),
        hashlib.sha256
    ).digest()
    headers['X-LINE-Authorization'] = base64.b64encode(signature).decode('utf-8')

    res = requests.post(f"{LINE_PAY_BASE_URL}/v3/payments/request", headers=headers, json=body)
    res_data = res.json()

    if "info" in res_data:
        return flask_request.redirect(res_data["info"]["paymentUrl"]["web"])
    else:
        return render_template_string(f"<h2>❌ 發起付款失敗</h2><pre>{json.dumps(res_data, indent=2)}</pre>")

@flask_app.route("/pay/confirm")
def pay_confirm_page():
    transaction_id = flask_request.args.get("transactionId")
    if not transaction_id:
        return render_template_string("<h2>❌ 缺少交易參數</h2>")

    headers = {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": LINE_PAY_CHANNEL_ID,
        "X-LINE-Authorization-Nonce": str(int(time.time())),
    }
    body = {"amount": 100, "currency": "TWD"}

    signature = hmac.new(
        LINE_PAY_CHANNEL_SECRET.encode("utf-8"),
        json.dumps(body, separators=(',', ':')).encode("utf-8"),
        hashlib.sha256
    ).digest()
    headers["X-LINE-Authorization"] = base64.b64encode(signature).decode("utf-8")

    res = requests.post(f"{LINE_PAY_BASE_URL}/v3/payments/{transaction_id}/confirm", headers=headers, json=body)
    res_data = res.json()

    if res_data.get("returnCode") == "0000":
        return render_template_string("<h2>✅ 支付成功，感謝購買！</h2>")
    else:
        return render_template_string(f"<h2>❌ 確認付款失敗</h2><pre>{json.dumps(res_data, indent=2)}</pre>")

@flask_app.route("/pay/cancel")
def pay_cancel_page():
    return render_template_string("<h2>❌ 已取消付款，歡迎再來。</h2>")

# === 同時啟動 FastAPI 與 Flask ===
def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
