
-- Chua tat ca thong tin
CREATE TABLE supermarket_raw (
    row_id INTEGER,
    order_id TEXT,
    order_date TEXT,    
    ship_date TEXT,       
    ship_mode TEXT,
    customer_id TEXT,
    customer_name TEXT,
    segment TEXT,
    country TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT, 
    region TEXT,
    product_id TEXT,
    category TEXT,
    sub_category TEXT,
    product_name TEXT,
    sales NUMERIC     
);
SELECT * FROM supermarket_raw;

-- Region
CREATE TABLE regions (
    region_name VARCHAR(50) PRIMARY KEY
);

INSERT INTO regions (region_name)
SELECT DISTINCT "region" FROM supermarket_raw;

-- Customer
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(150),
    segment VARCHAR(50)
);
INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT "customer_id", "customer_name", "segment" FROM supermarket_raw;


-- Products
CREATE TABLE products (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name TEXT,
    category VARCHAR(100),
    sub_category VARCHAR(100)
);
INSERT INTO products (product_id, product_name, category, sub_category)
SELECT DISTINCT ON (product_id)
    product_id,
    product_name,
    category,
    sub_category
FROM supermarket_raw
ORDER BY product_id;

SELECT * FROM products;


-- Orders
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
INSERT INTO orders (
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    country,
    city,
    state,
    postal_code,
    region
)
SELECT DISTINCT
    order_id,
    TO_DATE(order_date, 'DD/MM/YYYY'),
    TO_DATE(ship_date, 'DD/MM/YYYY'),
    ship_mode,
    customer_id,
    country,
    city,
    state,
    postal_code,
    region
FROM supermarket_raw;

SELECT * FROM orders;


-- Order items
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
INSERT INTO order_items (row_id, order_id, product_id, sales)
SELECT "row_id", "order_id", "product_id", "sales" FROM supermarket_raw;

SELECT * FROM order_items;

-- View Tinh to doanh thu theo Region và Category
CREATE VIEW v_sales_by_region_category AS
SELECT 
    o.region,
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.region, p.category;

-- View Thong ke doanh thu theo Tháng/Năm
CREATE VIEW v_sales_trend AS
SELECT 
    to_char(o.order_date, 'YYYY-MM') AS order_month,
    SUM(oi.sales) AS monthly_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY to_char(o.order_date, 'YYYY-MM')
ORDER BY order_month;

-- Index cho cac cot khoa ngoai de tang toc do JOIN
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_region ON orders(region);
CREATE INDEX idx_orderitems_order_id ON order_items(order_id);
CREATE INDEX idx_orderitems_product_id ON order_items(product_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);


-- =========================================================
-- 1. FUNCTION: Tính tổng doanh thu theo Region
-- =========================================================
CREATE OR REPLACE FUNCTION fn_total_sales_by_region(p_region VARCHAR)
RETURNS NUMERIC AS
$$
DECLARE
    total NUMERIC;
BEGIN
    SELECT SUM(oi.sales)
    INTO total
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.region = p_region;

    RETURN COALESCE(total, 0);
END;
$$ LANGUAGE plpgsql;

-- Test
SELECT fn_total_sales_by_region('West');



-- =========================================================
-- 2. FUNCTION: Đếm số đơn hàng của khách hàng
-- =========================================================
CREATE OR REPLACE FUNCTION fn_customer_order_count(p_customer_id VARCHAR)
RETURNS INTEGER AS
$$
DECLARE
    total_orders INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO total_orders
    FROM orders
    WHERE customer_id = p_customer_id;

    RETURN total_orders;
END;
$$ LANGUAGE plpgsql;

-- Test
SELECT fn_customer_order_count('CG-12520');



