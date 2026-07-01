"""宠物宝 (PetCare) — 数据模型"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, Enum, Table, DateTime, Date, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProductType(str, enum.Enum):
    药品 = "药品"
    食品 = "食品"
    保健品 = "保健品"


class Species(str, enum.Enum):
    猫 = "猫"
    狗 = "狗"


class PetSize(str, enum.Enum):
    小型 = "小型"
    中型 = "中型"
    大型 = "大型"


# 多对多：产品 ↔ 成分
product_ingredient = Table(
    "product_ingredient",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
    Column("sort_order", Integer, default=0, comment="成分排序"),
    Column("is_active", Integer, default=1, comment="是否主要成分"),
)

# 多对多：品种 ↔ 推荐产品
breed_product = Table(
    "breed_product",
    Base.metadata,
    Column("breed_id", Integer, ForeignKey("pet_breeds.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    country = Column(String(50), default="")
    description = Column(Text, default="")
    logo_url = Column(String(500), default="")

    products = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    type = Column(String(20), default="药品")  # 药品/食品/保健品

    children = relationship("Category", backref="parent", remote_side=[id])
    products = relationship("Product", back_populates="category")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, index=True, nullable=False)
    alias = Column(String(200), default="")
    category = Column(String(50), default="", comment="成分分类：驱虫/抗菌/营养等")
    safety_level = Column(Integer, default=3, comment="安全等级 1-5")
    description = Column(Text, default="")
    function = Column(String(500), default="", comment="功效说明")

    products = relationship("Product", secondary=product_ingredient, back_populates="ingredients")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    type = Column(String(20), default="药品")
    description = Column(Text, default="")
    approval_number = Column(String(100), default="", comment="批准文号")
    safety_score = Column(Float, default=0.0, comment="安全评分 0-5")
    image_url = Column(String(500), default="")
    usage_guide = Column(Text, default="", comment="使用说明")
    suitable_species = Column(String(50), default="猫狗", comment="适用物种")
    created_at = Column(DateTime, default=func.now())

    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    ingredients = relationship("Ingredient", secondary=product_ingredient, back_populates="products")
    suitable_breeds = relationship("PetBreed", secondary=breed_product, back_populates="recommended_products")


class PetBreed(Base):
    __tablename__ = "pet_breeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(10), nullable=False)  # 猫/狗
    size = Column(String(10), default="中型")
    common_issues = Column(Text, default="", comment="常见健康问题")
    description = Column(Text, default="")
    image_url = Column(String(500), default="")

    recommended_products = relationship("Product", secondary=breed_product, back_populates="suitable_breeds")


# ===== 用户系统 =====
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, default="")
    hashed_password = Column(String(200), nullable=False)
    nickname = Column(String(50), default="")
    avatar_url = Column(String(500), default="")
    created_at = Column(DateTime, default=func.now())

    favorites = relationship("Favorite", back_populates="user")
    history = relationship("BrowseHistory", back_populates="user")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 唯一约束：同一用户不能重复收藏同一产品
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_favorite_user_product'),
    )

    user = relationship("User", back_populates="favorites")
    product = relationship("Product")


class BrowseHistory(Base):
    __tablename__ = "browse_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=True)
    breed_id = Column(Integer, ForeignKey("pet_breeds.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="history")


# ===== 宠物健康记录 =====
class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String(50), default="我的宠物")
    record_type = Column(String(20), nullable=False, comment="便便/饮水/呕吐/体重/食欲/精神/用药/其他")
    
    # 通用字段
    value = Column(String(100), default="", comment="数值（如体重kg、饮水量ml）")
    note = Column(Text, default="", comment="备注")
    
    # 便便专用
    poop_color = Column(String(20), default="", comment="棕色/黑色/红色/绿色/黄色/白色")
    poop_shape = Column(String(20), default="", comment="正常/软便/稀便/硬便/带血")
    
    # 呕吐专用
    vomit_type = Column(String(20), default="", comment="食物/黄水/白沫/血丝/异物")
    
    # 通用状态
    severity = Column(String(10), default="normal", comment="normal/warning/danger")
    
    recorded_at = Column(DateTime, default=func.now(), comment="记录时间")
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")


# ===== 宠物日程提醒 =====
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String(50), default="我的宠物")
    schedule_type = Column(String(20), nullable=False, comment="体外驱虫/体内驱虫/疫苗/体检/自定义")
    title = Column(String(100), default="")
    interval_days = Column(Integer, nullable=False, comment="间隔天数")
    last_done_at = Column(DateTime, nullable=True, comment="上次完成时间")
    note = Column(String(200), default="")
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")


# ===== 用户评价/评论 =====
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False, comment="评分 1-5")
    content = Column(Text, default="", comment="评论内容")
    pet_type = Column(String(20), default="", comment="宠物类型：猫/狗")
    pet_age = Column(String(20), default="", comment="宠物年龄")
    is_anonymous = Column(Integer, default=0, comment="是否匿名")
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    product = relationship("Product")


# ===== 宠物档案 =====
class PetProfile(Base):
    __tablename__ = "pet_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String(50), nullable=False)
    breed_id = Column(Integer, ForeignKey("pet_breeds.id"), nullable=True)
    age = Column(String(20), default="")
    gender = Column(String(10), default="")
    weight = Column(Float, nullable=True)
    avatar_url = Column(String(500), default="")
    birthday = Column(Date, nullable=True)  # 生日，用于智能提醒计算
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    breed = relationship("PetBreed")
