from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from db.db import get_db_cursor
from config import verify_admin_jwt, JWT_SECRET_KEY, JWT_ALGORITHM
from fastapi import Query, HTTPException
from psycopg2 import errors
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import bcrypt
import uuid
import jwt

router = APIRouter()

# 後台載入商品資料
@router.get("/api/admin/products")
async def admin_get_products(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT id, name, price, description, image_url, created_at, category
            FROM products
            ORDER BY created_at DESC
        """)

        products = []
        for row in cursor.fetchall():
             products.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "description": row[3],
                "image_url": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "category": row[6]
            })
        
        return JSONResponse(products)

    except Exception as e:
        print("❌ 後台載入商品資料錯誤：", str(e))
        return JSONResponse({"error": "無法載入商品資料"}, status_code=500)
    
# 後台取得訂單資料
@router.get("/api/admin/orders")
async def admin_get_orders(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT id, order_id, amount, item_names, status, created_at, paid_at FROM orders ORDER BY created_at DESC")
        rows = cursor.fetchall()

        # 手動構建字典列表並格式化 datetime 欄位
        formatted_orders = []
        for row in rows:
            order_dict = {
                "id": row[0],
                "order_id": row[1],
                "amount": row[2],
                "item_names": row[3],
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None, # 格式化 datetime
                "paid_at": row[6].isoformat() if row[6] else None    # 格式化 datetime
            }
            formatted_orders.append(order_dict)

        return JSONResponse(formatted_orders)

    except Exception as e:
        print(f"❌ 後端查詢訂單錯誤： {e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)
    
# 後台更新訂單狀態
@router.post("/api/admin/update_order_status")
async def update_order_status(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        order_id = data.get("order_id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return JSONResponse({"error": "缺少必要參數"}, status_code=400)

        if new_status not in ["pending", "success", "fail"]:
            return JSONResponse({"error": "無效的訂單狀態"}, status_code=400)

        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return JSONResponse({"error": "找不到訂單"}, status_code=404)

        cursor.execute("""
            UPDATE orders 
            SET status=%s, 
                paid_at=CASE 
                    WHEN %s='success' THEN CURRENT_TIMESTAMP 
                    ELSE paid_at 
                END 
            WHERE order_id=%s
        """, (new_status, new_status, order_id))
        
        cursor.connection.commit()

        return JSONResponse({"message": "訂單狀態更新成功"})

    except Exception as e:
        print("❌ 更新訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "更新訂單狀態失敗"}, status_code=500)
    
# 後台新增商品
@router.post("/api/admin/products")
async def admin_add_product(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url")
    if not image_url:
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqqmt7zkmd-lRuFm44YueFePaZjxllx12CfQ&s"
    category = data.get("category", "")

    if not name or not price:
        return JSONResponse({"error": "❌ 商品名稱與價格為必填！"}, status_code=400)

    try:
        cursor.execute("""
            INSERT INTO products (name, price, description, image_url, category)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, price, description, image_url, category))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 商品已新增"})
    except errors.StringDataRightTruncation as e:
        # 資料過長
        return JSONResponse({"error": "❌ 文字長度超過限制，請修改再送出！"}, status_code=400)
    except Exception as e:
        print("❌ 新增商品時出錯：", e)
        return JSONResponse({"error": "❌ 新增商品失敗，請稍後再試！"}, status_code=500)

