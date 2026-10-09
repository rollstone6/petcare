#!/bin/bash
# PetCare 综合维护脚本（no_agent 模式）
# 整合：计划检查 + 同步部署 + 健康监控
# 全正常则静默，有问题才输出详情

cd /root/workspace/petcare
ISSUES=""
OUTPUT=""

# === 1. 计划检查 ===
PLAN_OUT=$(python3 /root/workspace/petcare/scripts/plan-check.py 2>&1)
if [ $? -ne 0 ]; then
    ISSUES="${ISSUES}\n📋 计划检查失败:\n${PLAN_OUT}\n"
else
    OUTPUT="${OUTPUT}📋 计划检查: ✅\n"
fi

# === 2. 同步部署 ===
DEPLOY_OUT=$(bash /root/workspace/petcare/scripts/sync-deploy.sh 2>&1) || true
if echo "$DEPLOY_OUT" | grep -qE "启动失败|ERROR|error"; then
    ISSUES="${ISSUES}\n📤 同步部署失败:\n${DEPLOY_OUT}\n"
elif echo "$DEPLOY_OUT" | grep -q "无改动"; then
    OUTPUT="${OUTPUT}📤 同步部署: ✅ (无改动)\n"
else
    OUTPUT="${OUTPUT}📤 同步部署: ✅ (已部署)\n"
fi

# === 3. 健康监控 ===
MONITOR_OUT=$(python3 ~/.hermes/scripts/petcare-monitor.py 2>&1)
MONITOR_EXIT=$?
if [ $MONITOR_EXIT -ne 0 ]; then
    ISSUES="${ISSUES}\n🏥 健康监控发现异常:\n${MONITOR_OUT}\n"
else
    OUTPUT="${OUTPUT}🏥 健康监控: ✅\n"
fi

# === 输出 ===
echo "🔧 PetCare 维护报告 · $(date '+%Y-%m-%d %H:%M')"
echo "════════════════════════════════════"
echo -e "$OUTPUT"

if [ -n "$ISSUES" ]; then
    echo -e "$ISSUES"
    echo "⚠️ 存在问题，请检查！"
    exit 1
else
    echo "✅ 所有任务正常"
    exit 0
fi
