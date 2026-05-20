-- PROCEDURE: Cập nhật phương thức giao hàng
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

-- PROCEDURE: Tăng doanh thu bán hàng theo tỷ lệ phần trăm
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
