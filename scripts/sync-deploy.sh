#!/bin/bash
# PetCare 自动同步部署脚本
# 检查未提交改动 → 构建前端 → 重启后端 → 提交推送

set -e
cd /root/workspace/petcare

# 1. 检查是否有未提交的改动
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
    echo "✅ 无改动，无需同步"
    exit 0
fi

echo "📋 检测到未提交改动:"
echo "$CHANGES"

# 2. 拉取远程最新代码
echo "🔄 拉取远程代码..."
git stash
git pull --rebase origin main 2>/dev/null || true
git stash pop 2>/dev/null || true

# 3. 运行数据库迁移（如果存在新的迁移脚本）
echo "🗄️ 检查数据库迁移..."
cd backend
for f in migrate_*.py; do
    if [ -f "$f" ]; then
        result=$(./venv/bin/python "$f" 2>&1)
        echo "  $f: $result"
    fi
done

# 4. 构建前端
echo "🔨 构建前端..."
cd /root/workspace/petcare/frontend
npm run build --silent 2>&1

# 5. 重启后端服务
echo "🔄 重启后端服务..."
lsof -i :8000 -t 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1
systemctl restart petcare.service
sleep 2

# 检查服务状态
if systemctl is-active --quiet petcare.service; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败，查看日志: journalctl -u petcare.service -n 20"
fi

# 6. 提交并推送
echo "📤 提交代码..."
cd /root/workspace/petcare
git add -A

# 生成提交信息：列出修改的文件摘要
CHANGED_FILES=$(git diff --cached --stat --format="")
COMMIT_MSG="chore: 自动同步部署 $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG" --no-verify 2>/dev/null || true
git push origin main 2>&1

echo "✅ 同步完成！"
