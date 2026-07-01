"""京东爬虫 — 抓取宠物食品/药品/保健品真实数据"""
import json
import re
import logging
from urllib.parse import quote
from bs4 import BeautifulSoup
from app.crawler.base import BaseCrawler

logger = logging.getLogger("crawler.jd")


class JDCrawler(BaseCrawler):
    """京东商品搜索 + 详情页爬虫"""

    SOURCE = "京东"
    BASE_URL = "https://search.jd.com/Search"
    DETAIL_URL = "https://item.jd.com/{sku_id}.html"
    # 京东搜索 API（移动端 H5，更稳定）
    SEARCH_API = "https://search.jd.com/Search"

    # 宠物产品搜索关键词
    SEARCH_KEYWORDS = [
        "猫粮", "狗粮", "猫零食", "狗零食",
        "宠物驱虫", "宠物疫苗", "宠物益生菌",
        "宠物营养膏", "宠物关节", "宠物美毛",
    ]

    def get_source_name(self) -> str:
        return self.SOURCE

    async def search_products(self, keyword: str, max_pages: int = 3) -> list[dict]:
        """搜索京东商品列表"""
        products = []

        for page in range(1, max_pages + 1):
            logger.info(f"[JD] 搜索 '{keyword}' 第{page}页")

            params = {
                "keyword": keyword,
                "enc": "utf-8",
                "page": page * 2 - 1,  # 京东翻页: 1,3,5...
                "s": (page - 1) * 60 + 1,
                "click": 0,
            }

            headers = {
                "Referer": "https://www.jd.com/",
            }

            resp = await self.fetch(
                self.SEARCH_API,
                headers=headers,
                params=params,
            )

            if not resp:
                logger.warning(f"[JD] 搜索页请求失败: {keyword} p{page}")
                continue

            # 解析搜索结果 HTML
            page_products = self._parse_search_page(resp.text, keyword)
            products.extend(page_products)
            logger.info(f"[JD] 第{page}页解析到 {len(page_products)} 个商品")

            if len(page_products) == 0:
                logger.info(f"[JD] 第{page}页无结果，停止翻页")
                break

        return products

    def _parse_search_page(self, html: str, keyword: str) -> list[dict]:
        """解析京东搜索结果页"""
        soup = BeautifulSoup(html, "lxml")
        products = []

        # 京东搜索结果在 <li class="gl-item"> 中
        items = soup.select("li.gl-item")
        if not items:
            # 备用选择器
            items = soup.select("div.gl-i-wrap")

        for item in items:
            try:
                product = self._parse_search_item(item, keyword)
                if product:
                    products.append(product)
            except Exception as e:
                logger.debug(f"[JD] 解析商品项失败: {e}")
                continue

        return products

    def _parse_search_item(self, item, keyword: str) -> dict:
        """解析单个搜索结果项"""
        result = {"source": self.SOURCE, "keyword": keyword}

        # 商品名
        name_el = item.select_one("div.p-name a em") or item.select_one("div.p-name a")
        if not name_el:
            return None
        result["name"] = name_el.get_text(strip=True)

        # 商品链接 & SKU ID
        link_el = item.select_one("div.p-name a")
        if link_el:
            href = link_el.get("href", "")
            if href.startswith("//"):
                href = "https:" + href
            result["url"] = href
            # 提取 SKU ID
            sku_match = re.search(r"(\d{6,12})\.html", href)
            if sku_match:
                result["sku_id"] = sku_match.group(1)

        # 价格
        price_el = item.select_one("div.p-price strong i") or item.select_one("div.p-price i")
        if price_el:
            result["price"] = price_el.get_text(strip=True)

        # 品牌
        brand_el = item.select_one("div.p-shop a") or item.select_one("div.p-shopnum a")
        if brand_el:
            result["shop"] = brand_el.get_text(strip=True)

        # 评论数
        comment_el = item.select_one("div.p-commit strong a")
        if comment_el:
            result["comment_count"] = comment_el.get_text(strip=True)

        # 图片
        img_el = item.select_one("div.p-img img") or item.select_one("img")
        if img_el:
            img_src = img_el.get("data-lazy-img") or img_el.get("src", "")
            if img_src.startswith("//"):
                img_src = "https:" + img_src
            result["image_url"] = img_src

        # 必须有名字才算有效
        if not result.get("name"):
            return None

        return result

    async def get_product_detail(self, sku_id: str) -> dict:
        """获取京东商品详情页"""
        url = self.DETAIL_URL.format(sku_id=sku_id)
        logger.info(f"[JD] 获取详情: {url}")

        resp = await self.fetch(url, referer="https://search.jd.com/")
        if not resp:
            return {}

        detail = {"sku_id": sku_id, "source": self.SOURCE}
        html = resp.text
        soup = BeautifulSoup(html, "lxml")

        # 商品名称
        title_el = soup.select_one("div.sku-name") or soup.select_one("h1.title")
        if title_el:
            detail["name"] = title_el.get_text(strip=True)

        # 品牌
        brand_el = soup.select_one("div.p-parameter-list li a") or soup.select_one("#parameter-brand li a")
        if brand_el:
            detail["brand"] = brand_el.get_text(strip=True)

        # 尝试从页面中提取 JSON 数据（京东经常把数据放在 script 标签中）
        detail["ingredients_text"] = self._extract_ingredients(html)
        detail["description"] = self._extract_description(soup)
        detail["specs"] = self._extract_specs(soup)

        # 商品参数（通常在页面的参数区域）
        detail["params"] = self._extract_params(soup)

        return detail

    def _extract_ingredients(self, html: str) -> str:
        """从详情页 HTML 提取配料表/成分信息"""
        # 方式1：从商品参数 JSON 中查找
        patterns = [
            r'"配料[表成]?[：:]"?\s*"([^"]+)"',
            r'"成分[表]?[：:]"?\s*"([^"]+)"',
            r'"原料[组成]?[：:]"?\s*"([^"]+)"',
            r'"主要成分[：:]"?\s*"([^"]+)"',
            r'"配方[：:]"?\s*"([^"]+)"',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1).strip()

        # 方式2：从详情描述中查找
        soup = BeautifulSoup(html, "lxml")
        detail_divs = soup.select("div.detail-content img, div.J-detail-content img")
        # 详情页图片中通常包含配料表，但需要 OCR（这里先跳过图片解析）

        # 方式3：从参数列表中查找
        param_items = soup.select("ul.p-parameter-list li")
        for item in param_items:
            text = item.get_text(strip=True)
            if any(kw in text for kw in ["配料", "成分", "原料", "配方"]):
                # 提取冒号后面的内容
                parts = re.split(r"[：:]", text, maxsplit=1)
                if len(parts) > 1:
                    return parts[1].strip()

        return ""

    def _extract_description(self, soup) -> str:
        """提取商品描述"""
        desc_parts = []

        # 副标题/卖点
        subtitle_el = soup.select_one("div.news") or soup.select_one("p.p-bfc")
        if subtitle_el:
            desc_parts.append(subtitle_el.get_text(strip=True))

        # 促销信息
        promo_el = soup.select_one("div.summary-price-wrap")
        if promo_el:
            text = promo_el.get_text(strip=True)
            if text:
                desc_parts.append(f"价格信息: {text}")

        return " | ".join(desc_parts)

    def _extract_specs(self, soup) -> dict:
        """提取规格信息"""
        specs = {}
        spec_items = soup.select("ul.p-parameter-list li")
        for item in spec_items:
            text = item.get_text(strip=True)
            parts = re.split(r"[：:]", text, maxsplit=1)
            if len(parts) == 2:
                specs[parts[0].strip()] = parts[1].strip()
        return specs

    def _extract_params(self, soup) -> dict:
        """提取商品参数表格"""
        params = {}
        tables = soup.select("table.Ptable, table.p-table")
        for table in tables:
            rows = table.select("tr")
            for row in rows:
                cells = row.select("td, th")
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        params[key] = value
        return params

    async def crawl_category(self, keyword: str, max_pages: int = 2, fetch_details: bool = False) -> list[dict]:
        """完整爬取流程：搜索 → (可选)获取详情"""
        products = await self.search_products(keyword, max_pages)
        logger.info(f"[JD] '{keyword}' 搜索到 {len(products)} 个商品")

        if fetch_details:
            for i, product in enumerate(products):
                sku_id = product.get("sku_id")
                if sku_id:
                    logger.info(f"[JD] 获取详情 {i+1}/{len(products)}: {product.get('name', '')[:30]}")
                    detail = await self.get_product_detail(sku_id)
                    product.update({k: v for k, v in detail.items() if v})

        return products
