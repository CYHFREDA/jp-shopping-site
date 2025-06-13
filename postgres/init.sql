CREATE TABLE "orders" (
	"id" SERIAL NOT NULL,
	"order_id" VARCHAR(50) NOT NULL,
	"amount" INTEGER NOT NULL,
	"item_names" TEXT NOT NULL,
	"status" VARCHAR(20) NULL DEFAULT 'pending',
	"created_at" TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	"paid_at" TIMESTAMP NULL DEFAULT NULL,
	"customer_id" INTEGER NULL DEFAULT NULL,
	"delivery_type" VARCHAR(20) NOT NULL DEFAULT 'home',
	"store_id" VARCHAR(20) NULL,
	"store_name" VARCHAR(100) NULL,
	"cvs_type" VARCHAR(20) NULL,
	"address" VARCHAR(200) NULL,
	"recipient_name" VARCHAR(50) NULL,
	"recipient_phone" VARCHAR(20) NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "orders_customer_id_fkey" FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id") ON UPDATE NO ACTION ON DELETE NO ACTION
);
COMMENT ON TABLE "orders" IS '訂單表格';
COMMENT ON COLUMN "orders"."id" IS '訂單流水號，自動增加';
COMMENT ON COLUMN "orders"."order_id" IS '訂單編號（唯一）';
COMMENT ON COLUMN "orders"."amount" IS '訂單總金額';
COMMENT ON COLUMN "orders"."item_names" IS '訂單商品明細';
COMMENT ON COLUMN "orders"."status" IS '訂單狀態（預設 pending）';
COMMENT ON COLUMN "orders"."created_at" IS '建立時間';
COMMENT ON COLUMN "orders"."paid_at" IS '付款時間（可為空）';
COMMENT ON COLUMN "orders"."customer_id" IS '客戶 ID';
COMMENT ON COLUMN "orders"."delivery_type" IS '配送方式（home=宅配, cvs=超商取貨）';
COMMENT ON COLUMN "orders"."store_id" IS '超商門市代號（超商取貨時使用）';
COMMENT ON COLUMN "orders"."store_name" IS '超商門市名稱（超商取貨時使用）';
COMMENT ON COLUMN "orders"."cvs_type" IS '超商類型（超商取貨時使用）';
COMMENT ON COLUMN "orders"."address" IS '收件地址（宅配時使用）';
COMMENT ON COLUMN "orders"."recipient_name" IS '收件人姓名';
COMMENT ON COLUMN "orders"."recipient_phone" IS '收件人電話';

-- 建立索引以提升查詢效能
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_order_id ON orders(order_id);

-- 新增複合索引以優化訂單查詢
CREATE INDEX idx_orders_customer_created ON orders(customer_id, created_at DESC);
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);

-- 優化現有索引
DROP INDEX IF EXISTS idx_orders_created_at;  -- 移除單獨的 created_at 索引，因為已包含在複合索引中
DROP INDEX IF EXISTS idx_orders_status;      -- 移除單獨的 status 索引，因為已包含在複合索引中

-------------------------------------------------------------------------------------
CREATE TABLE "products" (
	"id" SERIAL NOT NULL,
	"name" TEXT NOT NULL,
	"price" INTEGER NOT NULL,
	"description" TEXT NOT NULL,
	"image_url" TEXT NOT NULL,
	"created_at" TIMESTAMP NULL DEFAULT now(),
	"category" VARCHAR(255) NOT NULL DEFAULT NULL::character varying,
	PRIMARY KEY ("id")
);
COMMENT ON TABLE "products" IS '商品表格';
COMMENT ON COLUMN "products"."id" IS '商品 ID，主鍵，自動增加';
COMMENT ON COLUMN "products"."name" IS '商品名稱，必填';
COMMENT ON COLUMN "products"."price" IS '商品價格，必填，整數';
COMMENT ON COLUMN "products"."description" IS '商品描述，選填';
COMMENT ON COLUMN "products"."image_url" IS '商品圖片網址，選填';
COMMENT ON COLUMN "products"."created_at" IS '商品建立時間，預設為當下時間';
COMMENT ON COLUMN "products"."category" IS '商品分類，可多分類用「#」分隔';

