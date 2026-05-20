import streamlit as st

from core.db import fetch_data


def render_explorer_tab(db_params):
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

        selected_table = st.selectbox("👉 Chọn một Bảng hoặc View để xem:", table_list)

        if selected_table:
            limit = st.slider(
                "Số dòng hiển thị:",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
            )
            df = fetch_data(f"SELECT * FROM {selected_table} LIMIT {limit};", db_params)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Đang hiển thị {len(df)} dòng của '{selected_table}'.")

    except Exception as e:
        st.error(
            f"Lỗi truy vấn Database (Có thể do sai thông tin kết nối hoặc user không có quyền): {e}"
        )
