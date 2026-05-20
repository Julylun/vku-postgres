-- =========================================================
-- 12. ROLE-BASED ACCESS CONTROL (RBAC)
-- Kịch bản phân quyền cho Data Warehouse Supermarket
-- =========================================================

-- ==========================================
-- BƯỚC 1: XÓA ROLES CŨ (NẾU ĐÃ TỒN TẠI ĐỂ RE-RUN)
-- ==========================================
-- Gỡ bỏ các Role khỏi các User trước khi xóa (Revoke membership)
DO $$
BEGIN
    -- Chỉ thực hiện nếu các Role này đã tồn tại
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_analyst') THEN
        REVOKE data_analyst FROM "test";
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_admin') THEN
        REVOKE data_admin FROM "admin_user";
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_analyst') THEN
        REVOKE data_analyst FROM "analyst_user";
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'data_entry') THEN
        REVOKE data_entry FROM "entry_user";
    END IF;
END $$;

-- Xóa User (Roles có LOGIN)
DROP ROLE IF EXISTS "test";
DROP ROLE IF EXISTS "admin_user";
DROP ROLE IF EXISTS "analyst_user";
DROP ROLE IF EXISTS "entry_user";

-- Xóa Group (Roles không có LOGIN)
DROP ROLE IF EXISTS data_admin;
DROP ROLE IF EXISTS data_analyst;
DROP ROLE IF EXISTS data_entry;


-- ==========================================
-- BƯỚC 2: TẠO CÁC NHÓM VAI TRÒ (GROUPS)
-- (Roles KHÔNG có quyền đăng nhập)
-- ==========================================
CREATE ROLE data_admin;
CREATE ROLE data_analyst;
CREATE ROLE data_entry;


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
-- Cấp quyền SELECT trên toàn bộ Bảng và Views
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
-- Cho phép chạy Stored Procedure cập nhật dữ liệu
GRANT EXECUTE ON PROCEDURE pr_update_ship_mode(VARCHAR, VARCHAR) TO data_entry;
GRANT EXECUTE ON PROCEDURE pr_increase_sales(NUMERIC) TO data_entry;


-- ==========================================
-- BƯỚC 4: TẠO USERS ĐỂ ĐĂNG NHẬP
-- (Roles CÓ quyền đăng nhập)
-- ==========================================
CREATE ROLE "test" WITH LOGIN PASSWORD 'test';
CREATE ROLE "admin_user" WITH LOGIN PASSWORD 'admin123';
CREATE ROLE "analyst_user" WITH LOGIN PASSWORD 'read123';
CREATE ROLE "entry_user" WITH LOGIN PASSWORD 'entry123';


-- ==========================================
-- BƯỚC 5: GÁN USER VÀO CÁC NHÓM TƯƠNG ỨNG (GRANT ROLE)
-- ==========================================
-- Gán user 'test' vào nhóm data_analyst để bạn thử nghiệm quyền chỉ đọc (Read-Only)
GRANT data_analyst TO "test";

GRANT data_admin TO "admin_user";
GRANT data_analyst TO "analyst_user";
GRANT data_entry TO "entry_user";