# 後台編輯商品
@router.put("/api/admin/products/{id}")
async def admin_update_product(id: int, request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    name = data.get("name")
    price = data.get("price")
    description = data.get("description", "")
    image_url = data.get("image_url", "")
    category = data.get("category", "")

    cursor.execute("""
        UPDATE products
        SET name=%s, price=%s, description=%s, image_url=%s, category=%s
        WHERE id=%s
    """, (name, price, description, image_url, category, id))
    cursor.connection.commit()
    return JSONResponse({"message": "商品已更新"})

#後台刪除商品
@router.delete("/api/admin/products/{id}")
async def admin_delete_product(id: int, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    cursor.connection.commit()
    return JSONResponse({"message": "商品已刪除"})

# 後台出貨管理
@router.get("/api/admin/shipments")
async def admin_get_shipments(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    print("🚚 準備查詢出貨資料")
    try:
        cursor.execute("SELECT shipment_id, order_id, recipient_name, address, status, created_at, return_store_name, return_tracking_number FROM shipments ORDER BY created_at DESC")
        rows = cursor.fetchall()
        print("✅ 查詢結果：", rows)
    except Exception as e:
        print("❌ 出錯：", e)
    shipments = [{"shipment_id": r[0], "order_id": r[1], "recipient_name": r[2], "address": r[3], "status": r[4], "created_at": str(r[5]), "return_store_name": r[6], "return_tracking_number": r[7]} for r in rows]
    return JSONResponse(shipments)

# 更新出貨單資料
@router.post("/api/admin/update_shipment")
async def admin_update_shipment(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    shipment_id = data.get("shipment_id")
    recipient_name = data.get("recipient_name")
    address = data.get("address")
    status_ = data.get("status")

    if not shipment_id or not recipient_name or not address or not status_:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    cursor.execute("""
        UPDATE shipments SET recipient_name=%s, address=%s, status=%s
        WHERE shipment_id=%s
    """, (recipient_name, address, status_, shipment_id))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 出貨資料已更新！"})

#後台客戶管理
@router.get("/api/admin/customers")
async def admin_get_customers(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    cursor.execute("SELECT customer_id, name, email, phone, address, created_at FROM customers ORDER BY created_at DESC")
    rows = cursor.fetchall()
    customers = [
        {
            "customer_id": r[0],
            "name": r[1],
            "email": r[2],
            "phone": r[3],
            "address": r[4],
            "created_at": str(r[5])
        }
        for r in rows
    ]
    return JSONResponse(customers)

#後台客戶重置密碼
@router.post("/api/admin/reset_customer_password")
async def admin_reset_customer_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    customer_id = data.get("customer_id")
    new_password = data.get("new_password")

    if not customer_id or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    # bcrypt 雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # conn = get_db_conn()
    # cursor = conn.cursor()
    cursor.execute("UPDATE customers SET password=%s WHERE customer_id=%s", (hashed_password, customer_id))
    cursor.connection.commit()
    # cursor.close()
    # conn.close()
    return JSONResponse({"message": "✅ 密碼已重置（bcrypt 加密）"})

#後台編輯客戶資料
@router.post("/api/admin/update_customer")
async def admin_update_customer(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    customer_id = data.get("customer_id")
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address", "")
    if not customer_id or not name or not phone:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)

    # conn = get_db_conn()
    # cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name=%s, phone=%s, address=%s
        WHERE customer_id=%s
    """, (name, phone, address, customer_id))

    cursor.connection.commit()
    # cursor.close()
    # conn.close()

    return JSONResponse({"message": "✅ 客戶資料已更新！"})

#後台新增管理員
@router.post("/api/admin/create_admin")
async def create_admin(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (username, hashed_password))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 管理員已新增"})
    except psycopg2.IntegrityError:
        return JSONResponse({"error": "❌ 帳號已存在"}, status_code=400)
    finally:
        pass # 連線由依賴項管理，不需要手動關閉

#顯示後台使用者
@router.get("/api/admin/admin_users")
async def admin_get_admin_users(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    # 讀取 id, username, created_at 和 notes 欄位
    cursor.execute("SELECT id, username, created_at, notes FROM admin_users ORDER BY created_at")
    rows = cursor.fetchall()
    # 返回包含 id 和 notes 的使用者列表
    return [{"id": r[0], "username": r[1], "created_at": str(r[2]), "notes": r[3]} for r in rows]

# 刪除管理員
@router.delete("/api/admin/admin_users/{admin_id}")
async def admin_delete_admin(admin_id: int, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        # 執行刪除操作
        cursor.execute("DELETE FROM admin_users WHERE id=%s", (admin_id,))
        cursor.connection.commit()

        # 檢查是否有行被刪除
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="❌ 找不到該管理員或已刪除！")

        return JSONResponse({"message": "✅ 管理員已成功刪除！"})
    except HTTPException as e:
        raise e # 重新拋出 HTTPException
    except Exception as e:
        print(f"❌ 刪除管理員時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 刪除管理員失敗，請稍後再試！")
    
# 獲取系統設定
@router.get("/api/admin/settings")
async def get_admin_settings(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT site_title, contact_email, items_per_page FROM settings LIMIT 1")
        settings = cursor.fetchone()
        if settings:
            return JSONResponse(dict(settings))
        else:
            # 如果資料庫中沒有設定，返回預設值或空物件
            return JSONResponse({"site_title": "", "contact_email": "", "items_per_page": 10})
    except Exception as e:
        print(f"❌ 獲取系統設定時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 獲取系統設定失敗！")

# 更新系統設定
@router.post("/api/admin/settings")
async def update_admin_settings(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        data = await request.json()
        site_title = data.get("site_title")
        contact_email = data.get("contact_email")
        items_per_page = data.get("items_per_page")

        # 檢查設定是否存在，如果不存在則插入，否則更新
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]

        if count == 0:
            # 插入新設定
            cursor.execute("INSERT INTO settings (site_title, contact_email, items_per_page) VALUES (%s, %s, %s)",
                           (site_title, contact_email, items_per_page))
        else:
            # 更新現有設定
            cursor.execute("UPDATE settings SET site_title=%s, contact_email=%s, items_per_page=%s",
                           (site_title, contact_email, items_per_page))
        cursor.connection.commit()
        return JSONResponse({"message": "✅ 設定已成功保存！"})
    except Exception as e:
        print(f"❌ 保存系統設定時發生錯誤： {e}")
        raise HTTPException(status_code=500, detail="❌ 保存設定失敗！")

# 修改管理員資訊 (例如備註)
@router.post("/api/admin/update_admin")
async def admin_update_admin(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    admin_id = data.get("id") # 從前端傳入管理員 ID
    notes = data.get("notes")

    if not admin_id:
        raise HTTPException(status_code=400, detail="❌ 缺少管理員 ID")
    
    # 注意：這裡只允許更新 notes 欄位，如果需要更新其他欄位，需要修改這裡的 SQL 語句
    cursor.execute("UPDATE admin_users SET notes=%s WHERE id=%s", (notes, admin_id))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 管理員資料已更新！"})

#修改使用者密碼
@router.post("/api/admin/update_admin_password")
async def update_admin_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    new_password = data.get("new_password")
    if not username or not new_password:
        return JSONResponse({"error": "❌ 缺少必要欄位"}, status_code=400)
    
    # bcrypt 重新產生雜湊
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("UPDATE admin_users SET password=%s WHERE username=%s", (hashed_password, username))
    cursor.connection.commit()
    return JSONResponse({"message": "✅ 密碼已更新！"})

# 後台管理員重置密碼
@router.post("/api/admin/reset_admin_password")
async def admin_reset_admin_password(request: Request, auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="❌ 缺少使用者名稱")

    # 生成一個新的隨機密碼 (例如 8 個字元的英數字混合)
    new_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))

    # bcrypt 雜湊新密碼
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # 更新資料庫中的密碼
        cursor.execute("UPDATE admin_users SET password=%s WHERE username=%s", (hashed_password, username))
        cursor.connection.commit()
        # 返回新生成的明文密碼給前端 (請注意安全性)
        return JSONResponse({"message": "✅ 密碼已重置！", "new_password": new_password})
    except Exception as e:
        print(f"❌ 重置管理員密碼時出錯: {e}")
        raise HTTPException(status_code=500, detail="❌ 重置密碼失敗，請稍後再試！")

# 管理員登入
@router.post("/api/admin/login")
async def admin_login(request: Request, cursor=Depends(get_db_cursor)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse({"error": "帳號或密碼為必填！"}, status_code=400)
    cursor.execute("SELECT id, password FROM admin_users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if not row or not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return JSONResponse({"error": "帳號或密碼錯誤"}, status_code=401)
    admin_id = row["id"]
    token = jwt.encode({
        "admin_id": admin_id,
        "username": username, # 添加用户名到 token
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # 更新 current_token 實現後踢前機制
    cursor.execute("UPDATE admin_users SET current_token=%s WHERE id=%s", (token, admin_id))
    cursor.connection.commit()

    return JSONResponse({
        "message": "登入成功",
        "token": token,
        "admin_id": admin_id,
        "expire_at": (datetime.utcnow() + timedelta(minutes=30)).timestamp() * 1000 # 轉換為毫秒
    })

# 儀表板統計 API
@router.get("/api/admin/dashboard_summary")
async def admin_dashboard_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    auth=Depends(verify_admin_jwt),
    cursor=Depends(get_db_cursor)
):
    try:
        # 今日訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURRENT_DATE
        """)
        today_order = cursor.fetchone()[0]

        # 未付款訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM orders WHERE status = 'pending'
        """)
        unpaid_order = cursor.fetchone()[0]

        # 未出貨訂單數
        cursor.execute("""
            SELECT COUNT(*) FROM shipments WHERE status = 'pending'
        """)
        unshipped_order = cursor.fetchone()[0]

        # 總營業額（已付款訂單）
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'success'
        """)
        total_sales = float(cursor.fetchone()[0])

        # 處理日期區間
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if not start_date or not end_date:
            end_date = today.strftime('%Y-%m-%d')
            start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        # 查詢區間訂單數
        cursor.execute("""
            SELECT TO_CHAR(created_at, 'MM/DD') as day, COUNT(*)
            FROM orders
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY day
            ORDER BY day
        """, (start_date, end_date))
        rows = cursor.fetchall()
        date_map = {r[0]: r[1] for r in rows}
        # 產生區間所有日期
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        dates = [(start_dt + timedelta(days=i)).strftime('%m/%d') for i in range((end_dt - start_dt).days + 1)]
        counts = [date_map.get(d, 0) for d in dates]

        return JSONResponse({
            "todayOrder": today_order,
            "unpaidOrder": unpaid_order,
            "unshippedOrder": unshipped_order,
            "totalSales": total_sales,
            "orderChart": {
                "dates": dates,
                "counts": counts
            }
        })
    except Exception as e:
        print("❌ 儀表板統計 API 錯誤：", e)
        return JSONResponse({"error": "無法取得儀表板統計資料"}, status_code=500)

# 自動完成出貨單
@router.post("/api/admin/auto_complete_shipments")
async def auto_complete_shipments(auth=Depends(verify_admin_jwt), cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            UPDATE shipments
            SET status = 'completed'
            WHERE status = 'shipped'
              AND delivered_at IS NOT NULL
              AND delivered_at < NOW() - INTERVAL '7 days'
            RETURNING order_id;
        """)
        updated = cursor.fetchall()
        cursor.connection.commit()
        return {"message": f"自動完成 {len(updated)} 筆出貨單", "order_ids": [row[0] for row in updated]}
    except Exception as e:
        print(f"❌ 自動完成出貨單錯誤：{e}")
        return {"error": "自動完成失敗"}

class OrderIdRequest(BaseModel):
    order_id: str

# 模擬到店
@router.post("/api/admin/mock_delivered")
async def mock_delivered(
    req: OrderIdRequest,
    auth=Depends(verify_admin_jwt),
    cursor=Depends(get_db_cursor)
):
    order_id = req.order_id
    try:
        # 先檢查訂單狀態是否為已出貨
        cursor.execute("SELECT status FROM shipments WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": "找不到出貨單"}
        if row[0] != 'shipped':
            return {"error": "只有已出貨狀態才能模擬到店"}
        # 同時更新 delivered_at 與 status
        cursor.execute("""
            UPDATE shipments 
            SET delivered_at = NOW(), status = 'arrived'
            WHERE order_id = %s
        """, (order_id,))
        cursor.connection.commit()
        return {"message": f"已模擬到店，order_id: {order_id}"}
    except Exception as e:
        print(f"❌ 模擬到店錯誤：{e}")
        return {"error": "模擬到店失敗"}