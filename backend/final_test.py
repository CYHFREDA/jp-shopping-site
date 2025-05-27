import json
import hmac
import hashlib
import base64
import uuid
import os

channel_id = "2006462420"
channel_secret = "8c832c018d09a8be1738b32a3be1ee0a"
confirm_url = "https://shop.wvwwcw.xyz/pay/confirm"
cancel_url = "https://shop.wvwwcw.xyz/pay/cancel"

# 組出 body dict
body_dict = {
    "amount": 100,
    "currency": "TWD",
    "orderId": "ORDER-123456",
    "packages": [{
        "id": "package-1",
        "amount": 100,
        "name": "代購商品",
        "products": [
            {
                "name": "測試商品",
                "quantity": 1,
                "price": 100
            }
        ]
    }],
    "redirectUrls": {
        "confirmUrl": confirm_url,
        "cancelUrl": cancel_url
    }
}

# 用相同 separators，確保和產生簽名用的一模一樣
body_str = json.dumps(body_dict, separators=(',', ':'), ensure_ascii=False)

nonce = str(uuid.uuid4())
message = nonce + body_str + channel_secret

signature = hmac.new(
    channel_secret.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
).digest()
b64_signature = base64.b64encode(signature).decode("utf-8")

# 寫出 body.json
with open("body.json", "w", encoding="utf-8") as f:
    f.write(body_str)

print("nonce:", nonce)
print("X-LINE-Authorization:", b64_signature)

# 直接執行 curl
os.system(f'''
curl -v -X POST "https://sandbox-api-pay.line.me/v3/payments/request" \
  -H "Content-Type: application/json" \
  -H "X-LINE-ChannelId: {channel_id}" \
  -H "X-LINE-Authorization-Nonce: {nonce}" \
  -H "X-LINE-Authorization: {b64_signature}" \
  -d @body.json
''')
