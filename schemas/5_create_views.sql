-- =========================================================
-- VIEW TỔNG HỢP VÀ PHÂN TÍCH
-- =========================================================

-- 1. View Tính doanh thu theo Region và Category
CREATE VIEW v_sales_by_region_category AS
SELECT
    o.region,
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.region, p.category;

-- 2. View Thống kê doanh thu theo Tháng/Năm
CREATE VIEW v_sales_trend AS
SELECT
    to_char(o.order_date, 'YYYY-MM') AS order_month,
    SUM(oi.sales) AS monthly_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY to_char(o.order_date, 'YYYY-MM')
ORDER BY order_month;

-- 3. [MỚI] View: Báo cáo hiệu suất Khách hàng (Customer Lifetime Value - CLV)
CREATE VIEW v_customer_lifetime_value AS
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.sales) AS total_spent,
    AVG(oi.sales) AS avg_order_value,
    MAX(o.order_date) AS last_purchase_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name, c.segment;

-- 4. [MỚI] View: Báo cáo tỷ lệ giao hàng chậm (Trễ hạn)
-- Giả định thời gian giao hàng kỳ vọng là < 5 ngày
CREATE VIEW v_delayed_shipments AS
SELECT
    order_id,
    order_date,
    ship_date,
    ship_mode,
    (ship_date - order_date) AS days_to_ship,
    CASE
        WHEN (ship_date - order_date) > 5 THEN 'Delayed'
        ELSE 'On Time'
    END AS shipping_status
FROM orders;


-- =========================================================
-- MATERIALIZED VIEWS (Dữ liệu cache để truy vấn siêu tốc)
-- =========================================================

-- 5. MATERIALIZED VIEW: Tổng doanh thu theo Category
CREATE MATERIALIZED VIEW mv_category_sales AS
SELECT
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;

-- 6. [MỚI] MATERIALIZED VIEW: Doanh thu chi tiết theo Tỉnh/Thành phố
CREATE MATERIALIZED VIEW mv_state_city_sales AS
SELECT
    o.state,
    o.city,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.sales) AS total_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.state, o.city;

-- Lệnh làm mới dữ liệu (Chạy khi cần cập nhật dữ liệu)
-- REFRESH MATERIALIZED VIEW mv_category_sales;
-- REFRESH MATERIALIZED VIEW mv_state_city_sales;
