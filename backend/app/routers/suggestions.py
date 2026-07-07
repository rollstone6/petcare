"""产品众包建议 - 搜索0结果时用户提交配料表"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import ProductSuggestion, User

router = APIRouter(prefix="/suggestions", tags=["产品建议"])


class SuggestionCreate(BaseModel):
    search_query: str = ""
    product_name: str
    brand_name: str = ""
    product_type: str = "食品"
    ingredients_text: str = ""


class SuggestionOut(BaseModel):
    id: int
    search_query: str
    product_name: str
    brand_name: str
    product_type: str
    ingredients_text: str
    image_url: str
    ai_analysis: str
    ai_score: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=SuggestionOut)
async def create_suggestion(
    data: SuggestionCreate,
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """创建产品建议（支持匿名）"""
    
    # 处理图片上传
    image_url = ""
    if image:
        upload_dir = "uploads/suggestions"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        ext = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(filepath, "wb") as f:
            content = await image.read()
            f.write(content)
        
        image_url = f"/uploads/suggestions/{filename}"
    
    # 创建建议记录
    suggestion = ProductSuggestion(
        user_id=current_user.id if current_user else None,
        search_query=data.search_query,
        product_name=data.product_name,
        brand_name=data.brand_name,
        product_type=data.product_type,
        ingredients_text=data.ingredients_text,
        image_url=image_url,
        status="pending"
    )
    
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    
    return suggestion


@router.get("/{suggestion_id}", response_model=SuggestionOut)
def get_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """获取单个建议详情"""
    suggestion = db.query(ProductSuggestion).filter(
        ProductSuggestion.id == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="建议不存在")
    
    return suggestion


@router.get("/user")
def get_user_suggestions(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取当前用户的建议列表"""
    if not current_user:
        return {"suggestions": []}
    
    suggestions = db.query(ProductSuggestion).filter(
        ProductSuggestion.user_id == current_user.id
    ).order_by(ProductSuggestion.created_at.desc()).all()
    
    return {"suggestions": suggestions}