-- =========================================================
-- 3. PROCEDURE: Update ship mode
-- Procedure hỗ trợ COMMIT/ROLLBACK
-- =========================================================
CREATE OR REPLACE PROCEDURE pr_update_ship_mode(
    p_order_id VARCHAR,
    p_new_mode VARCHAR
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE orders
    SET ship_mode = p_new_mode
    WHERE order_id = p_order_id;

    COMMIT;
END;
$$;

-- Test
CALL pr_update_ship_mode('CA-2016-152156', 'First Class');



-- =========================================================
-- 4. PROCEDURE: Import dữ liệu sales tăng thêm %
-- =========================================================
CREATE OR REPLACE PROCEDURE pr_increase_sales(percent_value NUMERIC)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE order_items
    SET sales = sales + (sales * percent_value / 100);

    COMMIT;
END;
$$;

-- Test
CALL pr_increase_sales(5);



-- =========================================================
-- 5. TRIGGER: Tự động log khi UPDATE sales
-- =========================================================

-- Bảng log
CREATE TABLE sales_audit (
    audit_id SERIAL PRIMARY KEY,
    row_id INT,
    old_sales NUMERIC,
    new_sales NUMERIC,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function
CREATE OR REPLACE FUNCTION fn_log_sales_update()
RETURNS TRIGGER AS
$$
BEGIN
    INSERT INTO sales_audit(row_id, old_sales, new_sales)
    VALUES(OLD.row_id, OLD.sales, NEW.sales);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_sales_update
AFTER UPDATE OF sales
ON order_items
FOR EACH ROW
EXECUTE FUNCTION fn_log_sales_update();

-- Test
UPDATE order_items
SET sales = sales + 100
WHERE row_id = 1;



-- =========================================================
-- 6. MATERIALIZED VIEW
-- Tổng doanh thu theo Category
-- =========================================================
CREATE MATERIALIZED VIEW mv_category_sales AS
SELECT
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;

-- Refresh
REFRESH MATERIALIZED VIEW mv_category_sales;

SELECT * FROM mv_category_sales;



-- =========================================================
-- 7. WINDOW FUNCTION
-- Xếp hạng khách hàng theo doanh thu
-- =========================================================
SELECT
    c.customer_name,
    SUM(oi.sales) AS total_sales,

    RANK() OVER (
        ORDER BY SUM(oi.sales) DESC
    ) AS sales_rank

FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id

GROUP BY c.customer_name;



-- =========================================================
-- 8. WINDOW FUNCTION
-- Doanh thu lũy kế theo tháng
-- =========================================================
SELECT
    to_char(o.order_date, 'YYYY-MM') AS month,
    SUM(oi.sales) AS monthly_sales,

    SUM(SUM(oi.sales)) OVER (
        ORDER BY to_char(o.order_date, 'YYYY-MM')
    ) AS cumulative_sales

FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id

GROUP BY to_char(o.order_date, 'YYYY-MM')
ORDER BY month;



-- =========================================================
-- 9. DISTINCT ON
-- Lấy đơn hàng lớn nhất của mỗi khách hàng
-- =========================================================
SELECT DISTINCT ON (o.customer_id)
    o.customer_id,
    o.order_id,
    oi.sales

FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id

ORDER BY o.customer_id, oi.sales DESC;



-- =========================================================
-- 10. WITH RECURSIVE
-- Sinh chuỗi tháng liên tục
-- =========================================================
WITH RECURSIVE months AS (
    SELECT DATE '2020-01-01' AS month_date

    UNION ALL

    SELECT (month_date + INTERVAL '1 month')::DATE
    FROM months
    WHERE month_date < DATE '2020-12-01'
)

SELECT *
FROM months;



-- =========================================================
-- 11. PARTITION TABLE
-- Phân vùng theo năm order_date
-- =========================================================

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

-- Partition 2015
CREATE TABLE orders_2015
PARTITION OF orders_partitioned
FOR VALUES FROM ('2015-01-01') TO ('2016-01-01');

-- Partition 2016
CREATE TABLE orders_2016
PARTITION OF orders_partitioned
FOR VALUES FROM ('2016-01-01') TO ('2017-01-01');



-- =========================================================
-- 12. PREPARED STATEMENT
-- =========================================================
PREPARE get_sales_by_region(VARCHAR) AS
SELECT
    o.region,
    SUM(oi.sales) AS total_sales
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
WHERE o.region = $1
GROUP BY o.region;

-- Execute
EXECUTE get_sales_by_region('West');



-- =========================================================
-- 14. ARRAY Example
-- PostgreSQL hỗ trợ kiểu ARRAY
-- =========================================================
CREATE TABLE product_tags (
    product_id VARCHAR(30),
    tags TEXT[]
);

INSERT INTO product_tags
VALUES
('FUR-BO-10001798', ARRAY['furniture', 'wood', 'office']);

SELECT * FROM product_tags;



-- =========================================================
-- 15. JSONB Example
-- PostgreSQL hỗ trợ JSONB
-- =========================================================
CREATE TABLE customer_profiles (
    customer_id VARCHAR(20),
    profile JSONB
);

INSERT INTO customer_profiles
VALUES (
    'CG-12520',
    '{
        "age": 30,
        "membership": "gold",
        "preferences": ["office", "technology"]
    }'
);

SELECT *
FROM customer_profiles
WHERE profile->>'membership' = 'gold';