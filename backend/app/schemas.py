"""宠物宝 (PetCare) — Pydantic 模型"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


# ===== 品牌 =====
class BrandBase(BaseModel):
    name: str
    country: Optional[str] = ""
    description: Optional[str] = ""

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    model_config = {"from_attributes": True}


# ===== 品类 =====
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    type: Optional[str] = "药品"

class Category(CategoryBase):
    id: int
    children: List["Category"] = []
    model_config = {"from_attributes": True}

    @field_validator("children", mode="before")
    @classmethod
    def default_children(cls, v):
        return v or []


# ===== 成分 =====
class IngredientBase(BaseModel):
    name: str
    alias: Optional[str] = ""
    category: Optional[str] = ""
    safety_level: Optional[int] = 3
    description: Optional[str] = ""
    function: Optional[str] = ""

class Ingredient(IngredientBase):
    id: int
    model_config = {"from_attributes": True}


# ===== 产品 =====
class ProductIngredient(BaseModel):
    id: int
    name: str
    sort_order: int = 0
    function: Optional[str] = ""

class ProductBase(BaseModel):
    name: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[str] = "药品"
    description: Optional[str] = ""
    approval_number: Optional[str] = ""
    safety_score: Optional[float] = 0.0
    image_url: Optional[str] = ""
    usage_guide: Optional[str] = ""
    suitable_species: Optional[str] = "猫狗"
    target_size: Optional[str] = "全部"
    target_age: Optional[str] = "全部"

class ProductCreate(ProductBase):
    pass

class ProductListItem(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    type: str
    safety_score: float
    image_url: Optional[str] = ""
    suitable_species: Optional[str] = "猫狗"
    target_size: Optional[str] = "全部"
    target_age: Optional[str] = "全部"

class ProductDetail(ProductBase):
    id: int
    brand: Optional[Brand] = None
    category: Optional[Category] = None
    ingredients: List[ProductIngredient] = []
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ===== 品种 =====
class PetBreedBase(BaseModel):
    name: str
    species: str
    size: Optional[str] = "中型"
    common_issues: Optional[str] = ""
    description: Optional[str] = ""
    image_url: Optional[str] = ""

class PetBreed(PetBreedBase):
    id: int
    model_config = {"from_attributes": True}


# ===== 通用 =====
class Page(BaseModel):
    items: List
    total: int
    page: int
    page_size: int

class ApiResponse(BaseModel):
    code: int = 0
    data: Optional[dict | list] = None
    message: str = "ok"
