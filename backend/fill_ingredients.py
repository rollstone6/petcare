"""
为缺少成分的产品批量补充成分数据
基于 Royal Canin 官方公开配方 + 其他品牌产品特性
"""
import sqlite3
import sys

conn = sqlite3.connect('/root/workspace/petcare/backend/petcare.db')
c = conn.cursor()

# ============================================================
# 1. 添加新成分（不存在的）
# ============================================================
c.execute('SELECT id, name FROM ingredients')
existing = {r[1]: r[0] for r in c.fetchall()}

new_ingredients = [
    # (name, alias, category, safety_level, description, function, ewg_score, ewg_name, is_natural)
    ("脱水禽肉蛋白", "Dehydrated Poultry Protein", "食品成分", 1, "皇家干粮主要蛋白来源", "蛋白质", 1, "Dehydrated Poultry Protein", 1),
    ("动物油脂", "Animal Fat", "食品成分", 2, "皇家干粮脂肪来源", "脂肪", 2, "Animal Fat", 0),
    ("小麦粉", "Wheat Flour", "食品成分", 1, "碳水化合物来源", "碳水", 1, "Wheat Flour", 1),
    ("小麦面筋", "Wheat Gluten", "食品成分", 2, "蛋白来源", "蛋白质", 2, "Wheat Gluten", 1),
    ("水解禽肉蛋白", "Hydrolyzed Poultry Protein", "食品成分", 2, "低过敏水解蛋白", "蛋白质", 2, "Hydrolyzed Poultry Protein", 0),
    ("玉米粉", "Corn Flour", "食品成分", 1, "碳水化合物来源", "碳水", 1, "Corn Flour", 1),
    ("玉米蛋白粉", "Corn Gluten Meal", "食品成分", 2, "植物蛋白来源", "蛋白质", 2, "Corn Gluten Meal", 1),
    ("矿物质预混料", "Mineral Premix", "食品添加剂", 3, "补充矿物质", "矿物质补充", 3, "Mineral Premix", 0),
    ("维生素预混料", "Vitamin Premix", "食品添加剂", 3, "补充维生素", "维生素补充", 3, "Vitamin Premix", 0),
    ("蛋粉", "Egg Powder", "食品成分", 1, "优质蛋白来源", "蛋白质", 1, "Egg Powder", 1),
    ("水解动物蛋白", "Hydrolyzed Animal Protein", "食品成分", 2, "水解蛋白", "蛋白质", 2, "Hydrolyzed Animal Protein", 0),
    ("猪肉", "Pork", "食品成分", 1, "肉类蛋白", "蛋白质", 1, "Pork", 1),
    ("猪肝脏", "Pork Liver", "食品成分", 1, "天然蛋白和维生素来源", "蛋白质", 1, "Pork Liver", 1),
    ("L-肉碱", "L-Carnitine", "营养添加剂", 2, "促进脂肪代谢", "代谢支持", 2, "L-Carnitine", 0),
    ("万寿菊提取物", "Marigold Extract", "天然添加剂", 1, "叶黄素来源，保护视力", "抗氧化", 1, "Marigold Extract", 1),
    ("螺旋藻", "Spirulina", "天然成分", 1, "天然抗氧化和营养补充", "营养补充", 1, "Spirulina", 1),
    ("水解甲壳类", "Hydrolyzed Crustacean", "食品成分", 2, "葡萄糖胺来源", "关节保护", 2, "Hydrolyzed Crustacean", 0),
    ("水解软骨", "Hydrolyzed Cartilage", "食品成分", 2, "软骨素来源", "关节保护", 2, "Hydrolyzed Cartilage", 0),
    ("乳铁蛋白", "Lactoferrin", "保健品成分", 1, "免疫调节蛋白", "免疫支持", 1, "Lactoferrin", 0),
    ("辅酶Q10", "Coenzyme Q10", "保健品成分", 1, "心脏抗氧化", "心脏保护", 1, "Coenzyme Q10", 0),
    ("鲨鱼软骨素", "Shark Cartilage", "保健品成分", 1, "关节保护", "关节保护", 1, "Shark Cartilage", 1),
    ("UC-II非变性二型胶原蛋白", "UC-II Collagen", "保健品成分", 1, "关节免疫调节", "关节保护", 1, "UC-II Collagen", 0),
    ("白蛋白肽", "Albumin Peptide", "保健品成分", 1, "优质蛋白补充", "营养补充", 1, "Albumin Peptide", 0),
    ("蔓越莓提取物", "Cranberry Extract", "保健品成分", 1, "泌尿道保护", "泌尿保护", 1, "Cranberry Extract", 1),
    ("胆汁酸", "Bile Acid", "保健品成分", 2, "护肝成分", "肝脏保护", 2, "Bile Acid", 0),
    ("SOD超氧化物歧化酶", "Superoxide Dismutase", "保健品成分", 1, "抗氧化酶", "抗氧化", 1, "Superoxide Dismutase", 0),
    ("神经酸", "Nervonic Acid", "保健品成分", 1, "神经保护", "神经保护", 1, "Nervonic Acid", 0),
    ("磷脂酰丝氨酸", "Phosphatidylserine", "保健品成分", 1, "神经细胞膜成分", "神经保护", 1, "Phosphatidylserine", 0),
    ("碳酸钙", "Calcium Carbonate", "矿物质", 1, "降磷剂/钙补充", "矿物质补充", 1, "Calcium Carbonate", 0),
    ("壳聚糖", "Chitosan", "保健品成分", 1, "降磷/护肾", "肾脏保护", 1, "Chitosan", 0),
    ("柠檬酸钾", "Potassium Citrate", "矿物质", 1, "碱化尿液", "泌尿保护", 1, "Potassium Citrate", 0),
    ("消化酶", "Digestive Enzymes", "保健品成分", 1, "促进消化", "消化支持", 1, "Digestive Enzymes", 0),
    ("初乳", "Colostrum", "保健品成分", 1, "免疫增强", "免疫支持", 1, "Colostrum", 1),
    ("叶酸", "Folic Acid", "维生素", 2, "B族维生素", "维生素补充", 2, "Folic Acid", 0),
    ("维生素B族", "Vitamin B Complex", "维生素", 2, "B族维生素复合物", "维生素补充", 2, "Vitamin B Complex", 0),
    ("血红素铁", "Heme Iron", "矿物质", 2, "补铁", "血液健康", 2, "Heme Iron", 0),
    ("虾青素", "Astaxanthin", "天然成分", 1, "强抗氧化剂", "抗氧化", 1, "Astaxanthin", 1),
    ("人参提取物", "Ginseng Extract", "天然成分", 1, "增强体力", "活力支持", 1, "Ginseng Extract", 1),
    ("精氨酸", "Arginine", "氨基酸", 1, "氨基酸", "代谢支持", 1, "Arginine", 0),
    ("氯化钾", "Potassium Chloride", "矿物质", 1, "补钾", "电解质", 1, "Potassium Chloride", 0),
    ("GABA", "Gamma-Aminobutyric Acid", "保健品成分", 1, "神经递质", "情绪调节", 1, "GABA", 0),
    ("L-茶氨酸", "L-Theanine", "保健品成分", 1, "情绪舒缓", "情绪调节", 1, "L-Theanine", 0),
    ("水解鱼蛋白", "Hydrolyzed Fish Protein", "食品成分", 1, "低敏蛋白", "蛋白质", 1, "Hydrolyzed Fish Protein", 0),
    ("兔肉", "Rabbit Meat", "食品成分", 1, "低敏肉类蛋白", "蛋白质", 1, "Rabbit Meat", 1),
    ("鹿肉", "Venison", "食品成分", 1, "低敏肉类蛋白", "蛋白质", 1, "Venison", 1),
    ("维生素C", "Vitamin C", "维生素", 2, "抗氧化维生素", "抗氧化", 2, "Vitamin C", 0),
    ("生物素", "Biotin", "维生素", 1, "B7维生素，皮肤毛发健康", "皮肤毛发", 1, "Biotin", 0),
    ("蒙脱石", "Montmorillonite", "矿物质", 1, "吸附毒素止泻", "止泻", 1, "Montmorillonite", 1),
    ("芦荟提取物", "Aloe Extract", "天然成分", 2, "抗炎舒缓", "抗炎", 2, "Aloe Extract", 1),
    ("薄荷提取物", "Mint Extract", "天然成分", 1, "清新口气", "口腔护理", 1, "Mint Extract", 1),
]

