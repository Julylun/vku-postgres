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
