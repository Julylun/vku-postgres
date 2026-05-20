import os

import psycopg2

# ==========================================
# CẤU HÌNH KẾT NỐI DATABASE
# Hãy thay đổi thông tin này cho phù hợp với môi trường của bạn
# ==========================================
DB_PARAMS = {
    "host": "localhost",
    "port": "5432",
    "database": "supermarket_db",  # Thay bằng database của bạn
    "user": "test",
    "password": "test",  # Thay bằng password thật của bạn
}

# Đường dẫn thư mục chứa schemas và thư mục data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(BASE_DIR, "schemas")
CSV_FILE = os.path.join(BASE_DIR, "data", "supermarket.csv")

# Thứ tự các file SQL cần chạy (Bỏ qua file số 1 vì sẽ chạy riêng)
SQL_FILES = [
    "2_create_dnf_tables.sql",
    "3_migrate_and_transform_data.sql",
    "4_create_indexes.sql",
    "5_create_views.sql",
    "6_create_function.sql",
    "7_create_procedures.sql",
    "8_create_trigger.sql",
    "9_analytics_queries.sql",
    "10_prepared_statements.sql",
    "11_extended_types.sql",
    "12_rbac_security.sql",
]


def run_pipeline():
    conn = None
    cur = None
    try:
        print("=== BẮT ĐẦU CHẠY PIPELINE BẰNG PYTHON ===")

        # 1. Kết nối tới DB
        print("Đang kết nối Database...")
        conn = psycopg2.connect(**DB_PARAMS)
        # Bật autocommit để các câu lệnh CREATE/DROP không nằm trong transaction
        conn.autocommit = True
        cur = conn.cursor()
        print("-> Kết nối DB thành công!\n")

        # 2. Chạy Bước 1: Tạo bảng Staging
        file_1 = os.path.join(SCHEMA_DIR, "1_create_staging_tabel.sql")
        print("1. Đang chạy: 1_create_staging_tabel.sql (Tạo bảng Staging)...")
        with open(file_1, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        print("-> Tạo bảng Staging thành công!\n")

        # 3. Chạy Bước 1.5: Import CSV vào bảng supermarket_raw
        print(f"1.5. Đang import dữ liệu từ file CSV: {os.path.basename(CSV_FILE)} ...")
        # Sử dụng copy_expert để tối ưu tốc độ import và bỏ qua dòng header
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            # COPY table FROM STDIN. Định dạng CSV, có dòng tiêu đề.
            sql_copy = "COPY supermarket_raw FROM STDIN WITH CSV HEADER"
            cur.copy_expert(sql_copy, f)
        print("-> Import CSV thành công!\n")

        # 4. Chạy tuần tự các bước từ 2 đến 11
        print("2. Chạy các tiến trình Transform, Index, Views và Advanced Objects...")
        for filename in SQL_FILES:
            filepath = os.path.join(SCHEMA_DIR, filename)
            if os.path.exists(filepath):
                print(f"--> Đang chạy: {filename} ...")
                with open(filepath, "r", encoding="utf-8") as f:
                    # Chạy nội dung script
                    cur.execute(f.read())
                print(f"    ✅ Hoàn thành: {filename}")
            else:
                print(f"    ⚠️  Bỏ qua: Không tìm thấy file {filename}")

        print("\n=== PIPELINE HOÀN TẤT THÀNH CÔNG! ===")

    except psycopg2.Error as e:
        print(f"\n❌ LỖI DATABASE: {e}")
    except FileNotFoundError as e:
        print(f"\n❌ LỖI KHÔNG TÌM THẤY FILE: {e}")
    except Exception as e:
        print(f"\n❌ LỖI HỆ THỐNG: {e}")
    finally:
        # Đóng kết nối
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    run_pipeline()
