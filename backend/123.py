import json
import hmac
import hashlib
import base64
import uuid

channel_id = "2006462420"
channel_secret = "8c832c018d09a8be1738b32a3be1ee0a"

# 從檔案讀取要送出的 JSON body
with open("body.json", "r", encoding="utf-8") as f:
    body_str = f.read()

# 產生隨機 nonce
nonce = str(uuid.uuid4())

# LINE Pay 文件要求：簽名用 nonce + body + channelId
message = nonce + body_str + channel_id

# 產生 HMAC-SHA256 簽名
signature = hmac.new(
    channel_secret.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
).digest()

# base64 編碼
b64_signature = base64.b64encode(signature).decode("utf-8")

# 印出結果
print("nonce:", nonce)
print("X-LINE-Authorization:", b64_signature)