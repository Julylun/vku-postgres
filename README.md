# 🛒 Supermarket Data Warehouse Pipeline

Dự án tự động hóa việc đưa dữ liệu CSV thô vào PostgreSQL, chuẩn hóa, đánh index, tạo phân vùng, phân quyền (RBAC) và backup tự động.

## ⚙️ 1. Yêu cầu hệ thống
- **PostgreSQL** (Đã bật và có tài khoản admin/postgres).
- **Python 3.x**
- Cài đặt thư viện: `pip install -r requirements.txt`

## 🚀 2. Hướng dẫn chạy (Cực nhanh)

### Bước 1: Cấu hình Database
Mở file `run_pipeline.py` (hoặc `run_pipeline.sh`), sửa biến mật khẩu (`your_password`) và database (`supermarket_db`) cho khớp với máy bạn. Đảm bảo DB này đã được tạo sẵn trong Postgres.

### Bước 2: Chạy ngầm Pipeline (CLI)
Mở Terminal / Git Bash và chạy 1 trong 2 lệnh sau:

**Dùng Python (Khuyên dùng cho Windows):**
```bash
python run_pipeline.py
```
**Dùng Bash (Linux/Mac/Git Bash):**
```bash
./run_pipeline.sh
```

### Bước 3: Theo dõi trên giao diện Web (Streamlit)
Để tương tác trực tiếp với Database, gọi Procedure, Test Trigger và Backup dữ liệu, hãy chạy App Streamlit:
```bash
streamlit run app.py
```
*Giao diện sẽ tự bật lên ở `http://localhost:8501`*

---
## 🛡️ Tài khoản Test (Sau khi chạy Pipeline thành công)
Hệ thống RBAC tự động sinh ra 3 tài khoản để bạn kiểm thử bảo mật:
- **`admin_user` / `admin123`**: Toàn quyền thao tác, dùng để chạy Data Pipeline và Backup.
- **`entry_user` / `entry123`**: Quyền vận hành (Chỉ Insert/Update, gọi Trigger).
- **`test` / `test`**: Quyền Analyst (Chỉ được SELECT để xem data, chống ghi đè).