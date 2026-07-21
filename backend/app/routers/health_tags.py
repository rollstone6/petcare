"""宠物宝 (PetCare) — 健康标签 API"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app import models, auth
from app.health_tags import get_health_tags_list, check_product_warnings
import json

router = APIRouter(prefix="/health-tags", tags=["健康标签"])


class HealthTagsUpdate(BaseModel):
    tags: List[str] = []


@router.get("")
def list_tags():
    """获取所有可用健康标签（按分类分组）"""
    return {"code": 0, "data": get_health_tags_list()}


@router.put("/pets/{pet_id}")
def update_pet_health_tags(
    pet_id: int,
    req: HealthTagsUpdate,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """更新宠物的健康标签"""
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.user_id == user.id,
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    pet.health_tags = json.dumps(req.tags)
    db.commit()
    return {"code": 0, "data": {"health_tags": req.tags}, "message": "更新成功"}


@router.post("/check/{product_id}")
def check_warnings(
    product_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """检查产品是否触发当前用户宠物的健康警告"""
    # 获取产品（含成分、品牌、品类）
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return {"code": 0, "data": {"warnings": []}}

    # 构建产品 dict
    product_dict = {
        "id": product.id,
        "name": product.name,
        "type": product.type,
        "description": product.description or "",
        "category": {"name": product.category.name} if product.category else None,
        "brand": {"name": product.brand.name} if product.brand else None,
        "ingredients": [{"name": ing.name} for ing in product.ingredients] if product.ingredients else [],
    }

    # 获取用户所有宠物的健康标签
    pets = db.query(models.PetProfile).filter(
        models.PetProfile.user_id == user.id
    ).all()

    all_warnings = []
    for pet in pets:
        try:
            pet_tags = json.loads(pet.health_tags) if pet.health_tags else []
        except:
            pet_tags = []

        if pet_tags:
            warnings = check_product_warnings(product_dict, pet_tags)
            for w in warnings:
                w["pet_name"] = pet.pet_name
                w["pet_id"] = pet.id
                w["pet_species"] = pet.breed.species if pet.breed else "狗"
            all_warnings.extend(warnings)

    # 去重（同一规则对同一宠物只出现一次）
    seen = set()
    unique_warnings = []
    for w in all_warnings:
        key = f"{w['rule_id']}_{w['pet_id']}"
        if key not in seen:
            seen.add(key)
            unique_warnings.append(w)

    return {"code": 0, "data": {"warnings": unique_warnings}}
