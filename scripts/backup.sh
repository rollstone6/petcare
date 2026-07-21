#!/bin/bash
# PetCare 数据库自动备份脚本
# 保留最近7天的备份

set -e

BACKUP_DIR="/root/backups/petcare"
DB_PATH="/root/workspace/petcare/backend/petcare.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="petcare_${TIMESTAMP}.db"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库（使用 Python sqlite3 模块）
echo "📦 备份数据库: $BACKUP_FILE"
cd /root/workspace/petcare/backend
./venv/bin/python << EOF
import sqlite3
import shutil

source_db = "$DB_PATH"
backup_db = "$BACKUP_DIR/$BACKUP_FILE"

# 使用 Python 的 sqlite3 备份
source = sqlite3.connect(source_db)
backup = sqlite3.connect(backup_db)
with backup:
    source.backup(backup)
source.close()
backup.close()
EOF

# 压缩备份
gzip "$BACKUP_DIR/$BACKUP_FILE"
echo "✅ 备份完成: ${BACKUP_FILE}.gz"

# 删除7天前的备份
echo "🗑️ 清理旧备份..."
find "$BACKUP_DIR" -name "petcare_*.db.gz" -mtime +7 -delete
echo "✅ 清理完成"

# 显示当前备份列表
echo ""
echo "📋 当前备份列表:"
ls -lh "$BACKUP_DIR" | grep "petcare_"
