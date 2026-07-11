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

# 预设日程模板（含年龄分段周期规则）
PRESETS = {
    "体外驱虫": {
        "interval": 30,
        "title": "体外驱虫",
        "note": "滴剂/喷剂，沿脊柱滴在皮肤上",
        "icon": "🦟",
        "rules": [
            {"stage": "幼崽（2-6月龄）", "interval": 30, "desc": "每月1次，幼宠免疫力弱易感染跳蚤蜱虫"},
            {"stage": "成年（6月龄+）", "interval": 30, "desc": "每月1次；春夏活跃季建议2-3周补一次"},
            {"stage": "老年（7岁+）", "interval": 30, "desc": "每月1次，注意选择低刺激配方"},
        ],
        "tips": [
            "⚠️ 用药后48小时内不要洗澡",
            "⚠️ 猫用和犬用产品不可混用（含菊酯类对猫致命）",
            "💡 多宠家庭建议同一天全部驱虫，避免交叉感染",
        ],
    },
    "体内驱虫": {
        "interval": 90,
        "title": "体内驱虫",
        "note": "口服药/片剂，空腹效果更佳",
        "icon": "💊",
        "rules": [
            {"stage": "幼崽（2-6月龄）", "interval": 14, "desc": "每2周1次，蛔虫/绦虫/钩虫高发期"},
            {"stage": "幼年（6-12月龄）", "interval": 30, "desc": "每月1次，逐步过渡到成犬频率"},
            {"stage": "成年（1-7岁）", "interval": 90, "desc": "每3个月1次；生骨肉喂养建议每月1次"},
            {"stage": "老年（7岁+）", "interval": 90, "desc": "每3个月1次，注意肝肾功能评估后用药"},
        ],
        "tips": [
            "⚠️ 伊维菌素对柯利犬（牧羊犬类）有致命风险",
            "⚠️ 驱虫后观察便便，如有虫体排出属正常现象",
            "💡 体内驱虫和疫苗接种间隔至少1周",
        ],
    },
    "疫苗": {
        "interval": 365,
        "title": "疫苗接种",
        "note": "建议提前预约宠物医院",
        "icon": "💉",
        "rules": [
            {"stage": "首免（6-8周龄）", "interval": 21, "desc": "第1针联苗，之后每3-4周1针，共3针"},
            {"stage": "幼犬/猫（2-4月龄）", "interval": 21, "desc": "完成二免/三免 + 首针狂犬（3月龄后）"},
            {"stage": "成年（1岁+）", "interval": 365, "desc": "每年1针狂犬+联苗加强，可先测抗体水平"},
            {"stage": "老年（7岁+）", "interval": 365, "desc": "建议先测抗体滴度，达标可不补打"},
        ],
        "tips": [
            "⚠️ 接种前必须体内外驱虫已完成",
            "⚠️ 接种后1周内不要洗澡、不要剧烈运动",
            "💡 猫三联 vs 犬四/六/八联，根据生活场景选择",
        ],
    },
    "体检": {
        "interval": 180,
        "title": "健康体检",
        "note": "血常规 + 生化 + 尿检",
        "icon": "🩺",
        "rules": [
            {"stage": "幼年（1岁以下）", "interval": 180, "desc": "每半年1次，关注发育指标和先天性疾病"},
            {"stage": "成年（1-7岁）", "interval": 365, "desc": "每年1次常规体检即可"},
            {"stage": "老年（7岁+）", "interval": 180, "desc": "每半年1次，重点查心肝肾+关节+牙齿"},
        ],
        "tips": [
            "⚠️ 体检当天需要空腹（禁食8-12小时）",
            "💡 建议体检项目：血常规+生化全项+B超+尿检",
            "💡 7岁以上加做心脏超声和甲状腺功能检查",
        ],
    },
}


class CreateSchedule(BaseModel):
    pet_name: str = "我的宠物"
    schedule_type: str  # 体外驱虫/体内驱虫/疫苗/体检/自定义
    title: str = ""
    interval_days: Optional[int] = None
    note: str = ""


class UpdateSchedule(BaseModel):
    pet_name: Optional[str] = None
    interval_days: Optional[int] = None
    title: Optional[str] = None
    note: Optional[str] = None


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


@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    req: UpdateSchedule,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    s = db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.user_id == user.id,
    ).first()
    if not s:
        raise HTTPException(404, "日程不存在")

    if req.pet_name is not None:
        s.pet_name = req.pet_name
    if req.interval_days is not None:
        s.interval_days = req.interval_days
    if req.title is not None:
        s.title = req.title
    if req.note is not None:
        s.note = req.note

    db.commit()
    db.refresh(s)
    return {"code": 0, "data": _build_out(s), "message": "已更新"}


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
    """返回预设日程模板（含年龄分段规则 + 注意事项）"""
    items = []
    for key, val in PRESETS.items():
        items.append({
            "type": key,
            "title": val["title"],
            "interval_days": val["interval"],
            "note": val["note"],
            "icon": val.get("icon", "📅"),
            "rules": val.get("rules", []),
            "tips": val.get("tips", []),
        })
    return {"code": 0, "data": items}
