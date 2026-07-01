"""京东店铺爬虫 — 用 Playwright 抓取指定店铺的所有产品"""
import asyncio
import json
import re
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger("crawler.jd_store")


async def scrape_jd_store(store_url_or_name: str, headless: bool = True) -> list[dict]:
    """
    抓取京东店铺的所有产品列表。
    store_url_or_name: 店铺URL或店铺名称
    返回产品列表 [{name, price, sku_id, url, image_url, brand, shop, ...}]
    """
    products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        page = await context.new_page()

        # 判断是URL还是店铺名
        if store_url_or_name.startswith("http"):
            target_url = store_url_or_name
        else:
            # 先通过搜索找到店铺
            target_url = await _find_store_by_name(page, store_url_or_name)

        if not target_url:
            logger.error(f"无法找到店铺: {store_url_or_name}")
            await browser.close()
            return []

        logger.info(f"店铺URL: {target_url}")

        # 访问店铺商品列表页
        products = await _scrape_store_products(page, target_url)

        await browser.close()

    return products


async def _find_store_by_name(page, name: str) -> str | None:
    """通过店铺名称搜索，找到店铺页面URL"""
    search_url = f"https://search.jd.com/Search?keyword={name}&enc=utf-8&wq={name}"

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # 在搜索结果中找到店铺链接
        # 京东搜索结果中通常有店铺链接
        content = await page.content()

        # 尝试从页面中提取 mall.jd.com 或 shop.jd.com 链接
        shop_patterns = [
            r'(https?://mall\.jd\.com/index-\d+\.html)',
            r'(https?://shop\.jd\.com/\d+)',
            r'(//mall\.jd\.com/index-\d+\.html)',
            r'(//shop\.jd\.com/\d+)',
        ]

        for pattern in shop_patterns:
            match = re.search(pattern, content)
            if match:
                url = match.group(1)
                if url.startswith("//"):
                    url = "https:" + url
                return url

        # 备选：尝试从搜索结果中找到店铺名对应的链接
        links = await page.query_selector_all("a")
        for link in links:
            text = await link.inner_text()
            if name in text or "专营店" in text:
                href = await link.get_attribute("href")
                if href and ("mall.jd.com" in href or "shop.jd.com" in href):
                    if href.startswith("//"):
                        href = "https:" + href
                    return href

        # 再尝试通过店铺搜索API
        logger.info("从搜索结果未找到店铺链接，尝试店铺搜索...")
        shop_search_url = f"https://shopsearch.jd.com/search?keyword={name}&enc=utf-8"
        await page.goto(shop_search_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        for pattern in shop_patterns:
            match = re.search(pattern, content)
            if match:
                url = match.group(1)
                if url.startswith("//"):
                    url = "https:" + url
                return url

    except Exception as e:
        logger.error(f"搜索店铺失败: {e}")

    return None


async def _scrape_store_products(page, store_url: str) -> list[dict]:
    """抓取店铺内所有产品"""
    products = []

    # 构造店铺商品列表URL
    # mall.jd.com/index-XXXXX.html → 商品列表通常在 mall.jd.com/view_search-XXXXX-0-1-24-1.html
    # 或者直接访问店铺搜索页

    # 提取 shopId
    shop_id_match = re.search(r'index-(\d+)', store_url)
    if not shop_id_match:
        shop_id_match = re.search(r'shop\.jd\.com/(\d+)', store_url)

    if shop_id_match:
        shop_id = shop_id_match.group(1)
        # 店铺商品列表API
        list_url = f"https://mall.jd.com/view_search-{shop_id}-0-1-24-1.html"
    else:
        list_url = store_url

    logger.info(f"访问店铺商品列表: {list_url}")

    page_num = 1
    max_pages = 20  # 安全限制

    while page_num <= max_pages:
        if page_num == 1:
            url = list_url
        else:
            url = list_url.replace("-0-1-24-1", f"-0-{page_num}-24-1") if shop_id_match else f"{list_url}&page={page_num}"

        logger.info(f"抓取第 {page_num} 页: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # 滚动页面加载懒加载内容
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 800)")
                await page.wait_for_timeout(500)

            content = await page.content()

            # 解析产品列表
            page_products = _parse_store_page(content, shop_id_match.group(1) if shop_id_match else "")

            if not page_products:
                logger.info(f"第 {page_num} 页无产品，停止翻页")
                break

            products.extend(page_products)
            logger.info(f"第 {page_num} 页获取到 {len(page_products)} 个产品")
            page_num += 1

            # 礼貌延迟
            await page.wait_for_timeout(2000)

        except Exception as e:
            logger.error(f"抓取第 {page_num} 页失败: {e}")
            break

    return products


def _parse_store_page(html: str, shop_id: str) -> list[dict]:
    """解析店铺商品列表页"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    products = []

    # 京东店铺商品列表的常见选择器
    item_selectors = [
        "li.gl-item",
        "div.j-sku-item",
        "div.gl-i-wrap",
        "li.jd-store-item",
        ".mc .gl-item",
    ]

    items = []
    for selector in item_selectors:
        items = soup.select(selector)
        if items:
            break

    if not items:
        # 尝试从 JSON 数据中提取
        products = _parse_from_json(html)
        if products:
            return products

    for item in items:
        try:
            product = {}

            # 商品名
            name_el = (
                item.select_one("div.p-name a em")
                or item.select_one("div.p-name a")
                or item.select_one(".p-name")
                or item.select_one("a[title]")
            )
            if name_el:
                product["name"] = name_el.get("title") or name_el.get_text(strip=True)

            # 链接
            link_el = item.select_one("div.p-name a") or item.select_one("a")
            if link_el:
                href = link_el.get("href", "")
                if href.startswith("//"):
                    href = "https:" + href
                product["url"] = href
                sku_match = re.search(r"(\d{6,12})\.html", href)
                if sku_match:
                    product["sku_id"] = sku_match.group(1)

            # 价格
            price_el = item.select_one("div.p-price strong i") or item.select_one("div.p-price i") or item.select_one(".p-price")
            if price_el:
                product["price"] = price_el.get_text(strip=True)

            # 图片
            img_el = item.select_one("div.p-img img") or item.select_one("img")
            if img_el:
                img_src = img_el.get("data-lazy-img") or img_el.get("src", "")
                if img_src.startswith("//"):
                    img_src = "https:" + img_src
                product["image_url"] = img_src

            # 评论
            comment_el = item.select_one("div.p-commit strong a")
            if comment_el:
                product["comment_count"] = comment_el.get_text(strip=True)

            if product.get("name"):
                product["source"] = "京东"
                product["shop"] = "浙大动物医院专营店"
                products.append(product)

        except Exception as e:
            logger.debug(f"解析商品项失败: {e}")
            continue

    return products


def _parse_from_json(html: str) -> list[dict]:
    """尝试从页面中的 JSON 数据提取产品"""
    products = []

    # 京东经常把商品数据放在 script 标签中
    json_patterns = [
        r'var\s+pageConfig\s*=\s*(\{.*?\});',
        r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
        r'"wareList"\s*:\s*(\[.*?\])',
        r'"skuList"\s*:\s*(\[.*?\])',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                # 递归查找商品列表
                items = _find_items_in_data(data)
                for item in items:
                    product = {
                        "name": item.get("wname") or item.get("name") or item.get("wareName", ""),
                        "sku_id": str(item.get("wareId") or item.get("skuId") or item.get("id", "")),
                        "price": str(item.get("jdPrice") or item.get("price", "")),
                        "image_url": item.get("imageurl") or item.get("img", ""),
                        "source": "京东",
                    }
                    if product["sku_id"]:
                        product["url"] = f"https://item.jd.com/{product['sku_id']}.html"
                    if product.get("image_url") and product["image_url"].startswith("//"):
                        product["image_url"] = "https:" + product["image_url"]
                    if product.get("name"):
                        products.append(product)
                if products:
                    return products
            except (json.JSONDecodeError, TypeError):
                continue

    return products


def _find_items_in_data(data, depth=0) -> list:
    """递归在 JSON 数据中查找商品列表"""
    if depth > 5:
        return []

    if isinstance(data, list) and len(data) > 0:
        # 检查是否是商品列表
        if isinstance(data[0], dict) and any(
            k in data[0] for k in ["wname", "wareId", "skuId", "wareName", "name"]
        ):
            return data

    if isinstance(data, dict):
        for key, value in data.items():
            result = _find_items_in_data(value, depth + 1)
            if result:
                return result

    return []


async def get_product_detail_playwright(sku_id: str, headless: bool = True) -> dict:
    """用 Playwright 获取京东商品详情"""
    detail = {"sku_id": sku_id, "source": "京东"}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        page = await context.new_page()

        url = f"https://item.jd.com/{sku_id}.html"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            # 滚动加载
            for _ in range(5):
                await page.evaluate("window.scrollBy(0, 600)")
                await page.wait_for_timeout(400)

            content = await page.content()
            soup = BeautifulSoup(content, "lxml") if 'BeautifulSoup' in dir() else None

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "lxml")

            # 标题
            title_el = soup.select_one("div.sku-name") or soup.select_one("h1.title") or soup.select_one(".itemInfo-wrap .sku-name")
            if title_el:
                detail["name"] = title_el.get_text(strip=True)

            # 副标题
            subtitle_el = soup.select_one("div.news") or soup.select_one(".p-bfc")
            if subtitle_el:
                detail["description"] = subtitle_el.get_text(strip=True)

            # 品牌
            brand_el = soup.select_one("#parameter-brand li a") or soup.select_one("div.p-parameter-list li a")
            if brand_el:
                detail["brand"] = brand_el.get_text(strip=True)

            # 参数表
            param_items = soup.select("ul.p-parameter-list li")
            for item in param_items:
                text = item.get_text(strip=True)
                parts = re.split(r"[：:]", text, maxsplit=1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    detail[f"param_{key}"] = value
                    # 识别特殊字段
                    if "配料" in key or "成分" in key or "原料" in key:
                        detail["ingredients_text"] = value
                    elif "批准文号" in key or "兽药" in key:
                        detail["approval_number"] = value
                    elif "适用" in key or "适用对象" in key:
                        detail["suitable_species"] = value
                    elif "用法" in key or "使用" in key:
                        detail["usage_guide"] = value

            # 从 script 中提取 JSON 数据
            scripts = soup.select("script")
            for script in scripts:
                script_text = script.string or ""
                # 查找配料/成分信息
                for pattern in [
                    r'"配料[表成]?[：:]\\s*"([^"]+)"',
                    r'"成分[：:]\\s*"([^"]+)"',
                    r'"原料[：:]\\s*"([^"]+)"',
                ]:
                    match = re.search(pattern, script_text)
                    if match and not detail.get("ingredients_text"):
                        detail["ingredients_text"] = match.group(1)

            # 商品图片
            img_el = soup.select_one("#spec-img") or soup.select_one("img.main-img")
            if img_el:
                img_src = img_el.get("src", "")
                if img_src.startswith("//"):
                    img_src = "https:" + img_src
                detail["image_url"] = img_src

        except Exception as e:
            logger.error(f"获取商品详情失败 {sku_id}: {e}")
        finally:
            await browser.close()

    return detail


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

    import sys
    store = sys.argv[1] if len(sys.argv) > 1 else "浙大动物医院专营店"
    print(f"开始抓取店铺: {store}")

    results = asyncio.run(scrape_jd_store(store))
    print(f"\n共获取 {len(results)} 个产品:")
    for i, p in enumerate(results, 1):
        print(f"  {i}. {p.get('name', '?')} | {p.get('price', '?')} | {p.get('sku_id', '?')}")

    if results:
        with open(f"/tmp/jd_store_{store[:10]}.json", "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到 /tmp/jd_store_{store[:10]}.json")
