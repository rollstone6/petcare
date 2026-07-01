"""宠物宝 (PetCare) — 安全评分算法 v2

优化点：
1. 成分排序权重（排在前面的成分含量更高，权重更大）
2. 成分相互作用（某些成分组合可能有风险或增效）
3. 高风险成分惩罚（有1-2级成分时额外扣分）
4. 产品类型更细致的系数
5. 适用物种适配
"""

from sqlalchemy.orm import Session
from app import models


# 成分相互作用规则（简化版）
# key: (成分A类别, 成分B类别), value: (交互类型, 影响值)
# 交互类型: 'risk'(增加风险), 'benefit'(增效)
INGREDIENT_INTERACTIONS = {
    ('抗菌', '益生菌'): ('risk', -0.3),      # 抗菌剂可能杀死益生菌
    ('驱虫', '疫苗'): ('risk', -0.2),         # 驱虫和疫苗同时使用可能增加负担
    ('营养', '益生菌'): ('benefit', 0.2),     # 营养+益生菌协同增效
    ('抗氧化', '维生素'): ('benefit', 0.1),   # 抗氧化+维生素协同
}

# 产品类型系数（更细致）
TYPE_FACTORS = {
    '疫苗': 0.90,      # 疫苗风险略高
    '驱虫药': 0.92,    # 驱虫药有一定毒性
    '抗生素': 0.88,    # 抗生素风险较高
    '消炎药': 0.93,
    '营养补充': 1.05,  # 营养品较安全
    '益生菌': 1.08,    # 益生菌很安全
    '食品': 1.0,
    '保健品': 1.03,
    '药品': 0.95,      # 默认药品
}

# 物种敏感成分（简化版）
SPECIES_SENSITIVE = {
    '猫': ['除虫菊酯', '伊维菌素'],  # 猫对某些成分更敏感
    '狗': [],
}


def calculate_product_score(db: Session, product_id: int) -> float:
    """计算产品的综合安全评分 (0-5) v2"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return 0.0

    # 获取产品成分（按排序）
    pi_rows = db.query(models.product_ingredient).filter(
        models.product_ingredient.c.product_id == product_id
    ).order_by(models.product_ingredient.c.sort_order).all()

    if not pi_rows:
        return 3.0  # 无成分数据，默认中等

    # ===== 1. 成分排序加权 =====
    # 排在前面的成分权重更高（模拟含量从高到低）
    total_weight = 0
    weighted_score = 0
    ingredient_categories = []  # 记录成分类别用于交互检测
    min_safety = 5  # 记录最低安全等级

    for idx, pi in enumerate(pi_rows):
        ing = db.query(models.Ingredient).filter(models.Ingredient.id == pi.ingredient_id).first()
        if not ing:
            continue

        # 排序权重：第1个成分权重3.0，第2个2.5，第3个2.0，之后1.5
        position_weight = max(1.5, 3.0 - idx * 0.5)
        
        # 主要/次要成分权重
        active_weight = 1.5 if pi.is_active else 1.0
        
        # 最终权重
        weight = position_weight * active_weight
        weighted_score += ing.safety_level * weight
        total_weight += weight
        
        ingredient_categories.append(ing.category)
        min_safety = min(min_safety, ing.safety_level)

    ingredient_score = weighted_score / total_weight if total_weight > 0 else 3.0

    # ===== 2. 高风险成分惩罚 =====
    # 如果有1-2级成分，额外扣分
    risk_penalty = 0
    if min_safety <= 2:
        risk_penalty = -0.3  # 有高风险成分，扣0.3分
    elif min_safety == 3:
        risk_penalty = -0.1  # 有中等风险成分，扣0.1分

    # ===== 3. 成分相互作用 =====
    interaction_bonus = 0
    for i, cat_a in enumerate(ingredient_categories):
        for cat_b in ingredient_categories[i+1:]:
            key = tuple(sorted([cat_a, cat_b]))
            if key in INGREDIENT_INTERACTIONS:
                _, effect = INGREDIENT_INTERACTIONS[key]
                interaction_bonus += effect

    # ===== 4. 产品类型系数 =====
    type_factor = TYPE_FACTORS.get(product.type, TYPE_FACTORS.get('药品', 0.95))

    # ===== 5. 品牌系数（保留原逻辑）=====
    brand_factor = 1.0
    if product.brand:
        if product.brand.country in ("美国", "德国", "法国", "加拿大", "英国"):
            brand_factor = 1.03
        elif product.brand.country == "中国":
            brand_factor = 1.0

    # ===== 6. 适用物种适配 =====
    species_penalty = 0
    if product.suitable_species and '猫' in product.suitable_species:
        # 检查是否有猫敏感成分
        for pi in pi_rows:
            ing = db.query(models.Ingredient).filter(models.Ingredient.id == pi.ingredient_id).first()
            if ing and ing.name in SPECIES_SENSITIVE.get('猫', []):
                species_penalty = -0.2
                break

    # ===== 最终评分 =====
    score = ingredient_score + risk_penalty + interaction_bonus + species_penalty
    score = score * type_factor * brand_factor

    # 限制在 1-5 范围
    return round(max(1.0, min(5.0, score)), 1)


def recalculate_all_scores(db: Session) -> int:
    """重新计算所有产品的安全评分，返回更新数量"""
    products = db.query(models.Product).all()
    count = 0
    for p in products:
        new_score = calculate_product_score(db, p.id)
        if abs(p.safety_score - new_score) > 0.01:
            p.safety_score = new_score
            count += 1
    db.commit()
    return count
