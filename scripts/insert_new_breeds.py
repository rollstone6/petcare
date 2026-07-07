#!/usr/bin/env python3
"""Insert new pet breeds into the database"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "petcare.db")

new_breeds = [
    # Rabbits
    ("荷兰垂耳兔", "兔子", "小型", "牙齿过长、胃肠淤积、耳部感染", "性格温顺，耳朵下垂，是最受欢迎的宠物兔品种之一", "/avatars/荷兰垂耳兔.webp", "成年"),
    ("迷你雷克斯兔", "兔子", "小型", "牙齿过长、脚垫炎", "毛发如天鹅绒般柔软，体型小巧", "/avatars/迷你雷克斯兔.webp", "成年"),
    ("安哥拉兔", "兔子", "中型", "毛球症、牙齿过长", "长毛兔，需要定期梳理毛发", "/avatars/安哥拉兔.webp", "成年"),
    ("侏儒兔", "兔子", "小型", "牙齿过长、低血糖", "最小的家兔品种，圆脸大眼非常可爱", "/avatars/侏儒兔.webp", "成年"),
    ("荷兰兔", "兔子", "小型", "牙齿过长、肥胖", "经典的黑白配色，性格活泼", "/avatars/荷兰兔.webp", "成年"),
    # Hamsters
    ("金丝熊仓鼠", "仓鼠", "小型", "颊囊炎、湿尾症", "体型较大的仓鼠，性格温顺", "/avatars/金丝熊仓鼠.webp", "成年"),
    ("三线仓鼠", "仓鼠", "小型", "糖尿病、肿瘤", "最常见的仓鼠品种，背部有三条深色条纹", "/avatars/三线仓鼠.webp", "成年"),
    ("一线仓鼠", "仓鼠", "小型", "糖尿病、湿尾症", "体型较小，性格较独立", "/avatars/一线仓鼠.webp", "成年"),
    ("罗伯罗夫斯基仓鼠", "仓鼠", "小型", "应激反应、腹泻", "最小的仓鼠品种，速度极快", "/avatars/罗伯罗夫斯基仓鼠.webp", "成年"),
    # Birds
    ("虎皮鹦鹉", "鸟类", "小型", "PBFD、呼吸道疾病", "最常见的宠物鸟，聪明好动", "/avatars/虎皮鹦鹉.webp", "成年"),
    ("玄凤鹦鹉", "鸟类", "中型", "PBFD、肥胖", "头顶有黄色冠羽，性格亲人", "/avatars/玄凤鹦鹉.webp", "成年"),
    ("牡丹鹦鹉", "鸟类", "小型", "PBFD、喙羽病", "又称爱情鸟，常成对饲养", "/avatars/牡丹鹦鹉.webp", "成年"),
    ("金丝雀", "鸟类", "小型", "气囊螨、呼吸道疾病", "以美妙歌声闻名的小型鸟", "/avatars/金丝雀.webp", "成年"),
    ("文鸟", "鸟类", "小型", "气囊螨、念珠菌病", "性格温和的群居小鸟", "/avatars/文鸟.webp", "成年"),
    # Fish
    ("金鱼", "鱼类", "小型", "鳔病、白点病", "最受欢迎的观赏鱼，品种繁多", "/avatars/金鱼.webp", "成年"),
    ("锦鲤", "鱼类", "大型", "寄生虫、细菌感染", "大型观赏鱼，寿命长，寓意吉祥", "/avatars/锦鲤.webp", "成年"),
    ("斗鱼", "鱼类", "小型", "鳍腐病、白点病", "华丽的热带鱼，雄鱼好斗", "/avatars/斗鱼.webp", "成年"),
    ("孔雀鱼", "鱼类", "小型", "白点病、尾腐病", "色彩斑斓的小型热带鱼", "/avatars/孔雀鱼.webp", "成年"),
    # Reptiles
    ("豹纹守宫", "爬行类", "小型", "蜕皮困难、MBD", "温顺的蜥蜴，适合初学者", "/avatars/豹纹守宫.webp", "成年"),
    ("鬃狮蜥", "爬行类", "中型", "MBD、代谢性骨病", "性格温顺的中型蜥蜴", "/avatars/鬃狮蜥.webp", "成年"),
    # Turtles
    ("巴西龟", "爬行类", "中型", "壳腐病、维生素A缺乏", "最常见的宠物龟，适应性强", "/avatars/巴西龟.webp", "成年"),
    ("草龟", "爬行类", "中型", "壳腐病、肺炎", "中国传统宠物龟，寿命长", "/avatars/草龟.webp", "成年"),
    # Others
    ("非洲迷你刺猬", "刺猬", "小型", "螨虫、肥胖、WHS", "夜行性小动物，需要温暖环境", "/avatars/非洲迷你刺猬.webp", "成年"),
    ("雪貂", "雪貂", "小型", "肾上腺疾病、胰岛素瘤", "活泼好动的小型哺乳动物", "/avatars/雪貂.webp", "成年"),
    ("豚鼠", "豚鼠", "小型", "维生素C缺乏、牙齿过长", "温顺的群居动物，需要陪伴", "/avatars/豚鼠.webp", "成年"),
    ("龙猫", "龙猫", "小型", "中暑、牙齿问题", "毛茸茸的夜行动物，寿命长达15年", "/avatars/龙猫.webp", "成年"),
    ("蜜袋鼯", "蜜袋鼯", "小型", "钙磷比失调、营养不良", "会滑翔的有袋动物，需要大量陪伴", "/avatars/蜜袋鼯.webp", "成年"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

inserted = 0
for breed in new_breeds:
    # Check if already exists
    cur.execute("SELECT id FROM pet_breeds WHERE name = ?", (breed[0],))
    if cur.fetchone():
        print(f"  SKIP {breed[0]} (already exists)")
        continue
    try:
        cur.execute(
            "INSERT INTO pet_breeds (name, species, size, common_issues, description, image_url, age_stage) VALUES (?, ?, ?, ?, ?, ?, ?)",
            breed,
        )
        inserted += 1
        print(f"  + {breed[0]} ({breed[1]})")
    except Exception as e:
        print(f"  ERROR {breed[0]}: {e}")

conn.commit()
print(f"\nInserted {inserted} new breeds")

cur.execute("SELECT COUNT(*) FROM pet_breeds")
print(f"Total breeds: {cur.fetchone()[0]}")

cur.execute("SELECT DISTINCT species FROM pet_breeds ORDER BY species")
print(f"Species: {[r[0] for r in cur.fetchall()]}")

conn.close()
