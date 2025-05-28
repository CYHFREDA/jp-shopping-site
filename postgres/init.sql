CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,             -- 自動流水號
    order_id VARCHAR(50) NOT NULL,     -- 你的訂單編號
    amount INTEGER NOT NULL,           -- 總金額
    item_names TEXT NOT NULL,          -- 商品明細
    status VARCHAR(20) DEFAULT 'pending', -- 訂單狀態
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    paid_at TIMESTAMP NULL             -- 付款時間
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  description TEXT,
  image_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);