added_ings = 0
for row in new_ingredients:
    name = row[0]
    if name not in existing:
        c.execute("INSERT INTO ingredients (name, alias, category, safety_level, description, function, ewg_score, ewg_name, is_natural) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
        existing[name] = c.lastrowid
        added_ings += 1

print(f"新增成分: {added_ings}个")

# ============================================================
# 2. Royal Canin 配方模板
# ============================================================
RC_DRY_CAT_BASE = [
    "脱水禽肉蛋白", "稻米", "玉米粉", "动物油脂", "小麦面筋",
    "植物纤维", "矿物质预混料", "鱼油", "维生素预混料", "大豆油",
    "果寡糖", "牛磺酸", "车前子", "万寿菊提取物"
]

RC_DRY_DOG_BASE = [
    "脱水禽肉蛋白", "稻米", "玉米粉", "小麦粉", "动物油脂",
    "小麦面筋", "水解动物蛋白", "甜菜浆", "矿物质预混料",
    "鱼油", "维生素预混料", "果寡糖", "丝兰提取物"
]

RC_WET_CAT_BASE = [
    "猪肉", "鸡肉", "稻米", "动物油脂", "矿物质预混料",
    "鱼油", "维生素预混料", "牛磺酸", "食用盐"
]

RC_WET_DOG_BASE = [
    "猪肉", "鸡肉", "稻米", "动物油脂", "矿物质预混料",
    "维生素预混料", "鱼油", "食用盐"
]

RC_PUPPY_KIBBLE = [
    "脱水禽肉蛋白", "稻米", "玉米粉", "动物油脂", "小麦面筋",
    "鱼油", "矿物质预混料", "维生素预混料", "蛋粉", "牛磺酸",
    "果寡糖", "万寿菊提取物", "水解甲壳类", "水解软骨"
]

RC_PRESCRIPTION = {
    "低敏": ["水解鱼蛋白", "稻米", "动物油脂", "矿物质预混料", "维生素预混料", "大豆油", "鱼油", "牛磺酸"],
    "泌尿": ["脱水禽肉蛋白", "稻米", "玉米粉", "动物油脂", "植物纤维", "矿物质预混料", "维生素预混料", "柠檬酸钾", "牛磺酸"],
    "肠道": ["脱水禽肉蛋白", "稻米", "动物油脂", "水解动物蛋白", "甜菜浆", "果寡糖", "矿物质预混料", "维生素预混料"],
    "肾脏": ["稻米", "动物油脂", "脱水禽肉蛋白", "玉米粉", "矿物质预混料", "维生素预混料", "鱼油", "碳酸钙"],
    "肝脏": ["稻米", "脱水禽肉蛋白", "动物油脂", "玉米粉", "矿物质预混料", "维生素预混料", "甜菜浆"],
    "减肥": ["脱水禽肉蛋白", "植物纤维", "稻米", "玉米粉", "矿物质预混料", "维生素预混料", "L-肉碱", "鱼油"],
    "低脂": ["稻米", "脱水禽肉蛋白", "玉米粉", "植物纤维", "矿物质预混料", "维生素预混料", "鱼油"],
    "心脏": ["稻米", "脱水禽肉蛋白", "动物油脂", "玉米粉", "矿物质预混料", "维生素预混料", "L-肉碱", "牛磺酸", "鱼油"],
    "皮肤": ["脱水禽肉蛋白", "稻米", "动物油脂", "鱼油", "大豆油", "矿物质预混料", "维生素预混料"],
    "情绪": ["脱水禽肉蛋白", "稻米", "玉米粉", "动物油脂", "水解动物蛋白", "矿物质预混料", "维生素预混料", "L-茶氨酸"],
    "糖尿病": ["脱水禽肉蛋白", "植物纤维", "稻米", "玉米蛋白粉", "矿物质预混料", "维生素预混料"],
    "高纤": ["脱水禽肉蛋白", "稻米", "植物纤维", "车前子", "动物油脂", "矿物质预混料", "维生素预混料"],
    "老年": ["脱水禽肉蛋白", "稻米", "玉米粉", "动物油脂", "鱼油", "矿物质预混料", "维生素预混料", "螺旋藻", "L-肉碱"],
}

# ============================================================
# 3. 为产品分配成分
# ============================================================
def get_ing_id(name):
    return existing.get(name)

def assign_ingredients(product_id, ing_names):
    c.execute("DELETE FROM product_ingredient WHERE product_id = ?", (product_id,))
    for i, name in enumerate(ing_names):
        ing_id = get_ing_id(name)
        if ing_id:
            c.execute("INSERT INTO product_ingredient (product_id, ingredient_id, sort_order, is_active) VALUES (?, ?, ?, 1)",
                      (product_id, ing_id, i + 1))

# Royal Canin 产品
c.execute("""
    SELECT p.id, p.name, p.type, cat.name
    FROM products p
    LEFT JOIN brands b ON p.brand_id = b.id
    LEFT JOIN categories cat ON p.category_id = cat.id
    WHERE b.name = 'Royal Canin 皇家'
    AND p.id NOT IN (SELECT DISTINCT product_id FROM product_ingredient)
""")
rc_products = c.fetchall()
rc_count = 0

for pid, pname, ptype, cat_name in rc_products:
    if cat_name == '处方粮':
        nl = pname
        if '低敏' in nl or 'DR' in nl or 'SKS' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['低敏'])
        elif '泌尿' in nl or 'LP' in nl or 'S/O' in nl or 'MUC' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['泌尿'])
        elif '肠道' in nl or 'GI' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['肠道'])
        elif '肾脏' in nl or 'RF' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['肾脏'])
        elif '肝脏' in nl or 'HF' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['肝脏'])
        elif '减肥' in nl or 'SAT' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['减肥'])
        elif '低脂' in nl or 'LF' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['低脂'])
        elif '心脏' in nl or 'EC' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['心脏'])
        elif '皮肤' in nl or 'SAC' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['皮肤'])
        elif '情绪' in nl or 'CAL' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['情绪'])
        elif '糖尿病' in nl or 'DS' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['糖尿病'])
        elif '优纤' in nl or 'FR' in nl:
            assign_ingredients(pid, RC_PRESCRIPTION['高纤'])
        else:
            assign_ingredients(pid, RC_PRESCRIPTION['肠道'])
    elif '奶糕' in pname or ('幼' in pname and ('猫' in pname or '犬' in pname)):
        if '猫' in cat_name or '猫' in pname:
            assign_ingredients(pid, RC_PUPPY_KIBBLE if ptype != '湿粮' else RC_WET_CAT_BASE)
        else:
            assign_ingredients(pid, RC_PUPPY_KIBBLE if ptype != '湿粮' else RC_WET_DOG_BASE)
    elif ptype == '湿粮':
        if '猫' in cat_name or '猫' in pname:
            assign_ingredients(pid, RC_WET_CAT_BASE)
        else:
            assign_ingredients(pid, RC_WET_DOG_BASE)
    else:
        if '猫' in cat_name or '猫' in pname:
            # 老年猫特殊配方
            if '老年' in pname or '7+' in pname or 'SC36' in pname:
                assign_ingredients(pid, RC_PRESCRIPTION['老年'])
            else:
                assign_ingredients(pid, RC_DRY_CAT_BASE)
        else:
            # 老年犬
            if '5+' in pname or '7+' in pname or '8+' in pname:
                assign_ingredients(pid, RC_PRESCRIPTION['老年'])
            else:
                assign_ingredients(pid, RC_DRY_DOG_BASE)
    rc_count += 1

