PREPARE get_sales_by_region(VARCHAR) AS
SELECT
    o.region,
    SUM(oi.sales) AS total_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.region = $1
GROUP BY o.region;

-- Ví dụ thực thi:
-- EXECUTE get_sales_by_region('West');
