import streamlit as st
from tabs.dashboard import render_dashboard_tab
from tabs.interactive import render_interactive_tab
from tabs.migration import render_migration_tab

from tabs.explorer import render_explorer_tab
from tabs.pipeline import render_pipeline_tab

st.set_page_config(
    page_title="Supermarket Data Warehouse", page_icon="⚙️", layout="wide"
)


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

    # Tạo 5 Tabs giao diện
    tab_pipeline, tab_explorer, tab_interactive, tab_dashboard, tab_migration = st.tabs(
        [
            "🚀 1. Pipeline Monitor",
            "🔍 2. Database Explorer",
            "⚡ 3. Interactive Tools",
            "📊 4. Dashboard",
            "🛡️ 5. Lifecycle & Migration",
        ]
    )

    with tab_pipeline:
        render_pipeline_tab(db_params, db_password, db_user)

    with tab_explorer:
        render_explorer_tab(db_params)

    with tab_interactive:
        render_interactive_tab(db_params, db_user)

    with tab_dashboard:
        render_dashboard_tab(db_params)

    with tab_migration:
        render_migration_tab(db_params, db_password, db_user, db_name, db_host, db_port)


if __name__ == "__main__":
    main()
