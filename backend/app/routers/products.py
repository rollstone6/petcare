"""宠物宝 (PetCare) — 产品 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.scoring import calculate_product_score
from app import auth

router = APIRouter(prefix="/products", tags=["产品"])


@router.get("", response_model=schemas.ApiResponse)
@cache(expire=300)  # 缓存5分钟
def search_products(
    q: Optional[str] = Query("", description="搜索关键词"),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    type: Optional[str] = None,
    sort: Optional[str] = Query("score", description="排序方式: score/name/newest"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Product).options(
        joinedload(models.Product.brand),
        joinedload(models.Product.category)
    )

    if q:
        # 模糊搜索：同时匹配产品名、品牌名、品类名、成分名
        query = query.outerjoin(models.Brand).outerjoin(models.Category).outerjoin(
            models.product_ingredient
        ).outerjoin(models.Ingredient).filter(
            or_(
                models.Product.name.contains(q),
                models.Brand.name.contains(q),
                models.Category.name.contains(q),
                models.Ingredient.name.contains(q),
            )
        ).group_by(models.Product.id)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if brand_id:
        query = query.filter(models.Product.brand_id == brand_id)
    if type:
        query = query.filter(models.Product.type == type)

    total = query.count()
    
    # 分面搜索统计：用子查询避免 group_by 堆叠问题
    stats_sub = db.query(models.Product.id.label("pid"), models.Product.category_id, models.Product.brand_id)
    if q:
        stats_sub = stats_sub.outerjoin(models.Brand).outerjoin(models.Category).outerjoin(
            models.product_ingredient
        ).outerjoin(models.Ingredient).filter(
            or_(
                models.Product.name.contains(q),
                models.Brand.name.contains(q),
                models.Category.name.contains(q),
                models.Ingredient.name.contains(q),
            )
        ).distinct()
    if type:
        stats_sub = stats_sub.filter(models.Product.type == type)
    sub = stats_sub.subquery()
    # 品类统计（排除 category_id 筛选，保留 brand_id）
    cat_q = db.query(sub.c.category_id, func.count(sub.c.pid.distinct())).group_by(sub.c.category_id)
    if brand_id:
        cat_q = cat_q.filter(sub.c.brand_id == brand_id)
    category_stats = dict(cat_q.all())
    # 品牌统计（排除 brand_id 筛选，保留 category_id）
    brand_q = db.query(sub.c.brand_id, func.count(sub.c.pid.distinct())).group_by(sub.c.brand_id)
    if category_id:
        brand_q = brand_q.filter(sub.c.category_id == category_id)
    brand_stats = dict(brand_q.all())
    
    if sort == "name":
        query = query.order_by(models.Product.name)
    elif sort == "newest":
        query = query.order_by(models.Product.created_at.desc())
    else:
        query = query.order_by(models.Product.safety_score.desc())
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for p in products:
        items.append(schemas.ProductListItem(
            id=p.id,
            name=p.name,
            brand=p.brand.name if p.brand else None,
            category=p.category.name if p.category else None,
            type=p.type,
            safety_score=p.safety_score,
            image_url=p.image_url,
            suitable_species=p.suitable_species,
            target_size=p.target_size,
            target_age=p.target_age,
        ))

    return schemas.ApiResponse(data={
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "category_stats": category_stats,
        "brand_stats": brand_stats,
    })


@router.get("/{product_id}", response_model=schemas.ApiResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).options(
        joinedload(models.Product.brand),
        joinedload(models.Product.category)
    ).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 一次性查询产品-成分关联
    pi_records = db.query(models.product_ingredient).filter(
        models.product_ingredient.c.product_id == product_id
    ).all()
    
    ingredient_ids = [pi.ingredient_id for pi in pi_records]
    ingredients_data = {}
    if ingredient_ids:
        ingredients = db.query(models.Ingredient).filter(models.Ingredient.id.in_(ingredient_ids)).all()
        ingredients_data = {ing.id: ing for ing in ingredients}
    
    ingredients = []
    for pi in pi_records:
        ing = ingredients_data.get(pi.ingredient_id)
        if ing:
            import json
            risk_tags = []
            if ing.risk_tags:
                try:
                    risk_tags = json.loads(ing.risk_tags)
                except:
                    risk_tags = []
            ingredients.append(schemas.ProductIngredient(
                id=ing.id,
                name=ing.name,
                sort_order=pi.sort_order or 0,
                function=ing.function,
                risk_tags=risk_tags,
            ))

    return schemas.ApiResponse(data=schemas.ProductDetail(
        id=product.id,
        name=product.name,
        brand=schemas.Brand.model_validate(product.brand) if product.brand else None,
        category=schemas.Category.model_validate(product.category) if product.category else None,
        type=product.type,
        description=product.description,
        approval_number=product.approval_number,
        safety_score=product.safety_score,
        image_url=product.image_url,
        usage_guide=product.usage_guide,
        suitable_species=product.suitable_species,
        ingredients=ingredients,
        created_at=product.created_at,
    ).model_dump())


@router.post("/recalculate-scores")
def recalculate_scores(
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """重新计算所有产品安全评分（需登录）"""
    from app.scoring import recalculate_all_scores
    count = recalculate_all_scores(db)
    return {"code": 0, "data": {"updated": count}, "message": f"已更新 {count} 个产品的评分"}


@router.get("/{product_id}/breed-compatibility", response_model=schemas.ApiResponse)
def get_breed_compatibility(
    product_id: int,
    pet_id: Optional[int] = Query(None, description="宠物档案ID"),
    db: Session = Depends(get_db),
):
    """计算产品与用户宠物的品种契合度"""
    import json
    
    # 1. 获取产品
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 2. 获取宠物档案
    pet = None
    if pet_id:
        pet = db.query(models.PetProfile).filter(models.PetProfile.id == pet_id).first()
    
    if not pet or not pet.breed_id:
        # 没有绑定宠物或没有品种，返回默认安全评分
        return schemas.ApiResponse(data={
            "compatibility_score": None,
            "risk_ingredients": [],
            "warnings": [],
            "message": "请先在「宠物档案」中绑定宠物品种，获取个性化契合度分析"
        })
    
    # 3. 获取品种健康标签
    breed = db.query(models.PetBreed).filter(models.PetBreed.id == pet.breed_id).first()
    if not breed:
        return schemas.ApiResponse(data={
            "compatibility_score": None,
            "risk_ingredients": [],
            "warnings": [],
            "message": "品种信息不存在"
        })
    
    health_tags = []
    if breed.health_tags:
        try:
            health_tags = json.loads(breed.health_tags)
        except:
            health_tags = []
    
    if not health_tags:
        return schemas.ApiResponse(data={
            "compatibility_score": None,
            "risk_ingredients": [],
            "warnings": [],
            "message": f"{breed.name}暂无健康风险数据"
        })
    
    # 4. 遍历产品成分，匹配风险
    pi_records = db.query(models.product_ingredient).filter(
        models.product_ingredient.c.product_id == product_id
    ).all()
    
    ingredient_ids = [pi.ingredient_id for pi in pi_records]
    ingredients_data = {}
    if ingredient_ids:
        ingredients = db.query(models.Ingredient).filter(models.Ingredient.id.in_(ingredient_ids)).all()
        ingredients_data = {ing.id: ing for ing in ingredients}
    
    risk_ingredients = []
    matched_health_tags = set()
    
    for pi in pi_records:
        ing = ingredients_data.get(pi.ingredient_id)
        if not ing or not ing.risk_tags:
            continue
        
        try:
            ing_risk_tags = json.loads(ing.risk_tags)
        except:
            continue
        
        # 找匹配的风险标签
        overlapping = set(ing_risk_tags) & set(health_tags)
        if overlapping:
            matched_health_tags.update(overlapping)
            risk_ingredients.append({
                "id": ing.id,
                "name": ing.name,
                "function": ing.function or "",
                "risk_tags": list(overlapping),
                "all_risk_tags": ing_risk_tags,
            })
    
    # 5. 计算契合度分数
    # 基础分 100，每个风险成分扣 10-15 分
    if not risk_ingredients:
        compatibility_score = 100
    else:
        # 风险越多扣分越多，但保底 20 分
        penalty = 0
        for ri in risk_ingredients:
            penalty += min(15, 8 + len(ri["risk_tags"]) * 3)
        compatibility_score = max(20, 100 - penalty)
    
    # 6. 生成警告文案
    warnings = []
    for ri in risk_ingredients:
        tags_str = "、".join(ri["risk_tags"])
        warnings.append(
            f"⚠️ {breed.name}易患{tags_str}，该产品含有「{ri['name']}」可能加重风险"
        )
    
    return schemas.ApiResponse(data={
        "compatibility_score": compatibility_score,
        "pet_name": pet.pet_name,
        "breed_name": breed.name,
        "breed_health_tags": health_tags,
        "risk_ingredients": risk_ingredients,
        "warnings": warnings,
        "matched_health_tags": list(matched_health_tags),
    })
