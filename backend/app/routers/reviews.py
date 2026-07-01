"""用户评价/评论 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, require_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


# ===== Schemas =====
class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    content: str = ""
    pet_type: str = ""
    pet_age: str = ""
    is_anonymous: bool = False

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("评分必须在 1-5 之间")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if len(v) > 500:
            raise ValueError("评论内容不能超过 500 字")
        return v


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    content: str
    pet_type: str
    pet_age: str
    is_anonymous: int
    created_at: datetime
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ReviewStats(BaseModel):
    product_id: int
    total_reviews: int
    avg_rating: float
    rating_distribution: dict  # {1: 5, 2: 3, 3: 10, 4: 20, 5: 50}


# ===== API Endpoints =====
@router.get("/product/{product_id}", response_model=dict)
def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取产品评论列表"""
    # 统计信息
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
    total = len(reviews)
    
    if total == 0:
        return {
            "code": 0,
            "data": {
                "items": [],
                "total": 0,
                "stats": {
                    "product_id": product_id,
                    "total_reviews": 0,
                    "avg_rating": 0.0,
                    "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                }
            },
            "message": "ok"
        }
    
    # 计算评分分布
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        distribution[r.rating] += 1
    
    avg_rating = sum(r.rating for r in reviews) / total
    
    # 分页查询
    offset = (page - 1) * page_size
    paginated_reviews = db.query(models.Review).filter(
        models.Review.product_id == product_id
    ).order_by(models.Review.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 批量查询用户信息，避免 N+1
    user_ids = [r.user_id for r in paginated_reviews if not r.is_anonymous]
    users_data = {}
    if user_ids:
        users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
        users_data = {u.id: u for u in users}
    
    # 构建返回数据
    items = []
    for r in paginated_reviews:
        item = {
            "id": r.id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "content": r.content,
            "pet_type": r.pet_type,
            "pet_age": r.pet_age,
            "is_anonymous": r.is_anonymous,
            "created_at": r.created_at,
        }
        
        # 匿名用户不显示用户信息
        user = users_data.get(r.user_id) if not r.is_anonymous else None
        if user:
            item["username"] = user.username
            item["nickname"] = user.nickname or user.username
            item["avatar_url"] = user.avatar_url
        else:
            item["username"] = "匿名用户"
            item["nickname"] = "匿名用户"
            item["avatar_url"] = ""
        
        items.append(item)
    
    return {
        "code": 0,
        "data": {
            "items": items,
            "total": total,
            "stats": {
                "product_id": product_id,
                "total_reviews": total,
                "avg_rating": round(avg_rating, 1),
                "rating_distribution": distribution
            }
        },
        "message": "ok"
    }


@router.post("/", response_model=dict)
def create_review(
    review: ReviewCreate,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """创建评论（需登录）"""
    # 检查产品是否存在
    product = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 检查是否已经评论过
    existing = db.query(models.Review).filter(
        models.Review.user_id == user.id,
        models.Review.product_id == review.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已经评论过该产品")
    
    # 创建评论
    new_review = models.Review(
        user_id=user.id,
        product_id=review.product_id,
        rating=review.rating,
        content=review.content,
        pet_type=review.pet_type,
        pet_age=review.pet_age,
        is_anonymous=1 if review.is_anonymous else 0
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return {
        "code": 0,
        "data": {"id": new_review.id},
        "message": "评论成功"
    }


@router.delete("/{review_id}", response_model=dict)
def delete_review(
    review_id: int,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """删除自己的评论（需登录）"""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的评论")
    
    db.delete(review)
    db.commit()
    
    return {"code": 0, "data": None, "message": "删除成功"}


@router.get("/my", response_model=dict)
def get_my_reviews(
    user: models.User = Depends(require_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取我的评论列表（需登录）"""
    total = db.query(models.Review).filter(models.Review.user_id == user.id).count()
    
    offset = (page - 1) * page_size
    reviews = db.query(models.Review).filter(
        models.Review.user_id == user.id
    ).order_by(models.Review.created_at.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for r in reviews:
        # 获取产品信息
        product = db.query(models.Product).filter(models.Product.id == r.product_id).first()
        items.append({
            "id": r.id,
            "product_id": r.product_id,
            "product_name": product.name if product else "未知产品",
            "rating": r.rating,
            "content": r.content,
            "pet_type": r.pet_type,
            "pet_age": r.pet_age,
            "created_at": r.created_at
        })
    
    return {
        "code": 0,
        "data": {"items": items, "total": total},
        "message": "ok"
    }
