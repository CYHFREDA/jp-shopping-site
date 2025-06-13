from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from db.db import get_db_cursor
from typing import Optional
from config import verify_customer_jwt
from datetime import datetime, timezone
import random
import requests
import hashlib
import urllib.parse

router = APIRouter()

# 顧客訂單
@router.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(
    customer_id: int, 
    page: int = 1, 
    limit: int = 10,
    auth=Depends(verify_customer_jwt), 
    cursor=Depends(get_db_cursor)
):
    try:
        # 验证 token 中的 customer_id 是否匹配
        if auth.get("customer_id") != customer_id:
            return JSONResponse({"error": "無權訪問此客戶的訂單"}, status_code=403)

        # 計算總訂單數
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM orders
            WHERE customer_id=%s
        """, (customer_id,))
        total = cursor.fetchone()["total"]

        # 計算分頁
        offset = (page - 1) * limit

        # 使用 LIMIT 和 OFFSET 進行分頁查詢
        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at
            FROM orders
            WHERE customer_id=%s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (customer_id, limit, offset))
        orders = cursor.fetchall()
        
        # 將 datetime 物件轉換為字串以便 JSON 序列化
        formatted_orders = []
        for order_row in orders:
            # 將 DictRow 轉換為標準 Python 字典
            order_dict = dict(order_row)
            # 格式化 datetime 物件為字串以便 JSON 序列化
            if order_dict.get('created_at'):
                order_dict['created_at'] = order_dict['created_at'].isoformat()
            if order_dict.get('paid_at'):
                order_dict['paid_at'] = order_dict['paid_at'].isoformat()
            formatted_orders.append(order_dict)

        return JSONResponse({
            "orders": formatted_orders,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        })

    except Exception as e:
        print(f"❌ 後端查詢客戶 {customer_id} 訂單錯誤： {e}")
        return JSONResponse({"error": "內部伺服器錯誤"}, status_code=500)

# 取得單筆訂單明細
@router.get("/api/orders/{order_id}")
async def get_order_by_id(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at
            FROM orders WHERE order_id=%s
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到訂單"}, status_code=404)
        order = {
            "order_id": row[0],
            "amount": row[1],
            "item_names": row[2],
            "status": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "paid_at": row[5].isoformat() if row[5] else None
        }
        return JSONResponse(order)
    except Exception as e:
        print(f"❌ 查詢單一訂單錯誤：{e}")
        return JSONResponse({"error": "查詢訂單失敗"}, status_code=500)

# 取得訂單狀態
@router.get("/api/orders/{order_id}/status")
async def get_order_status(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
        row = cursor.fetchone()

        if row:
            return JSONResponse({"order_id": order_id, "status": row[0]})
        else:
            return JSONResponse({"error": "Order not found"}, status_code=404)

    except Exception as e:
        print("❌ 後端查詢訂單狀態錯誤：", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)
    
# 取得出貨單
@router.get("/api/orders/{order_id}/shipment")
async def get_order_shipment(order_id: str, cursor=Depends(get_db_cursor)):
    try:
        cursor.execute("""
            SELECT shipment_id, order_id, recipient_name, address, status, created_at
            FROM shipments WHERE order_id=%s
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({})
        shipment = {
            "shipment_id": row[0],
            "order_id": row[1],
            "recipient_name": row[2],
            "address": row[3],
            "status": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        }
        return JSONResponse(shipment)
    except Exception as e:
        print(f"❌ 查詢出貨單錯誤：{e}")
        return JSONResponse({"error": "查詢出貨單失敗"}, status_code=500)

# 顧客確認取貨
@router.post("/api/orders/{order_id}/mark-picked-up")
async def mark_picked_up(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        # 先檢查出貨單狀態是否為已到店，並確認是否為該客戶的訂單
        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'arrived':
            return JSONResponse({"error": "只有已到店狀態才能確認取貨"}, status_code=400)
        
        # 更新狀態為 'picked_up' 並記錄取貨時間
        cursor.execute("UPDATE shipments SET status='picked_up', picked_up_at = NOW() WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "狀態已更新為已取貨"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 確認取貨錯誤：{e}")
        return JSONResponse({"error": "狀態更新失敗"}, status_code=500)

# 完成訂單
@router.post("/api/orders/{order_id}/complete")
async def complete_order(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'picked_up':
            return JSONResponse({"error": "只有已取貨狀態才能完成訂單"}, status_code=400)
        
        cursor.execute("UPDATE shipments SET status='completed' WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "訂單已完成"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 完成訂單錯誤：{e}")
        return JSONResponse({"error": "訂單完成失敗"}, status_code=500)
           
# 取消訂單（未付款才可）
@router.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: str, cursor=Depends(get_db_cursor)):
    cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
    row = cursor.fetchone()
    if not row:
        return JSONResponse({"error": "找不到訂單"}, status_code=404)

    if row[0] != "pending":
        return JSONResponse({"error": "已付款訂單無法取消"}, status_code=400)

    cursor.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))
    cursor.connection.commit()
    return {"message": "訂單已取消"}

