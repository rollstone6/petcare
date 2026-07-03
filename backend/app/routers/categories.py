"""宠物宝 (PetCare) — 品类 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/categories", tags=["品类"])


@router.get("", response_model=schemas.ApiResponse)
def list_categories(
    type: Optional[str] = Query(None, description="药品/食品/保健品"),
    db: Session = Depends(get_db),
):
    query = db.query(
        models.Category,
        func.count(models.Product.id).label("product_count")
    ).outerjoin(
        models.Product, models.Product.category_id == models.Category.id
    ).filter(models.Category.parent_id.is_(None))
    if type:
        query = query.filter(models.Category.type == type)

    rows = query.group_by(models.Category.id).order_by(
        func.count(models.Product.id).desc()
    ).all()

    items = []
    for cat, count in rows:
        d = schemas.Category.model_validate(cat).model_dump()
        d["product_count"] = count
        items.append(d)

    return schemas.ApiResponse(data={
        "items": items,
    })
