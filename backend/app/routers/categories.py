"""宠物宝 (PetCare) — 品类 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/categories", tags=["品类"])


@router.get("", response_model=schemas.ApiResponse)
def list_categories(
    type: Optional[str] = Query(None, description="药品/食品/保健品"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Category).filter(models.Category.parent_id.is_(None))
    if type:
        query = query.filter(models.Category.type == type)

    categories = query.order_by(models.Category.name).all()
    return schemas.ApiResponse(data={
        "items": [schemas.Category.model_validate(c).model_dump() for c in categories],
    })
