"""淘宝爬虫 — 使用移动端 H5 API 抓取真实数据"""
import re
import json
import logging
from urllib.parse import quote, urlencode
from app.crawler.base import BaseCrawler

logger = logging.getLogger("crawler.taobao")


class TaobaoCrawler(BaseCrawler):
    """淘宝/天猫商品搜索 + 详情页爬虫"""

    SOURCE = "淘宝"
    # 淘宝 H5 搜索 API（移动端，相对稳定）
    SEARCH_URL = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
    # 备用搜索 URL
    SEARCH_URL_ALT = "https://s.taobao.com/search"

    def get_source_name(self) -> str:
        return self.SOURCE

    async def search_products(self, keyword: str, max_pages: int = 3) -> list[dict]:
        """搜索淘宝商品（使用 PC 端搜索页）"""
        products = []

        for page in range(0, max_pages):
            logger.info(f"[TB] 搜索 '{keyword}' 第{page+1}页")

            params = {
                "q": keyword,
                "imgfile": "",
                "js": 1,
                "stats_click": "search_rnoa",
                "sort": "sale-desc",  # 按销量排序
                "initiative_id": "staobaoz_20240101",
                "tab": "all",
                "s": page * 44,  # 淘宝每页 44 个
            }

            headers = {
                "Referer": "https://www.taobao.com/",
            }

            resp = await self.fetch(
                self.SEARCH_URL_ALT,
                headers=headers,
                params=params,
            )

            if not resp:
                logger.warning(f"[TB] 搜索页请求失败: {keyword} p{page+1}")
                continue

            # 解析搜索结果
            page_products = self._parse_search_page(resp.text, keyword)
            products.extend(page_products)
            logger.info(f"[TB] 第{page+1}页解析到 {len(page_products)} 个商品")

            if len(page_products) == 0:
                logger.info(f"[TB] 第{page+1}页无结果，停止翻页")
                break

        return products

    def _parse_search_page(self, html: str, keyword: str) -> list[dict]:
        """解析淘宝搜索结果页"""
        products = []

        # 方式1：从页面中提取 JSON 数据（淘宝常把数据放在 script 标签）
        json_patterns = [
            r'g_page_config\s*=\s*({.*?});',
            r'"rawData"\s*:\s*({.*?})\s*[,}]',
            r'pageData\s*=\s*({.*?});',
        ]

        for pattern in json_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    products.extend(self._parse_json_data(data, keyword))
                    if products:
                        return products
                except json.JSONDecodeError:
                    continue

        # 方式2：从 HTML 中解析（备用）
        products = self._parse_html_items(html, keyword)

        return products

    def _parse_json_data(self, data: dict, keyword: str) -> list[dict]:
        """从 JSON 数据中解析商品列表"""
        products = []

        # 尝试不同的数据路径
        items_paths = [
            lambda d: d.get("mods", {}).get("itemlist", {}).get("data", {}).get("auctions", []),
            lambda d: d.get("data", {}).get("itemList", []),
            lambda d: d.get("items", []),
        ]

        items = []
        for path_fn in items_paths:
            try:
                items = path_fn(data)
                if items:
                    break
            except (KeyError, TypeError, AttributeError):
                continue

        for item in items:
            try:
                product = {
                    "source": self.SOURCE,
                    "keyword": keyword,
                    "name": item.get("raw_title") or item.get("title", ""),
                    "price": str(item.get("view_price", "")),
                    "shop": item.get("nick") or item.get("shopName", ""),
                    "location": item.get("item_loc", ""),
                    "sales": item.get("view_sales", ""),
                    "comment_count": item.get("comment_count", ""),
                    "image_url": item.get("pic_url", ""),
                }

                # 提取 item_id
                item_id = item.get("nid") or item.get("item_id") or item.get("auctionId")
                if item_id:
                    product["item_id"] = str(item_id)
                    product["url"] = f"https://item.taobao.com/item.htm?id={item_id}"

                if product["name"]:
                    products.append(product)

            except Exception as e:
                logger.debug(f"[TB] 解析商品项失败: {e}")
                continue

        return products

    def _parse_html_items(self, html: str, keyword: str) -> list[dict]:
        """从 HTML 中解析商品（备用方案）"""
        from bs4 import BeautifulSoup

        products = []
        soup = BeautifulSoup(html, "lxml")

        # 淘宝搜索结果项
        items = soup.select("div.J_MouserOnverReq, div.item, div[data-category]")
        for item in items:
            try:
                product = {"source": self.SOURCE, "keyword": keyword}

                # 商品名
                title_el = item.select_one("div.title a, div.row-title a, a.J_ClickStat")
                if title_el:
                    product["name"] = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    if "id=" in href:
                        match = re.search(r"id=(\d+)", href)
                        if match:
                            product["item_id"] = match.group(1)
                            product["url"] = f"https://item.taobao.com/item.htm?id={match.group(1)}"

                # 价格
                price_el = item.select_one("strong span, div.price strong")
                if price_el:
                    product["price"] = price_el.get_text(strip=True)

                # 店铺
                shop_el = item.select_one("div.shopname a, div.shop a")
                if shop_el:
                    product["shop"] = shop_el.get_text(strip=True)

                # 图片
                img_el = item.select_one("img")
                if img_el:
                    img_src = img_el.get("data-src") or img_el.get("src", "")
                    if img_src.startswith("//"):
                        img_src = "https:" + img_src
                    product["image_url"] = img_src

                if product.get("name"):
                    products.append(product)

            except Exception as e:
                logger.debug(f"[TB] HTML 解析失败: {e}")
                continue

        return products

    async def get_product_detail(self, item_id: str) -> dict:
        """获取淘宝商品详情页"""
        url = f"https://item.taobao.com/item.htm?id={item_id}"
        logger.info(f"[TB] 获取详情: {url}")

        # 使用移动端页面，更容易解析
        mobile_url = f"https://h5.m.taobao.com/awp/core/detail.htm?id={item_id}"

        resp = await self.fetch(mobile_url, mobile=True, referer="https://s.taobao.com/")
        if not resp:
            return {}

        detail = {"item_id": item_id, "source": self.SOURCE}
        html = resp.text

        # 提取 JSON 数据
        detail.update(self._extract_detail_data(html))

        # 提取配料表
        detail["ingredients_text"] = self._extract_ingredients(html)

        return detail

    def _extract_detail_data(self, html: str) -> dict:
        """从详情页提取商品数据"""
        detail = {}

        # 尝试提取 JSON 数据
        json_patterns = [
            r'g_config\s*=\s*({.*?});',
            r'data-spm-data-args\s*=\s*"({.*?})"',
            r'var\s+_DATA_\s*=\s*({.*?});',
        ]

        for pattern in json_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if "title" in data or "item" in data:
                        item_data = data.get("item", data)
                        detail["name"] = item_data.get("title", "")
                        detail["brand"] = item_data.get("brand", "")
                        break
                except json.JSONDecodeError:
                    continue

        return detail

    def _extract_ingredients(self, html: str) -> str:
        """提取配料表/成分信息"""
        patterns = [
            r'"配料[表成]?[：:]"?\s*"([^"]+)"',
            r'"成分[表]?[：:]"?\s*"([^"]+)"',
            r'"原料[组成]?[：:]"?\s*"([^"]+)"',
            r'"主要成分[：:]"?\s*"([^"]+)"',
            r'"配方[：:]"?\s*"([^"]+)"',
            r'配料[：:]\s*([^\n<]{5,200})',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                text = match.group(1).strip()
                if len(text) > 5:
                    return text

        return ""

    async def crawl_category(self, keyword: str, max_pages: int = 2, fetch_details: bool = False) -> list[dict]:
        """完整爬取流程"""
        products = await self.search_products(keyword, max_pages)
        logger.info(f"[TB] '{keyword}' 搜索到 {len(products)} 个商品")

        if fetch_details:
            for i, product in enumerate(products):
                item_id = product.get("item_id")
                if item_id:
                    logger.info(f"[TB] 获取详情 {i+1}/{len(products)}: {product.get('name', '')[:30]}")
                    detail = await self.get_product_detail(item_id)
                    product.update({k: v for k, v in detail.items() if v})

        return products
