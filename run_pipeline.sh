#!/bin/bash

# Dừng script nếu có bất kỳ lỗi nào xảy ra
set -e

# ==========================================
# CẤU HÌNH KẾT NỐI DATABASE
# Hãy thay đổi thông tin này cho phù hợp với môi trường của bạn
# ==========================================
export PGHOST="localhost"
export PGPORT="5432"
export PGUSER="test"
export PGPASSWORD="test"   # Thay bằng password thật của bạn
export PGDATABASE="supermarket_db"  # Thay bằng tên DB bạn muốn chạy vào

# Đường dẫn thư mục chứa schemas và thư mục data
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_DIR="$BASE_DIR/schemas"
CSV_FILE="$BASE_DIR/data/supermarket.csv"

echo "==========================================="
echo "=== BẮT ĐẦU CHẠY PIPELINE BẰNG BASH ==="
echo "==========================================="

# Kiểm tra xem có thể kết nối tới DB không
echo "Kiểm tra kết nối DB..."
psql -c "\conninfo" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "-> Kết nối DB thành công!"
else
    echo "-> LỖI: Không thể kết nối tới Database. Hãy kiểm tra cấu hình!"
    exit 1
fi

echo "-------------------------------------------"

# 1. Chạy file số 1 (Tạo bảng Staging)
FILE_1="$SCHEMA_DIR/1_create_staging_tabel.sql"
if [ -f "$FILE_1" ]; then
    echo "⏳ 1. Đang chạy: 1_create_staging_tabel.sql (Tạo bảng Staging)..."
    psql -v ON_ERROR_STOP=1 -q -f "$FILE_1"
    echo "✅ Tạo bảng Staging thành công!"
else
    echo "❌ LỖI: Không tìm thấy $FILE_1"
    exit 1
fi

# 1.5. Import CSV vào bảng supermarket_raw
if [ -f "$CSV_FILE" ]; then
    echo "⏳ 1.5. Đang import dữ liệu từ file CSV: $(basename "$CSV_FILE") ..."
    # Sử dụng \copy của psql để import dữ liệu từ máy trạm vào DB
    psql -v ON_ERROR_STOP=1 -q -c "\copy supermarket_raw FROM '$CSV_FILE' WITH (FORMAT csv, HEADER true);"
    echo "✅ Import CSV thành công!"
else
    echo "❌ LỖI: Không tìm thấy file CSV tại $CSV_FILE"
    exit 1
fi

# 2. Vòng lặp tự động chạy các script từ 2 đến 11
FILES=(
    "2_create_dnf_tables.sql"
    "3_migrate_and_transform_data.sql"
    "4_create_indexes.sql"
    "5_create_views.sql"
    "6_create_function.sql"
    "7_create_procedures.sql"
    "8_create_trigger.sql"
    "9_analytics_queries.sql"
    "10_prepared_statements.sql"
    "11_extended_types.sql"
    "12_rbac_security.sql"
)

echo "⏳ 2. Chạy các tiến trình Transform, Index, Views và Advanced Objects..."
for file in "${FILES[@]}"; do
    FILE_PATH="$SCHEMA_DIR/$file"

    if [ -f "$FILE_PATH" ]; then
        echo "--> Đang chạy: $file ..."
        psql -v ON_ERROR_STOP=1 -q -f "$FILE_PATH"
        echo "    ✅ Hoàn thành: $file"
    else
        echo "    ⚠️  Bỏ qua: Không tìm thấy $file"
    fi
done

echo "==========================================="
echo "=== PIPELINE HOÀN TẤT THÀNH CÔNG! ==="
echo "==========================================="
