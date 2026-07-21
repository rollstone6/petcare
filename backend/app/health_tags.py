"""宠物宝 (PetCare) — 健康标签规则引擎

铲屎官在健康中心为宠物勾选健康标签，
当浏览产品时，系统根据标签匹配规则弹出警告。
"""

# ===== 常见健康标签定义 =====
HEALTH_TAGS = [
    {
        "id": "obesity_mild",
        "label": "轻度肥胖",
        "icon": "🐷",
        "category": "体重管理",
        "color": "orange",
        "description": "体重略超标准，需注意热量摄入",
    },
    {
        "id": "obesity_severe",
        "label": "重度肥胖",
        "icon": "🐷",
        "category": "体重管理",
        "color": "red",
        "description": "体重严重超标，需严格控制饮食",
    },
    {
        "id": "underweight",
        "label": "偏瘦",
        "icon": "🦴",
        "category": "体重管理",
        "color": "blue",
        "description": "体重偏低，需要高营养食物",
    },
    {
        "id": "stomach_sensitive",
        "label": "肠胃敏感",
        "icon": "🤢",
        "category": "消化系统",
        "color": "yellow",
        "description": "容易软便/拉稀，需温和配方",
    },
    {
        "id": "pancreatitis",
        "label": "胰腺炎史",
        "icon": "🏥",
        "category": "消化系统",
        "color": "red",
        "description": "曾患胰腺炎，需严格低脂饮食",
    },
    {
        "id": "kidney_disease",
        "label": "肾脏问题",
        "icon": "💧",
        "category": "泌尿系统",
        "color": "purple",
        "description": "肾功能异常，需低蛋白低磷",
    },
    {
        "id": "urinary_stones",
        "label": "泌尿结石",
        "icon": "💎",
        "category": "泌尿系统",
        "color": "purple",
        "description": "有结石病史，需控制矿物质",
    },
    {
        "id": "allergy_chicken",
        "label": "鸡肉过敏",
        "icon": "🍗",
        "category": "过敏",
        "color": "red",
        "description": "对鸡肉蛋白过敏",
    },
    {
        "id": "allergy_beef",
        "label": "牛肉过敏",
        "icon": "🥩",
        "category": "过敏",
        "color": "red",
        "description": "对牛肉蛋白过敏",
    },
    {
        "id": "allergy_fish",
        "label": "鱼肉过敏",
        "icon": "🐟",
        "category": "过敏",
        "color": "red",
        "description": "对鱼类蛋白过敏",
    },
    {
        "id": "allergy_grain",
        "label": "谷物过敏",
        "icon": "🌾",
        "category": "过敏",
        "color": "orange",
        "description": "对谷物（小麦/玉米等）过敏",
    },
    {
        "id": "diabetes",
        "label": "糖尿病",
        "icon": "💉",
        "category": "内分泌",
        "color": "red",
        "description": "血糖异常，需低糖饮食",
    },
    {
        "id": "heart_disease",
        "label": "心脏问题",
        "icon": "❤️",
        "category": "心血管",
        "color": "red",
        "description": "心脏功能异常，需低钠饮食",
    },
    {
        "id": "joint_issues",
        "label": "关节问题",
        "icon": "🦵",
        "category": "骨骼关节",
        "color": "orange",
        "description": "关节炎/髋关节发育不良等",
    },
    {
        "id": "skin_issues",
        "label": "皮肤敏感",
        "icon": "🧴",
        "category": "皮肤毛发",
        "color": "yellow",
        "description": "容易皮肤发红/脱毛/瘙痒",
    },
    {
        "id": "dental_issues",
        "label": "牙齿问题",
        "icon": "🦷",
        "category": "口腔",
        "color": "yellow",
        "description": "牙结石/牙龈炎，不适合硬零食",
    },
    {
        "id": "liver_disease",
        "label": "肝脏问题",
        "icon": "🏥",
        "category": "消化系统",
        "color": "red",
        "description": "肝功能异常，需低脂低蛋白",
    },
    {
        "id": "pregnancy",
        "label": "怀孕/哺乳",
        "icon": "🤰",
        "category": "特殊阶段",
        "color": "pink",
        "description": "孕期或哺乳期，需高营养",
    },
    {
        "id": "senior",
        "label": "老年期",
        "icon": "👴",
        "category": "特殊阶段",
        "color": "gray",
        "description": "7岁以上，需易消化配方",
    },
    {
        "id": "puppy",
        "label": "幼年期",
        "icon": "🍼",
        "category": "特殊阶段",
        "color": "green",
        "description": "1岁以下，需高钙高蛋白",
    },
]

