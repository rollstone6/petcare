"""安全审计 2026-10 迁移：users 表添加 token_version 列（JWT 吊销机制）

用法: venv/bin/python migrate_security_audit.py
幂等：列已存在时跳过。
"""
import sqlite3
import sys

DB_PATH = "/root/workspace/petcare/backend/petcare.db"


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "token_version" in columns:
        print("token_version 列已存在，跳过")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        print("✅ 已添加 users.token_version（默认 0，存量 token 的 tv 缺省按 0 匹配，不强制重登录）")
    conn.close()


if __name__ == "__main__":
    migrate()
