from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from db.db import get_db_cursor
from typing import Optional
from config import verify_customer_jwt
from datetime import datetime, timezone
import random

router = APIRouter()

# 顧客訂單
@router.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: int, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        # 验证 token 中的 customer_id 是否匹配
        if auth.get("customer_id") != customer_id:
            return JSONResponse({"error": "無權訪問此客戶的訂單"}, status_code=403)

        cursor.execute("""
            SELECT order_id, amount, item_names, status, created_at, paid_at
            FROM orders
            WHERE customer_id=%s
            ORDER BY created_at DESC
        """, (customer_id,))
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

        return JSONResponse(formatted_orders)

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

# 設定退貨物流（選擇 7-11 門市）
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
        store_id = data.get("store_id")      # 7-11 店號
        store_name = data.get("store_name")  # 7-11 店名
        
        if not all([customer_id, store_id, store_name]):
            return JSONResponse({"error": "缺少必要資訊"}, status_code=400)

        # 檢查訂單狀態
        cursor.execute("""
            SELECT status 
            FROM orders 
            WHERE order_id = %s AND customer_id = %s
        """, (order_id, customer_id))
        
        row = cursor.fetchone()
        if not row or row["status"] != "return_requested":
            return JSONResponse({"error": "訂單狀態不正確"}, status_code=400)

        # 建立退貨物流記錄
        cursor.execute("""
            INSERT INTO return_logistics (
                order_id, 
                store_id,
                store_name,
                status,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (order_id, store_id, store_name))
        
        # 更新訂單狀態
        cursor.execute("""
            UPDATE orders 
            SET status = 'returning',
                updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (order_id,))
        
        cursor.connection.commit()
        return JSONResponse({
            "message": "退貨門市已設定",
            "store_id": store_id,
            "store_name": store_name
        })
        
    except Exception as e:
        cursor.connection.rollback()
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