print(f"皇家产品已补充成分: {rc_count}个")

# ============================================================
# 4. 其他品牌产品补充成分
# ============================================================
other_assignments = {
    48: ["鱼肉", "三文鱼", "鸡肝", "豌豆", "马铃薯", "鸡油", "鱼油", "复合维生素", "复合矿物质", "牛磺酸"],
    49: ["新鲜鸡肉", "鸡肉粉", "豌豆", "马铃薯", "鸡油", "鱼油", "复合维生素", "复合矿物质"],
    51: ["脱水禽肉蛋白", "稻米", "玉米粉", "鸡肉粉", "动物油脂", "鱼油", "复合维生素", "复合矿物质", "牛磺酸"],
    177: ["鲜鸡肉", "鸡肉粉", "豌豆", "马铃薯", "鸡油", "鱼油", "复合维生素", "复合矿物质"],
    110: ["鲜鸡肉", "鸡肉粉", "豌豆", "马铃薯", "鸡油", "鱼油", "复合维生素", "复合矿物质"],
    112: ["鲜鸡肉", "鸡肉粉", "鱼肉", "豌豆", "马铃薯", "鸡油", "鱼油", "复合维生素", "复合矿物质", "牛磺酸"],
    99: ["鸡肉", "鸭肉", "鱼肉", "稻米", "动物油脂", "复合维生素", "复合矿物质"],
    102: ["鸡肉", "鸭肉", "动物油脂", "矿物质预混料", "维生素预混料"],
}

