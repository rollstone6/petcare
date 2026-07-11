"""宠物宝 (PetCare) — 安全评分算法 v3 (EWG标准)

评分体系（1-10分，基于EWG Skin Deep数据库）：
- 1-2: 低危害（绿色）- 天然成分、已知安全
- 3-6: 中等危害（黄色）- 有一定关注
- 7-10: 高危害（红色）- 致癌、致畸、内分泌干扰

规则：
- 基础肉类原料（天然食材）: 1分
- 化学添加剂: 按EWG数据库评分
"""

from sqlalchemy.orm import Session
from app import models


def calculate_product_score(db: Session, product_id: int) -> float:
    """
    计算产品的综合安全评分（1-10分制，基于EWG标准）
    
    算法：
    1. 成分加权平均（考虑含量排序）
    2. 高风险成分惩罚（含7-10分成分额外扣分）
    3. 产品类型修正（食品/药品/保健品不同基准）
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return 5.0
    
    # 获取产品成分（按排序）
    pi_rows = db.query(models.product_ingredient).filter(
        models.product_ingredient.c.product_id == product_id
    ).order_by(models.product_ingredient.c.sort_order).all()
    
    if not pi_rows:
        return 5.0  # 无成分数据，默认中等
    
    # 1. 成分加权评分（前3个成分权重更高）
    weights = [3.0, 2.5, 2.0, 1.5, 1.2, 1.0, 1.0, 1.0]  # 递减权重
    total_weight = 0
    weighted_score = 0
    
    for i, pi in enumerate(pi_rows):
        ing = db.query(models.Ingredient).filter(models.Ingredient.id == pi.ingredient_id).first()
        if not ing:
            continue
        
        # 优先使用 ewg_score，否则用 safety_level 映射
        ewg = ing.ewg_score if ing.ewg_score else ing.safety_level * 2  # 旧1-5分映射到1-10
        
        weight = weights[min(i, len(weights)-1)]
        weighted_score += ewg * weight
        total_weight += weight
    
    base_score = weighted_score / total_weight if total_weight > 0 else 5.0
    
    # 2. 高风险成分惩罚
    high_risk_count = 0
    for pi in pi_rows:
        ing = db.query(models.Ingredient).filter(models.Ingredient.id == pi.ingredient_id).first()
        if ing and ing.ewg_score and ing.ewg_score >= 7:
            high_risk_count += 1
    
    penalty = high_risk_count * 0.8  # 每个高风险成分扣0.8分
    
    # 3. 产品类型修正
    type_modifier = {
        '食品': 0.5,    # 食品应该更安全
        '保健品': 0,     # 保健品中性
        '药品': -0.3     # 药品允许更高风险
    }.get(product.type, 0)
    
    # 最终评分
    final_score = base_score - penalty + type_modifier
    
    # 限制在1-10范围内
    return round(max(1.0, min(10.0, final_score)), 1)


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
