-- [1] Ứng dụng kiểu ARRAY để lưu tag nhãn sản phẩm
-- CREATE TABLE product_tags (
--     product_id VARCHAR(30),
--     tags TEXT[]
-- );

INSERT INTO product_tags
VALUES ('FUR-BO-10001798', ARRAY['furniture', 'wood', 'office']);


-- [2] Ứng dụng kiểu JSONB lưu trữ hồ sơ linh hoạt không định hình của khách hàng
-- CREATE TABLE customer_profiles (
--     customer_id VARCHAR(20),
--     profile JSONB
-- );

INSERT INTO customer_profiles
VALUES (
    'CG-12520',
    '{"age": 30, "membership": "gold", "preferences": ["office", "technology"]}'
);

-- Truy vấn lọc sâu vào thuộc tính JSONB
SELECT *
FROM customer_profiles
WHERE profile->>'membership' = 'gold';
