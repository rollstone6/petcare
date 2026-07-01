"""数据处理器 — 清洗、成分匹配、入库"""
import re
import logging
from typing import Optional
from app.database import SessionLocal
from app import models

logger = logging.getLogger("crawler.processor")


class DataProcessor:
    """处理爬虫抓取的原始数据，清洗、匹配成分、写入数据库"""

    # 宠物食品/药品关键词过滤（只保留相关产品）
    PET_KEYWORDS = [
        "猫", "狗", "犬", "宠物", "猫咪", "狗狗", "幼犬", "幼猫",
        "成犬", "成猫", "全价", "主粮", "猫粮", "狗粮", "罐头",
        "冻干", "营养膏", "益生菌", "驱虫", "疫苗", "化毛",
        "美毛", "关节", "卵磷脂", "鱼油", "钙片", "维生素",
    ]

    # 排除词（非宠物产品）
    EXCLUDE_KEYWORDS = [
        "人用", "儿童", "婴儿", "成人", "男士", "女士",
        "汽车", "手机", "电脑", "键盘", "鼠标",
    ]

    # 产品类型映射
    TYPE_MAPPING = {
        "猫粮": ("食品", "猫粮"),
        "狗粮": ("食品", "狗粮"),
        "猫零食": ("食品", "猫零食"),
        "狗零食": ("食品", "狗零食"),
        "冻干": ("食品", "猫零食"),
        "罐头": ("食品", "猫零食"),
        "处方粮": ("食品", "处方粮"),
        "驱虫": ("药品", "驱虫药"),
        "疫苗": ("药品", "疫苗"),
        "益生菌": ("保健品", "益生菌"),
        "营养膏": ("保健品", "营养膏"),
        "化毛膏": ("保健品", "化毛膏"),
        "关节": ("保健品", "关节保护"),
        "美毛": ("保健品", "美毛护肤"),
        "卵磷脂": ("保健品", "美毛护肤"),
        "鱼油": ("保健品", "美毛护肤"),
        "维生素": ("保健品", "综合营养"),
        "钙片": ("保健品", "综合营养"),
    }

    def __init__(self):
        self.db = SessionLocal()
        self._ingredient_cache = {}
        self._brand_cache = {}
        self._category_cache = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def is_pet_product(self, product: dict) -> bool:
        """判断是否为宠物产品"""
        name = product.get("name", "")
        keyword = product.get("keyword", "")

        # 排除非宠物产品
        if any(ex in name for ex in self.EXCLUDE_KEYWORDS):
            return False

        # 搜索关键词本身就是宠物相关
        if any(kw in keyword for kw in ["猫", "狗", "宠物", "犬"]):
            return True

        # 产品名中包含宠物关键词
        return any(kw in name for kw in self.PET_KEYWORDS)

    def classify_product(self, product: dict) -> tuple[str, str]:
        """分类产品：返回 (type, category_name)"""
        name = product.get("name", "") + " " + product.get("keyword", "")

        # 按优先级匹配
        priority_order = [
            "驱虫", "疫苗", "处方粮",
            "猫粮", "狗粮", "猫零食", "狗零食", "冻干", "罐头",
            "益生菌", "营养膏", "化毛膏", "关节", "美毛", "卵磷脂",
            "鱼油", "维生素", "钙片",
        ]

        for key in priority_order:
            if key in name:
                return self.TYPE_MAPPING.get(key, ("食品", "猫粮"))

        # 默认分类
        if "猫" in name:
            return ("食品", "猫粮")
        elif "狗" in name or "犬" in name:
            return ("食品", "狗粮")

        return ("食品", "猫粮")

    def get_or_create_brand(self, brand_name: str, shop_name: str = "") -> models.Brand:
        """获取或创建品牌"""
        if not brand_name:
            brand_name = shop_name if shop_name else "其他品牌"

        # 清理品牌名
        brand_name = brand_name.strip()

        if brand_name in self._brand_cache:
            return self._brand_cache[brand_name]

        brand = self.db.query(models.Brand).filter(
            models.Brand.name == brand_name
        ).first()

        if not brand:
            # 尝试模糊匹配
            brand = self.db.query(models.Brand).filter(
                models.Brand.name.like(f"%{brand_name[:4]}%")
            ).first()

        if not brand:
            brand = models.Brand(name=brand_name, country="", description="")
            self.db.add(brand)
            self.db.flush()
            logger.info(f"创建新品牌: {brand_name}")

        self._brand_cache[brand_name] = brand
        return brand

    def get_category(self, category_name: str) -> Optional[models.Category]:
        """获取品类"""
        if category_name in self._category_cache:
            return self._category_cache[category_name]

        category = self.db.query(models.Category).filter(
            models.Category.name == category_name
        ).first()

        self._category_cache[category_name] = category
        return category

    def parse_ingredients(self, text: str) -> list[str]:
        """从配料文本中解析成分列表"""
        if not text:
            return []

        # 清理文本
        text = text.replace("；", "、").replace("，", "、").replace(",", "、")
        text = text.replace("(", "（").replace(")", "）")

        # 分割
        parts = [p.strip() for p in text.split("、") if p.strip()]

        ingredients = []
        for part in parts:
            # 跳过过短的
            if len(part) < 2:
                continue
            # 去掉序号前缀
            part = re.sub(r"^\d+[.、]\s*", "", part)
            # 去掉百分比
            part = re.sub(r"[\(（]?\d+\.?\d*%[\)）]?", "", part)
            part = part.strip()

            if part and len(part) >= 2:
                ingredients.append(part)

        return ingredients

    def match_ingredients(self, ingredient_names: list[str]) -> list[models.Ingredient]:
        """匹配数据库中的成分"""
        matched = []
        seen_ids = set()

        for name in ingredient_names:
            if not name:
                continue

            # 精确匹配
            ingredient = self.db.query(models.Ingredient).filter(
                models.Ingredient.name == name
            ).first()

            # 模糊匹配
            if not ingredient:
                ingredient = self.db.query(models.Ingredient).filter(
                    models.Ingredient.name.like(f"%{name[:4]}%")
                ).first()

            # 别名匹配
            if not ingredient and len(name) >= 3:
                ingredient = self.db.query(models.Ingredient).filter(
                    models.Ingredient.alias.like(f"%{name}%")
                ).first()

            if ingredient and ingredient.id not in seen_ids:
                matched.append(ingredient)
                seen_ids.add(ingredient.id)

        return matched

    def process_product(self, raw: dict) -> Optional[models.Product]:
        """处理单个产品数据并入库"""
        # 过滤非宠物产品
        if not self.is_pet_product(raw):
            return None

        name = raw.get("name", "").strip()
        if not name or len(name) < 4:
            return None

        # 检查是否已存在
        existing = self.db.query(models.Product).filter(
            models.Product.name == name
        ).first()
        if existing:
            logger.debug(f"产品已存在，跳过: {name[:30]}")
            return None

        # 分类
        product_type, category_name = self.classify_product(raw)

        # 品牌
        brand_name = raw.get("brand", "")
        shop_name = raw.get("shop", "")
        brand = self.get_or_create_brand(brand_name, shop_name)

        # 品类
        category = self.get_category(category_name)

        # 创建产品
        product = models.Product(
            name=name,
            brand_id=brand.id if brand else None,
            category_id=category.id if category else None,
            type=product_type,
            description=raw.get("description", ""),
            approval_number="",
            safety_score=3.5,  # 默认安全评分，后续可优化
            image_url=raw.get("image_url", ""),
            usage_guide="",
            suitable_species="猫狗",
        )

        # 判断适用物种
        if "猫" in name and "狗" not in name and "犬" not in name:
            product.suitable_species = "猫"
        elif ("狗" in name or "犬" in name) and "猫" not in name:
            product.suitable_species = "狗"

        self.db.add(product)
        self.db.flush()

        # 匹配成分
        ingredients_text = raw.get("ingredients_text", "")
        if ingredients_text:
            ingredient_names = self.parse_ingredients(ingredients_text)
            matched = self.match_ingredients(ingredient_names)
            for i, ing in enumerate(matched):
                product.ingredients.append(ing)
                logger.debug(f"  匹配成分: {ing.name}")

        logger.info(f"✅ 入库: {name[:40]} | {brand.name} | {category_name}")
        return product

    def process_batch(self, raw_products: list[dict]) -> dict:
        """批量处理产品数据"""
        stats = {"total": 0, "added": 0, "skipped": 0, "failed": 0}

        for raw in raw_products:
            stats["total"] += 1
            try:
                product = self.process_product(raw)
                if product:
                    stats["added"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"处理产品失败: {raw.get('name', 'unknown')[:30]} - {e}")

        # 提交所有更改
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"数据库提交失败: {e}")
            self.db.rollback()
            stats["failed"] += stats["added"]
            stats["added"] = 0

        return stats
