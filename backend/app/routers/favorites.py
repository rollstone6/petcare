"""宠物宝 (PetCare) — 收藏 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app import models, auth, schemas

router = APIRouter(prefix="/favorites", tags=["收藏"])


class FavoriteReq(BaseModel):
    product_id: int


@router.get("")
def list_favorites(
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    favs = db.query(models.Favorite).filter(models.Favorite.user_id == user.id).order_by(models.Favorite.created_at.desc()).all()
    items = []
    for f in favs:
        p = f.product
        if p:
            items.append(schemas.ProductListItem(
                id=p.id, name=p.name,
                brand=p.brand.name if p.brand else None,
                category=p.category.name if p.category else None,
                type=p.type, safety_score=p.safety_score,
                image_url=p.image_url,
            ).model_dump())
    return {"code": 0, "data": {"items": items}}


@router.post("")
def add_favorite(
    req: FavoriteReq,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    exists = db.query(models.Favorite).filter(
        models.Favorite.user_id == user.id,
        models.Favorite.product_id == req.product_id,
    ).first()
    if exists:
        return {"code": 0, "message": "已收藏"}

    fav = models.Favorite(user_id=user.id, product_id=req.product_id)
    db.add(fav)
    try:
        db.commit()
        return {"code": 0, "data": {"id": fav.id}, "message": "收藏成功"}
    except IntegrityError:
        db.rollback()
        # 唯一约束冲突，说明已收藏
        return {"code": 0, "message": "已收藏"}


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    db.query(models.Favorite).filter(
        models.Favorite.user_id == user.id,
        models.Favorite.product_id == product_id,
    ).delete()
    db.commit()
    return {"code": 0, "message": "已取消收藏"}
