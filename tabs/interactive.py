import streamlit as st

from core.db import fetch_data, get_connection


def render_interactive_tab(db_params, db_user):
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
                st.write("📋 **5 lịch sử cập nhật gần nhất trong bảng `sales_audit`:**")
                st.dataframe(df_audit, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi thao tác: {e}")
