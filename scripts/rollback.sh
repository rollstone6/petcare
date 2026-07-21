#!/bin/bash
# PetCare 一键回滚脚本

set -e

if [ -z "$1" ]; then
    echo "用法: ./rollback.sh <commit-hash>"
    echo ""
    echo "最近的提交:"
    git log --oneline -10
    exit 1
fi

COMMIT=$1
echo "═══════════════════════════════════════════════════════════"
echo "🔄 PetCare 回滚到: $COMMIT"
echo "═══════════════════════════════════════════════════════════"

# 1. 备份当前状态
echo ""
echo "1️⃣ 备份当前状态..."
./scripts/backup.sh

# 2. 回滚代码
echo ""
echo "2️⃣ 回滚代码..."
git checkout $COMMIT

# 3. 重建前端
echo ""
echo "3️⃣ 重建前端..."
cd frontend && npm install && npm run build && cd ..

# 4. 重启服务
echo ""
echo "4️⃣ 重启后端服务..."
sudo systemctl restart petcare.service
sleep 5

# 5. 健康检查
echo ""
echo "5️⃣ 健康检查..."
if curl -f -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ 回滚成功，服务运行正常"
else
    echo "❌ 回滚后服务异常，请检查日志"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ 回滚完成"
echo "═══════════════════════════════════════════════════════════"
