"""宠物宝 (PetCare) — 用户 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/auth", tags=["用户"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    model_config = {"from_attributes": True}


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
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})
    return {"code": 0, "data": {"token": token, "user": UserInfo.model_validate(user).model_dump()}, "message": "注册成功"}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not auth.verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"code": 0, "data": {"token": token, "user": UserInfo.model_validate(user).model_dump()}, "message": "登录成功"}


@router.get("/me")
def me(user: models.User = Depends(auth.require_user)):
    return {"code": 0, "data": UserInfo.model_validate(user).model_dump()}
