import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD
from dotenv import load_dotenv

load_dotenv()

# 發送驗證 Email 的輔助函式
async def send_verification_email(recipient_email: str, username: str, verification_link: str):
    if not all([EMAIL_HOST, EMAIL_USERNAME, EMAIL_PASSWORD]):
        print("❌ 無法發送 Email：Email 服務設定不完整。")
        return False

    sender_email = EMAIL_USERNAME
    sender_password = EMAIL_PASSWORD

    if not sender_email or not sender_password:
        print("❌ [Email服務] 錯誤：SMTP 環境變數未完整設定。")
        raise ValueError("SMTP environment variables are not fully set.")

    # 使用 MIMEMultipart 來同時包含純文字和 HTML 內容
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "歡迎加入！請驗證您的 Email 以啟用帳戶"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # Email 的純文字內容 (重新加入)
    text = f"""
        哈囉 {username},
        感謝您註冊我們的服務！
        請點擊以下連結驗證您的 Email：
        {verification_link}
        此連結將於 5 分鐘內過期。
        如果您沒有註冊，請忽略此 Email。
        """

    # Email 的 HTML 內容 (Notion 風格卡片)
    html = f"""
        <!DOCTYPE html>
        <html lang=\"zh-TW\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>CleVora 帳戶驗證通知</title>
        </head>
        <body style=\"background:#f8f9fa;padding:32px 0;\">
          <div style=\"max-width:480px;margin:0 auto;font-family:'Segoe UI','Arial','Microsoft JhengHei',sans-serif;\">
            <h2 style=\"color:#38302e;text-align:center;margin-bottom:8px;\">驗證您的信箱</h2>
            <p style=\"text-align:center;color:#555;margin-bottom:24px;\">感謝您註冊 Clevora 日本代購，請確認以下資訊並完成驗證：</p>
            <div style=\"background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);padding:24px 20px 16px 20px;margin-bottom:24px;\">
              <div style=\"display:flex;align-items:center;margin-bottom:12px;\">
                <span style=\"font-size:20px;margin-right:10px;\">📧</span>
                <span style=\"color:#a18a7b;font-weight:bold;width:80px;display:inline-block;\">信箱</span>
                <span style=\"color:#38302e;\">{recipient_email}</span>
              </div>
              <div style=\"display:flex;align-items:center;margin-bottom:12px;\">
                <span style=\"font-size:20px;margin-right:10px;\">⏰</span>
                <span style=\"color:#a18a7b;font-weight:bold;width:80px;display:inline-block;\">有效時間</span>
                <span style=\"color:#38302e;\">5 分鐘內</span>
              </div>
              <div style="display:flex;align-items:center;margin-bottom:12px;">
                <span style="font-size:20px;margin-right:10px;">🔗</span>
                <span style="color:#a18a7b;font-weight:bold;width:80px;display:inline-block;">驗證連結</span>
                <span style="color:#a18a7b;">點此下方連結完成驗證</span>
              </div>
            </div>
            <a href="{verification_link}" style="display:block;width:100%;max-width:320px;margin:0 auto 24px auto;background:#a18a7b;color:#fff;text-align:center;padding:14px 0;border-radius:8px;font-size:1.15rem;font-weight:bold;text-decoration:none;">立即驗證信箱</a>
            <p style="color:#888;font-size:0.95rem;text-align:center;margin-bottom:8px;">如果你沒有註冊 Clevora，請忽略此信件。</p>
            <p style="color:#bbb;font-size:0.85rem;text-align:center;">Clevora 日本代購 &nbsp;|&nbsp; <a href="mailto:clevora.service@gmail.com" style="color:#bbb;">客服信箱</a></p>
          </div>
        </body>
        </html>
        """

    # 將純文字和 HTML 內容附加到 MIMEMultipart 物件 (純文字在前，HTML 在後)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    msg.attach(part1)
    msg.attach(part2)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"✅ [Email服務] 驗證信成功寄送給 {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ [Email服務] 寄送驗證信失敗：{e}")
        return False