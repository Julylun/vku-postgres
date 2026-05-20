-- Bảng lưu vết lịch sử thay đổi doanh thu (Đã được tạo ở 2_create_dnf_tables.sql)
-- (Comment đoạn này lại để tránh lỗi relation already exists)
-- CREATE TABLE sales_audit (
--     audit_id SERIAL PRIMARY KEY,
--     row_id INT,
--     old_sales NUMERIC,
--     new_sales NUMERIC,
--     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Hàm xử lý Trigger
CREATE OR REPLACE FUNCTION fn_log_sales_update()
RETURNS TRIGGER AS
$$
BEGIN
    INSERT INTO sales_audit(row_id, old_sales, new_sales)
    VALUES(OLD.row_id, OLD.sales, NEW.sales);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Thiết lập Trigger kích hoạt sau khi UPDATE cột sales
CREATE TRIGGER trg_sales_update
AFTER UPDATE OF sales
ON order_items
FOR EACH ROW
EXECUTE FUNCTION fn_log_sales_update();