# 顧客申請退貨
@router.post("/api/orders/{order_id}/return")
async def request_return(
    order_id: str, 
    request: Request,
    auth=Depends(verify_customer_jwt), 
    cursor=Depends(get_db_cursor)
):
    try:
        data = await request.json()
        customer_id = auth.get("customer_id")
        return_reason = data.get("return_reason")
        
        if not customer_id:
            return JSONResponse({"error": "客戶認證失敗"}, status_code=401)

        # 檢查訂單是否存在且屬於該客戶
        cursor.execute("""
            SELECT o.status, o.created_at, s.status as shipment_status
            FROM orders o
            LEFT JOIN shipments s ON o.order_id = s.order_id
            WHERE o.order_id = %s AND o.customer_id = %s
        """, (order_id, customer_id))
        
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到訂單或訂單不屬於該客戶"}, status_code=404)
            
        order_status = row["status"]
        shipment_status = row["shipment_status"]
        created_at = row["created_at"]
        
        # 檢查訂單狀態是否允許退貨
        if order_status not in ["shipped", "delivered", "completed"] or shipment_status not in ["delivered", "picked_up", "completed"]:
            return JSONResponse({"error": "訂單狀態不允許退貨"}, status_code=400)
            
        # 檢查是否在退貨期限內（14天）
        current_time = datetime.now(timezone.utc)
        days_diff = (current_time - created_at).days
        if days_diff > 14:
            return JSONResponse({"error": "已超過退貨期限（14天）"}, status_code=400)
            
        # 更新訂單狀態為退貨申請中
        cursor.execute("""
            UPDATE orders 
            SET status = 'return_requested', 
                return_reason = %s,
                updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (return_reason, order_id))
        
        cursor.connection.commit()
        return JSONResponse({"message": "退貨申請已提交"})
        
    except Exception as e:
        cursor.connection.rollback()
        print(f"❌ [退貨申請] 發生錯誤：{str(e)}")
        return JSONResponse({"error": "退貨申請失敗"}, status_code=500)

# 設定退貨物流（選擇超商門市，並建立綠界物流單）
@router.post("/api/orders/{order_id}/set-return-logistics")
async def set_return_logistics(
    order_id: str, 
    request: Request,
    auth=Depends(verify_customer_jwt), 
    cursor=Depends(get_db_cursor)
):
    try:
        data = await request.json()
        customer_id = auth.get("customer_id")
        store_id = data.get("store_id")      # 門市代號
        store_name = data.get("store_name")  # 門市名稱
        cvs_type = data.get("cvs_type")      # 超商類型（如 UNIMART, FAMI, HILIFE, OKMART）

        print(f"收到的退貨物流資料：customer_id={customer_id}, store_id={store_id}, store_name={store_name}, cvs_type={cvs_type}")

        # 檢查必要資訊
        if not customer_id:
            return JSONResponse({"error": "客戶認證失敗"}, status_code=401)
        if not store_id:
            return JSONResponse({"error": "缺少門市代號"}, status_code=400)
        if not store_name:
            return JSONResponse({"error": "缺少門市名稱"}, status_code=400)
        if not cvs_type:
            return JSONResponse({"error": "缺少超商類型"}, status_code=400)

        # 超商類型代碼轉換
        cvs_type_mapping = {
            "全家": "FAMI",
            "7-11": "UNIMART",
            "萊爾富": "HILIFE",
            "OK": "OKMART",
            # 如果前端直接傳綠界代碼，保持原樣
            "FAMI": "FAMI",
            "UNIMART": "UNIMART",
            "HILIFE": "HILIFE",
            "OKMART": "OKMART"
        }
        
        # 轉換超商類型代碼
        ecpay_cvs_type = cvs_type_mapping.get(cvs_type)
        if not ecpay_cvs_type:
            return JSONResponse({"error": f"不支援的超商類型：{cvs_type}"}, status_code=400)

        # 檢查訂單狀態是否允許退貨
        cursor.execute("""
            SELECT status, customer_id 
            FROM orders 
            WHERE order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return JSONResponse({"error": "找不到訂單"}, status_code=404)
            
        if order["customer_id"] != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)
            
        if order["status"] not in ["shipped", "delivered", "completed"]:
            return JSONResponse({"error": "訂單狀態不允許退貨"}, status_code=400)

        # 呼叫綠界API建立物流單
        merchant_id = "2000132"
        hash_key = "5294y06JbISpM5x9"
        hash_iv = "v77hoKGq4kWxNNIS"

        params = {
            "MerchantID": merchant_id,
            "MerchantTradeNo": f"TEST{order_id[-10:]}",
            "LogisticsType": "CVS",
            "LogisticsSubType": ecpay_cvs_type,  # 使用轉換後的超商類型代碼
            "GoodsAmount": 100,
            "CollectionAmount": 0,
            "IsCollection": "N",
            "GoodsName": "退貨商品",
            "SenderName": "測試賣家",
            "SenderPhone": "0223456789",
            "ReceiverName": "測試買家",
            "ReceiverPhone": "0912345678",
            "ReceiverCellPhone": "0912345678",
            "ReceiverEmail": "test@example.com",
            "TradeDesc": "退貨測試",
            "ServerReplyURL": "/api/ecpay/logistics_notify",
            "ReceiverStoreID": store_id,
            "ReturnStoreID": store_id,
            "PlatformID": "",
        }
        params["CheckMacValue"] = gen_check_mac_value(params, hash_key, hash_iv)

        url = "https://logistics-stage.ecpay.com.tw/Express/Create"
        try:
            resp = requests.post(url, data=params, timeout=10)  # 設置 10 秒超時
            result = resp.text
            print(f"綠界回應：{result}")

            # 解析綠界回傳內容
            ecpay_result = dict(item.split('=') for item in result.split('&') if '=' in item)
            logistics_id = ecpay_result.get("AllPayLogisticsID")
            rtn_code = ecpay_result.get("RtnCode")
            rtn_msg = ecpay_result.get("RtnMsg")

            if rtn_code != "1" or not logistics_id:
                return JSONResponse({"error": f"綠界建立物流單失敗: {rtn_msg}"}, status_code=400)

        except requests.exceptions.Timeout:
            return JSONResponse({"error": "綠界 API 請求超時"}, status_code=504)
        except requests.exceptions.RequestException as e:
            return JSONResponse({"error": f"綠界 API 請求失敗: {str(e)}"}, status_code=502)

        try:
            # 開始交易
            cursor.execute("BEGIN")

            # 寫入 return_logistics 資料表
            cursor.execute("""
                INSERT INTO return_logistics (
                    order_id, 
                    logistics_id, 
                    store_id, 
                    store_name, 
                    cvs_type, 
                    status, 
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (order_id) DO UPDATE
                SET logistics_id = EXCLUDED.logistics_id,
                    store_id = EXCLUDED.store_id,
                    store_name = EXCLUDED.store_name,
                    cvs_type = EXCLUDED.cvs_type,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (order_id, logistics_id, store_id, store_name, ecpay_cvs_type, "created"))

            # 更新訂單狀態為退貨處理中
            cursor.execute("""
                UPDATE orders 
                SET status = 'return_processing',
                    updated_at = NOW()
                WHERE order_id = %s
            """, (order_id,))

            # 提交交易
            cursor.execute("COMMIT")

        except Exception as e:
            # 發生錯誤時回滾交易
            cursor.execute("ROLLBACK")
            print(f"❌ 資料庫操作失敗：{str(e)}")
            return JSONResponse({"error": "資料庫操作失敗"}, status_code=500)

        return JSONResponse({
            "logistics_id": logistics_id,
            "rtn_msg": rtn_msg,
            "store_id": store_id,
            "store_name": store_name,
            "cvs_type": ecpay_cvs_type,
            "order_status": "return_processing"
        })

    except Exception as e:
        print(f"❌ [設定退貨物流] 發生錯誤：{str(e)}")
        return JSONResponse({"error": "設定退貨物流失敗"}, status_code=500)

# 查詢退貨狀態
@router.get("/api/orders/{order_id}/return-status")
async def get_return_status(
    order_id: str,
    auth=Depends(verify_customer_jwt), 
    cursor=Depends(get_db_cursor)
):
    try:
        customer_id = auth.get("customer_id")
        
        cursor.execute("""
            SELECT 
                o.status as order_status,
                o.return_reason,
                rl.store_id,
                rl.store_name,
                rl.status as logistics_status,
                rl.created_at,
                rl.updated_at
            FROM orders o
            LEFT JOIN return_logistics rl ON o.order_id = rl.order_id
            WHERE o.order_id = %s AND o.customer_id = %s
        """, (order_id, customer_id))
        
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到退貨記錄"}, status_code=404)
            
        return JSONResponse({
            "order_status": row["order_status"],
            "return_reason": row["return_reason"],
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "logistics_status": row["logistics_status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
        })
        
    except Exception as e:
        print(f"❌ [查詢退貨狀態] 發生錯誤：{str(e)}")
        return JSONResponse({"error": "查詢退貨狀態失敗"}, status_code=500)

def gen_check_mac_value(params, hash_key, hash_iv):
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&" + "&".join(f"{k}={v}" for k, v in sorted_params) + f"&HashIV={hash_iv}"
    encode_str = urllib.parse.quote_plus(encode_str).lower()
    check_mac = hashlib.md5(encode_str.encode('utf-8')).hexdigest().upper()
    return check_mac