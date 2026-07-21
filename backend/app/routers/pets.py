"""宠物宝 (PetCare) — 宠物档案 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.database import get_db
from app import models, auth
from app.reminder_rules import generate_default_reminders, get_age_category_display

router = APIRouter(prefix="/pets", tags=["宠物档案"])


class PetCreate(BaseModel):
    pet_name: str = Field(..., min_length=1, max_length=50)
    breed_id: Optional[int] = None
    age: Optional[str] = ""
    gender: Optional[str] = ""
    weight: Optional[float] = None
    avatar_url: Optional[str] = ""
    birthday: Optional[date] = None
    body_condition: Optional[str] = ""
    auto_reminders: Optional[bool] = True  # 是否自动生成默认提醒
    health_tags: Optional[list] = None  # 健康标签列表


class PetUpdate(BaseModel):
    pet_name: Optional[str] = Field(None, min_length=1, max_length=50)
    breed_id: Optional[int] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    avatar_url: Optional[str] = None
    birthday: Optional[date] = None
    body_condition: Optional[str] = None
    health_tags: Optional[list] = None


@router.get("")
def list_pets(
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有宠物"""
    pets = db.query(models.PetProfile).filter(
        models.PetProfile.user_id == user.id
    ).order_by(models.PetProfile.created_at.desc()).all()

    items = []
    for p in pets:
        # 解析 health_tags JSON
        import json
        health_tags_list = []
        try:
            if p.health_tags:
                health_tags_list = json.loads(p.health_tags)
        except:
            health_tags_list = []
        
        item = {
            "id": p.id,
            "pet_name": p.pet_name,
            "age": p.age,
            "gender": p.gender,
            "weight": p.weight,
            "avatar_url": p.avatar_url,
            "birthday": str(p.birthday) if p.birthday else None,
            "body_condition": p.body_condition or "",
            "health_tags": health_tags_list,
            "age_category": get_age_category_display(p.birthday, p.breed.species if p.breed else "狗"),
            "created_at": str(p.created_at),
            "breed": None,
        }
        if p.breed:
            item["breed"] = {
                "id": p.breed.id,
                "name": p.breed.name,
                "species": p.breed.species,
                "size": p.breed.size,
                "image_url": p.breed.image_url,
            }
        items.append(item)
    return {"code": 0, "data": {"items": items}}


@router.post("")
def create_pet(
    req: PetCreate,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """添加宠物"""
    import json
    # 创建宠物档案
    pet = models.PetProfile(
        user_id=user.id,
        pet_name=req.pet_name,
        breed_id=req.breed_id,
        age=req.age or "",
        gender=req.gender or "",
        weight=req.weight,
        avatar_url=req.avatar_url or "",
        birthday=req.birthday,
        body_condition=req.body_condition or "",
        health_tags=json.dumps(req.health_tags or []),
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    
    # 获取宠物品类
    species = "狗"  # 默认
    if pet.breed:
        species = pet.breed.species
    
    # 自动生成默认提醒
    created_reminders = 0
    if req.auto_reminders:
        reminders = generate_default_reminders(
            pet_name=pet.pet_name,
            birthday=req.birthday,
            species=species,
            age=req.age,
        )
        
        # 为每个提醒创建 Schedule 记录
        for reminder in reminders:
            schedule = models.Schedule(
                user_id=user.id,
                pet_name=pet.pet_name,
                title=reminder["title"],
                interval_days=reminder["interval_days"],
                schedule_type=reminder["schedule_type"],
                note=reminder["note"],
                last_done_at=datetime.utcnow(),  # 设置当前时间为起点，开始倒计时
            )
            db.add(schedule)
            created_reminders += 1
        
        if created_reminders > 0:
            db.commit()
    
    return {
        "code": 0, 
        "data": {
            "id": pet.id,
            "reminders_created": created_reminders,
        }, 
        "message": f"添加成功！已自动生成 {created_reminders} 个提醒" if created_reminders > 0 else "添加成功"
    }


@router.put("/{pet_id}")
def update_pet(
    pet_id: int,
    req: PetUpdate,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """更新宠物信息"""
    import json
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.user_id == user.id,
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    if req.pet_name is not None:
        pet.pet_name = req.pet_name
    if req.breed_id is not None:
        pet.breed_id = req.breed_id
    if req.age is not None:
        pet.age = req.age
    if req.gender is not None:
        pet.gender = req.gender
    if req.weight is not None:
        pet.weight = req.weight
    if req.avatar_url is not None:
        pet.avatar_url = req.avatar_url
    if req.birthday is not None:
        pet.birthday = req.birthday
    if req.body_condition is not None:
        pet.body_condition = req.body_condition
    if req.health_tags is not None:
        pet.health_tags = json.dumps(req.health_tags)

    db.commit()
    return {"code": 0, "message": "更新成功"}


@router.delete("/{pet_id}")
def delete_pet(
    pet_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """删除宠物"""
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.user_id == user.id,
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    db.delete(pet)
    db.commit()
    return {"code": 0, "message": "删除成功"}
