#!/usr/bin/env python3
"""统一所有品种的 image_url 指向 webp，修复文件名不匹配"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "petcare.db")
AVATARS_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "avatars")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id, name, image_url FROM pet_breeds ORDER BY id")
rows = cur.fetchall()

updates = 0
issues = []

for bid, name, old_url in rows:
    # DB name might use () like 贵宾犬(泰迪), but files use _ like 贵宾犬_泰迪
    # Try both forms
    file_name_db = name.replace("(", "_").replace(")", "").replace("（", "_").replace("）", "")
    file_name_db = file_name_db.replace(" ", "")

    webp_path = os.path.join(AVATARS_DIR, f"{file_name_db}.webp")
    png_path = os.path.join(AVATARS_DIR, f"{file_name_db}.png")
    svg_path = os.path.join(AVATARS_DIR, f"{file_name_db}.svg")

    # Also try with original name (parentheses)
    webp_orig = os.path.join(AVATARS_DIR, f"{name}.webp")
    png_orig = os.path.join(AVATARS_DIR, f"{name}.png")
    svg_orig = os.path.join(AVATARS_DIR, f"{name}.svg")

    found = False
    if os.path.exists(webp_path):
        found = True
    elif os.path.exists(webp_orig):
        found = True
        file_name_db = name  # use original
    elif os.path.exists(png_path):
        found = True
    elif os.path.exists(png_orig):
        found = True
        file_name_db = name
    elif os.path.exists(svg_path):
        found = True
    elif os.path.exists(svg_orig):
        found = True
        file_name_db = name

    if found:
        # Prefer webp > png > svg
        if os.path.exists(os.path.join(AVATARS_DIR, f"{file_name_db}.webp")):
            ext = ".webp"
        elif os.path.exists(os.path.join(AVATARS_DIR, f"{file_name_db}.png")):
            ext = ".png"
        else:
            ext = ".svg"

        new_url = f"/avatars/{file_name_db}{ext}"
        if new_url != old_url:
            cur.execute("UPDATE pet_breeds SET image_url = ? WHERE id = ?", (new_url, bid))
            updates += 1
            print(f"  {name}: {old_url} -> {new_url}")
        else:
            print(f"  {name}: OK ({old_url})")
    else:
        issues.append(f"  MISSING: {name} (tried {file_name_db})")

conn.commit()
print(f"\nUpdated {updates} records")
if issues:
    print(f"\n{len(issues)} issues:")
    for i in issues:
        print(i)
else:
    print("All breeds have matching avatar files!")

conn.close()
