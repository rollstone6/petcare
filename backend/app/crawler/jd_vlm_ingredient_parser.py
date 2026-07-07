"""
京东商品配料表解析器 - 使用多模态 VLM 解析背标图片

核心思路：
1. 抓取商品详情页的所有图片
2. 识别并下载包含配料表的背标图片
3. 使用多模态 VLM（如 Qwen-VL）解析图片内容
4. 结构化提取配料表数据并保存到数据库

作者：AI助手
日期：2026-01-06
"""

import asyncio
import base64
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app import models
from app.models import product_ingredient
from app.database import SessionLocal

logger = logging.getLogger(__name__)


# 复用现有火山引擎 ARK API 配置（与 ai.py 相同）
def _get_ark_config():
    """从 hermes 配置读取 API key"""
    import yaml
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config.get("model", {}).get("api_key", ""), os.getenv("ARK_API_KEY", "")
    except Exception:
        return os.getenv("ARK_API_KEY", "")


# 火山引擎 ARK 多模态端点（兼容 OpenAI 格式）
ARK_VLM_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
# 火山引擎支持的多模态模型（豆包视觉模型）
VLM_MODEL = os.environ.get("PETCARE_VLM_MODEL", "doubao-1-5-vision-pro-250328")


class IngredientExtractor:
    """配料表提取器 - 使用火山引擎多模态 VLM 解析背标图片"""
    
    def __init__(self, api_key: str = None):
        if api_key is None:
            ark_key, env_key = _get_ark_config()
            api_key = ark_key or env_key
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def parse_ingredient_image(self, image_path: Path) -> Optional[dict]:
        """
        使用 VLM 解析配料表图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            结构化的配料表数据，格式：
            {
                "ingredients": ["鸡肉", "鸭肉", "红薯粉", ...],
                "additives": ["山梨酸钾", "牛磺酸", ...],
                "guaranteed_analysis": {
                    "protein": "32%",
                    "fat": "15%",
                    "calcium": "1.2%"
                }
            }
        """
        if not image_path.exists():
            logger.error(f"图片不存在: {image_path}")
            return None
        
        if not self.api_key:
            logger.error("VLM API key 未配置")
            return None
            
        # 读取图片并转换为 base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 根据文件扩展名确定 MIME 类型
        ext = image_path.suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        
        # 构建 VLM 提示词
        prompt = """你是一个严谨的宠物食品数据清洗专家。请仔细阅读这张宠物食品/保健品包装背标图片。

任务要求：
1. 提取出完整的「原料组成/配料表」和「添加剂组成」，严格保持包装袋上的先后顺序（因为顺序代表含量高低）
2. 提取出「成分分析保证值」（如粗蛋白、粗脂肪、钙、总磷的百分比）
3. 不要任何解释说明，严格输出以下 JSON 格式：

{
  "ingredients": ["鸡肉", "鸭肉", "红薯粉"],
  "additives": ["山梨酸钾", "牛磺酸", "轻质碳酸钙"],
  "guaranteed_analysis": {
    "protein": "32%",
    "fat": "15%",
    "calcium": "1.2%"
  }
}

如果某个字段在图片中不存在，请返回空数组或空对象。只返回 JSON，不要包含任何其他文字。"""

        # 构建 OpenAI 兼容格式的请求（火山引擎 ARK 支持）
        payload = {
            "model": VLM_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"正在解析图片: {image_path.name} (模型: {VLM_MODEL})")
            response = await self.client.post(ARK_VLM_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应
            content = result["choices"][0]["message"]["content"]
            
            # 解析 JSON - 清理可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed = json.loads(content)
            logger.info(f"成功解析配料表，包含 {len(parsed.get('ingredients', []))} 种原料")
            return parsed
            
        except httpx.HTTPStatusError as e:
            logger.error(f"VLM API 错误 ({e.response.status_code}): {e.response.text[:200]}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"VLM 返回内容无法解析为 JSON: {content[:200] if 'content' in dir() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"VLM 解析失败: {e}")
            return None


class JDDetailScraper:
    """京东商品详情抓取器 - 专注于提取背标图片"""
    
    def __init__(self):
        self.download_dir = Path("/root/workspace/petcare/data/jd_images")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def scrape_product_images(self, sku_id: str) -> list[Path]:
        """
        抓取商品详情页的所有图片，特别是背标图片
        
        Args:
            sku_id: 京东商品 SKU ID
            
        Returns:
            下载的图片文件路径列表
        """
        logger.info(f"开始抓取商品 {sku_id} 的图片")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            url = f"https://item.jd.com/{sku_id}.html"
            logger.info(f"访问: {url}")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # 滚动页面加载所有图片
                logger.info("滚动页面加载图片...")
                for i in range(10):
                    await page.evaluate(f"window.scrollTo(0, {i * 1000})")
                    await asyncio.sleep(0.5)
                
                # 提取所有图片 URL
                images = await page.evaluate("""
                    () => {
                        const imgs = Array.from(document.querySelectorAll('img'));
                        return imgs.map(img => ({
                            src: img.src || img.dataset.lazyloadSrc || img.dataset.src,
                            alt: img.alt || '',
                            className: img.className || '',
                            parentClass: img.parentElement?.className || ''
                        }));
                    }
                """)
                
                logger.info(f"找到 {len(images)} 张图片")
                
                # 筛选可能的背标图片
                # 背标图片通常在详情区域，且尺寸较大
                candidate_images = []
                for img in images:
                    src = img.get("src", "")
                    if not src or "loading" in src or "logo" in src.lower():
                        continue
                    
                    # 补全 URL
                    if src.startswith("//"):
                        src = "https:" + src
                    
                    # 过滤条件
                    # 1. 排除小图标（通常 < 100px）
                    # 2. 优先选择详情区域的图片
                    alt = img.get("alt", "").lower()
                    parent_class = img.get("parentClass", "").lower()
                    
                    # 关键词匹配
                    is_detail_image = any(kw in alt for kw in ["详情", "背标", "配料", "成分", "标签"])
                    is_detail_area = any(kw in parent_class for kw in ["detail", "content", "description"])
                    
                    if is_detail_image or is_detail_area or "/jfs/" in src:
                        candidate_images.append(src)
                
                # 去重
                candidate_images = list(set(candidate_images))
                logger.info(f"筛选出 {len(candidate_images)} 张候选图片")
                
                # 下载图片
                downloaded = []
                async with httpx.AsyncClient(timeout=30.0) as client:
                    for idx, img_url in enumerate(candidate_images[:20]):  # 最多下载 20 张
                        try:
                            response = await client.get(img_url)
                            response.raise_for_status()
                            
                            # 保存文件
                            ext = ".jpg"
                            if ".png" in img_url:
                                ext = ".png"
                            elif ".webp" in img_url:
                                ext = ".webp"
                                
                            filename = f"{sku_id}_{idx:02d}{ext}"
                            filepath = self.download_dir / filename
                            
                            with open(filepath, "wb") as f:
                                f.write(response.content)
                                
                            logger.info(f"下载: {filename} ({len(response.content)} bytes)")
                            downloaded.append(filepath)
                            
                        except Exception as e:
                            logger.warning(f"下载失败 {img_url}: {e}")
                            continue
                
                return downloaded
                
            except Exception as e:
                logger.error(f"抓取失败: {e}")
                return []
            finally:
                await browser.close()


class IngredientProcessor:
    """配料表处理器 - 整合抓取、解析、存储流程"""
    
    def __init__(self, vlm_api_key: str = None):
        self.scraper = JDDetailScraper()
        self.extractor = IngredientExtractor(vlm_api_key)
        
    async def process_product(self, sku_id: str) -> Optional[dict]:
        """
        处理单个商品：抓取图片 → VLM 解析 → 返回结构化数据
        
        Args:
            sku_id: 京东商品 SKU ID
            
        Returns:
            结构化的配料表数据
        """
        logger.info(f"处理商品 {sku_id}")
        
        # 1. 抓取图片
        images = await self.scraper.scrape_product_images(sku_id)
        if not images:
            logger.warning(f"商品 {sku_id} 未找到图片")
            return None
            
        # 2. 尝试解析每张图片
        for img_path in images:
            result = await self.extractor.parse_ingredient_image(img_path)
            if result and result.get("ingredients"):
                logger.info(f"成功从 {img_path.name} 解析出配料表")
                result["_source_image"] = str(img_path)
                return result
                
        logger.warning(f"商品 {sku_id} 的所有图片均未解析出配料表")
        return None
        
    def save_to_database(self, product_id: int, ingredient_data: dict):
        """
        将解析的配料表保存到数据库
        
        Args:
            product_id: 产品 ID
            ingredient_data: VLM 解析的配料表数据
        """
        db = SessionLocal()
        try:
            # 更新产品配料文本
            product = db.query(models.Product).get(product_id)
            if not product:
                logger.error(f"产品 {product_id} 不存在")
                return
                
            # 构建配料文本
            ingredients = ingredient_data.get("ingredients", [])
            additives = ingredient_data.get("additives", [])
            
            full_text = "原料组成：" + "、".join(ingredients)
            if additives:
                full_text += " | 添加剂组成：" + "、".join(additives)
                
            # 添加配料文本字段（如果 Product 模型有的话）
            # product.ingredients_text = full_text
            
            # 获取已存在的成分关联
            from sqlalchemy import select
            existing_stmt = select(product_ingredient.c.ingredient_id).where(
                product_ingredient.c.product_id == product_id
            )
            existing_ingredients = [row[0] for row in db.execute(existing_stmt).all()]
            
            for idx, name in enumerate(ingredients):
                # 查找或创建成分
                ingredient = db.query(models.Ingredient).filter(
                    models.Ingredient.name == name
                ).first()
                
                if not ingredient:
                    # 创建新成分（默认安全评分 3）
                    ingredient = models.Ingredient(
                        name=name,
                        category="原料",
                        safety_level=3,
                        function="",
                        description=""
                    )
                    db.add(ingredient)
                    db.flush()
                    logger.info(f"创建新成分: {name}")
                
                # 检查是否已存在关联
                if ingredient.id not in existing_ingredients:
                    # 创建产品-成分关联
                    db.execute(
                        product_ingredient.insert().values(
                            product_id=product_id,
                            ingredient_id=ingredient.id,
                            is_active=0,
                            sort_order=idx
                        )
                    )
            
            db.commit()
            logger.info(f"已保存配料表到产品 {product_id}，共 {len(ingredients)} 种原料")
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存失败: {e}")
            raise
        finally:
            db.close()


async def main():
    """主函数 - 示例用法"""
    import sys
    
    # API key 自动从 ~/.hermes/config.yaml 或 ARK_API_KEY 环境变量加载
    # 也可以通过环境变量手动指定：export PETCARE_VLM_API_KEY=xxx
    
    # 获取 SKU ID
    sku_id = sys.argv[1] if len(sys.argv) > 1 else "100012043978"  # 示例 SKU
    
    # 处理商品
    processor = IngredientProcessor()
    result = await processor.process_product(sku_id)
    
    if result:
        print("\n=== 解析结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 如果有 product_id，可以保存到数据库
        # product_id = 123
        # processor.save_to_database(product_id, result)
    else:
        print("解析失败")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )
    asyncio.run(main())
