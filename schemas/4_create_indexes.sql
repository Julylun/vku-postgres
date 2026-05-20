CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_region ON orders(region);
CREATE INDEX idx_orderitems_order_id ON order_items(order_id);
CREATE INDEX idx_orderitems_product_id ON order_items(product_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
