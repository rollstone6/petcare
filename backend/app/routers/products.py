"""宠物宝 (PetCare) — 产品 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload
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
        query = query.filter(models.Product.name.contains(q))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if brand_id:
        query = query.filter(models.Product.brand_id == brand_id)
    if type:
        query = query.filter(models.Product.type == type)

    total = query.count()
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
        ))

    return schemas.ApiResponse(data={
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
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
            ingredients.append(schemas.ProductIngredient(
                id=ing.id,
                name=ing.name,
                sort_order=pi.sort_order or 0,
                function=ing.function,
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