-- 建立索引以提升查詢效能
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_created_at ON products(created_at);

-- 建立複合索引，用於商品搜尋
CREATE INDEX idx_products_search ON products(name, description);

-------------------------------------------------------------------------------------
CREATE TABLE "customers" (
	"customer_id" SERIAL NOT NULL,
	"username" VARCHAR(50) NOT NULL,
	"name" VARCHAR(50) NOT NULL,
	"email" VARCHAR(100) NOT NULL,
	"phone" VARCHAR(20) NOT NULL,
	"password" VARCHAR(100) NOT NULL,
	"created_at" TIMESTAMP NULL DEFAULT now(),
	"address" VARCHAR(255) NOT NULL DEFAULT NULL::character varying,
	"is_verified" BOOLEAN NULL DEFAULT false,
	"verification_token" VARCHAR(255) NULL DEFAULT NULL,
	"token_expiry" TIMESTAMPTZ NULL DEFAULT NULL,
	PRIMARY KEY ("customer_id"),
	UNIQUE ("username")
);
COMMENT ON TABLE "customers" IS '客戶表格';
COMMENT ON COLUMN "customers"."customer_id" IS '客戶 ID，自動增加';
COMMENT ON COLUMN "customers"."username" IS '使用者名稱，唯一且必填';
COMMENT ON COLUMN "customers"."name" IS '使用者姓名，必填';
COMMENT ON COLUMN "customers"."email" IS '電子郵件，可選填';
COMMENT ON COLUMN "customers"."phone" IS '電話，可選填';
COMMENT ON COLUMN "customers"."password" IS '密碼（bcrypt 雜湊後的結果），必填';
COMMENT ON COLUMN "customers"."created_at" IS '建立時間，預設當下';
COMMENT ON COLUMN "customers"."address" IS '地址';
COMMENT ON COLUMN "customers"."is_verified" IS '是否驗證';
COMMENT ON COLUMN "customers"."verification_token" IS '驗證令牌';
COMMENT ON COLUMN "customers"."token_expiry" IS '驗證令牌過期時間';

-- 建立客戶相關索引
CREATE INDEX idx_customers_username ON customers(username);
CREATE INDEX idx_customers_email ON customers(email);

-------------------------------------------------------------------------------------
CREATE TABLE "shipments" (
	"shipment_id" SERIAL NOT NULL,
	"order_id" VARCHAR(50) NOT NULL,
	"recipient_name" VARCHAR(50) NOT NULL,
	"delivery_type" VARCHAR(20) NOT NULL DEFAULT 'home',
	"store_id" VARCHAR(20) NULL,
	"store_name" VARCHAR(100) NULL,
	"cvs_type" VARCHAR(20) NULL,
	"address" VARCHAR(200) NULL,
	"status" VARCHAR(20) NOT NULL,
	"created_at" TIMESTAMP NULL DEFAULT now(),
	PRIMARY KEY ("shipment_id")
);
COMMENT ON TABLE "shipments" IS '出貨單表格';
COMMENT ON COLUMN "shipments"."shipment_id" IS '出貨單 ID，自動增加';
COMMENT ON COLUMN "shipments"."order_id" IS '對應的訂單編號';
COMMENT ON COLUMN "shipments"."recipient_name" IS '收件人姓名';
COMMENT ON COLUMN "shipments"."delivery_type" IS '配送方式（home=宅配, cvs=超商取貨）';
COMMENT ON COLUMN "shipments"."store_id" IS '超商門市代號（超商取貨時使用）';
COMMENT ON COLUMN "shipments"."store_name" IS '超商門市名稱（超商取貨時使用）';
COMMENT ON COLUMN "shipments"."cvs_type" IS '超商類型（超商取貨時使用）';
COMMENT ON COLUMN "shipments"."address" IS '收件地址（宅配時使用）';
COMMENT ON COLUMN "shipments"."status" IS '出貨狀態（例：pending、shipped...）';
COMMENT ON COLUMN "shipments"."created_at" IS '建立時間';

