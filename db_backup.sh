#!/bin/bash
set -e

export PGHOST="localhost"
export PGPORT="5432"
export PGUSER="postgres"
export PGPASSWORD="your_password"   # Thay mật khẩu admin (postgres)
export PGDATABASE="supermarket_db"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$BASE_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/supermarket_backup_$TIMESTAMP.dump"

echo "==========================================="
echo "=== 🛡️  BẮT ĐẦU BACKUP (PG_DUMP) ==="
echo "==========================================="

echo "⏳ Đang tiến hành backup database '$PGDATABASE'..."
# -F c: Định dạng custom (nén tối ưu của Postgres)
# -b: Bao gồm large objects (blobs)
# -v: In log chi tiết
pg_dump -F c -b -v -f "$BACKUP_FILE"

echo "✅ Backup thành công! File lưu tại: $BACKUP_FILE"
