from fastapi import APIRouter, Request, Depends, HTTPException, status
from db.db import get_db_cursor
from utils.email import send_verification_email
from config import FRONTEND_URL
import uuid
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

router = APIRouter()

# Email 驗證端點
@router.get("/verify-email")
async def verify_email(token: str, cursor=Depends(get_db_cursor)):
    print(f"[Email 驗證] 收到 Email 驗證請求，Token: {token}")
    try:
        cursor.execute("SELECT customer_id, username, is_verified, token_expiry FROM customers WHERE verification_token = %s", (token,))
        customer = cursor.fetchone()

        if not customer:
            print(f"❌ [Email 驗證] 驗證失敗: 無效或找不到 token: {token}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="無效或已使用的驗證連結。")

        customer_id, username, is_verified, token_expiry = customer
        print(f"[Email 驗證] 找到客戶 '{username}', 已驗證狀態: {is_verified}, 過期時間: {token_expiry}")

        if is_verified:
            print(f"✅ [Email 驗證] 客戶 '{username}' 已驗證成功，無需重複驗證。")
            return JSONResponse({"message": "您的 Email 已驗證成功，無需重複驗證。"})

        if token_expiry and datetime.utcnow() > token_expiry.replace(tzinfo=None):
            print(f"❌ [Email 驗證] 驗證失敗: 客戶 '{username}' 的 token 已過期。")
            # 清除過期的 token 和過期時間
            cursor.execute("UPDATE customers SET verification_token = NULL, token_expiry = NULL WHERE customer_id = %s", (customer_id,))
            cursor.connection.commit()
            print(f"✅ [Email 驗證] 客戶 '{username}' 的過期 token 已被清除。")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已過期，請重新註冊或申請新連結。")

        print(f"[Email 驗證] 嘗試更新客戶 '{username}' 為已驗證狀態。")
        cursor.execute("UPDATE customers SET is_verified = TRUE, verification_token = NULL, token_expiry = NULL WHERE customer_id = %s", (customer_id,))
        cursor.connection.commit()
        print(f"✅ [Email 驗證] 客戶 '{username}' Email 已驗證成功並更新資料庫！")

        return JSONResponse({"message": "✅ Email 驗證成功！您現在可以登入。"})

    except HTTPException as e:
        print(f"❌ [Email 驗證] 發生 HTTP 錯誤：{e.detail}")
        raise e
    except Exception as e:
        print(f"❌ [Email 驗證] 發生未知錯誤：{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email 驗證失敗，請稍後再試！")

# 重新發送驗證 Email 端點
@router.post("/resend-verification-email")
async def resend_verification_email_endpoint(request: Request, cursor=Depends(get_db_cursor)):
    data = await request.json()
    email = data.get("email")

    if not email:
        print("❌ [重新發送驗證信] 請求缺少 Email。")
        return JSONResponse({"error": "缺少 Email 地址"}, status_code=400)

    try:
        print(f"[重新發送驗證信] 收到重新發送請求，Email: {email}")
        cursor.execute("SELECT customer_id, username, is_verified FROM customers WHERE email = %s", (email,))
        customer = cursor.fetchone()

        if not customer:
            print(f"❌ [重新發送驗證信] Email '{email}' 未註冊或不存在。")
            return JSONResponse({"error": "此 Email 地址未註冊。"}, status_code=404)

        customer_id, username, is_verified = customer

        if is_verified:
            print(f"✅ [重新發送驗證信] Email '{email}' 已驗證，無需重新發送。")
            return JSONResponse({"message": "您的 Email 已驗證成功，無需重新發送。"}, status_code=200)

        # 生成新的驗證 token 和過期時間
        verification_token = str(uuid.uuid4())
        token_expiry = datetime.utcnow() + timedelta(minutes=5) # 5 分鐘過期

        print(f"[重新發送驗證信] 為 Email '{email}' 生成新 token: {verification_token}, 過期時間: {token_expiry}")

        # 更新資料庫中的 token 和過期時間
        cursor.execute(
            "UPDATE customers SET verification_token = %s, token_expiry = %s WHERE customer_id = %s",
            (verification_token, token_expiry, customer_id)
        )
        cursor.connection.commit()
        print(f"✅ [重新發送驗證信] 資料庫已更新 Email '{email}' 的驗證 token。")

        # 重新發送驗證 Email
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        email_sent = await send_verification_email(email, username, verification_link)

        if email_sent:
            print(f"✅ [重新發送驗證信] 驗證信已成功重新發送給 {email}。")
            return JSONResponse({"message": "✅ 驗證信已成功重新發送，請檢查您的 Email 收件箱。"}, status_code=200)
        else:
            print(f"❌ [重新發送驗證信] 重新發送驗證信給 {email} 失敗。")
            return JSONResponse({"error": "重新發送驗證信失敗，請稍後再試。"}, status_code=500)

    except Exception as e:
        print(f"❌ [重新發送驗證信] 發生錯誤：{e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)