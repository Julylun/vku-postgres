-- [1] Xếp hạng khách hàng theo tổng doanh thu (RANK)
SELECT
    c.customer_name,
    SUM(oi.sales) AS total_sales,
    RANK() OVER (ORDER BY SUM(oi.sales) DESC) AS sales_rank
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_name;

-- [2] Tính doanh thu lũy kế chạy dài qua các tháng (Cumulative Sales)
SELECT
    to_char(o.order_date, 'YYYY-MM') AS month,
    SUM(oi.sales) AS monthly_sales,
    SUM(SUM(oi.sales)) OVER (ORDER BY to_char(o.order_date, 'YYYY-MM')) AS cumulative_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY to_char(o.order_date, 'YYYY-MM')
ORDER BY month;

-- [3] Lấy ra chi tiết dòng sản phẩm có giá trị lớn nhất của từng khách hàng độc bản
SELECT DISTINCT ON (o.customer_id)
    o.customer_id,
    o.order_id,
    oi.sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
ORDER BY o.customer_id, oi.sales DESC;

-- [4] Đệ quy sinh chuỗi thời gian liên tục (Recursive CTE)
WITH RECURSIVE months AS (
    SELECT DATE '2020-01-01' AS month_date
    UNION ALL
    SELECT (month_date + INTERVAL '1 month')::DATE
    FROM months
    WHERE month_date < DATE '2020-12-01'
)
SELECT * FROM months;
