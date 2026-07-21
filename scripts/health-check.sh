#!/bin/bash
# PetCare 健康检查脚本
# 检查服务状态、API响应、数据库连接

set -e

ALERT_THRESHOLD=3  # 连续失败次数触发告警
STATE_FILE="/tmp/petcare_health_state"

# 初始化状态文件
if [ ! -f "$STATE_FILE" ]; then
    echo "0" > "$STATE_FILE"
fi

check_service() {
    echo "🔍 检查 systemd 服务..."
    if systemctl is-active --quiet petcare.service; then
        echo "✅ petcare.service 运行正常"
        return 0
    else
        echo "❌ petcare.service 未运行"
        return 1
    fi
}

check_api() {
    echo "🔍 检查 API 响应..."
    if curl -f -s http://127.0.0.1:8000/ > /dev/null; then
        echo "✅ API 响应正常"
        return 0
    else
        echo "❌ API 响应失败"
        return 1
    fi
}

check_database() {
    echo "🔍 检查数据库..."
    DB_PATH="/root/workspace/petcare/backend/petcare.db"
    if [ -f "$DB_PATH" ]; then
        cd /root/workspace/petcare/backend
        if ./venv/bin/python -c "import sqlite3; conn = sqlite3.connect('$DB_PATH'); conn.execute('SELECT COUNT(*) FROM users'); conn.close()" 2>/dev/null; then
            echo "✅ 数据库连接正常"
            return 0
        else
            echo "❌ 数据库连接失败"
            return 1
        fi
    else
        echo "❌ 数据库文件不存在"
        return 1
    fi
}

check_disk() {
    echo "🔍 检查磁盘空间..."
    USAGE=$(df /root | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$USAGE" -lt 90 ]; then
        echo "✅ 磁盘使用率: ${USAGE}%"
        return 0
    else
        echo "⚠️ 磁盘使用率过高: ${USAGE}%"
        return 1
    fi
}

# 执行所有检查
echo "═══════════════════════════════════════════════════════════"
echo "🏥 PetCare 健康检查 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════"

FAILED=0
check_service || FAILED=$((FAILED + 1))
check_api || FAILED=$((FAILED + 1))
check_database || FAILED=$((FAILED + 1))
check_disk || FAILED=$((FAILED + 1))

echo "═══════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo "✅ 所有检查通过"
    echo "0" > "$STATE_FILE"
else
    echo "❌ $FAILED 项检查失败"
    FAIL_COUNT=$(cat "$STATE_FILE")
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "$FAIL_COUNT" > "$STATE_FILE"
    
    if [ $FAIL_COUNT -ge $ALERT_THRESHOLD ]; then
        echo ""
        echo "🚨 连续失败 $FAIL_COUNT 次，需要立即处理！"
        echo "📱 告警已触发"
        # 这里可以接入微信通知或其他告警渠道
    fi
fi
