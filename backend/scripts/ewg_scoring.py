#!/usr/bin/env python3
"""
EWG 成分安全评分 ETL 脚本

评分体系（1-10分，基于EWG Skin Deep数据库）：
- 1-2: 低危害（绿色）- 天然成分、已知安全
- 3-6: 中等危害（黄色）- 有一定关注
- 7-10: 高危害（红色）- 致癌、致畸、内分泌干扰

规则：
- 基础肉类原料（天然食材）: 1分
- 化学添加剂: 按EWG数据库评分
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# EWG 评分映射表
# 格式: 中文名 -> (英文名, EWG评分, 是否天然)
EWG_DATABASE = {
    # ===== 天然肉类原料 (1分) =====
    "鲜鸡肉": ("Fresh Chicken", 1, True),
    "鲜鸡胸肉": ("Fresh Chicken Breast", 1, True),
    "鸡胸肉": ("Chicken Breast", 1, True),
    "冻干鸡肉": ("Freeze-Dried Chicken", 1, True),
    "冻干鸡肉脖子": ("Freeze-Dried Chicken Necks", 1, True),
    "鸡肉粉": ("Chicken Meal", 1, True),
    "脱水鸡肉": ("Dehydrated Chicken", 1, True),
    "脱水禽肉": ("Dehydrated Poultry", 1, True),
    "鲜牛肉": ("Fresh Beef", 1, True),
    "牛肉粉": ("Beef Meal", 1, True),
    "牛肉": ("Beef", 1, True),
    "羊肉": ("Lamb", 1, True),
    "鸭肉": ("Duck", 1, True),
    "鲜鱼肉": ("Fresh Fish", 1, True),
    "三文鱼": ("Salmon", 1, True),
    "鲑鱼": ("Salmon", 1, True),
    "金枪鱼": ("Tuna", 1, True),
    "鳕鱼": ("Cod", 1, True),
    "沙丁鱼": ("Sardine", 1, True),
    "鱼粉": ("Fish Meal", 1, True),
    "深海鱼油": ("Deep Sea Fish Oil", 1, True),
    "鱼油": ("Fish Oil", 1, True),
    "鸡肝": ("Chicken Liver", 1, True),
    "牛肝": ("Beef Liver", 1, True),
    "鸡心": ("Chicken Heart", 1, True),
    
    # ===== 天然植物原料 (1-2分) =====
    "糙米": ("Brown Rice", 1, True),
    "稻米": ("Rice", 1, True),
    "白米": ("White Rice", 1, True),
    "燕麦": ("Oats", 1, True),
    "大麦": ("Barley", 1, True),
    "红薯": ("Sweet Potato", 1, True),
    "马铃薯": ("Potato", 1, True),
    "豌豆": ("Pea", 1, True),
    "豌豆蛋白": ("Pea Protein", 2, True),
    "玉米": ("Corn", 1, True),
    "玉米麸质": ("Corn Gluten", 1, True),
    "小麦": ("Wheat", 1, True),
    "大豆": ("Soybean", 1, True),
    "大豆油": ("Soybean Oil", 2, True),
    "亚麻籽": ("Flaxseed", 1, True),
    "葵花籽": ("Sunflower Seeds", 1, True),
    "南瓜": ("Pumpkin", 1, True),
    "胡萝卜": ("Carrot", 1, True),
    "蓝莓": ("Blueberry", 1, True),
    "蔓越莓": ("Cranberry", 1, True),
    "苹果": ("Apple", 1, True),
    "菠菜": ("Spinach", 1, True),
    "西兰花": ("Broccoli", 1, True),
    
    # ===== 天然油脂 (1-2分) =====
    "鸡油": ("Chicken Fat", 1, True),
    "牛油": ("Beef Tallow", 1, True),
    "葵花籽油": ("Sunflower Oil", 1, True),
    "亚麻籽油": ("Flaxseed Oil", 1, True),
    "菜籽油": ("Canola Oil", 2, True),
    "椰子油": ("Coconut Oil", 1, True),
    
    # ===== 维生素类 (2-4分) =====
    "维生素A": ("Vitamin A", 3, False),
    "维生素D3": ("Cholecalciferol", 2, False),
    "维生素E": ("Tocopherol", 2, False),
    "维生素B1": ("Thiamine", 2, False),
    "维生素B2": ("Riboflavin", 2, False),
    "维生素B6": ("Pyridoxine", 2, False),
    "维生素B12": ("Cyanocobalamin", 2, False),
    "维生素C": ("Ascorbic Acid", 2, False),
    "维生素K": ("Menadione", 6, False),  # 合成维生素K风险较高
    "复合维生素": ("Multivitamin Complex", 3, False),
    "烟酸": ("Niacin", 2, False),
    "泛酸": ("Pantothenic Acid", 2, False),
    "叶酸": ("Folic Acid", 2, False),
    "生物素": ("Biotin", 1, False),
    
    # ===== 矿物质 (2-4分) =====
    "硫酸锌": ("Zinc Sulfate", 3, False),
    "硫酸亚铁": ("Ferrous Sulfate", 3, False),
    "硫酸铜": ("Copper Sulfate", 4, False),
    "硫酸锰": ("Manganese Sulfate", 3, False),
    "亚硒酸钠": ("Sodium Selenite", 5, False),  # 硒化合物中等风险
    "碘酸钾": ("Potassium Iodate", 3, False),
    "碳酸钙": ("Calcium Carbonate", 1, False),
    "磷酸氢钙": ("Dicalcium Phosphate", 2, False),
    "氯化钾": ("Potassium Chloride", 2, False),
    "氯化钠": ("Sodium Chloride", 1, False),
    "食用盐": ("Salt", 1, False),
    "复合矿物质": ("Mineral Complex", 3, False),
    
    # ===== 氨基酸 (2-3分) =====
    "牛磺酸": ("Taurine", 1, False),  # 对猫必需，非常安全
    "L-赖氨酸": ("L-Lysine", 2, False),
    "DL-蛋氨酸": ("DL-Methionine", 3, False),
    "L-色氨酸": ("L-Tryptophan", 2, False),
    
    # ===== 益生菌 (1-2分) =====
    "益生菌": ("Probiotics", 1, False),
    "乳酸菌": ("Lactobacillus", 1, False),
    "双歧杆菌": ("Bifidobacterium", 1, False),
    "酵母": ("Yeast", 1, False),
    "啤酒酵母": ("Brewer's Yeast", 1, False),
    
    # ===== 增稠剂/凝胶 (3-6分) =====
    "卡拉胶": ("Carrageenan", 6, False),  # 争议较大
    "瓜尔胶": ("Guar Gum", 2, False),
    "黄原胶": ("Xanthan Gum", 2, False),
    "琼脂": ("Agar", 1, False),
    "明胶": ("Gelatin", 1, False),
    "刺槐豆胶": ("Locust Bean Gum", 2, False),
    
    # ===== 防腐剂 (3-10分) =====
    "混合生育酚": ("Mixed Tocopherols", 2, False),  # 天然维生素E防腐
    "山梨酸钾": ("Potassium Sorbate", 3, False),
    "山梨酸": ("Sorbic Acid", 3, False),
    "BHA": ("Butylated Hydroxyanisole", 9, False),  # 高致癌风险
    "BHT": ("Butylated Hydroxytoluene", 8, False),  # 内分泌干扰
    "乙氧基喹啉": ("Ethoxyquin", 8, False),  # 高致癌风险
    "亚硝酸钠": ("Sodium Nitrite", 9, False),  # 高致癌风险
    "苯甲酸钠": ("Sodium Benzoate", 6, False),
    
    # ===== 色素 (5-10分) =====
    "焦糖色": ("Caramel Color", 7, False),  # 可能含致癌物
    "二氧化钛": ("Titanium Dioxide", 6, False),  # 纳米颗粒风险
    "红色40号": ("Red 40", 8, False),
    "黄色5号": ("Yellow 5", 8, False),
    "黄色6号": ("Yellow 6", 8, False),
    "蓝色1号": ("Blue 1", 7, False),
    "蓝色2号": ("Blue 2", 7, False),
    "胭脂红": ("Carmine", 4, False),
    "姜黄": ("Turmeric", 1, True),  # 天然色素
    
    # ===== 调味剂 (2-4分) =====
    "天然香料": ("Natural Flavor", 2, False),
    "人工香料": ("Artificial Flavor", 6, False),
    "甜菜浆": ("Beet Pulp", 1, True),
    "果寡糖": ("Fructooligosaccharides", 1, False),
    "低聚果糖": ("FOS", 1, False),
    "甘露寡糖": ("Mannan-oligosaccharides", 1, False),
    
    # ===== 其他添加剂 =====
    "磷酸": ("Phosphoric Acid", 3, False),
    "柠檬酸": ("Citric Acid", 2, False),
    "苹果酸": ("Malic Acid", 2, False),
    "抗氧化剂": ("Antioxidants", 2, False),
    "植物纤维": ("Plant Fiber", 1, True),
    "丝兰提取物": ("Yucca Extract", 1, True),
    "车前子": ("Psyllium Husk", 1, True),
    "动物脂肪": ("Animal Fat", 2, False),
    "水解动物蛋白": ("Hydrolyzed Animal Protein", 2, False),
    
    # ===== 药品成分 (需要特别评分) =====
    # 驱虫药
    "塞拉菌素": ("Selamectin", 5, False),  # 处方药，需兽医指导
    # ===== 驱虫药 =====
    "塞拉菌素": ("Selamectin", 5, False),
    "莫昔克丁": ("Moxidectin", 5, False),
    "伊维菌素": ("Ivermectin", 6, False),
    "非泼罗尼": ("Fipronil", 6, False),
    "吡喹酮": ("Praziquantel", 5, False),
    "米尔贝肟": ("Milbemycin Oxime", 5, False),
    "阿福拉纳": ("Afoxolaner", 5, False),
    "氟拉纳": ("Fluralaner", 5, False),
    # 抗生素
    "阿莫西林克拉维酸钾": ("Amoxicillin-Clavulanate", 5, False),
    "恩诺沙星": ("Enrofloxacin", 6, False),  # 氟喹诺酮类
    "头孢氨苄": ("Cephalexin", 5, False),
    
    # 抗炎药
    "美洛昔康": ("Meloxicam", 6, False),  # NSAID
    "泼尼松龙": ("Prednisolone", 6, False),  # 类固醇
    
    # 抗真菌
    "特比萘芬": ("Terbinafine", 6, False),
    "酮康唑": ("Ketoconazole", 7, False),  # 肝毒性风险
    "莫匹罗星": ("Mupirocin", 5, False),
    
    # 心脏药
    "匹莫苯丹": ("Pimobendan", 5, False),  # 处方药
    "贝那普利": ("Benazepril", 5, False),  # ACE抑制剂
    
    # 关节保健
    "葡萄糖胺": ("Glucosamine", 2, False),  # 非常安全
    "硫酸软骨素": ("Chondroitin Sulfate", 2, False),  # 非常安全
    "绿唇贻贝提取物": ("Green Lipped Mussel Extract", 1, True),
    
    # ===== 营养补充 =====
    "Omega-3脂肪酸": ("Omega-3 Fatty Acids", 1, False),
    "Omega-3 脂肪酸": ("Omega-3 Fatty Acids", 1, False),
    "赖氨酸": ("Lysine", 1, False),
    "L-抗坏血酸": ("L-Ascorbic Acid", 2, False),
    
    # 疫苗抗原
    "犬瘟热病毒抗原": ("Canine Distemper Virus Antigen", 2, False),
    "犬细小病毒抗原": ("Canine Parvovirus Antigen", 2, False),
    "狂犬病病毒抗原": ("Rabies Virus Antigen", 2, False),
    "猫泛白细胞减少症病毒抗原": ("Feline Panleukopenia Virus Antigen", 2, False),
    "猫疱疹病毒抗原": ("Feline Herpesvirus Antigen", 2, False),
    "猫杯状病毒抗原": ("Feline Calicivirus Antigen", 2, False),
}


def update_ingredient_scores():
    """更新所有成分的EWG评分"""
    db_path = Path(__file__).parent.parent / 'petcare.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有成分
    cursor.execute('SELECT id, name, category FROM ingredients')
    ingredients = cursor.fetchall()
    
    updated = 0
    not_found = []
    
    print(f"\n{'='*60}")
    print(f"EWG 成分安全评分更新")
    print(f"{'='*60}\n")
    
    for ing_id, name, category in ingredients:
        # 去除括号内容匹配
        base_name = name.split('(')[0].strip()
        
        # 查找匹配
        match = None
        for key, value in EWG_DATABASE.items():
            if base_name in key or key in base_name:
                match = (key, value)
                break
        
        if match:
            key, (ewg_name, score, is_natural) = match
            
            # 更新数据库
            cursor.execute('''
                UPDATE ingredients 
                SET ewg_score = ?, ewg_name = ?, is_natural = ?
                WHERE id = ?
            ''', (score, ewg_name, 1 if is_natural else 0, ing_id))
            
            updated += 1
            
            # 打印详情
            risk_color = "🟢" if score <= 2 else "🟡" if score <= 6 else "🔴"
            natural_tag = "[天然]" if is_natural else "[化学]"
            print(f"{risk_color} {natural_tag} {name:<20} → EWG {score:2d}分 ({ewg_name})")
        else:
            not_found.append((ing_id, name, category))
    
    conn.commit()
    conn.close()
    
    # 打印未匹配的成分
    print(f"\n{'='*60}")
    print(f"统计结果")
    print(f"{'='*60}")
    print(f"✅ 成功更新: {updated} 个成分")
    print(f"❌ 未匹配: {len(not_found)} 个成分")
    
    if not_found:
        print("\n未匹配的成分（需要手动添加）:")
        for ing_id, name, category in not_found:
            print(f"  - {name} ({category})")
    
    return updated, not_found


if __name__ == "__main__":
    update_ingredient_scores()
