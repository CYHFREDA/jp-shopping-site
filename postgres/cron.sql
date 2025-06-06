-- PostgreSQL 自動刪除未付款訂單 + 備份紀錄 SOP
-- 目標說明
-- 每天 00:00 自動刪除「超過 3 天未付款」的訂單。
-- 刪除前備份至 orders_delete_log 表。
-- 每週日 03:00 自動清理「90 天前的備份紀錄」。
-- 所有排程任務由 pg_cron 管理。

-- 啟用 pg_cron 擴充功能
CREATE EXTENSION pg_cron;
-- 建立備份表（附欄位備註）
CREATE TABLE orders_delete_log (
  id SERIAL PRIMARY KEY,
  original_id INTEGER,
  order_id TEXT,
  amount INTEGER,
  item_names TEXT,
  status TEXT,
  created_at TIMESTAMP,
  paid_at TIMESTAMP,
  customer_id TEXT,
  deleted_at TIMESTAMP DEFAULT now()
);
-- 註解
COMMENT ON TABLE orders_delete_log IS '紀錄從 orders 表刪除的資料備份表';
COMMENT ON COLUMN orders_delete_log.original_id IS '對應原始 orders 表的 id';
COMMENT ON COLUMN orders_delete_log.order_id IS '訂單編號';
COMMENT ON COLUMN orders_delete_log.amount IS '訂單金額';
COMMENT ON COLUMN orders_delete_log.item_names IS '訂購商品名稱';
COMMENT ON COLUMN orders_delete_log.status IS '訂單狀態（如 pending、false）';
COMMENT ON COLUMN orders_delete_log.created_at IS '訂單建立時間';
COMMENT ON COLUMN orders_delete_log.paid_at IS '付款時間（若尚未付款為 NULL）';
COMMENT ON COLUMN orders_delete_log.customer_id IS '訂單所屬客戶 ID';
COMMENT ON COLUMN orders_delete_log.deleted_at IS '該筆訂單於何時被自動刪除';

-- 建立刪除任務（每天執行）
SELECT cron.schedule(
  'delete_old_orders',
  '0 0 * * *',
  $$
  INSERT INTO orders_delete_log (
    original_id, order_id, amount, item_names, status, created_at, paid_at, customer_id, deleted_at
  )
  SELECT id, order_id, amount, item_names, status, created_at, paid_at, customer_id, now()
  FROM orders
  WHERE (status = 'pending' OR status = 'false')
    AND created_at < now() - interval '3 days';

  DELETE FROM orders
  WHERE (status = 'pending' OR status = 'false')
    AND created_at < now() - interval '3 days';
  $$
);
-- 建立備份清理任務（每週執行）
SELECT cron.schedule(
  'cleanup_delete_log',
  '0 0 * * 0',
  $$
  DELETE FROM orders_delete_log
  WHERE deleted_at < now() - interval '90 days';
  $$
);

-- 例行檢查 / 排錯指令
-- 查看目前已排程的任務：
SELECT jobid, jobname, schedule, command FROM cron.job;
-- 取消特定任務（如果要修改）
SELECT cron.unschedule(jobid);
-- 查看排程任務：
SELECT * FROM cron.job;

-- 測試用 SQL
-- 查將被刪除資料：
SELECT * FROM orders WHERE status = 'pending' AND created_at < now() - interval '3 days';
-- 查將清除備份：
SELECT * FROM orders_delete_log WHERE deleted_at < now() - interval '90 days';

-- 還原某筆被刪除的訂單
NSERT INTO orders (order_id, amount, item_names, status, created_at, paid_at, customer_id)
SELECT order_id, amount, item_names, status, created_at, paid_at, customer_id
FROM orders_delete_log
WHERE original_id = 123;  -- 換成要還原的 ID


-- 刪除排程任務：
SELECT cron.unschedule(job_id) FROM cron.job WHERE jobname = 'delete_old_orders';
-- 查時區
SHOW timezone
-- 修改時區台灣時間
SET timezone = 'Asia/Taipei';
