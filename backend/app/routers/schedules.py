"""宠物日程提醒 API — 驱虫/疫苗/体检倒计时 + 日历导出"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/schedules", tags=["日程提醒"])

# 预设日程模板
PRESETS = {
    "体外驱虫": {"interval": 30, "title": "体外驱虫", "note": "每月一次，滴剂/喷剂"},
    "体内驱虫": {"interval": 90, "title": "体内驱虫", "note": "每季度一次，口服药"},
    "疫苗": {"interval": 365, "title": "疫苗接种", "note": "每年一次，建议提前预约"},
    "体检": {"interval": 180, "title": "体检", "note": "每半年一次，血常规+生化"},
}


class CreateSchedule(BaseModel):
    pet_name: str = "我的宠物"
    schedule_type: str  # 体外驱虫/体内驱虫/疫苗/体检/自定义
    title: str = ""
    interval_days: Optional[int] = None
    note: str = ""


class ScheduleOut(BaseModel):
    id: int
    pet_name: str
    schedule_type: str
    title: str
    interval_days: int
    last_done_at: Optional[str] = None
    next_due_at: Optional[str] = None
    days_left: Optional[int] = None
    status: str = "normal"  # normal/warning/urgent/overdue
    note: str
    model_config = {"from_attributes": True}

    @field_validator("last_done_at", "next_due_at", mode="before")
    @classmethod
    def format_dt(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v else None


def _build_out(schedule: models.Schedule) -> dict:
    """计算倒计时和状态"""
    now = datetime.utcnow()
    days_left = None
    next_due_at = None
    status = "normal"

    if schedule.last_done_at:
        next_due = schedule.last_done_at + timedelta(days=schedule.interval_days)
        next_due_at = next_due.isoformat()
        days_left = (next_due - now).days
        if days_left < 0:
            status = "overdue"
        elif days_left <= 3:
            status = "urgent"
        elif days_left <= 7:
            status = "warning"

    return {
        "id": schedule.id,
        "pet_name": schedule.pet_name,
        "schedule_type": schedule.schedule_type,
        "title": schedule.title or schedule.schedule_type,
        "interval_days": schedule.interval_days,
        "last_done_at": schedule.last_done_at.isoformat() if schedule.last_done_at else None,
        "next_due_at": next_due_at,
        "days_left": days_left,
        "status": status,
        "note": schedule.note or "",
    }


@router.get("")
def list_schedules(
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    schedules = db.query(models.Schedule).filter(
        models.Schedule.user_id == user.id
    ).order_by(models.Schedule.last_done_at.asc().nullsfirst()).all()

    items = [_build_out(s) for s in schedules]

    # 排序：过期 > 紧急 > 警告 > 正常 > 未开始
    def sort_key(x):
        if x["status"] == "overdue": return (0, x["days_left"] or -999)
        if x["status"] == "urgent": return (1, x["days_left"] or 0)
        if x["status"] == "warning": return (2, x["days_left"] or 0)
        if x["days_left"] is not None: return (3, x["days_left"])
        return (4, 0)

    items.sort(key=sort_key)
    return {"code": 0, "data": {"items": items, "total": len(items)}}


@router.post("")
def create_schedule(
    req: CreateSchedule,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    preset = PRESETS.get(req.schedule_type)
    interval = req.interval_days or (preset["interval"] if preset else 30)
    title = req.title or (preset["title"] if preset else req.schedule_type)
    note = req.note or (preset["note"] if preset else "")

    s = models.Schedule(
        user_id=user.id,
        pet_name=req.pet_name,
        schedule_type=req.schedule_type,
        title=title,
        interval_days=interval,
        note=note,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"code": 0, "data": _build_out(s), "message": "创建成功"}


@router.post("/{schedule_id}/done")
def mark_done(
    schedule_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    s = db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.user_id == user.id,
    ).first()
    if not s:
        raise HTTPException(404, "日程不存在")

    s.last_done_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    return {"code": 0, "data": _build_out(s), "message": f"已标记完成，{s.interval_days}天后提醒"}


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    s = db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.user_id == user.id,
    ).first()
    if not s:
        raise HTTPException(404, "日程不存在")
    db.delete(s)
    db.commit()
    return {"code": 0, "message": "已删除"}


@router.get("/{schedule_id}/ics")
def export_ics(
    schedule_id: int,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """导出为 .ics 日历文件，一键导入手机系统日历"""
    s = db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.user_id == user.id,
    ).first()
    if not s or not s.last_done_at:
        raise HTTPException(404, "请先标记完成一次，才能导出日历")

    next_due = s.last_done_at + timedelta(days=s.interval_days)
    now = datetime.utcnow()

    # ICS text escaping: escape backslashes, semicolons, commas, and convert newlines
    def escape_ics_text(text):
        if not text:
            return ""
        return (text.replace("\\", "\\\\")
                .replace(";", "\\;")
                .replace(",", "\\,")
                .replace("\n", "\\n")
                .replace("\r", ""))

    title_escaped = escape_ics_text(s.title or s.schedule_type)
    pet_name_escaped = escape_ics_text(s.pet_name)
    note_escaped = escape_ics_text(s.note or '')

    # 生成 iCalendar 格式
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PetCare//Schedule//CN
BEGIN:VEVENT
DTSTART:{next_due.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{(next_due + timedelta(hours=1)).strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{title_escaped} - {pet_name_escaped}
DESCRIPTION:{note_escaped}\\n下次提醒: {next_due.strftime('%Y-%m-%d')}\\n间隔: {s.interval_days}天
DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}
UID:petcare-schedule-{s.id}@petcare.yjyblog.xyz
BEGIN:VALARM
TRIGGER:-PT1D
ACTION:DISPLAY
DESCRIPTION:{title_escaped}提醒: 还剩1天!
END:VALARM
END:VEVENT
END:VCALENDAR"""

    safe_name = f"{s.schedule_type}_{s.pet_name}".encode("ascii", "ignore").decode() or "schedule"
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.ics"'},
    )


@router.get("/presets/list")
def list_presets():
    """返回预设日程模板"""
    items = []
    for key, val in PRESETS.items():
        items.append({
            "type": key,
            "title": val["title"],
            "interval_days": val["interval"],
            "note": val["note"],
            "icon": {"体外驱虫": "🦟", "体内驱虫": "💊", "疫苗": "💉", "体检": "🩺"}.get(key, "📅"),
        })
    return {"code": 0, "data": items}
