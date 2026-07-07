"""京东店铺爬虫 — 使用 browser-use AI 自动化抓取"""
import asyncio
import json
import logging
from browser_use import Agent
from langchain_openai import ChatOpenAI
from app.database import SessionLocal
from app import models

logger = logging.getLogger("crawler.jd_browseruse")


async def scrape_jd_store_with_browseruse(store_name: str = "浙大宠物医院") -> list[dict]:
    """
    使用 browser-use 抓取京东店铺的所有产品
    
    Args:
        store_name: 店铺名称
        
    Returns:
        产品列表 [{name, price, brand, ingredients_text, sku_id, image_url, ...}]
    """
    
    # 初始化 LLM (使用 OpenAI)
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
    )
    
    # 创建 Agent 任务
    task = f"""
    访问京东网站 (jd.com)，搜索店铺 "{store_name}"，进入该店铺的商品列表页面。
    
    任务要求：
    1. 找到并进入店铺 "{store_name}"
    2. 浏览店铺的所有商品列表（如果有分页，翻页浏览）
    3. 对于每个商品，提取以下信息：
       - 商品名称 (name)
       - 价格 (price)
       - 品牌 (brand)
       - SKU ID (sku_id)
       - 商品链接 (url)
       - 图片链接 (image_url)
       - 评论数 (comment_count)
    4. 点击每个商品进入详情页，提取：
       - 配料表/成分 (ingredients_text)
       - 批准文号 (approval_number)
       - 适用物种 (suitable_species)
       - 使用说明 (usage_guide)
    5. 将所有商品信息整理成 JSON 格式返回
    
    注意事项：
    - 如果遇到验证码，尝试完成验证
    - 如果页面加载慢，等待几秒钟
    - 尽量多抓取商品数据
    - 确保数据完整准确
    """
    
    logger.info(f"开始抓取店铺: {store_name}")
    
    # 创建 Agent
    agent = Agent(
        task=task,
        llm=llm,
        max_steps=100,  # 最多执行100步
    )
    
    # 运行 Agent
    result = await agent.run()
    
    # 解析结果
    products = []
    try:
        # browser-use 返回的结果中包含 AI 的执行摘要和数据
        # 我们需要从结果中提取商品数据
        result_text = str(result)
        logger.info(f"Agent 执行完成，结果长度: {len(result_text)}")
        
        # 尝试从结果中解析 JSON 数据
        # browser-use 会在浏览器中执行操作，我们可以通过历史记录获取数据
        history = agent.history()
        
        for step in history:
            if hasattr(step, 'result') and step.result:
                # 检查是否包含商品数据
                if isinstance(step.result, str) and ('商品名称' in step.result or 'sku_id' in step.result):
                    try:
                        # 尝试解析 JSON
                        data = json.loads(step.result)
                        if isinstance(data, list):
                            products.extend(data)
                        elif isinstance(data, dict):
                            products.append(data)
                    except json.JSONDecodeError:
                        pass
        
        logger.info(f"共抓取 {len(products)} 个产品")
        
    except Exception as e:
        logger.error(f"解析结果失败: {e}")
    
    return products


def save_products_to_db(products: list[dict]):
    """将抓取的产品保存到数据库"""
    db = SessionLocal()
    
    saved_count = 0
    for product_data in products:
        try:
            # 检查是否已存在
            sku_id = product_data.get('sku_id')
            if sku_id:
                existing = db.query(models.Product).filter(
                    models.Product.approval_number == f"JD:{sku_id}"
                ).first()
                if existing:
                    logger.info(f"产品已存在，跳过: {product_data.get('name')}")
                    continue
            
            # 查找或创建品牌
            brand_name = product_data.get('brand', '')
            brand = None
            if brand_name:
                brand = db.query(models.Brand).filter(models.Brand.name == brand_name).first()
                if not brand:
                    brand = models.Brand(name=brand_name)
                    db.add(brand)
                    db.flush()
            
            # 查找或创建品类（根据商品名称推断）
            category = None
            name = product_data.get('name', '')
            if '粮' in name:
                category = db.query(models.Category).filter(models.Category.name.like('%粮%')).first()
            elif '药' in name or '驱虫' in name:
                category = db.query(models.Category).filter(models.Category.name.like('%药%')).first()
            
            # 创建产品
            product = models.Product(
                name=product_data.get('name', ''),
                brand_id=brand.id if brand else None,
                category_id=category.id if category else None,
                type='食品' if '粮' in name else '药品',
                description=product_data.get('description', ''),
                approval_number=f"JD:{sku_id}" if sku_id else '',
                safety_score=3.0,  # 默认评分
                image_url=product_data.get('image_url', ''),
                usage_guide=product_data.get('usage_guide', ''),
                suitable_species=product_data.get('suitable_species', '猫狗'),
            )
            db.add(product)
            db.flush()
            
            # 处理成分
            ingredients_text = product_data.get('ingredients_text', '')
            if ingredients_text:
                ingredient_names = [i.strip() for i in ingredients_text.replace(',', '、').split('、')]
                for ing_name in ingredient_names:
                    if ing_name:
                        ingredient = db.query(models.Ingredient).filter(
                            models.Ingredient.name.like(f'%{ing_name}%')
                        ).first()
                        if ingredient:
                            product.ingredients.append(ingredient)
            
            saved_count += 1
            logger.info(f"保存产品: {product.name}")
            
        except Exception as e:
            logger.error(f"保存产品失败: {e}")
            db.rollback()
    
    db.commit()
    db.close()
    
    logger.info(f"成功保存 {saved_count} 个产品")
    return saved_count


async def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 抓取数据
    products = await scrape_jd_store_with_browseruse("浙大宠物医院")
    
    # 保存到文件
    if products:
        with open('/tmp/jd_zheda_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存原始数据到 /tmp/jd_zheda_products.json")
        
        # 保存到数据库
        save_products_to_db(products)
    
    print(f"\n抓取完成！共获取 {len(products)} 个产品")


if __name__ == "__main__":
    asyncio.run(main())