-- 建立索引以提升查詢效能
CREATE INDEX idx_shipments_order_id ON shipments(order_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_shipments_created_at ON shipments(created_at);

-------------------------------------------------------------------------------------
CREATE TABLE "admin_users" (
    id SERIAL PRIMARY KEY,                              -- 流水號
    username VARCHAR(50) UNIQUE NOT NULL,               -- 帳號
    password TEXT NOT NULL,                             -- bcrypt 雜湊後的密碼
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 建立時間
    notes TEXT NULL DEFAULT NULL,                        -- 備註
    PRIMARY KEY ("id"),
    UNIQUE ("username")
);

COMMENT ON TABLE "admin_users" IS '管理員使用者表格';
COMMENT ON COLUMN "admin_users"."id" IS '流水號';
COMMENT ON COLUMN "admin_users"."username" IS '管理員帳號';
COMMENT ON COLUMN "admin_users"."password" IS '密碼（bcrypt 雜湊）';
COMMENT ON COLUMN "admin_users"."created_at" IS '建立時間';
COMMENT ON COLUMN "admin_users"."notes" IS '備註';

-- 建立管理員相關索引
CREATE INDEX idx_admin_users_username ON admin_users(username);

-- 新增使用者管理員,帳號admin密碼1234
-- 生成 python -c "import bcrypt; print(bcrypt.hashpw(b'1234', bcrypt.gensalt()).decode())"
-- 驗證 python -c "import bcrypt; print(bcrypt.checkpw(b'1234', b'$2b$12$VRZbqsMIwOa5NeJqG/BkduteRLXKnmfu5pNxd1obytRFLhs0ccYlq'))"
-- INSERT INTO admin_users (username, password)
-- VALUES ('admin', '$2b$12$k56Kb.WBCHwpNxnX9WmWOu9FDe9wTNQtL/eIA4aCRvjErQ0lnbl5C');
-- UPDATE admin_users
-- SET password = '$2b$12$GlHpWCpnlVjGFkcEFvSJDeYDMIW7otvygdBaewrnui/5oT6TTEMui'
-- WHERE username = 'admin';
---
CREATE TABLE "cleanup_logs" (
	"id" SERIAL NOT NULL,
	"operation" VARCHAR(50) NULL DEFAULT NULL,
	"records_affected" INTEGER NULL DEFAULT NULL,
	"executed_at" TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);
COMMENT ON TABLE "cleanup_logs" IS '清除日誌表格';
COMMENT ON COLUMN "cleanup_logs"."id" IS '流水號';
COMMENT ON COLUMN "cleanup_logs"."operation" IS '操作';
COMMENT ON COLUMN "cleanup_logs"."records_affected" IS '影響筆數';
COMMENT ON COLUMN "cleanup_logs"."executed_at" IS '執行時間';

-------------------------------------------------------------------------------------
-- 退貨物流表格
CREATE TABLE return_logistics (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    logistics_id VARCHAR(50) NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    cvs_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 建立索引以提升查詢效能
CREATE INDEX idx_return_logistics_order_id ON return_logistics(order_id);
CREATE INDEX idx_return_logistics_logistics_id ON return_logistics(logistics_id);
CREATE INDEX idx_return_logistics_status ON return_logistics(status);

COMMENT ON TABLE "return_logistics" IS '退貨物流表格';
COMMENT ON COLUMN "return_logistics"."id" IS '流水號';
COMMENT ON COLUMN "return_logistics"."order_id" IS '訂單編號';
COMMENT ON COLUMN "return_logistics"."logistics_id" IS '物流編號';
COMMENT ON COLUMN "return_logistics"."store_id" IS '7-11 店號';
COMMENT ON COLUMN "return_logistics"."store_name" IS '7-11 店名';
COMMENT ON COLUMN "return_logistics"."cvs_type" IS '超商類型';
COMMENT ON COLUMN "return_logistics"."status" IS '退貨狀態';
COMMENT ON COLUMN "return_logistics"."created_at" IS '建立時間';
COMMENT ON COLUMN "return_logistics"."updated_at" IS '更新時間';