#!/usr/bin/env python3
"""
品种图片哈希化工具
功能：将图片文件名改为带内容哈希的格式，更新数据库记录
用法：
  - 批量处理：python3 hash_avatars.py
  - 单个文件：python3 hash_avatars.py 柴犬.webp
"""
import sqlite3
import hashlib
import shutil
import sys
from pathlib import Path

AVATAR_DIR = Path("/var/www/petcare/avatars")
DB_PATH = Path("/root/workspace/petcare/backend/petcare.db")

def compute_file_hash(filepath: Path) -> str:
    """计算文件内容的 MD5 哈希，返回前8位"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()[:8]

def hash_single_file(filename: str):
    """处理单个图片文件"""
    filepath = AVATAR_DIR / filename
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        return None
    
    # 计算哈希
    content_hash = compute_file_hash(filepath)
    
    # 生成新文件名
    stem = filepath.stem
    suffix = filepath.suffix
    new_filename = f"{stem}_{content_hash}{suffix}"
    new_filepath = AVATAR_DIR / new_filename
    
    # 如果新文件已存在且哈希相同，跳过
    if new_filepath.exists():
        print(f"⏭️  已存在: {new_filename}")
        return f"/avatars/{new_filename}"
    
    # 重命名文件
    shutil.move(str(filepath), str(new_filepath))
    print(f"✅ 重命名: {filename} → {new_filename}")
    
    return f"/avatars/{new_filename}"

def update_database(old_url: str, new_url: str):
    """更新数据库中的 image_url"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pet_breeds SET image_url = ? WHERE image_url = ?", (new_url, old_url))
    if cursor.rowcount > 0:
        print(f"📝 数据库更新: {old_url} → {new_url}")
    conn.commit()
    conn.close()

def batch_process():
    """批量处理所有图片"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, image_url FROM pet_breeds WHERE image_url IS NOT NULL")
    breeds = cursor.fetchall()
    conn.close()
    
    print(f"\n🔄 开始处理 {len(breeds)} 个品种的图片...\n")
    
    updated_count = 0
    for breed_id, name, old_url in breeds:
        if "_[a-f0-9]" in old_url:  # 已经有哈希了
            print(f"⏭️  跳过 {name} (已有哈希)")
            continue
        
        filename = old_url.split("/")[-1]
        filepath = AVATAR_DIR / filename
        
        if not filepath.exists():
            print(f"❌ 文件不存在: {name} → {filename}")
            continue
        
        new_url = hash_single_file(filename)
        if new_url:
            update_database(old_url, new_url)
            updated_count += 1
    
    print(f"\n✅ 完成！更新了 {updated_count} 个品种的图片")

def main():
    if len(sys.argv) > 1:
        # 处理单个文件
        filename = sys.argv[1]
        new_url = hash_single_file(filename)
        if new_url:
            # 更新数据库（查找匹配的旧 URL）
            stem = Path(filename).stem
            old_url = f"/avatars/{stem}.webp"
            update_database(old_url, new_url)
    else:
        # 批量处理
        batch_process()

if __name__ == "__main__":
    main()
