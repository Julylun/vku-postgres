-- FUNCTION: Tính tổng doanh thu theo Region
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

-- FUNCTION: Đếm số đơn hàng của khách hàng
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

-- [MỚI] FUNCTION: Tìm top N sản phẩm bán chạy nhất trong một tháng cụ thể
CREATE OR REPLACE FUNCTION fn_top_products_by_month(p_year_month VARCHAR, p_limit INT DEFAULT 5)
RETURNS TABLE (
    product_name TEXT,
    category VARCHAR,
    total_revenue NUMERIC
) AS
$$
BEGIN
    RETURN QUERY
    SELECT
        p.product_name,
        p.category,
        SUM(oi.sales) AS total_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE to_char(o.order_date, 'YYYY-MM') = p_year_month
    GROUP BY p.product_name, p.category
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- [MỚI] FUNCTION: Phân loại trạng thái khách hàng (Mới / Đang hoạt động / Rời bỏ)
CREATE OR REPLACE FUNCTION fn_get_customer_status(p_customer_id VARCHAR)
RETURNS VARCHAR AS
$$
DECLARE
    v_last_order_date DATE;
    v_days_since_last_order INT;
    v_status VARCHAR;
BEGIN
    -- Lấy ngày mua hàng gần nhất
    SELECT MAX(order_date) INTO v_last_order_date
    FROM orders
    WHERE customer_id = p_customer_id;

    IF v_last_order_date IS NULL THEN
        RETURN 'Not Found';
    END IF;

    -- Tính số ngày kể từ lần mua cuối (so với ngày dữ liệu mới nhất trong DB)
    SELECT (MAX(order_date) - v_last_order_date) INTO v_days_since_last_order
    FROM orders;

    -- Phân loại
    IF v_days_since_last_order <= 90 THEN
        v_status := 'Active (Mua gần đây)';
    ELSIF v_days_since_last_order <= 180 THEN
        v_status := 'At Risk (Sắp rời bỏ)';
    ELSE
        v_status := 'Churned (Đã rời bỏ)';
    END IF;

    RETURN v_status;
END;
$$ LANGUAGE plpgsql;
