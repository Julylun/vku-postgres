-- Bảng lưu vết lịch sử thay đổi doanh thu (Đã được tạo ở 2_create_dnf_tables.sql)
-- (Comment đoạn này lại để tránh lỗi relation already exists)
-- CREATE TABLE sales_audit (
--     audit_id SERIAL PRIMARY KEY,
--     row_id INT,
--     old_sales NUMERIC,
--     new_sales NUMERIC,
--     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- =========================================================
-- TRIGGER 1: KIỂM TOÁN THAY ĐỔI DOANH THU (AUDIT)
-- =========================================================
-- Hàm xử lý Trigger
CREATE OR REPLACE FUNCTION fn_log_sales_update()
RETURNS TRIGGER AS
$$
BEGIN
    -- Chỉ log khi giá trị sales thực sự thay đổi
    IF OLD.sales IS DISTINCT FROM NEW.sales THEN
        INSERT INTO sales_audit(row_id, old_sales, new_sales)
        VALUES(OLD.row_id, OLD.sales, NEW.sales);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Thiết lập Trigger kích hoạt sau khi UPDATE cột sales
CREATE TRIGGER trg_sales_update
AFTER UPDATE OF sales
ON order_items
FOR EACH ROW
EXECUTE FUNCTION fn_log_sales_update();


-- =========================================================
-- TRIGGER 2: TỰ ĐỘNG CẬP NHẬT NGÀY SHIP GIAO HÀNG (VALIDATION)
-- =========================================================
-- Đảm bảo ngày ship_date không bao giờ bé hơn (trước) order_date
CREATE OR REPLACE FUNCTION fn_validate_ship_date()
RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.ship_date < NEW.order_date THEN
        -- Nếu nhập sai, tự động sửa ship_date bằng order_date (giao hàng ngay trong ngày)
        NEW.ship_date := NEW.order_date;
        -- (Tùy chọn: Bạn có thể thay bằng RAISE EXCEPTION để chặn luôn lệnh INSERT/UPDATE)
        -- RAISE EXCEPTION 'Lỗi: Ngày giao hàng không thể trước ngày đặt hàng';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_dates
BEFORE INSERT OR UPDATE
ON orders
FOR EACH ROW
EXECUTE FUNCTION fn_validate_ship_date();
