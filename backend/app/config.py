import os
from dotenv import load_dotenv
from utils.email import send_verification_email

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_verification_email(to_email, username, link):
    # 實作寄信邏輯，或從原本 main.py 搬進來
    pass  # ← 如果你還沒實作，先寫 pass，不會爆錯