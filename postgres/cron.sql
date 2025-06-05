-- PostgreSQL + pg_cron 清除過期未驗證帳號任務 SOP
-- 啟用 pg_cron 擴充功能
CREATE EXTENSION pg_cron;

-- 建立紀錄表
CREATE TABLE IF NOT EXISTS cleanup_logs (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50),
    records_affected INTEGER,
    executed_at TIMESTAMP
);

--建立函數：刪除過期未驗證帳號 + 紀錄清除筆數
CREATE OR REPLACE FUNCTION cleanup_expired_unverified_records()
RETURNS void AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    DELETE FROM customers 
    WHERE is_verified = FALSE 
    AND token_expiry < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    INSERT INTO cleanup_logs (operation, records_affected, executed_at)
    VALUES ('cleanup_expired_unverified', affected_rows, CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- 取消舊的排程（保險用，避免重複）
SELECT cron.unschedule(jobid)
FROM cron.job
WHERE jobname = 'cleanup-expired-records';

--  建立新的排程（每分鐘執行一次）
SSELECT cron.schedule(
  'cleanup-expired-records',
  '* * * * *',
  $$SELECT cleanup_expired_unverified_records();$$
);

-- 驗證
-- 查 log 執行紀錄：
SELECT * FROM cleanup_logs ORDER BY executed_at DESC LIMIT 10;
-- 查排程執行狀況：
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;
-- 查目前排程：
SELECT * FROM cron.job;
-- 查時區
SHOW timezone
-- 修改時區台灣時間
SET timezone = 'Asia/Taipei';