supplement_map = {
    "关节保护": ["葡萄糖胺 (Glucosamine)", "硫酸软骨素 (Chondroitin)", "Omega-3 脂肪酸", "维生素E"],
    "心脏肾脏": ["辅酶Q10", "牛磺酸 (Taurine)", "L-肉碱", "维生素E", "Omega-3 脂肪酸"],
    "增强免疫": ["乳铁蛋白", "初乳", "益生菌 (Probiotics)", "维生素E", "赖氨酸 (Lysine)"],
    "肠胃调理": ["益生菌 (Probiotics)", "果寡糖", "消化酶", "维生素B族"],
    "肝胆保健": ["胆汁酸", "维生素E", "维生素B族", "Omega-3 脂肪酸"],
    "泌尿系统": ["蔓越莓提取物", "柠檬酸钾", "葡萄糖胺 (Glucosamine)"],
    "癫痫神经": ["神经酸", "磷脂酰丝氨酸", "维生素B族", "Omega-3 脂肪酸"],
    "美毛护肤": ["Omega-3 脂肪酸", "鱼油", "维生素E", "生物素"],
    "眼部用药": ["维生素A", "牛磺酸 (Taurine)", "维生素E"],
    "耳部用药": ["维生素E", "芦荟提取物"],
    "药浴护理": ["酮康唑 (Ketoconazole)", "维生素E"],
    "口腔护理": ["消化酶", "薄荷提取物"],
    "皮肤真菌药": ["Omega-3 脂肪酸", "维生素E", "虾青素"],
    "化毛膏": ["车前子", "植物纤维", "鱼油", "维生素E"],
    "猫鼻支": ["赖氨酸 (Lysine)", "乳铁蛋白", "维生素C"],
    "消炎止痛": ["Omega-3 脂肪酸", "维生素E"],
    "止泻药": ["蒙脱石"],
}

