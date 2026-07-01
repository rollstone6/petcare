"""宠物宝 (PetCare) — 品牌 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/brands", tags=["品牌"])


@router.get("/hot", response_model=schemas.ApiResponse)
def get_hot_brands(
    limit: int = Query(8, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db),
):
    """获取热门品牌（按产品数量排序）"""
    from sqlalchemy import func
    
    # 统计每个品牌的产品数量
    brand_counts = db.query(
        models.Brand,
        func.count(models.Product.id).label('product_count')
    ).outerjoin(
        models.Product, models.Product.brand_id == models.Brand.id
    ).group_by(
        models.Brand.id
    ).order_by(
        func.count(models.Product.id).desc()
    ).limit(limit).all()
    
    return schemas.ApiResponse(data={
        "items": [
            {
                **schemas.Brand.model_validate(brand).model_dump(),
                "product_count": count
            }
            for brand, count in brand_counts
        ]
    })


@router.get("", response_model=schemas.ApiResponse)
def list_brands(
    q: Optional[str] = Query("", description="搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(models.Brand)
    if q:
        query = query.filter(models.Brand.name.contains(q))

    total = query.count()
    brands = query.order_by(models.Brand.name).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return schemas.ApiResponse(data={
        "items": [schemas.Brand.model_validate(b).model_dump() for b in brands],
        "total": total,
        "page": page,
        "page_size": page_size,
    })
