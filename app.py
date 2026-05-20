import os
import time

import pandas as pd
import psycopg2
import streamlit as st

st.set_page_config(
    page_title="Supermarket Data Warehouse", page_icon="⚙️", layout="wide"
)

# Đường dẫn thư mục
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


def get_connection(db_params):
    return psycopg2.connect(**db_params)


def fetch_data(query, db_params, params=None):
    """Hàm hỗ trợ lấy dữ liệu và trả về Pandas DataFrame"""
    conn = get_connection(db_params)
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=columns)
        return df
    finally:
        conn.close()


def main():
    st.title("⚙️ Supermarket Data Warehouse")

    with st.sidebar:
        st.header("1. Cấu hình Database")
        db_host = st.text_input("Host", "localhost")
        db_port = st.text_input("Port", "5432")
        db_name = st.text_input("Database Name", "supermarket_db")
        db_user = st.text_input("User", value="test")
        db_password = st.text_input("Password", value="test", type="password")

        st.info(
            "💡 **Gợi ý tài khoản**\n- **test** / **test**: Chỉ có quyền xem (Read-Only).\n- **admin_user** / **admin123**: Full quyền thao tác.\n- **entry_user** / **entry123**: Quyền nhập liệu."
        )

    db_params = {
        "host": db_host,
        "port": db_port,
        "database": db_name,
        "user": db_user,
        "password": db_password,
    }

    # Tạo 4 Tabs giao diện
    tab_pipeline, tab_explorer, tab_interactive, tab_migration = st.tabs(
        [
            "🚀 1. Pipeline Monitor",
            "🔍 2. Database Explorer",
            "⚡ 3. Interactive Tools",
            "🛡️ 4. Lifecycle & Migration",
        ]
    )

    # ==========================================
    # TAB 1: PIPELINE MONITOR
    # ==========================================
    with tab_pipeline:
        st.markdown(
            "Theo dõi quá trình Import dữ liệu và Build Data Warehouse từ file CSV."
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            start_btn = st.button(
                "🚀 Chạy lại Pipeline", type="primary", use_container_width=True
            )

        progress_bar = st.progress(0)
        status_text = st.empty()
        log_area = st.empty()

        if start_btn:
            if not db_password:
                st.warning("⚠️ Vui lòng nhập mật khẩu Database ở thanh bên (Sidebar).")
            elif db_user != "postgres" and db_user != "admin_user":
                st.error(
                    "⚠️ Bạn cần dùng tài khoản 'postgres' hoặc 'admin_user' để có quyền DROP/CREATE database pipeline!"
                )
            else:
                run_pipeline(db_params, progress_bar, status_text, log_area)

    # ==========================================
    # TAB 2: DATABASE EXPLORER
    # ==========================================
    with tab_explorer:
        st.header("🔍 Duyệt dữ liệu các Bảng & Views")
        st.markdown("Xem trực tiếp dữ liệu bên trong Data Warehouse.")

        try:
            # Lấy danh sách Tables & Views
            query_tables = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """
            tables_df = fetch_data(query_tables, db_params)
            table_list = tables_df["table_name"].tolist()

            selected_table = st.selectbox(
                "👉 Chọn một Bảng hoặc View để xem:", table_list
            )

            if selected_table:
                limit = st.slider(
                    "Số dòng hiển thị:",
                    min_value=10,
                    max_value=1000,
                    value=100,
                    step=10,
                )
                df = fetch_data(
                    f"SELECT * FROM {selected_table} LIMIT {limit};", db_params
                )
                st.dataframe(df, use_container_width=True)
                st.caption(f"Đang hiển thị {len(df)} dòng của '{selected_table}'.")

        except Exception as e:
            st.error(
                f"Lỗi truy vấn Database (Có thể do sai thông tin kết nối hoặc user không có quyền): {e}"
            )

    # ==========================================
    # TAB 3: INTERACTIVE TOOLS
    # ==========================================
    with tab_interactive:
        st.header("⚡ Tương tác với CSDL (Functions & Triggers)")
        st.markdown("Bạn đang đăng nhập bằng user: **`{}`**".format(db_user))

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("1. Gọi Function: Tổng doanh thu theo Region")
            region_input = st.selectbox(
                "Chọn Vùng (Region):", ["West", "East", "Central", "South"]
            )
            if st.button("Tính Doanh Thu"):
                try:
                    df_fn = fetch_data(
                        "SELECT fn_total_sales_by_region(%s) AS total_sales;",
                        db_params,
                        (region_input,),
                    )
                    st.success(
                        f"💰 Tổng doanh thu của vùng **{region_input}** là: **{df_fn.iloc[0]['total_sales']}**"
                    )
                except Exception as e:
                    st.error(f"Lỗi: {e}")

            st.markdown("---")

            st.subheader("2. Gọi Procedure: Cập nhật Phương thức Giao hàng")
            st.caption("Yêu cầu quyền admin_user hoặc entry_user")
            order_id_input = st.text_input(
                "Mã đơn hàng (Order ID):", value="CA-2016-152156"
            )
            ship_mode_input = st.selectbox(
                "Phương thức giao hàng mới:",
                ["First Class", "Second Class", "Standard Class", "Same Day"],
            )
            if st.button("Cập nhật Ship Mode"):
                try:
                    conn = get_connection(db_params)
                    conn.autocommit = True
                    cur = conn.cursor()
                    cur.execute(
                        "CALL pr_update_ship_mode(%s, %s);",
                        (order_id_input, ship_mode_input),
                    )
                    st.success(f"✅ Đã cập nhật thành công đơn hàng {order_id_input}!")
                    conn.close()
                except Exception as e:
                    st.error(
                        f"Lỗi truy cập (Có thể do User '{db_user}' không có quyền UPDATE/EXECUTE): {e}"
                    )

        with col_right:
            st.subheader("3. Test Trigger: Audit Log khi cập nhật Sales")
            st.caption(
                "Khi bạn tăng giá trị Sales của một món hàng, Trigger sẽ tự động ghi log vào bảng sales_audit. Yêu cầu admin_user hoặc entry_user."
            )
            row_id_input = st.number_input(
                "ID của Order Item (row_id):", min_value=1, value=1, step=1
            )
            sales_add_input = st.number_input(
                "Số tiền Sales cộng thêm:", min_value=1.0, value=50.0, step=10.0
            )

            if st.button("Cộng tiền & Xem Audit Log"):
                try:
                    conn = get_connection(db_params)
                    conn.autocommit = True
                    cur = conn.cursor()
                    # Cập nhật order_items
                    cur.execute(
                        "UPDATE order_items SET sales = sales + %s WHERE row_id = %s;",
                        (sales_add_input, row_id_input),
                    )
                    st.success(
                        "✅ Đã cập nhật bảng order_items thành công. Trigger đã kích hoạt!"
                    )
                    conn.close()

                    # Truy vấn lại bảng Log để show
                    df_audit = fetch_data(
                        "SELECT * FROM sales_audit ORDER BY audit_id DESC LIMIT 5;",
                        db_params,
                    )
                    st.write(
                        "📋 **5 lịch sử cập nhật gần nhất trong bảng `sales_audit`:**"
                    )
                    st.dataframe(df_audit, use_container_width=True)
                except Exception as e:
                    st.error(f"Lỗi thao tác: {e}")

    # ==========================================
    # TAB 4: LIFECYCLE & MIGRATION
    # ==========================================
    with tab_migration:
        st.header("🛡️ Quản trị vòng đời (Backup & Restore)")
        st.markdown(
            "Giả lập quy trình Di trú dữ liệu khi nâng cấp phiên bản PostgreSQL (Major Version Upgrade)."
        )

        st.info(
            "💡 **Gợi ý:** Để thực hiện chức năng này, ứng dụng sẽ gọi trực tiếp các tiện ích dòng lệnh `pg_dump` và `pg_restore` của PostgreSQL thay vì dùng lệnh SQL thuần."
        )

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.subheader("1. Xuất dữ liệu (Backup - pg_dump)")
            st.caption(
                f"Tạo bản sao lưu toàn bộ cấu trúc và dữ liệu từ DB `{db_name}`."
            )

            if st.button("🛡️ Tiến hành Backup", use_container_width=True):
                if db_user != "postgres" and db_user != "admin_user":
                    st.error("⚠️ Cần tài khoản admin để chạy pg_dump.")
                else:
                    backup_dir = os.path.join(BASE_DIR, "backups")
                    os.makedirs(backup_dir, exist_ok=True)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    backup_file = os.path.join(
                        backup_dir, f"supermarket_{timestamp}.dump"
                    )

                    # Dùng subprocess gọi lệnh OS
                    import subprocess

                    env = os.environ.copy()
                    env["PGPASSWORD"] = db_password
                    cmd = [
                        "pg_dump",
                        "-h",
                        db_host,
                        "-p",
                        db_port,
                        "-U",
                        db_user,
                        "-F",
                        "c",
                        "-b",
                        "-f",
                        backup_file,
                        db_name,
                    ]
                    try:
                        with st.spinner("Đang chạy pg_dump..."):
                            res = subprocess.run(
                                cmd, env=env, capture_output=True, text=True, check=True
                            )
                        st.success(
                            f"✅ Backup thành công!\nFile lưu tại: `{backup_file}`"
                        )
                    except subprocess.CalledProcessError as e:
                        st.error(f"❌ Lỗi pg_dump:\n{e.stderr}")
                    except FileNotFoundError:
                        st.error(
                            "❌ Không tìm thấy lệnh `pg_dump`. Hãy chắc chắn đã cài PostgreSQL client và thêm vào PATH môi trường."
                        )

        with col_m2:
            st.subheader("2. Khôi phục dữ liệu (Restore - pg_restore)")
            st.caption(
                "Khôi phục bản backup mới nhất vào Database (thường là DB trắng khi nâng cấp)."
            )

            target_db = st.text_input(
                "Database Đích để Restore:", value=f"{db_name}_new"
            )

            if st.button("♻️ Tiến hành Restore", use_container_width=True):
                if db_user != "postgres" and db_user != "admin_user":
                    st.error("⚠️ Cần tài khoản admin để chạy pg_restore.")
                else:
                    backup_dir = os.path.join(BASE_DIR, "backups")
                    if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
                        st.warning("⚠️ Không có file backup nào trong hệ thống!")
                    else:
                        # Lấy file mới nhất
                        files = sorted(
                            [
                                os.path.join(backup_dir, f)
                                for f in os.listdir(backup_dir)
                                if f.endswith(".dump")
                            ],
                            key=os.path.getctime,
                            reverse=True,
                        )
                        if not files:
                            st.warning("⚠️ Không tìm thấy file `.dump` nào!")
                        else:
                            latest_file = files[0]
                            st.info(
                                f"📁 Dùng file backup: `{os.path.basename(latest_file)}`"
                            )

                            import subprocess

                            env = os.environ.copy()
                            env["PGPASSWORD"] = db_password

                            try:
                                with st.spinner(
                                    f"Kiểm tra và tạo DB '{target_db}' nếu chưa có..."
                                ):
                                    conn = get_connection(
                                        {**db_params, "database": "postgres"}
                                    )
                                    conn.autocommit = True
                                    cur = conn.cursor()
                                    cur.execute(
                                        f"SELECT 1 FROM pg_database WHERE datname = '{target_db}'"
                                    )
                                    if not cur.fetchone():
                                        cur.execute(f"CREATE DATABASE {target_db}")
                                    conn.close()

                                with st.spinner("Đang chạy pg_restore (Đa luồng)..."):
                                    cmd = [
                                        "pg_restore",
                                        "-h",
                                        db_host,
                                        "-p",
                                        db_port,
                                        "-U",
                                        db_user,
                                        "-d",
                                        target_db,
                                        "-j",
                                        "4",
                                        "-c",
                                        latest_file,
                                    ]
                                    subprocess.run(
                                        cmd,
                                        env=env,
                                        capture_output=True,
                                        text=True,
                                        check=True,
                                    )

                                st.success(
                                    f"✅ Đã Restore thành công dữ liệu vào DB `{target_db}`!"
                                )
                                st.balloons()
                            except subprocess.CalledProcessError as e:
                                st.error(f"❌ Lỗi pg_restore:\n{e.stderr}")
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")


def run_pipeline(db_params, progress_bar, status_text, log_area):
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


if __name__ == "__main__":
    main()
