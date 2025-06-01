CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,                          -- 訂單流水號，自動增加
    order_id VARCHAR(50) NOT NULL,                  -- 訂單編號（唯一）
    amount INTEGER NOT NULL,                        -- 訂單總金額
    item_names TEXT NOT NULL,                       -- 訂單商品明細
    status VARCHAR(20) DEFAULT 'pending',           -- 訂單狀態（預設 pending）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    paid_at TIMESTAMP NULL                          -- 付款時間（可為空）
);

COMMENT ON COLUMN orders.id IS '訂單流水號，自動增加';
COMMENT ON COLUMN orders.order_id IS '訂單編號（唯一）';
COMMENT ON COLUMN orders.amount IS '訂單總金額';
COMMENT ON COLUMN orders.item_names IS '訂單商品明細';
COMMENT ON COLUMN orders.status IS '訂單狀態（預設 pending）';
COMMENT ON COLUMN orders.created_at IS '建立時間';
COMMENT ON COLUMN orders.paid_at IS '付款時間（可為空）';

-------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,               -- 商品 ID，主鍵，自動增加
  name TEXT NOT NULL,                  -- 商品名稱，必填
  price INTEGER NOT NULL,              -- 商品價格，必填，整數
  description TEXT NOT NULL,           -- 商品描述，必填
  image_url TEXT NOT NULL,             -- 商品圖片網址，必填
  created_at TIMESTAMP DEFAULT NOW(),  -- 商品建立時間，預設為當下時間
  category VARCHAR(255)                -- 商品分類，可多分類用「#」分隔
);

COMMENT ON COLUMN products.id IS '商品 ID，主鍵，自動增加';
COMMENT ON COLUMN products.name IS '商品名稱，必填';
COMMENT ON COLUMN products.price IS '商品價格，必填，整數';
COMMENT ON COLUMN products.description IS '商品描述，選填';
COMMENT ON COLUMN products.image_url IS '商品圖片網址，選填';
COMMENT ON COLUMN products.created_at IS '商品建立時間，預設為當下時間';
COMMENT ON COLUMN products.category IS '商品分類，可多分類用「#」分隔';
-------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
  customer_id SERIAL PRIMARY KEY,          -- 客戶 ID，自動增加
  username VARCHAR(50) UNIQUE NOT NULL,    -- 使用者名稱，唯一且必填
  name VARCHAR(50) NOT NULL,               -- 使用者姓名，必填
  email VARCHAR(100) NOT NULL,             -- 電子郵件，必填
  phone VARCHAR(20) NOT NULL,              -- 電話，必填
  password VARCHAR(100) NOT NULL,          -- 密碼（bcrypt 雜湊後的結果），必填
  address VARCHAR(255)  NOT NULL,          -- 地址，必填
  created_at TIMESTAMP DEFAULT NOW()       -- 建立時間，預設當下
);

COMMENT ON COLUMN customers.customer_id IS '客戶 ID，自動增加';
COMMENT ON COLUMN customers.username IS '使用者名稱，唯一且必填';
COMMENT ON COLUMN customers.name IS '使用者姓名，必填';
COMMENT ON COLUMN customers.email IS '電子郵件，必填';
COMMENT ON COLUMN customers.phone IS '電話，必填';
COMMENT ON COLUMN customers.password IS '密碼（bcrypt 雜湊後的結果），必填';
COMMENT ON COLUMN customers.address IS '地址，必填';
COMMENT ON COLUMN customers.created_at IS '建立時間，預設當下';
-------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipments (
  shipment_id SERIAL PRIMARY KEY,        -- 出貨單 ID，自動增加
  order_id VARCHAR(50) NOT NULL,         -- 對應的訂單編號，必填
  recipient_name VARCHAR(50) NOT NULL,   -- 收件人姓名，必填
  address VARCHAR(200) NOT NULL,         -- 收件地址，必填
  status VARCHAR(20) NOT NULL,           -- 出貨狀態（例：pending、shipped...），必填
  created_at TIMESTAMP DEFAULT NOW()     -- 建立時間
);
COMMENT ON COLUMN shipments.shipment_id IS '出貨單 ID，自動增加';
COMMENT ON COLUMN shipments.order_id IS '對應的訂單編號';
COMMENT ON COLUMN shipments.recipient_name IS '收件人姓名';
COMMENT ON COLUMN shipments.address IS '收件地址';
COMMENT ON COLUMN shipments.status IS '出貨狀態（例：pending、shipped...）';
COMMENT ON COLUMN shipments.created_at IS '建立時間';
-------------------------------------------------------------------------------------
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,                              -- 流水號
    username VARCHAR(50) UNIQUE NOT NULL,               -- 帳號
    password TEXT NOT NULL,                             -- bcrypt 雜湊後的密碼
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 建立時間
);

-- 新增使用者管理員,密碼1234
INSERT INTO admin_users (username, password)
VALUES ('admin', '$2b$12$6WZclmZ.QN4Bi53PBWqWbeUeu/Sqx0ruFoZn6QgUoZkRSVOSFiP0C');

COMMENT ON TABLE admin_users IS '管理員使用者表格';
COMMENT ON COLUMN admin_users.id IS '流水號';
COMMENT ON COLUMN admin_users.username IS '管理員帳號';
COMMENT ON COLUMN admin_users.password IS '密碼（bcrypt 雜湊）';
COMMENT ON COLUMN admin_users.created_at IS '建立時間';