#!/usr/bin/env python3
"""
宠物宝项目每日总结脚本
每天早上8点执行，生成前一天的变更总结并推送到微信
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path("/root/workspace/petcare")
CHANGE_LOG = PROJECT_DIR / "logs" / "changes.json"

def load_changes():
    """加载变更记录"""
    if CHANGE_LOG.exists():
        with open(CHANGE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"date": None, "items": []}

def generate_summary():
    """生成每日总结"""
    changes = load_changes()
    
    # 如果没有记录，返回空
    if not changes.get("items"):
        return None
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    summary = []
    summary.append(f"🐾 宠物宝项目日报 - {yesterday}")
    summary.append("")
    
    # 数据库统计
    stats = changes.get("last_stats")
    if stats:
        summary.append("📊 当前数据规模:")
        summary.append(f"  • 产品: {stats['products']} 个")
        summary.append(f"  • 品牌: {stats['brands']} 个")
        summary.append(f"  • 品类: {stats['categories']} 个")
        summary.append(f"  • 成分: {stats['ingredients']} 个")
        summary.append("")
    
    # 变更内容
    if changes["items"]:
        summary.append("✨ 昨日变更:")
        for i, item in enumerate(changes["items"], 1):
            summary.append(f"  {i}. {item}")
        summary.append("")
    
    # 待办提醒
    summary.append("📝 待办事项提醒:")
    todos = [
        "品牌筛选功能",
        "数据扩充（成分完善）",
        "首页推荐优化",
        "搜索体验优化",
        "成分详情页增强",
        "数据看板"
    ]
    for i, todo in enumerate(todos, 1):
        summary.append(f"  {i}. {todo}")
    
    return "\n".join(summary)

def main():
    summary = generate_summary()
    
    if summary:
        print(summary)
        print("\n" + "=" * 50)
        print("请手动复制以上内容发送到微信")
        print("或配置微信推送 API 实现自动发送")
    else:
        print("昨日无变更")

if __name__ == "__main__":
    main()
