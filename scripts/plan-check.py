#!/usr/bin/env python3
"""
宠物宝项目计划检查和优化脚本
每小时执行一次，检查项目状态并记录变更
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/root/workspace/petcare")
LOG_FILE = PROJECT_DIR / "logs" / "plan-check.log"
CHANGE_LOG = PROJECT_DIR / "logs" / "changes.json"

def log(msg):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def load_changes():
    """加载变更记录"""
    if CHANGE_LOG.exists():
        with open(CHANGE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"date": None, "items": []}

def save_changes(changes):
    """保存变更记录"""
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANGE_LOG, 'w', encoding='utf-8') as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)

def check_database_stats():
    """检查数据库统计"""
    try:
        sys.path.insert(0, str(PROJECT_DIR / "backend"))
        os.chdir(PROJECT_DIR / "backend")
        
        # 激活虚拟环境
        venv_path = PROJECT_DIR / "backend" / "browseract-env"
        if venv_path.exists():
            import subprocess
            result = subprocess.run(
                ["python3", "-c", """
from app.database import SessionLocal
from app import models
from sqlalchemy import func
db = SessionLocal()
products = db.query(models.Product).count()
brands = db.query(models.Brand).count()
categories = db.query(models.Category).count()
ingredients = db.query(models.Ingredient).count()
print(f"{products},{brands},{categories},{ingredients}")
db.close()
"""],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_DIR / "backend"),
                env={**os.environ, "VIRTUAL_ENV": str(venv_path), "PATH": f"{venv_path}/bin:{os.environ.get('PATH', '')}"}
            )
            if result.returncode == 0:
                stats = result.stdout.strip().split(',')
                return {
                    "products": int(stats[0]),
                    "brands": int(stats[1]),
                    "categories": int(stats[2]),
                    "ingredients": int(stats[3])
                }
    except Exception as e:
        log(f"⚠️ 数据库检查失败: {e}")
    return None

def check_build_status():
    """检查前端构建状态"""
    dist_dir = PROJECT_DIR / "frontend" / "dist"
    if dist_dir.exists():
        # 检查最近的修改时间
        index_html = dist_dir / "index.html"
        if index_html.exists():
            mtime = os.path.getmtime(index_html)
            mtime_dt = datetime.fromtimestamp(mtime)
            return {
                "last_build": mtime_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "age_hours": (datetime.now() - mtime_dt).total_seconds() / 3600
            }
    return None

def check_avatar_count():
    """检查头像数量"""
    avatar_dir = PROJECT_DIR / "frontend" / "public" / "avatars"
    if avatar_dir.exists():
        png_count = len(list(avatar_dir.glob("*.png")))
        svg_count = len(list(avatar_dir.glob("*.svg")))
        return {"png": png_count, "svg": svg_count, "total": png_count + svg_count}
    return None

def main():
    log("=" * 60)
    log("开始项目计划检查")
    
    changes = load_changes()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 如果是新的一天，重置变更记录
    if changes["date"] != today:
        changes = {"date": today, "items": []}
    
    # 检查数据库统计
    stats = check_database_stats()
    if stats:
        log(f"📊 数据库统计: 产品 {stats['products']}, 品牌 {stats['brands']}, 品类 {stats['categories']}, 成分 {stats['ingredients']}")
        
        # 检查是否有新增
        if changes.get("last_stats"):
            for key in ["products", "brands", "categories", "ingredients"]:
                diff = stats[key] - changes["last_stats"][key]
                if diff > 0:
                    item = f"新增 {diff} 个{key}"
                    changes["items"].append(item)
                    log(f"✨ {item}")
    
    changes["last_stats"] = stats
    
    # 检查构建状态
    build = check_build_status()
    if build:
        log(f"🏗️ 最近构建: {build['last_build']} ({build['age_hours']:.1f}小时前)")
        if build['age_hours'] > 24:
            log("⚠️ 构建文件超过24小时未更新")
            changes["items"].append("构建文件过期，建议重新构建")
    
    # 检查头像数量
    avatars = check_avatar_count()
    if avatars:
        log(f"🖼️ 头像文件: PNG {avatars['png']}, SVG {avatars['svg']}, 总计 {avatars['total']}")
    
    # 检查待办事项
    todos = [
        "品牌筛选功能（搜索页加品牌 chip）",
        "数据继续扩充（成分数据完善）",
        "首页推荐（根据宠物档案推荐产品）",
        "搜索体验优化（品类筛选改为下拉展开）",
        "成分详情页增强（常见搭配、注意事项）",
        "数据看板（首页展示统计数字）"
    ]
    log(f"📝 待办事项: {len(todos)} 项")
    for i, todo in enumerate(todos, 1):
        log(f"   {i}. {todo}")
    
    # 保存变更记录
    save_changes(changes)
    
    log("检查完成")
    log("=" * 60)
    
    return changes

if __name__ == "__main__":
    main()
