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


-- [MỚI] PROCEDURE: Cập nhật/Sửa đổi thông tin phân khúc khách hàng hàng loạt
CREATE OR REPLACE PROCEDURE pr_reassign_customer_segment(
    p_old_segment VARCHAR,
    p_new_segment VARCHAR
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE customers
    SET segment = p_new_segment
    WHERE segment = p_old_segment;

    COMMIT;
END;
$$;


-- [MỚI] PROCEDURE: Xóa khách hàng và toàn bộ lịch sử đơn hàng của họ (Dọn dẹp rác/Tuân thủ quyền riêng tư)
-- (Sử dụng với tài khoản có quyền cao nhất)
CREATE OR REPLACE PROCEDURE pr_delete_customer_completely(
    p_customer_id VARCHAR
)
LANGUAGE plpgsql
AS
$$
BEGIN
    -- Xóa các order_items trước (Khóa ngoại)
    DELETE FROM order_items
    WHERE order_id IN (
        SELECT order_id FROM orders WHERE customer_id = p_customer_id
    );

    -- Xóa orders
    DELETE FROM orders WHERE customer_id = p_customer_id;

    -- Xóa customer_profiles (Bảng JSONB)
    DELETE FROM customer_profiles WHERE customer_id = p_customer_id;

    -- Xóa khách hàng
    DELETE FROM customers WHERE customer_id = p_customer_id;

    COMMIT;
END;
$$;
