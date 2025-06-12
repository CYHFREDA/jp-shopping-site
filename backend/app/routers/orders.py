from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from db.db import get_db_cursor
from typing import Optional
from dependencies.auth import verify_customer_jwt
import datetime

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
async def request_return(order_id: str, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
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
            return JSONResponse({"error": "只有已取貨狀態才能申請退貨"}, status_code=400)
        
        # 更新狀態為 'returned_pending'，表示退貨申請中
        cursor.execute("UPDATE shipments SET status='returned_pending' WHERE order_id=%s", (order_id,))
        cursor.connection.commit()
        return JSONResponse({"message": "已成功申請退貨，等待管理員處理。"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 申請退貨錯誤：{e}")
        return JSONResponse({"error": "申請退貨失敗"}, status_code=500)

# 設定退貨物流
@router.post("/api/orders/{order_id}/set-return-logistics")
async def set_return_logistics(order_id: str, request: Request, auth=Depends(verify_customer_jwt), cursor=Depends(get_db_cursor)):
    try:
        customer_id = auth.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=401, detail="客戶認證失敗")

        data = await request.json()
        return_store_name = data.get("return_store_name")

        if not return_store_name:
            return JSONResponse({"error": "請提供 7-11 門市名稱！"}, status_code=400)

        # 檢查出貨單狀態是否為 'returned_pending'，並確認是否為該客戶的訂單
        cursor.execute("SELECT s.status, o.customer_id FROM shipments s JOIN orders o ON s.order_id = o.order_id WHERE s.order_id=%s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"error": "找不到出貨單或訂單"}, status_code=404)
        
        shipment_status = row[0]
        order_customer_id = row[1]

        if order_customer_id != customer_id:
            return JSONResponse({"error": "無權操作此訂單"}, status_code=403)

        if shipment_status != 'returned_pending':
            return JSONResponse({"error": "只有退貨申請中的訂單才能設定退貨物流"}, status_code=400)

        # 生成一個模擬的退貨物流編號
        return_tracking_number = f"711-{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

        # 更新出貨單資料，新增 7-11 門市名稱和物流編號
        cursor.execute("""
            UPDATE shipments
            SET return_store_name = %s, return_tracking_number = %s
            WHERE order_id = %s
        """, (return_store_name, return_tracking_number, order_id))
        cursor.connection.commit()

        return JSONResponse({"message": "7-11 退貨物流已設定成功！", "tracking_number": return_tracking_number})

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ 設定 7-11 退貨物流錯誤：{e}")
        return JSONResponse({"error": "設定 7-11 退貨物流失敗！"}, status_code=500)