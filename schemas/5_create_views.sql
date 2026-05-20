-- View Tính doanh thu theo Region và Category
CREATE VIEW v_sales_by_region_category AS
SELECT 
    o.region,
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.region, p.category;

-- View Thống kê doanh thu theo Tháng/Năm
CREATE VIEW v_sales_trend AS
SELECT 
    to_char(o.order_date, 'YYYY-MM') AS order_month,
    SUM(oi.sales) AS monthly_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY to_char(o.order_date, 'YYYY-MM')
ORDER BY order_month;

-- MATERIALIZED VIEW: Tổng doanh thu theo Category
CREATE MATERIALIZED VIEW mv_category_sales AS
SELECT
    p.category,
    SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;

-- Lệnh làm mới dữ liệu (Chạy khi cần cập nhật dữ liệu)
-- REFRESH MATERIALIZED VIEW mv_category_sales;
