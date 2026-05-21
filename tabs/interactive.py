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

        st.subheader("2. Hàm (Function): Trạng thái khách hàng")
        customer_id_status = st.text_input(
            "Nhập Mã Khách Hàng (vd: CG-12520):", value="CG-12520", key="cust_status"
        )
        if st.button("Kiểm tra trạng thái"):
            try:
                df_status = fetch_data(
                    "SELECT fn_get_customer_status(%s) AS status;",
                    db_params,
                    (customer_id_status,),
                )
                st.info(
                    f"Trạng thái khách hàng **{customer_id_status}**: **{df_status.iloc[0]['status']}**"
                )
            except Exception as e:
                st.error(f"Lỗi: {e}")

        st.markdown("---")

        st.subheader("3. Gọi Procedure: Cập nhật Phương thức Giao hàng")
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
        st.subheader("4. Procedure: Đổi tên Phân khúc Khách hàng")
        st.caption(
            "Thay đổi hàng loạt phân khúc (vd: 'Consumer' thành 'B2C'). Yêu cầu admin_user hoặc entry_user."
        )
        old_segment = st.text_input("Phân khúc cũ:", value="Consumer")
        new_segment = st.text_input("Phân khúc mới:", value="B2C")
        if st.button("Cập nhật Phân khúc"):
            try:
                conn = get_connection(db_params)
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(
                    "CALL pr_reassign_customer_segment(%s, %s);",
                    (old_segment, new_segment),
                )
                st.success(
                    f"✅ Đã đổi phân khúc '{old_segment}' thành '{new_segment}'!"
                )
                conn.close()
            except Exception as e:
                st.error(
                    f"Lỗi truy cập (Có thể do User '{db_user}' không có quyền UPDATE): {e}"
                )

        st.markdown("---")

        st.subheader("5. Test Trigger: Audit Log khi cập nhật Sales")
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

        st.markdown("---")

        st.subheader("6. Test Trigger: Validate Ngày Giao Hàng")
        st.caption(
            "Ngày giao hàng (Ship Date) không thể xảy ra TRƯỚC ngày đặt hàng (Order Date). Trigger `trg_validate_dates` sẽ tự động sửa lỗi này."
        )

        test_order_id = st.text_input(
            "Mã đơn hàng (để test update):",
            value="CA-2016-152156",
            key="test_trigger_date",
        )

        if st.button("Cố tình Update ngày Ship Date = 2010-01-01 (Sai logic)"):
            try:
                # Lấy ngày order_date hiện tại để so sánh
                df_order = fetch_data(
                    "SELECT order_date, ship_date FROM orders WHERE order_id = %s;",
                    db_params,
                    (test_order_id,),
                )

                if df_order.empty:
                    st.error(f"Không tìm thấy đơn hàng {test_order_id}")
                else:
                    old_order_date = df_order.iloc[0]["order_date"]
                    old_ship_date = df_order.iloc[0]["ship_date"]

                    st.write(
                        f"ℹ️ **Trạng thái ban đầu:** Order Date: `{old_order_date}` | Ship Date: `{old_ship_date}`"
                    )
                    st.write(
                        "⏳ Đang cố gắng thực thi: `UPDATE orders SET ship_date = '2010-01-01' WHERE order_id = ...`"
                    )

                    # Cố tình update ship_date về quá khứ (năm 2010)
                    conn = get_connection(db_params)
                    conn.autocommit = True
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE orders SET ship_date = '2010-01-01' WHERE order_id = %s;",
                        (test_order_id,),
                    )
                    conn.close()

                    # Truy vấn lại để xem Trigger đã sửa thành gì
                    df_after = fetch_data(
                        "SELECT order_date, ship_date FROM orders WHERE order_id = %s;",
                        db_params,
                        (test_order_id,),
                    )
                    new_ship_date = df_after.iloc[0]["ship_date"]

                    st.success("✅ Lệnh UPDATE đã chạy qua Trigger bảo vệ dữ liệu!")
                    st.warning(
                        f"🚨 **Kết quả thực tế sau khi Update:** Ship Date không bị sửa thành 2010, mà đã bị Trigger tự động ép về bằng với Order Date: `{new_ship_date}`"
                    )

            except Exception as e:
                st.error(
                    f"Lỗi truy cập (Có thể do User '{db_user}' không có quyền UPDATE): {e}"
                )

        st.divider()

        st.subheader("7. Procedure: Tăng giá bán hàng loạt")
        st.caption(
            "Tăng doanh thu (sales) của tất cả order items lên X%. Yêu cầu admin_user hoặc entry_user."
        )
        percent_increase = st.number_input(
            "Nhập phần trăm tăng (%):", min_value=1.0, value=5.0, step=1.0
        )
        if st.button("Tăng doanh thu"):
            try:
                conn = get_connection(db_params)
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute("CALL pr_increase_sales(%s);", (percent_increase,))
                st.success(
                    f"✅ Đã tăng doanh thu toàn hệ thống lên {percent_increase}%!"
                )
                conn.close()
            except Exception as e:
                st.error(
                    f"Lỗi truy cập (Có thể do User '{db_user}' không có quyền UPDATE/EXECUTE): {e}"
                )

        st.markdown("---")

        st.subheader("8. Procedure: Xóa hoàn toàn khách hàng")
        st.caption(
            "Xóa sạch khách hàng và toàn bộ lịch sử đơn hàng (Cascade Delete). Chỉ admin_user mới được phép!"
        )
        delete_cust_id = st.text_input(
            "Nhập mã khách hàng cần xóa:", value="SO-20335", key="del_cust"
        )
        if st.button("Xóa sạch dữ liệu khách hàng", type="primary"):
            try:
                conn = get_connection(db_params)
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(
                    "CALL pr_delete_customer_completely(%s);", (delete_cust_id,)
                )
                st.success(
                    f"✅ Đã xóa hoàn toàn khách hàng {delete_cust_id} khỏi hệ thống!"
                )
                conn.close()
            except Exception as e:
                st.error(f"Lỗi truy cập (Yêu cầu tài khoản Admin/Postgres): {e}")
