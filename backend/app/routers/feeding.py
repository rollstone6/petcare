"""喂养记录与换粮日记 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/feeding", tags=["喂养日记"])


# ===== FeedingLog =====
class CreateFeedingLog(BaseModel):
    pet_name: str
    product_id: int
    start_date: Optional[str] = None  # 默认今天
    note: str = ""


class FeedingLogOut(BaseModel):
    id: int
    pet_name: str
    product_id: int
    product_name: str = ""
    product_type: str = ""
    brand_name: str = ""
    start_date: str
    is_active: int
    note: str
    days_since_start: int = 0
    model_config = {"from_attributes": True}


class UpdateFeedingLog(BaseModel):
    is_active: Optional[int] = None
    note: Optional[str] = None


@router.post("/logs")
def create_feeding_log(
    req: CreateFeedingLog,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    # 验证产品存在
    product = db.query(models.Product).filter(models.Product.id == req.product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")

    # 检查是否已有同一个宠物+产品的活跃记录
    existing = db.query(models.FeedingLog).filter(
        models.FeedingLog.user_id == user.id,
        models.FeedingLog.pet_name == req.pet_name,
        models.FeedingLog.product_id == req.product_id,
        models.FeedingLog.is_active == 1,
    ).first()
    if existing:
        raise HTTPException(400, f"{req.pet_name} 已经在吃这个产品了")

    start = date.fromisoformat(req.start_date) if req.start_date else date.today()
    log = models.FeedingLog(
        user_id=user.id,
        pet_name=req.pet_name,
        product_id=req.product_id,
        start_date=start,
        note=req.note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"code": 0, "data": _log_to_dict(log, db), "message": "记录成功"}


@router.get("/logs")
def list_feeding_logs(
    pet_name: Optional[str] = None,
    active_only: bool = Query(False),
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.FeedingLog).filter(
        models.FeedingLog.user_id == user.id,
    )
    if pet_name:
        query = query.filter(models.FeedingLog.pet_name == pet_name)
    if active_only:
        query = query.filter(models.FeedingLog.is_active == 1)

    logs = query.order_by(models.FeedingLog.start_date.desc()).all()
    return {"code": 0, "data": {"items": [_log_to_dict(l, db) for l in logs]}}


@router.put("/logs/{log_id}")
def update_feeding_log(
    log_id: int,
    req: UpdateFeedingLog,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    log = db.query(models.FeedingLog).filter(
        models.FeedingLog.id == log_id,
        models.FeedingLog.user_id == user.id,
    ).first()
    if not log:
        raise HTTPException(404, "记录不存在")
    if req.is_active is not None:
        log.is_active = req.is_active
    if req.note is not None:
        log.note = req.note
    db.commit()
    db.refresh(log)
    return {"code": 0, "data": _log_to_dict(log, db), "message": "更新成功"}


@router.delete("/logs/{log_id}")
def delete_feeding_log(
    log_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    log = db.query(models.FeedingLog).filter(
        models.FeedingLog.id == log_id,
        models.FeedingLog.user_id == user.id,
    ).first()
    if not log:
        raise HTTPException(404, "记录不存在")
    db.delete(log)
    db.commit()
    return {"code": 0, "message": "已删除"}


# ===== FeedingDiary =====
class CreateDiary(BaseModel):
    pet_name: str
    feeding_log_id: Optional[int] = None
    day_number: Optional[int] = None
    record_date: Optional[str] = None  # 默认今天
    poop_status: str = ""
    poop_count: int = 0
    appetite: str = ""
    energy: str = ""
    vomiting: int = 0
    note: str = ""


class DiaryOut(BaseModel):
    id: int
    pet_name: str
    feeding_log_id: Optional[int] = None
    product_name: str = ""
    day_number: Optional[int] = None
    record_date: str
    poop_status: str
    poop_count: int
    appetite: str
    energy: str
    vomiting: int
    note: str
    model_config = {"from_attributes": True}


@router.post("/diaries")
def create_diary(
    req: CreateDiary,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    rec_date = date.fromisoformat(req.record_date) if req.record_date else date.today()
    diary = models.FeedingDiary(
        user_id=user.id,
        pet_name=req.pet_name,
        feeding_log_id=req.feeding_log_id,
        day_number=req.day_number,
        record_date=rec_date,
        poop_status=req.poop_status,
        poop_count=req.poop_count,
        appetite=req.appetite,
        energy=req.energy,
        vomiting=req.vomiting,
        note=req.note,
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return {"code": 0, "data": _diary_to_dict(diary, db), "message": "记录成功"}


@router.get("/diaries")
def list_diaries(
    pet_name: Optional[str] = None,
    feeding_log_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.FeedingDiary).filter(
        models.FeedingDiary.user_id == user.id,
    )
    if pet_name:
        query = query.filter(models.FeedingDiary.pet_name == pet_name)
    if feeding_log_id:
        query = query.filter(models.FeedingDiary.feeding_log_id == feeding_log_id)

    total = query.count()
    diaries = query.order_by(models.FeedingDiary.record_date.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 0,
        "data": {
            "items": [_diary_to_dict(d, db) for d in diaries],
            "total": total,
        },
    }


@router.delete("/diaries/{diary_id}")
def delete_diary(
    diary_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    diary = db.query(models.FeedingDiary).filter(
        models.FeedingDiary.id == diary_id,
        models.FeedingDiary.user_id == user.id,
    ).first()
    if not diary:
        raise HTTPException(404, "记录不存在")
    db.delete(diary)
    db.commit()
    return {"code": 0, "message": "已删除"}


# ===== 检查用户是否在某产品的喂养列表中 =====
@router.get("/check/{product_id}")
def check_product_feeding(
    product_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """检查当前用户是否有宠物正在吃这个产品"""
    logs = db.query(models.FeedingLog).filter(
        models.FeedingLog.user_id == user.id,
        models.FeedingLog.product_id == product_id,
        models.FeedingLog.is_active == 1,
    ).all()
    return {
        "code": 0,
        "data": {
            "feeding": len(logs) > 0,
            "pets": [l.pet_name for l in logs],
        },
    }


# ===== 工具函数 =====
def _log_to_dict(log: models.FeedingLog, db: Session) -> dict:
    product = db.query(models.Product).filter(models.Product.id == log.product_id).first()
    today = date.today()
    days_since = (today - log.start_date).days if log.start_date else 0
    return {
        "id": log.id,
        "pet_name": log.pet_name,
        "product_id": log.product_id,
        "product_name": product.name if product else "",
        "product_type": product.type if product else "",
        "brand_name": product.brand.name if product and product.brand else "",
        "start_date": log.start_date.isoformat() if log.start_date else "",
        "is_active": log.is_active,
        "note": log.note,
        "days_since_start": days_since,
    }


def _diary_to_dict(diary: models.FeedingDiary, db: Session) -> dict:
    product_name = ""
    if diary.feeding_log_id:
        log = db.query(models.FeedingLog).filter(models.FeedingLog.id == diary.feeding_log_id).first()
        if log:
            product = db.query(models.Product).filter(models.Product.id == log.product_id).first()
            product_name = product.name if product else ""
    return {
        "id": diary.id,
        "pet_name": diary.pet_name,
        "feeding_log_id": diary.feeding_log_id,
        "product_name": product_name,
        "day_number": diary.day_number,
        "record_date": diary.record_date.isoformat() if diary.record_date else "",
        "poop_status": diary.poop_status,
        "poop_count": diary.poop_count,
        "appetite": diary.appetite,
        "energy": diary.energy,
        "vomiting": diary.vomiting,
        "note": diary.note,
    }
