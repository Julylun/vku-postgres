# 📚 Tóm tắt Hệ thống Data Warehouse (Supermarket)

Tài liệu này tóm tắt sơ lược về các đối tượng cơ sở dữ liệu nâng cao (Database Objects) đã được thiết lập trong dự án. Tất cả các đối tượng này đều tuân thủ chặt chẽ kiến trúc Data Warehouse và hệ thống phân quyền (RBAC).

---

## 1. Views & Materialized Views (Truy xuất & Phân tích)
*Views dùng để lưu sẵn các câu truy vấn phức tạp (ảo), trong khi Materialized Views lưu trữ kết quả truy vấn thành dạng bảng vật lý trên ổ cứng để tăng tốc đọc.*

*   **`v_sales_by_region_category`**: Báo cáo tổng doanh thu nhóm theo từng Vùng (Region) và Ngành hàng (Category).
*   **`v_sales_trend`**: Báo cáo xu hướng tăng/giảm doanh thu theo từng Tháng.
*   **`v_customer_lifetime_value`**: Tính toán giá trị vòng đời của từng khách hàng (Số đơn đã mua, Tổng chi tiêu, Giá trị trung bình/đơn). Phân tích hiệu suất khách hàng (CLV).
*   **`v_delayed_shipments`**: Tìm ra các đơn hàng giao trễ (ship_date trễ hơn order_date trên 5 ngày). Phục vụ cho báo cáo vận hành.
*   **`mv_category_sales` (Materialized)**: Bảng lưu kết quả doanh thu tổng hợp theo Category. (Cần dùng lệnh `REFRESH MATERIALIZED VIEW` để cập nhật).
*   **`mv_state_city_sales` (Materialized)**: Bảng lưu kết quả doanh thu chi tiết tới cấp độ Tỉnh/Thành phố.

---

## 2. Functions (Hàm xử lý Dữ liệu)
*Functions trả về một kết quả (hoặc một bảng kết quả) sau khi thực hiện các thuật toán tính toán.*

*   **`fn_total_sales_by_region(region)`**: Trả về tổng doanh thu ($) của một vùng cụ thể (Kiểu dữ liệu NUMERIC).
*   **`fn_customer_order_count(customer_id)`**: Trả về tổng số lượng đơn hàng mà một khách hàng đã đặt (Kiểu dữ liệu INTEGER).
*   **`fn_top_products_by_month(month, limit)`**: Trả về danh sách (Table) các sản phẩm bán chạy nhất trong một tháng được chỉ định (vd: '2016-11'). Hữu ích cho Dashboard.
*   **`fn_get_customer_status(customer_id)`**: Tính toán trạng thái hoạt động của khách hàng (`Active`, `At Risk`, `Churned`) dựa vào khoảng cách từ ngày mua cuối cùng đến nay.
*   **`fn_log_sales_update()`**: Hàm chạy ngầm phục vụ cho `trg_sales_update`. Ghi vết lịch sử khi cột `sales` bị thay đổi.
*   **`fn_validate_ship_date()`**: Hàm chạy ngầm phục vụ cho `trg_validate_dates`. Tự động gán `ship_date = order_date` nếu phát hiện lỗi logic về thời gian.

---

## 3. Procedures (Thủ tục Vận hành)
*Khác với Function, Procedures dùng để THỰC THI sự thay đổi dữ liệu (INSERT, UPDATE, DELETE) hàng loạt và hỗ trợ Transaction (COMMIT/ROLLBACK). Hệ thống RBAC quản lý quyền chạy các Procedures này rất nghiêm ngặt.*

*   **`pr_update_ship_mode(order_id, mode)`**: Cập nhật lại phương thức giao hàng cho một đơn. (Quyền: Vận hành).
*   **`pr_increase_sales(percent)`**: Tăng đồng loạt doanh thu của tất cả các mặt hàng lên X phần trăm (Chạy chiến dịch giá). (Quyền: Vận hành).
*   **`pr_reassign_customer_segment(old, new)`**: Thay tên/Chuyển đổi phân khúc khách hàng hàng loạt. (Quyền: Vận hành).
*   **`pr_delete_customer_completely(customer_id)`**: Xóa sạch sẽ toàn bộ thông tin và lịch sử mua hàng của một khách hàng. Giải quyết triệt để lỗi vi phạm khóa ngoại (Cascade Delete: Xóa `order_items` -> `orders` -> `customer_profiles` -> `customers`). **(Quyền: Chỉ dành cho Admin).**

---

## 4. Triggers (Cò súng Tự động)
*Triggers tự động chạy ngầm một Function khi có một sự kiện (INSERT, UPDATE, DELETE) diễn ra trên bảng.*

*   **`trg_sales_update`**: Gắn trên bảng `order_items` (Sự kiện AFTER UPDATE). Tự động bắt sự kiện khi doanh thu (sales) bị sửa đổi, sau đó ghi lại lịch sử giá cũ, giá mới, thời gian sửa vào bảng kiểm toán `sales_audit`.
*   **`trg_validate_dates`**: Gắn trên bảng `orders` (Sự kiện BEFORE INSERT/UPDATE). Kích hoạt trước khi ghi dữ liệu xuống DB để kiểm tra tính hợp lệ. Nếu nhân viên nhập ngày giao hàng (`ship_date`) xảy ra TRƯỚC ngày đặt hàng (`order_date`), hệ thống sẽ tự động ép ngày giao bằng ngày đặt để chống rác dữ liệu.

---

## 5. Dữ liệu nâng cao (Advanced Types)
*PostgreSQL nổi tiếng với khả năng xử lý dữ liệu bán cấu trúc (Semi-structured data).*

*   **Kiểu ARRAY (Mảng)**: Bảng `product_tags` lưu trữ nhiều tag của một sản phẩm trong một mảng `TEXT[]` duy nhất (Ví dụ: `{'wood', 'furniture'}`). Giúp tìm kiếm linh hoạt bằng toán tử `ANY`.
*   **Kiểu JSONB**: Bảng `customer_profiles` lưu trữ cấu hình hồ sơ khách hàng không định dạng (Tuổi, Điểm thưởng, Sở thích) dưới dạng đối tượng JSON. Hỗ trợ query sâu vào các key như `profile->>'membership'`.
