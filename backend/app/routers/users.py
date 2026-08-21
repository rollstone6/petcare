"""宠物宝 (PetCare) — 用户 API"""
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app import models, auth
from app.config import settings

router = APIRouter(prefix="/auth", tags=["用户"])

# 微信 code2session 接口（wx.login 的 code 换 openid/session_key）
WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class WxLoginRequest(BaseModel):
    code: str


class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    email: Optional[str] = ""
    has_wx_bind: bool = False
    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user: models.User) -> dict:
        data = cls.model_validate(user).model_dump()
        data["email"] = data["email"] or ""  # 未填邮箱统一输出空串，兼容前端
        data["has_wx_bind"] = bool(user.wx_openid)
        return data


# 微信 jscode2session 错误码（参考微信开放文档《微信登录开发指南》）：
#   -1     微信系统繁忙（可稍后重试）
#   40029  code 无效
#   40163  code 已被使用（code 一次性、有效期约 10 分钟）
#   45011  接口频率限制（同一用户 1 分钟内合计不能超 180 次）
#   40125  AppSecret 配置错误（服务端问题）
_WX_ERR_BUSY = -1
_WX_ERR_RATE_LIMITED = 45011
_WX_ERR_BAD_SECRET = 40125
_WX_ERR_CODE_INVALID = {40029, 40163, 41008}


def code2session(code: str) -> dict:
    """用小程序 wx.login 的 code 向微信服务器换取 openid/session_key。

    安全约定（官方文档要求）：
    - AppSecret 只存服务端 .env，绝不下发客户端；
    - session_key 仅服务端使用（解密手机号等场景），绝不下发前端；
    - code 一次性使用，客户端每次登录都应重新 wx.login 获取。
    """
    if not settings.wx_appid or not settings.wx_app_secret:
        raise HTTPException(500, "服务端未配置微信登录参数")
    try:
        resp = httpx.get(
            WX_CODE2SESSION_URL,
            params={
                "appid": settings.wx_appid,
                "secret": settings.wx_app_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        data = resp.json()
    except Exception:
        raise HTTPException(502, "微信服务暂不可用，请稍后重试")

    if "openid" in data:
        return data

    errcode = data.get("errcode")
    if errcode in _WX_ERR_CODE_INVALID:
        # 前端可重新 wx.login 换新 code 重试
        raise HTTPException(400, "微信凭证无效，请重试")
    if errcode == _WX_ERR_RATE_LIMITED:
        # 提示稍后再试，避免立即重试加剧触发频控
        raise HTTPException(503, "微信接口繁忙，请稍后再试")
    if errcode == _WX_ERR_BAD_SECRET:
        raise HTTPException(500, "服务端微信配置有误，请联系管理员")
    if errcode == _WX_ERR_BUSY:
        raise HTTPException(502, "微信系统繁忙，请稍后重试")
    raise HTTPException(400, f"微信登录失败（errcode={errcode}）")


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if len(req.username) < 2 or len(req.username) > 20:
        raise HTTPException(400, "用户名长度2-20位")
    if len(req.password) < 8:
        raise HTTPException(400, "密码至少8位")
    import re
    if not re.search(r"[a-zA-Z]", req.password) or not re.search(r"\d", req.password):
        raise HTTPException(400, "密码需包含字母和数字")
    if db.query(models.User).filter(models.User.username == req.username).first():
        raise HTTPException(400, "用户名已存在")

    user = models.User(
        username=req.username,
        email=req.email or None,  # 空字符串转为 None，避免 unique 冲突
        nickname=req.username,
        hashed_password=auth.hash_password(req.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # 并发注册等极端场景下的唯一约束冲突（username/email），转为友好 400
        db.rollback()
        raise HTTPException(400, "注册信息冲突，请更换用户名后重试")
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})
    return {"code": 0, "data": {"token": token, "user": UserInfo.from_user(user)}, "message": "注册成功"}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not auth.verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"code": 0, "data": {"token": token, "user": UserInfo.from_user(user)}, "message": "登录成功"}


@router.post("/wx-login")
def wx_login(req: WxLoginRequest, db: Session = Depends(get_db)):
    """微信小程序一键登录：code 换 openid，未绑定则自动注册新用户。

    返回结构与 /login 完全一致，前端无需区分两种登录方式。
    """
    wx_data = code2session(req.code)
    openid = wx_data["openid"]
    unionid = wx_data.get("unionid")

    user = db.query(models.User).filter(models.User.wx_openid == openid).first()
    is_new = user is None
    if is_new:
        # 自动注册：生成唯一用户名；密码为随机串（微信用户无需密码，
        # 之后可通过账号绑定关联；hashed_password 不可为空故必须填充）
        base_name = "wx_" + secrets.token_hex(4)
        username = base_name
        suffix = 1
        while db.query(models.User).filter(models.User.username == username).first():
            suffix += 1
            username = f"{base_name}_{suffix}"
        user = models.User(
            username=username,
            nickname="微信用户",
            email=None,  # 微信用户无邮箱；NULL 不占 unique 约束
            hashed_password=auth.hash_password(secrets.token_urlsafe(24)),
            wx_openid=openid,
            wx_unionid=unionid,
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            # 并发场景下 wx_openid/username 撞唯一约束，提示重试即可
            db.rollback()
            raise HTTPException(400, "微信登录冲突，请重试")
        db.refresh(user)
    elif unionid and not user.wx_unionid:
        # 补齐 unionid（绑定微信开放平台后微信才会返回）
        user.wx_unionid = unionid
        db.commit()

    token = auth.create_access_token({"sub": str(user.id)})
    return {
        "code": 0,
        "data": {"token": token, "user": UserInfo.from_user(user), "is_new": is_new},
        "message": "登录成功",
    }


@router.post("/bind-wx")
def bind_wx(
    req: WxLoginRequest,
    user: models.User = Depends(auth.require_user),
    db: Session = Depends(get_db),
):
    """已登录用户把当前微信绑定到账号上（实现账号 ↔ 微信身份互通）。

    - openid 已被其他账号绑定 → 400
    - 当前账号已绑定其他微信 → 允许更新为新微信（换绑）
    """
    wx_data = code2session(req.code)
    openid = wx_data["openid"]

    existing = db.query(models.User).filter(models.User.wx_openid == openid).first()
    if existing and existing.id != user.id:
        raise HTTPException(400, "该微信已绑定其他账号，请直接用微信登录")

    user.wx_openid = openid
    if wx_data.get("unionid"):
        user.wx_unionid = wx_data["unionid"]
    db.commit()
    db.refresh(user)
    return {"code": 0, "data": UserInfo.from_user(user), "message": "绑定成功"}


@router.get("/me")
def me(user: models.User = Depends(auth.require_user)):
    return {"code": 0, "data": UserInfo.from_user(user)}
