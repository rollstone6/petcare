"""从 Open Pet Food Facts 导入宠物食品数据"""
import urllib.request, json, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app import models
from app.scoring import calculate_product_score

db = SessionLocal()

BASE = "https://world.openpetfoodfacts.org/api/v2"
PAGE_SIZE = 50
MAX_PRODUCTS = 500

# 品类映射（英文标签 → 中文品类名）
CATEGORY_MAP = {
    "dog-food": ("狗粮", "食品"),
    "cat-food": ("猫粮", "食品"),
    "dog-treats": ("狗零食", "食品"),
    "cat-treats": ("猫零食", "食品"),
    "dog-dietetic": ("处方粮", "食品"),
    "cat-dietetic": ("处方粮", "食品"),
    "pet-food": ("综合食品", "食品"),
}

# 安全等级估算（基于成分关键词）
SAFE_KEYWORDS = ["chicken", "turkey", "salmon", "lamb", "beef", "rice", "pea", "lentil", "potato", "sweet potato", "blueberry", "cranberry", "pumpkin", "spinach", "carrot", "apple", "fish oil", "salmon oil", "taurine", "vitamin", "mineral", "probiotic", "glucosamine", "chondroitin"]
CAUTION_KEYWORDS = ["corn", "wheat", "soy", "by-product", "meal", "gluten", "brewers rice", "cellulose", "sugar", "salt", "carrageenan", "artificial", "preservative", "color", "flavor", "rendered", "animal fat", "menadione", "ethoxyquin", "bha", "bht", "propylene glycol"]

def estimate_safety(ingredients_text):
    if not ingredients_text:
        return 3.0
    text = ingredients_text.lower()
    safe_count = sum(1 for kw in SAFE_KEYWORDS if kw in text)
    caution_count = sum(1 for kw in CAUTION_KEYWORDS if kw in text)
    total = safe_count + caution_count
    if total == 0:
        return 3.0
    return round(3.0 + (safe_count - caution_count) / max(total, 1) * 2, 1)

def get_or_create_brand(name):
    if not name:
        return None
    name = name.strip()[:100]
    brand = db.query(models.Brand).filter(models.Brand.name == name).first()
    if not brand:
        brand = models.Brand(name=name, country="", description=f"来自 Open Pet Food Facts")
        db.add(brand)
        db.flush()
    return brand

def get_or_create_category(cat_name, cat_type):
    if not cat_name:
        return None
    cat = db.query(models.Category).filter(models.Category.name == cat_name).first()
    if not cat:
        cat = models.Category(name=cat_name, type=cat_type)
        db.add(cat)
        db.flush()
    return cat

def get_or_create_ingredient(name):
    if not name or len(name) < 2:
        return None
    name = name.strip()[:200]
    ing = db.query(models.Ingredient).filter(models.Ingredient.name == name).first()
    if not ing:
        ing = models.Ingredient(name=name, safety_level=3, category="食品成分")
        db.add(ing)
        db.flush()
    return ing

def parse_ingredients(ingredients_text):
    """解析成分文本为列表"""
    if not ingredients_text:
        return []
    # 移除括号内容
    import re
    text = re.sub(r'\([^)]*\)', '', ingredients_text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    # 按逗号分割
    parts = [p.strip().lower() for p in text.split(',')]
    # 清理
    result = []
    for p in parts:
        p = re.sub(r'\d+\.?\d*%?', '', p).strip()
        p = re.sub(r'^and\s+', '', p)
        if len(p) > 2 and not p.startswith(':'):
            result.append(p)
    return result[:20]  # 最多 20 个成分

# 按品类分别拉取
categories_to_fetch = [
    ("en:dog-food", "狗粮", "食品"),
    ("en:cat-food", "猫粮", "食品"),
    ("en:dog-treats", "狗零食", "食品"),
    ("en:cat-treats", "猫零食", "食品"),
]

total_imported = 0
total_ingredients = 0

for cat_tag, cat_name, cat_type in categories_to_fetch:
    print(f"\n📦 拉取品类: {cat_name} ({cat_tag})")
    category = get_or_create_category(cat_name, cat_type)
    
    page = 1
    imported = 0
    
    while imported < 100:  # 每个品类最多 100 个
        url = f"{BASE}/search?categories_tags={cat_tag}&page_size={PAGE_SIZE}&page={page}&fields=product_name,brands,ingredients_text,nutriments,additives_tags,image_url"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PetCare/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"  ⚠️ 第{page}页失败: {e}")
            break
        
        products = data.get('products', [])
        if not products:
            break
        
        for p in products:
            name = (p.get('product_name') or '').strip()
            if not name or len(name) < 3:
                continue
            
            # 检查是否已存在
            existing = db.query(models.Product).filter(models.Product.name == name).first()
            if existing:
                continue
            
            brand_name = (p.get('brands') or '').split(',')[0].strip()
            brand = get_or_create_brand(brand_name)
            
            ingredients_text = p.get('ingredients_text', '')
            safety = estimate_safety(ingredients_text)
            
            product = models.Product(
                name=name[:200],
                brand_id=brand.id if brand else None,
                category_id=category.id if category else None,
                type=cat_type,
                description=f"来自 Open Pet Food Facts 数据库",
                safety_score=safety,
                image_url=p.get('image_url', '') or '',
                suitable_species="狗" if "dog" in cat_tag else "猫",
            )
            db.add(product)
            db.flush()
            
            # 解析并关联成分
            ingredients = parse_ingredients(ingredients_text)
            seen_ings = set()
            for idx, ing_name in enumerate(ingredients):
                if ing_name in seen_ings:
                    continue
                seen_ings.add(ing_name)
                ing = get_or_create_ingredient(ing_name)
                if ing:
                    # 检查是否已关联
                    existing_pi = db.query(models.product_ingredient).filter(
                        models.product_ingredient.c.product_id == product.id,
                        models.product_ingredient.c.ingredient_id == ing.id,
                    ).first()
                    if not existing_pi:
                        db.execute(models.product_ingredient.insert().values(
                            product_id=product.id,
                            ingredient_id=ing.id,
                            sort_order=idx + 1,
                            is_active=1 if idx < 5 else 0,
                        ))
                        total_ingredients += 1
            
            imported += 1
            total_imported += 1
            
            if imported % 20 == 0:
                db.commit()
                print(f"  ✅ 已导入 {imported} 款 ({cat_name})")
        
        db.commit()
        print(f"  📄 第{page}页完成，品类累计 {imported} 款")
        page += 1
        time.sleep(1)
        
        if total_imported >= MAX_PRODUCTS:
            break
    
    print(f"  🎉 {cat_name} 完成: {imported} 款")

db.commit()

# 统计
brand_count = db.query(models.Brand).count()
ing_count = db.query(models.Ingredient).count()
prod_count = db.query(models.Product).count()

print(f"\n{'='*50}")
print(f"📊 导入完成!")
print(f"  新产品: {total_imported} 款")
print(f"  新成分: {ing_count} 种")
print(f"  品牌总数: {brand_count}")
print(f"  产品总数: {prod_count}")
print(f"{'='*50}")

db.close()
