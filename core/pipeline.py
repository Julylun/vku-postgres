import os
import time

import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(BASE_DIR, "schemas")
CSV_FILE = os.path.join(BASE_DIR, "data", "supermarket.csv")

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


def run_pipeline(db_params, progress_bar, status_text, log_area, st):
    conn = None
    cur = None
    logs = []

    def add_log(message):
        logs.append(message)
        log_area.code("\n".join(logs), language="bash")

    try:
        status_text.info("Đang khởi tạo...")
        add_log("=== BẮT ĐẦU CHẠY PIPELINE ===")

        add_log("Đang kết nối Database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cur = conn.cursor()
        add_log("-> Kết nối DB thành công!")
        progress_bar.progress(10)

        status_text.info("Đang dọn dẹp Database cũ...")
        add_log("-> Đang Drop Schema 'public' để làm sạch DB...")
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        add_log("-> Dọn dẹp thành công!")

        # Bước 1
        file_1 = os.path.join(SCHEMA_DIR, "1_create_staging_tabel.sql")
        add_log("1. Đang chạy: 1_create_staging_tabel.sql (Tạo bảng Staging)...")
        with open(file_1, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        add_log("-> Tạo bảng Staging thành công!")
        progress_bar.progress(20)

        # Bước 1.5
        status_text.info("Đang import dữ liệu CSV...")
        add_log(
            f"1.5. Đang import dữ liệu từ file CSV: {os.path.basename(CSV_FILE)} ..."
        )
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            sql_copy = "COPY supermarket_raw FROM STDIN WITH CSV HEADER"
            cur.copy_expert(sql_copy, f)
        add_log("-> Import CSV thành công!")
        progress_bar.progress(35)

        # Bước 2->12
        status_text.info("Bắt đầu xử lý dữ liệu, tạo Schema và phân quyền (RBAC)...")
        add_log("2. Chạy các tiến trình Transform, Index, Views và RBAC...")

        step_progress = 60 / len(SQL_FILES)
        current_progress = 35

        for filename in SQL_FILES:
            filepath = os.path.join(SCHEMA_DIR, filename)
            if os.path.exists(filepath):
                add_log(f"--> Đang chạy: {filename} ...")
                with open(filepath, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                add_log(f"    ✅ Hoàn thành: {filename}")
            else:
                add_log(f"    ⚠️  Bỏ qua: Không tìm thấy file {filename}")

            current_progress += step_progress
            progress_bar.progress(int(current_progress))
            time.sleep(0.5)

        add_log("===========================================")
        add_log("=== PIPELINE HOÀN TẤT THÀNH CÔNG! ===")
        add_log("===========================================")
        progress_bar.progress(100)
        status_text.success("🎉 Toàn bộ Pipeline đã chạy thành công!")
        st.balloons()

    except psycopg2.Error as e:
        add_log(f"\n❌ LỖI DATABASE:\n{e}")
        status_text.error("Gặp lỗi trong quá trình thực thi Database.")
        progress_bar.progress(100)
    except FileNotFoundError as e:
        add_log(f"\n❌ LỖI KHÔNG TÌM THẤY FILE:\n{e}")
        status_text.error("Gặp lỗi thiếu file hệ thống.")
        progress_bar.progress(100)
    except Exception as e:
        add_log(f"\n❌ LỖI HỆ THỐNG:\n{e}")
        status_text.error("Gặp lỗi hệ thống không xác định.")
        progress_bar.progress(100)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
