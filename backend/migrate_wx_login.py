"""给 users 表添加微信登录字段（wx_openid / wx_unionid）

幂等脚本，可重复执行。与 migrate_health_tags.py 同样惯例：
直连 SQLite 执行 ALTER TABLE（SQLAlchemy 的 create_all 不会给已有表加列）。
"""
import os
import sqlite3

DB_PATH = os.environ.get("PETCARE_DB", os.path.join(os.path.dirname(__file__), "petcare.db"))


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在（{DB_PATH}），首次启动时 create_all 会直接建出含新字段的表，无需迁移")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 表不存在（全新库由应用 create_all 建表，自带新字段）则跳过
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("users 表不存在，跳过（create_all 会建出含新字段的表）")
        conn.close()
        return

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "wx_openid" in columns:
        print("wx_openid 列已存在，跳过")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN wx_openid VARCHAR(64)")
        print("✅ 已添加 wx_openid 列")

    if "wx_unionid" in columns:
        print("wx_unionid 列已存在，跳过")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN wx_unionid VARCHAR(64)")
        print("✅ 已添加 wx_unionid 列")

    # openid 唯一索引（NULL 不参与唯一约束，未绑定用户不受影响）
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_wx_openid ON users(wx_openid)"
    )

    # 数据订正：历史数据中 email='' 的多条记录会互相撞 unique 约束
    # （email 列 default="" + unique=True 的遗留问题），统一改为 NULL
    cursor.execute("UPDATE users SET email = NULL WHERE email = ''")
    if cursor.rowcount:
        print(f"✅ 已把 {cursor.rowcount} 条空邮箱记录订正为 NULL")

    # password_set：标记"用户是否知道自己的密码"。
    # 迁移时点存量用户全部是账密注册的 → 一律标记 1；
    # 之后微信自动注册的新用户由模型默认 False，设置密码后置 True
    if "password_set" in columns:
        print("password_set 列已存在，跳过")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN password_set BOOLEAN NOT NULL DEFAULT 0")
        cursor.execute("UPDATE users SET password_set = 1")
        print(f"✅ password_set 列已添加，{cursor.rowcount} 位存量用户标记为已设密码")

    conn.commit()
    conn.close()
    print("✅ 微信登录字段迁移完成:", DB_PATH)


if __name__ == "__main__":
    migrate()