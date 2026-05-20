import streamlit as st

from core.pipeline import run_pipeline


def render_pipeline_tab(db_params, db_password, db_user):
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
            run_pipeline(db_params, progress_bar, status_text, log_area, st)
