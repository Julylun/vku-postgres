import os
import subprocess
import time

import streamlit as st

from core.db import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render_migration_tab(db_params, db_password, db_user, db_name, db_host, db_port):
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
        st.caption(f"Tạo bản sao lưu toàn bộ cấu trúc và dữ liệu từ DB `{db_name}`.")

        if st.button("🛡️ Tiến hành Backup", use_container_width=True):
            if db_user != "postgres" and db_user != "admin_user":
                st.error("⚠️ Cần tài khoản admin để chạy pg_dump.")
            else:
                backup_dir = os.path.join(BASE_DIR, "backups")
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(backup_dir, f"supermarket_{timestamp}.dump")

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
                    st.success(f"✅ Backup thành công!\nFile lưu tại: `{backup_file}`")
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

        target_db = st.text_input("Database Đích để Restore:", value=f"{db_name}_new")

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
                                    "-c",  # Clean: Bắt buộc để ghi đè DB đã tồn tại
                                    "--if-exists",  # Bỏ qua lỗi DROP không tồn tại
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
