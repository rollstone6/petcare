"""添加 body_condition 字段到 pet_profiles 表"""
import sqlite3
import sys

DB_PATH = "/root/workspace/petcare/backend/petcare.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(pet_profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "body_condition" in columns:
        print("body_condition 列已存在，跳过")
        conn.close()
        return

    cursor.execute("""
        ALTER TABLE pet_profiles 
        ADD COLUMN body_condition TEXT DEFAULT ''
    """)
    
    conn.commit()
    print("✅ 成功添加 body_condition 列到 pet_profiles 表")
    conn.close()

if __name__ == "__main__":
    main()