# 按 category 分组，供前端展示
TAG_CATEGORIES = {}
for tag in HEALTH_TAGS:
    cat = tag["category"]
    if cat not in TAG_CATEGORIES:
        TAG_CATEGORIES[cat] = []
    TAG_CATEGORIES[cat].append(tag)


# ===== 产品风险匹配规则 =====
# 每条规则：
#   health_tags: 触发此规则的健康标签列表
#   product_match: 产品匹配条件（type / category关键词 / 成分关键词 / 描述关键词）
#   warning: 警告文案模板（{product_name} 会被替换）
#   severity: low / medium / high
WARNING_RULES = [
    # ── 肥胖 → 高脂/高热量产品 ──
    {
        "id": "high_fat_obesity",
        "health_tags": ["obesity_mild", "obesity_severe"],
        "product_match": {
            "type": ["食品", "保健品"],
            "category_keywords": ["冻干", "零食", "营养膏", "增肥", "增重", "发腮"],
            "ingredient_keywords": ["动物脂肪", "鸡油", "鸭油", "鱼油", "植物油", "油脂"],
            "description_keywords": ["高脂", "高热量", "增肥", "增重", "发腮", "高能"],
        },
        "warning": "⚠️ 健康中心提醒：您家宝贝目前处于【控制体重】阶段，本品可能脂肪/热量偏高，建议酌情减量或更换低脂粮。",
        "severity": "high",
    },
    {
        "id": "high_calorie_treats",
        "health_tags": ["obesity_mild", "obesity_severe"],
        "product_match": {
            "type": ["食品"],
            "category_keywords": ["零食", "肉干", "肉条", "冻干零食", "营养膏"],
        },
        "warning": "⚠️ 健康中心提醒：零食热量较高，肥胖宠物建议少量喂食或选择低卡替代品。",
        "severity": "medium",
    },
    # ── 胰腺炎 → 高脂产品 ──
    {
        "id": "pancreatitis_high_fat",
        "health_tags": ["pancreatitis"],
        "product_match": {
            "type": ["食品", "保健品"],
            "ingredient_keywords": ["动物脂肪", "鸡油", "鸭油", "黄油", "奶油", "植物油", "鱼油"],
            "category_keywords": ["冻干", "零食", "营养膏", "增肥", "发腮"],
            "description_keywords": ["高脂", "高热量", "脂肪含量"],
        },
        "warning": "🚨 严重警告：胰腺炎宠物必须严格低脂饮食！本品含高脂成分，可能诱发胰腺炎复发。",
        "severity": "high",
    },
    # ── 肠胃敏感 → 刺激性成分 ──
    {
        "id": "stomach_irritant",
        "health_tags": ["stomach_sensitive"],
        "product_match": {
            "ingredient_keywords": ["乳糖", "辣椒", "大蒜", "洋葱", "葡萄", "木糖醇", "酒精"],
            "description_keywords": ["辛辣", "刺激"],
        },
        "warning": "⚠️ 健康中心提醒：您家宝贝肠胃敏感，本品含可能刺激肠胃的成分，请谨慎使用。",
        "severity": "high",
    },
    {
        "id": "stomach_raw_food",
        "health_tags": ["stomach_sensitive"],
        "product_match": {
            "type": ["食品"],
            "category_keywords": ["生骨肉", "生肉", "BARF"],
            "description_keywords": ["生骨肉", "生肉", "BARF", "生食"],
        },
        "warning": "⚠️ 健康中心提醒：肠胃敏感宠物切换生骨肉需循序渐进，建议先咨询兽医。",
        "severity": "medium",
    },
    # ── 肾脏问题 → 高蛋白/高磷 ──
    {
        "id": "kidney_high_protein",
        "health_tags": ["kidney_disease"],
        "product_match": {
            "type": ["食品"],
            "category_keywords": ["高蛋白", "增肌", "冻干"],
            "description_keywords": ["高蛋白", "高磷", "增肌"],
            "ingredient_keywords": ["磷酸", "磷酸钙", "磷酸氢钙"],
        },
        "warning": "🚨 严重警告：肾脏问题宠物需低蛋白低磷饮食！本品蛋白质/磷含量可能偏高，请咨询兽医后再使用。",
        "severity": "high",
    },
    # ── 泌尿结石 → 高矿物质 ──
    {
        "id": "urinary_minerals",
        "health_tags": ["urinary_stones"],
        "product_match": {
            "ingredient_keywords": ["碳酸钙", "磷酸钙", "磷酸氢钙", "氧化镁", "硫酸镁"],
            "description_keywords": ["补钙", "高钙", "高矿物质"],
            "category_keywords": ["钙片", "补钙", "矿物质"],
        },
        "warning": "⚠️ 健康中心提醒：泌尿结石宠物需控制矿物质摄入，本品含钙/镁成分，请咨询兽医。",
        "severity": "medium",
    },
    # ── 鸡肉过敏 ──
    {
        "id": "allergy_chicken_match",
        "health_tags": ["allergy_chicken"],
        "product_match": {
            "ingredient_keywords": ["鸡肉", "鸡肝", "鸡心", "鸡粉", "鸡油", "鸡肉粉", "鸡胸肉", "鸡蛋"],
            "description_keywords": ["鸡肉", "鸡肝"],
        },
        "warning": "🚨 过敏警告：本品含鸡肉/鸡蛋相关成分，您家宝贝对鸡肉过敏，请避免使用！",
        "severity": "high",
    },
    # ── 牛肉过敏 ──
    {
        "id": "allergy_beef_match",
        "health_tags": ["allergy_beef"],
        "product_match": {
            "ingredient_keywords": ["牛肉", "牛肝", "牛心", "牛骨粉", "牛油", "牛肉粉"],
            "description_keywords": ["牛肉", "牛肝"],
        },
        "warning": "🚨 过敏警告：本品含牛肉相关成分，您家宝贝对牛肉过敏，请避免使用！",
        "severity": "high",
    },
    # ── 鱼肉过敏 ──
    {
        "id": "allergy_fish_match",
        "health_tags": ["allergy_fish"],
        "product_match": {
            "ingredient_keywords": ["鱼肉", "鱼粉", "鱼油", "三文鱼", "金枪鱼", "鳕鱼", "鲑鱼", "沙丁鱼", "虾", "蟹"],
            "description_keywords": ["鱼肉", "深海鱼", "三文鱼"],
        },
        "warning": "🚨 过敏警告：本品含鱼类/海鲜成分，您家宝贝对鱼肉过敏，请避免使用！",
        "severity": "high",
    },
    # ── 谷物过敏 ──
    {
        "id": "allergy_grain_match",
        "health_tags": ["allergy_grain"],
        "product_match": {
            "ingredient_keywords": ["小麦", "玉米", "大麦", "燕麦", "米粉", "糙米", "白米", "面粉"],
            "description_keywords": ["含谷", "小麦", "玉米"],
        },
        "warning": "⚠️ 健康中心提醒：本品含谷物成分，您家宝贝对谷物过敏，建议选择无谷配方。",
        "severity": "high",
    },
    # ── 糖尿病 → 高糖 ──
    {
        "id": "diabetes_sugar",
        "health_tags": ["diabetes"],
        "product_match": {
            "ingredient_keywords": ["蔗糖", "果糖", "葡萄糖", "糖浆", "蜂蜜", "糖蜜", "麦芽糖"],
            "description_keywords": ["高糖", "甜味", "含糖"],
            "category_keywords": ["零食", "营养膏"],
        },
        "warning": "🚨 严重警告：糖尿病宠物需严格控糖！本品含糖分较高，请避免使用。",
        "severity": "high",
    },
    # ── 心脏问题 → 高钠 ──
    {
        "id": "heart_sodium",
        "health_tags": ["heart_disease"],
        "product_match": {
            "ingredient_keywords": ["食盐", "氯化钠", "亚硝酸钠"],
            "description_keywords": ["高钠", "高盐", "腌制"],
            "category_keywords": ["零食", "肉干"],
        },
        "warning": "⚠️ 健康中心提醒：心脏问题宠物需低钠饮食，本品钠含量可能偏高。",
        "severity": "medium",
    },
    # ── 关节问题 → 推荐含关节保护成分 ──
    {
        "id": "joint_recommend",
        "health_tags": ["joint_issues"],
        "product_match": {
            "type": ["保健品"],
            "ingredient_keywords": ["氨基葡萄糖", "软骨素", "葡萄糖胺", "MSM", "透明质酸", "胶原蛋白"],
        },
        "warning": "💡 健康中心提示：本品含关节保护成分（氨基葡萄糖/软骨素），适合有关节问题的宝贝。",
        "severity": "info",
    },
    # ── 关节问题 → 避免高钙（过量补钙反而伤关节） ──
    {
        "id": "joint_avoid_excess_calcium",
        "health_tags": ["joint_issues"],
        "product_match": {
            "type": ["保健品"],
            "category_keywords": ["钙片", "补钙", "高钙"],
            "description_keywords": ["高钙", "大量补钙"],
        },
        "warning": "⚠️ 健康中心提醒：关节问题宠物过量补钙可能加重负担，建议优先补充氨基葡萄糖/软骨素。",
        "severity": "medium",
    },
    # ── 肝脏问题 → 高脂 ──
    {
        "id": "liver_high_fat",
        "health_tags": ["liver_disease"],
        "product_match": {
            "type": ["食品", "保健品"],
            "ingredient_keywords": ["动物脂肪", "鸡油", "鸭油", "黄油", "奶油"],
            "description_keywords": ["高脂", "高热量"],
        },
        "warning": "⚠️ 健康中心提醒：肝脏问题宠物需低脂饮食，本品脂肪含量可能偏高。",
        "severity": "high",
    },
    # ── 牙齿问题 → 硬零食 ──
    {
        "id": "dental_hard",
        "health_tags": ["dental_issues"],
        "product_match": {
            "type": ["食品"],
            "category_keywords": ["磨牙棒", "洁齿骨", "咬胶", "硬零食"],
            "description_keywords": ["磨牙", "洁齿", "硬", "耐咬"],
        },
        "warning": "⚠️ 健康中心提醒：您家宝贝有牙齿问题，硬质零食可能加重牙龈损伤，建议泡软后喂食。",
        "severity": "medium",
    },
]


