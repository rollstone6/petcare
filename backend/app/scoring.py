"""宠物宝 (PetCare) — 安全评分算法 v4 (0-100分制)

评分体系（0-100分，高分=安全）：
- 90-100: 优秀（绿色）- 天然纯净配方
- 70-89: 良好（浅绿）- 基本安全
- 50-69: 中等（黄色）- 有一定风险
- 30-49: 较差（橙色）- 风险较高
- 0-29: 危险（红色）- 高风险成分多

评分规则：
- 基础分 100
- 成分数量扣分：每个成分 -2（成分越多=加工越深）
- 高风险成分（EWG 7-10）：每个 -20
- 中风险成分（EWG 4-6）：每个 -8
- 产品类型修正：食品 +5，保健品 +2，药品 -8
"""

from sqlalchemy.orm import Session
from app import models


def calculate_product_score(db: Session, product_id: int) -> float:
    """
    计算产品的综合安全评分（0-100分制，高分=安全）
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return 50.0
    
    # 获取产品成分
    pi_rows = db.query(models.product_ingredient).filter(
        models.product_ingredient.c.product_id == product_id
    ).order_by(models.product_ingredient.c.sort_order).all()
    
    if not pi_rows:
        return 50.0  # 无成分数据，默认中等
    
    # 基础分
    score = 100.0
    
    # 统计各风险等级成分数量
    high_risk = 0  # EWG 7-10
    medium_risk = 0  # EWG 4-6
    
    for pi in pi_rows:
        ing = db.query(models.Ingredient).filter(models.Ingredient.id == pi.ingredient_id).first()
        if not ing:
            continue
        
        # 优先使用 ewg_score，否则用 safety_level 映射
        ewg = ing.ewg_score if ing.ewg_score else (6 - ing.safety_level) * 2
        
        if ewg >= 7:
            high_risk += 1
        elif ewg >= 4:
            medium_risk += 1
    
    # 成分数量扣分（核心区分度来源）
    score -= len(pi_rows) * 2
    
    # 高风险成分重罚
    score -= high_risk * 20
    score -= medium_risk * 8
    
    # 产品类型修正
    type_modifier = {
        '食品': 5,
        '保健品': 2,
        '药品': -8
    }.get(product.type, 0)
    score += type_modifier
    
    # 限制在0-100范围内
    return round(max(0.0, min(100.0, score)), 1)


def recalculate_all_scores(db: Session) -> int:
    """重新计算所有产品的安全评分，返回更新数量"""
    products = db.query(models.Product).all()
    count = 0
    for p in products:
        new_score = calculate_product_score(db, p.id)
        old_score = p.safety_score if p.safety_score is not None else 5.0
        if abs(old_score - new_score) > 0.01:
            p.safety_score = new_score
            count += 1
    db.commit()
    return count
