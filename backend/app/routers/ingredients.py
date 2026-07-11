"""宠物宝 (PetCare) — 成分 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/ingredients", tags=["成分"])


@router.get("/dangerous", response_model=schemas.ApiResponse)
def get_dangerous_ingredients(
    limit: int = Query(8, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db),
):
    """获取高危成分（EWG评分 >= 7 的成分）"""
    ingredients = db.query(models.Ingredient).filter(
        models.Ingredient.ewg_score >= 7
    ).order_by(
        models.Ingredient.ewg_score.desc()
    ).limit(limit).all()
    
    return schemas.ApiResponse(data={
        "items": [schemas.Ingredient.model_validate(i).model_dump() for i in ingredients]
    })


@router.get("", response_model=schemas.ApiResponse)
def search_ingredients(
    q: Optional[str] = Query("", description="搜索关键词"),
    category: Optional[str] = Query(None, description="成分分类筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Ingredient)
    if q:
        query = query.filter(
            models.Ingredient.name.contains(q) | models.Ingredient.alias.contains(q)
        )
    if category:
        query = query.filter(models.Ingredient.category == category)

    total = query.count()
    ingredients = query.order_by(models.Ingredient.name).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return schemas.ApiResponse(data={
        "items": [schemas.Ingredient.model_validate(i).model_dump() for i in ingredients],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{ingredient_id}", response_model=schemas.ApiResponse)
def get_ingredient(
    ingredient_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="成分不存在")

    # 获取包含该成分的产品（分页）
    base_query = db.query(models.Product).join(
        models.product_ingredient
    ).filter(
        models.product_ingredient.c.ingredient_id == ingredient_id
    )
    total = base_query.count()
    products = base_query.offset((page - 1) * page_size).limit(page_size).all()

    return schemas.ApiResponse(data={
        "ingredient": schemas.Ingredient.model_validate(ingredient).model_dump(),
        "products": {
            "items": [
                schemas.ProductListItem(
                    id=p.id, name=p.name,
                    brand=p.brand.name if p.brand else None,
                    category=p.category.name if p.category else None,
                    type=p.type, safety_score=p.safety_score,
                    image_url=p.image_url,
                ).model_dump() for p in products
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    })
