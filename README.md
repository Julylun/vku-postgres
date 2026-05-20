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
## 📁 3. Cấu trúc thư mục (Folder Structure)
Dự án được thiết kế theo chuẩn module hóa, dễ dàng bảo trì và mở rộng:

```text
supermarket/
│
├── core/                # Logic xử lý chính (Backend)
│   ├── db.py            # Hàm kết nối PostgreSQL và truy xuất dữ liệu (dùng Pandas)
│   └── pipeline.py      # Script thực thi tuần tự các file SQL để build Data Warehouse
│
├── data/                # Chứa file dữ liệu thô (đã cấu hình .gitignore)
│   └── supermarket.csv  # Dữ liệu nguồn (Raw data)
│
├── schemas/             # File SQL phân tách logic (DDL & DML)
│   ├── 1_create_staging_tabel.sql
│   ├── ... (các bước transform, view, index)
│   └── 12_rbac_security.sql
│
├── tabs/                # Giao diện UI chia nhỏ theo từng Tab (Streamlit)
│   ├── pipeline.py      # Giám sát tiến trình chạy
│   ├── explorer.py      # Truy vấn trực tiếp các Bảng/View
│   ├── dashboard.py     # Vẽ biểu đồ KPI, Line, Pie
│   ├── interactive.py   # Test Trigger, Procedure, Function
│   └── migration.py     # Di trú dữ liệu (Backup/Restore)
│
├── app.py               # File gốc khởi chạy ứng dụng Web
├── requirements.txt     # Danh sách thư viện Python
├── db_backup.sh         # Script CLI để dump database
└── db_restore.sh        # Script CLI để restore database
```

---
## 🛡️ 4. Tài khoản Test (Sau khi chạy Pipeline thành công)
Hệ thống RBAC tự động sinh ra 3 tài khoản để bạn kiểm thử bảo mật:
- **`admin_user` / `admin123`**: Toàn quyền thao tác, dùng để chạy Data Pipeline và Backup.
- **`entry_user` / `entry123`**: Quyền vận hành (Chỉ Insert/Update, gọi Trigger).
- **`test` / `test`**: Quyền Analyst (Chỉ được SELECT để xem data, chống ghi đè).