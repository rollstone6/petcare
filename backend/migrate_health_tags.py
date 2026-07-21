"""添加 health_tags 字段到 pet_profiles 表"""
import sqlite3
import sys

DB_PATH = "/root/workspace/petcare/backend/petcare.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(pet_profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "health_tags" in columns:
        print("health_tags 列已存在，跳过")
        conn.close()
        return
    
    # 添加列
    cursor.execute("""
        ALTER TABLE pet_profiles 
        ADD COLUMN health_tags TEXT DEFAULT '[]'
    """)
    
    conn.commit()
    print("✅ 成功添加 health_tags 列到 pet_profiles 表")
    conn.close()

if __name__ == "__main__":
    migrate()
