-- =========================================================
-- 2. CÁC BẢNG DANH MỤC TRONG MÔ HÌNH CHUẨN HÓA (DIMENSIONS)
-- =========================================================

-- Bảng Vùng miền
CREATE TABLE regions (
    region_name VARCHAR(50) PRIMARY KEY
);

-- Bảng Khách hàng
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(150),
    segment VARCHAR(50)
);

-- Bảng Sản phẩm
CREATE TABLE products (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name TEXT,
    category VARCHAR(100),
    sub_category VARCHAR(100)
);

-- =========================================================
-- 3. CÁC BẢNG SỰ KIỆN TRONG MÔ HÌNH CHUẨN HÓA (FACTS)
-- =========================================================

-- Bảng Đơn hàng (Tổng quát)
CREATE TABLE orders (
    order_id VARCHAR(30) PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),

    CONSTRAINT fk_customer
        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_region
        FOREIGN KEY(region)
        REFERENCES regions(region_name)
);

-- Bảng Chi tiết mặt hàng trong đơn
CREATE TABLE order_items (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(30),
    product_id VARCHAR(30),
    sales NUMERIC(12,2),

    CONSTRAINT fk_order
        FOREIGN KEY(order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_product
        FOREIGN KEY(product_id)
        REFERENCES products(product_id)
);

-- =========================================================
-- 4. BẢNG PHÂN VÙNG DỮ LIỆU (PARTITION TABLES)
-- =========================================================

-- Bảng cấu trúc phân vùng chính
CREATE TABLE orders_partitioned (
    order_id VARCHAR(30),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50)
)
PARTITION BY RANGE(order_date);

-- Các bảng phân vùng vật lý theo năm
CREATE TABLE orders_2015
PARTITION OF orders_partitioned
FOR VALUES FROM ('2015-01-01') TO ('2016-01-01');

CREATE TABLE orders_2016
PARTITION OF orders_partitioned
FOR VALUES FROM ('2016-01-01') TO ('2017-01-01');

-- =========================================================
-- 5. BẢNG ĐẶC THÙ BỔ TRỢ (AUDIT LOGS & EXTENDED DATA)
-- =========================================================

-- Bảng lưu vết lịch sử thay đổi doanh thu (Dùng cho Trigger)
CREATE TABLE sales_audit (
    audit_id SERIAL PRIMARY KEY,
    row_id INT,
    old_sales NUMERIC,
    new_sales NUMERIC,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng minh họa kiểu dữ liệu Mảng (ARRAY)
CREATE TABLE product_tags (
    product_id VARCHAR(30),
    tags TEXT[]
);

-- Bảng minh họa kiểu dữ liệu JSON hóa (JSONB)
CREATE TABLE customer_profiles (
    customer_id VARCHAR(20),
    profile JSONB
);