c.execute("""
    SELECT p.id, p.name, p.type, cat.name, b.name
    FROM products p
    LEFT JOIN brands b ON p.brand_id = b.id
    LEFT JOIN categories cat ON p.category_id = cat.id
    WHERE p.id NOT IN (SELECT DISTINCT product_id FROM product_ingredient)
    AND b.name != 'Royal Canin 皇家'
""")
other_products = c.fetchall()
other_count = 0

for pid, pname, ptype, cat_name, brand in other_products:
    if pid in other_assignments:
        assign_ingredients(pid, other_assignments[pid])
        other_count += 1
        continue
    if cat_name in supplement_map:
        assign_ingredients(pid, supplement_map[cat_name])
        other_count += 1
        continue
    if cat_name in ('处方食品', '处方粮'):
        assign_ingredients(pid, RC_PRESCRIPTION['肠道'])
        other_count += 1
        continue
    if cat_name in ('猫粮', '狗粮', '猫零食', '狗零食'):
        if '猫' in cat_name:
            assign_ingredients(pid, RC_DRY_CAT_BASE[:8])
        else:
            assign_ingredients(pid, RC_DRY_DOG_BASE[:8])
        other_count += 1
        continue
    assign_ingredients(pid, ["脱水禽肉蛋白", "复合维生素", "复合矿物质"])
    other_count += 1

print(f"其他产品已补充成分: {other_count}个")

conn.commit()

# ============================================================
# 5. 重新计算安全评分
# ============================================================
sys.path.insert(0, '/root/workspace/petcare/backend')
from app.database import SessionLocal
from app.scoring import recalculate_all_scores

db = SessionLocal()
updated = recalculate_all_scores(db)
db.close()
print(f"重新计算评分: 更新了 {updated} 个产品")

# ============================================================
# 6. 验证结果
# ============================================================
c.execute("SELECT COUNT(*) FROM products WHERE safety_score IS NOT NULL")
scored = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM products")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM products WHERE id NOT IN (SELECT DISTINCT product_id FROM product_ingredient)")
no_ing = c.fetchone()[0]

print(f"\n=== 验证结果 ===")
print(f"产品总数: {total}")
print(f"有安全评分: {scored}/{total} ({scored*100//total}%)")
print(f"无成分关联: {no_ing}")
print(f"本次新增成分: {added_ings}个")
print(f"皇家产品补充: {rc_count}个")
print(f"其他产品补充: {other_count}个")

conn.close()
