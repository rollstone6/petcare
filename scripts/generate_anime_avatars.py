#!/usr/bin/env python3
"""
批量生成动漫风格宠物头像
"""
import sqlite3
import json
import os

DB_PATH = '/root/workspace/petcare/backend/petcare.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('SELECT id, name, species FROM pet_breeds ORDER BY species, name')
breeds = cur.fetchall()
conn.close()

# 生成每个品种的 prompt
prompts = []
for bid, name, species in breeds:
    prompt = f"""A cute anime-style portrait illustration of a {name} ({species}), 
kawaii art style, round face, big sparkling eyes, soft pastel colors, 
professional pet portrait, 512x512 square format, white background, 
studio ghibli inspired, adorable and detailed"""
    
    prompts.append({
        'id': bid,
        'name': name,
        'species': species,
        'prompt': prompt
    })

# 输出为 JSON 供批量处理
output_file = '/tmp/anime_avatar_prompts.json'
with open(output_file, 'w') as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print(f"生成 {len(prompts)} 个品种的 prompt")
print(f"已保存到 {output_file}")
print(f"\n示例 prompt:")
print(prompts[0]['prompt'])