def check_product_warnings(product, pet_health_tags):
    """
    检查产品是否触发宠物的健康标签警告

    Args:
        product: dict, 产品信息（含 ingredients, category, description）
        pet_health_tags: list[str], 宠物的健康标签 ID 列表

    Returns:
        list[dict]: 触发的警告列表
    """
    if not pet_health_tags:
        return []

    warnings = []

    # 构建产品文本（用于关键词匹配）
    product_name = product.get("name", "")
    product_type = product.get("type", "")
    category_name = ""
    if product.get("category"):
        category_name = product["category"].get("name", "") if isinstance(product["category"], dict) else str(product["category"])
    description = product.get("description", "")

    ingredient_names = []
    if product.get("ingredients"):
        for ing in product["ingredients"]:
            if isinstance(ing, dict):
                ingredient_names.append(ing.get("name", ""))
            else:
                ingredient_names.append(str(ing))

    # 合并所有文本用于搜索
    all_text = " ".join([product_name, category_name, description])
    all_ingredients = " ".join(ingredient_names)

    for rule in WARNING_RULES:
        # 检查宠物的健康标签是否匹配规则
        matched_tags = [t for t in rule["health_tags"] if t in pet_health_tags]
        if not matched_tags:
            continue

        # 检查产品是否匹配规则条件
        match_conf = rule["product_match"]
        matched = False

        # 类型匹配
        if "type" in match_conf:
            if product_type in match_conf["type"]:
                # 如果只有 type 条件，直接匹配
                other_conditions = [k for k in match_conf if k != "type"]
                if not other_conditions:
                    matched = True

        # 品类关键词匹配
        if not matched and "category_keywords" in match_conf:
            for kw in match_conf["category_keywords"]:
                if kw in category_name or kw in product_name:
                    matched = True
                    break

        # 成分关键词匹配
        if not matched and "ingredient_keywords" in match_conf:
            for kw in match_conf["ingredient_keywords"]:
                if kw in all_ingredients:
                    matched = True
                    break

        # 描述关键词匹配
        if not matched and "description_keywords" in match_conf:
            for kw in match_conf["description_keywords"]:
                if kw in description or kw in product_name:
                    matched = True
                    break

        if matched:
            tag_labels = []
            for tid in matched_tags:
                for tag in HEALTH_TAGS:
                    if tag["id"] == tid:
                        tag_labels.append(tag["label"])

            warnings.append({
                "rule_id": rule["id"],
                "severity": rule["severity"],
                "message": rule["warning"],
                "matched_tags": matched_tags,
                "matched_tag_labels": tag_labels,
                "category": rule.get("category", ""),
            })

    # 按严重程度排序：high > medium > low > info
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    warnings.sort(key=lambda w: severity_order.get(w["severity"], 9))

    return warnings


def get_health_tags_list():
    """返回所有健康标签定义（按分类分组）"""
    return {
        "tags": HEALTH_TAGS,
        "categories": {cat: tags for cat, tags in TAG_CATEGORIES.items()},
    }
