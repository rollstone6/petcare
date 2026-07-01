"""宠物日常健康记录 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/records", tags=["健康记录"])


class CreateRecord(BaseModel):
    pet_name: str = "我的宠物"
    record_type: str
    value: str = ""
    note: str = ""
    poop_color: str = ""
    poop_shape: str = ""
    vomit_type: str = ""
    severity: str = "normal"
    recorded_at: Optional[str] = None


class RecordOut(BaseModel):
    id: int
    pet_name: str
    record_type: str
    value: str
    note: str
    poop_color: str
    poop_shape: str
    vomit_type: str
    severity: str
    recorded_at: str
    model_config = {"from_attributes": True}

    @field_validator("recorded_at", mode="before")
    @classmethod
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v else ""


@router.post("")
def create_record(
    req: CreateRecord,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    rec = models.HealthRecord(
        user_id=user.id,
        pet_name=req.pet_name,
        record_type=req.record_type,
        value=req.value,
        note=req.note,
        poop_color=req.poop_color,
        poop_shape=req.poop_shape,
        vomit_type=req.vomit_type,
        severity=req.severity,
        recorded_at=datetime.fromisoformat(req.recorded_at) if req.recorded_at else datetime.utcnow(),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"code": 0, "data": RecordOut.model_validate(rec).model_dump(), "message": "记录成功"}


@router.get("")
def list_records(
    record_type: Optional[str] = None,
    pet_name: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.HealthRecord).filter(models.HealthRecord.user_id == user.id)
    if record_type:
        query = query.filter(models.HealthRecord.record_type == record_type)
    if pet_name:
        query = query.filter(models.HealthRecord.pet_name == pet_name)

    total = query.count()
    records = query.order_by(models.HealthRecord.recorded_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 0,
        "data": {
            "items": [RecordOut.model_validate(r).model_dump() for r in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/stats")
def record_stats(
    days: int = Query(7, ge=1, le=90),
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)
    records = db.query(models.HealthRecord).filter(
        models.HealthRecord.user_id == user.id,
        models.HealthRecord.recorded_at >= since,
    ).all()

    by_type = {}
    severity_count = {"normal": 0, "warning": 0, "danger": 0}
    for r in records:
        by_type[r.record_type] = by_type.get(r.record_type, 0) + 1
        severity_count[r.severity] = severity_count.get(r.severity, 0) + 1

    return {
        "code": 0,
        "data": {
            "total_records": len(records),
            "by_type": by_type,
            "severity": severity_count,
            "days": days,
        },
    }


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    rec = db.query(models.HealthRecord).filter(
        models.HealthRecord.id == record_id,
        models.HealthRecord.user_id == user.id,
    ).first()
    if not rec:
        raise HTTPException(404, "记录不存在")
    db.delete(rec)
    db.commit()
    return {"code": 0, "message": "已删除"}
