import pandas as pd
import plotly.express as px
import streamlit as st

from core.db import fetch_data, get_connection


def render_dashboard_tab(db_params):
    st.header("📊 Báo cáo phân tích doanh thu")
    st.markdown(
        "Trực quan hóa dữ liệu từ các View và Advanced Queries trong PostgreSQL."
    )

    try:
        # --- KPI TỔNG QUAN ---
        kpi_query = """
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS total_customers,
            SUM(oi.sales) AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id;
        """
        kpi_df = fetch_data(kpi_query, db_params)

        if not kpi_df.empty and pd.notna(kpi_df.iloc[0]["total_revenue"]):
            total_rev = float(kpi_df.iloc[0]["total_revenue"])
            total_orders = int(kpi_df.iloc[0]["total_orders"])
            total_cust = int(kpi_df.iloc[0]["total_customers"])
            aov = total_rev / total_orders if total_orders > 0 else 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("💰 Tổng Doanh Thu", f"${total_rev:,.2f}")
            k2.metric("📦 Tổng Số Đơn Hàng", f"{total_orders:,}")
            k3.metric("👥 Số Lượng Khách", f"{total_cust:,}")
            k4.metric("📈 Giá trị trung bình/đơn", f"${aov:,.2f}")

            st.divider()

            # --- BIỂU ĐỒ XU HƯỚNG ---
            st.subheader("📈 Xu hướng doanh thu theo Tháng/Năm")
            trend_df = fetch_data("SELECT * FROM v_sales_trend;", db_params)
            if not trend_df.empty:
                fig_trend = px.line(
                    trend_df,
                    x="order_month",
                    y="monthly_sales",
                    markers=True,
                    title="Doanh thu hàng tháng",
                    labels={
                        "order_month": "Tháng",
                        "monthly_sales": "Doanh Thu ($)",
                    },
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            col_d1, col_d2 = st.columns(2)

            with col_d1:
                # --- BIỂU ĐỒ DOANH THU THEO DANH MỤC (MATERIALIZED VIEW) ---
                st.subheader("🍩 Doanh thu theo Danh mục")
                st.caption("Dữ liệu từ Materialized View `mv_category_sales`")
                cat_df = fetch_data(
                    "SELECT * FROM mv_category_sales ORDER BY total_sales DESC;",
                    db_params,
                )
                if not cat_df.empty:
                    fig_cat = px.pie(
                        cat_df, values="total_sales", names="category", hole=0.4
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)

                    if st.button("🔄 Làm mới MV (Refresh)"):
                        conn = get_connection(db_params)
                        conn.autocommit = True
                        conn.cursor().execute(
                            "REFRESH MATERIALIZED VIEW mv_category_sales;"
                        )
                        conn.close()
                        st.success("Đã làm mới Materialized View thành công!")
                        st.rerun()

            with col_d2:
                # --- BẢNG XẾP HẠNG KHÁCH HÀNG (WINDOW FUNCTION) ---
                st.subheader("🏆 Top 10 Khách Hàng (Window Function)")
                rank_query = """
                SELECT
                    c.customer_name,
                    SUM(oi.sales) AS total_sales,
                    RANK() OVER (ORDER BY SUM(oi.sales) DESC) AS sales_rank
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_name
                LIMIT 10;
                """
                rank_df = fetch_data(rank_query, db_params)
                if not rank_df.empty:
                    st.dataframe(rank_df, use_container_width=True, hide_index=True)

            st.divider()

            # --- BÁO CÁO NÂNG CAO (VIEWS MỚI) ---
            st.subheader("📊 Báo cáo nâng cao (Views mới)")
            col_v1, col_v2 = st.columns(2)

            with col_v1:
                st.markdown("**1. Khách hàng VIP (Customer Lifetime Value)**")
                st.caption("Dữ liệu từ View `v_customer_lifetime_value`")
                clv_df = fetch_data(
                    "SELECT * FROM v_customer_lifetime_value ORDER BY total_spent DESC LIMIT 5;",
                    db_params,
                )
                if not clv_df.empty:
                    st.dataframe(clv_df, use_container_width=True, hide_index=True)

            with col_v2:
                st.markdown("**2. Báo cáo giao hàng trễ hạn**")
                st.caption("Dữ liệu từ View `v_delayed_shipments`")
                delayed_df = fetch_data(
                    "SELECT shipping_status, COUNT(*) as total_orders FROM v_delayed_shipments GROUP BY shipping_status;",
                    db_params,
                )
                if not delayed_df.empty:
                    fig_delayed = px.pie(
                        delayed_df,
                        values="total_orders",
                        names="shipping_status",
                        hole=0.4,
                        color="shipping_status",
                        color_discrete_map={"On Time": "green", "Delayed": "red"},
                    )
                    st.plotly_chart(fig_delayed, use_container_width=True)

            st.markdown("**3. Top 5 Sản phẩm bán chạy theo tháng (Function)**")
            st.caption("Sử dụng hàm `fn_top_products_by_month`")
            selected_month = st.text_input("Nhập tháng (YYYY-MM):", value="2016-11")
            if selected_month:
                top_products_df = fetch_data(
                    "SELECT * FROM fn_top_products_by_month(%s, 5);",
                    db_params,
                    (selected_month,),
                )
                if not top_products_df.empty:
                    st.dataframe(
                        top_products_df, use_container_width=True, hide_index=True
                    )
                else:
                    st.info(f"Không có dữ liệu bán hàng trong tháng {selected_month}")

            st.divider()

            # --- KHAI THÁC JSONB & ARRAY ---
            st.subheader("🔎 Tra cứu Dữ liệu Nâng cao (Advanced Types)")
            col_adv1, col_adv2 = st.columns(2)

            with col_adv1:
                st.markdown("**1. Tìm kiếm bằng JSONB (customer_profiles)**")
                membership = st.selectbox(
                    "Chọn hạng thành viên:", ["gold", "silver", "platinum"]
                )
                json_query = """
                SELECT customer_id, profile->>'age' AS age, profile->'preferences' AS preferences
                FROM customer_profiles
                WHERE profile->>'membership' = %s;
                """
                json_df = fetch_data(json_query, db_params, (membership,))
                if not json_df.empty:
                    st.dataframe(json_df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"Không tìm thấy khách hàng hạng {membership}")

            with col_adv2:
                st.markdown("**2. Tìm sản phẩm theo Tags (ARRAY)**")
                st.caption(
                    "Tìm sản phẩm chứa tag 'office' hoặc 'wood' bằng toán tử ANY/CONTAINS"
                )
                tag_input = st.text_input(
                    "Nhập tag cần tìm (vd: office, wood, furniture):",
                    value="office",
                )
                if tag_input:
                    array_query = """
                    SELECT product_id, tags
                    FROM product_tags
                    WHERE %s = ANY(tags);
                    """
                    array_df = fetch_data(array_query, db_params, (tag_input.strip(),))
                    if not array_df.empty:
                        st.dataframe(
                            array_df, use_container_width=True, hide_index=True
                        )
                    else:
                        st.info(f"Không tìm thấy sản phẩm nào có tag '{tag_input}'")
        else:
            st.warning("⚠️ Database trống! Hãy chạy Pipeline để nạp dữ liệu trước.")
    except Exception as e:
        st.error(
            f"Lỗi truy xuất Dashboard (Có thể chưa chạy Pipeline hoặc Database chưa có đủ View): {e}"
        )
