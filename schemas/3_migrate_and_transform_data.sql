-- Nạp Regions
INSERT INTO regions (region_name)
SELECT DISTINCT "region" FROM supermarket_raw;

-- Nạp Customers
INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT "customer_id", "customer_name", "segment" FROM supermarket_raw;

-- Nạp Products
INSERT INTO products (product_id, product_name, category, sub_category)
SELECT DISTINCT ON (product_id)
    product_id, product_name, category, sub_category
FROM supermarket_raw
ORDER BY product_id;

-- Nạp Orders (Chuyển đổi chuỗi thành DATE)
INSERT INTO orders (
    order_id, order_date, ship_date, ship_mode, customer_id, country, city, state, postal_code, region
)
SELECT DISTINCT
    order_id,
    TO_DATE(order_date, 'DD/MM/YYYY'),
    TO_DATE(ship_date, 'DD/MM/YYYY'),
    ship_mode, customer_id, country, city, state, postal_code, region
FROM supermarket_raw;

-- Nạp Order Items
INSERT INTO order_items (row_id, order_id, product_id, sales)
SELECT "row_id", "order_id", "product_id", "sales" FROM supermarket_raw;
