-- =========================================================
-- 12. ROLE-BASED ACCESS CONTROL (RBAC)
-- Kịch bản phân quyền cho Data Warehouse Supermarket
-- =========================================================

-- ==========================================
-- BƯỚC 1 & 2: TẠO ROLES (GROUPS & USERS)
-- Thay vì xóa (DROP) gây lỗi liên đới tới các Database khác (như db được restore),
-- ta dùng khối DO để kiểm tra, nếu chưa có thì CREATE, nếu có rồi thì giữ nguyên.
-- ==========================================
DO $$
BEGIN
    -- Tạo Groups
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_admin') THEN
        CREATE ROLE data_admin;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_analyst') THEN
        CREATE ROLE data_analyst;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_entry') THEN
        CREATE ROLE data_entry;
    END IF;

    -- Tạo Users
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test') THEN
        CREATE ROLE "test" WITH LOGIN PASSWORD 'test';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin_user') THEN
        CREATE ROLE "admin_user" WITH LOGIN PASSWORD 'admin123';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_user') THEN
        CREATE ROLE "analyst_user" WITH LOGIN PASSWORD 'read123';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'entry_user') THEN
        CREATE ROLE "entry_user" WITH LOGIN PASSWORD 'entry123';
    END IF;
END $$;


-- ==========================================
-- BƯỚC 3: CẤP QUYỀN (PRIVILEGES) CHO TỪNG NHÓM
-- ==========================================

-- 3.1. Nhóm DATA ADMIN (Toàn quyền trên schema public)
GRANT ALL PRIVILEGES ON SCHEMA public TO data_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO data_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO data_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO data_admin;
GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA public TO data_admin;

-- 3.2. Nhóm DATA ANALYST (Chỉ đọc - Read Only)
GRANT USAGE ON SCHEMA public TO data_analyst;
-- Cấp quyền SELECT trên toàn bộ Bảng và Views (Bao gồm cả Materialized View)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO data_analyst;
-- (Lưu ý: Mặc định Postgres không cho phép tự động SELECT các bảng tạo MỚI trong tương lai,
--  nên dùng lệnh ALTER DEFAULT PRIVILEGES để đảm bảo analyst luôn đọc được bảng mới)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO data_analyst;
-- Cấp quyền chạy Function (để xem report)
GRANT EXECUTE ON FUNCTION fn_total_sales_by_region(VARCHAR) TO data_analyst;
GRANT EXECUTE ON FUNCTION fn_customer_order_count(VARCHAR) TO data_analyst;

-- 3.3. Nhóm DATA ENTRY (Vận hành, Nhập liệu)
GRANT USAGE ON SCHEMA public TO data_entry;
-- Cho phép đọc/ghi/cập nhật bảng Orders và Order_items
GRANT SELECT, INSERT, UPDATE ON orders TO data_entry;
GRANT SELECT, INSERT, UPDATE ON order_items TO data_entry;
GRANT SELECT ON products TO data_entry; -- Chỉ đọc products
GRANT SELECT ON customers TO data_entry; -- Chỉ đọc customers

-- Cho phép thao tác với bảng sales_audit và chuỗi SEQUENCE tự tăng của nó (quan trọng cho Trigger)
GRANT SELECT, INSERT ON sales_audit TO data_entry;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE sales_audit_audit_id_seq TO data_entry;

-- Cho phép chạy Stored Procedure cập nhật dữ liệu
GRANT EXECUTE ON PROCEDURE pr_update_ship_mode(VARCHAR, VARCHAR) TO data_entry;
GRANT EXECUTE ON PROCEDURE pr_increase_sales(NUMERIC) TO data_entry;
GRANT EXECUTE ON PROCEDURE pr_reassign_customer_segment(VARCHAR, VARCHAR) TO data_entry;

-- Quyền cao nhất cho admin
GRANT EXECUTE ON PROCEDURE pr_delete_customer_completely(VARCHAR) TO data_admin;

-- Cho phép entry_user chạy Function liên quan đến Trigger (bắt buộc để kích hoạt Trigger thành công)
GRANT EXECUTE ON FUNCTION fn_log_sales_update() TO data_entry;
GRANT EXECUTE ON FUNCTION fn_validate_ship_date() TO data_entry;


-- ==========================================
-- BƯỚC 4: GÁN USER VÀO CÁC NHÓM TƯƠNG ỨNG (GRANT ROLE)
-- ==========================================
-- Gán user 'test' vào nhóm data_analyst để bạn thử nghiệm quyền chỉ đọc (Read-Only)
GRANT data_analyst TO "test";

GRANT data_admin TO "admin_user";
GRANT data_analyst TO "analyst_user";
GRANT data_entry TO "entry_user";
