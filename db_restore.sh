#!/bin/bash
set -e

export PGHOST="localhost"
export PGPORT="5432"
export PGUSER="postgres"
export PGPASSWORD="your_password"
export PGDATABASE="supermarket_db_new" # Thường restore vào DB trống để test

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$BASE_DIR/backups"

# Lấy file backup mới nhất
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.dump | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ Không tìm thấy file backup nào trong thư mục $BACKUP_DIR"
    exit 1
fi

echo "==========================================="
echo "=== ♻️  BẮT ĐẦU RESTORE (PG_RESTORE) ==="
echo "==========================================="
echo "📁 Sử dụng file backup mới nhất: $(basename "$LATEST_BACKUP")"

# Chú ý: Nên tạo database trắng trước khi restore
echo "⏳ Kiểm tra và tạo database đích '$PGDATABASE' nếu chưa có..."
psql -d postgres -c "SELECT 'CREATE DATABASE $PGDATABASE' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$PGDATABASE')\gexec"

echo "⏳ Đang tiến hành restore..."
# -d: database đích
# -j 4: Dùng 4 luồng song song để restore siêu nhanh
# -c: Clean (Drop) object trước khi tạo lại (nếu có)
pg_restore -d "$PGDATABASE" -j 4 -c -v "$LATEST_BACKUP"

echo "✅ Restore thành công vào database '$PGDATABASE'!"
