"""用 curl_cffi chrome107 访问京东商品详情 + 搜索"""
from curl_cffi import requests
import re
import json
from bs4 import BeautifulSoup

session = requests.Session(impersonate='chrome107')

# 1. Visit homepage for cookies
print("=== Step 1: Homepage ===")
resp = session.get('https://www.jd.com/', timeout=15)
print(f"Homepage: {resp.status_code}, {len(resp.text)} bytes, cookies: {len(session.cookies)}")

# 2. Try product detail pages directly
print("\n=== Step 2: Product detail pages ===")
test_skus = [
    '100012043978',  # test
    '100008062498',  # Royal Canin
    '100038662530',  # pet product
    '100008379588',  # Orijen
    '100039004637',  # pet supplement
]

for sku in test_skus:
    url = f'https://item.jd.com/{sku}.html'
    try:
        resp = session.get(url, timeout=15)
        final_url = str(resp.url)
        if 'risk_handler' not in final_url and len(resp.text) > 5000:
            soup = BeautifulSoup(resp.text, 'lxml')
            title_el = soup.select_one('.sku-name') or soup.select_one('title')
            title = title_el.get_text(strip=True) if title_el else '?'
            print(f"  ✅ {sku}: {len(resp.text)} bytes - {title[:60]}")
            
            # Save first success
            if sku == test_skus[0]:
                with open('/tmp/jd_detail_success.html', 'w') as f:
                    f.write(resp.text)
        else:
            title_match = re.search(r'<title>(.*?)</title>', resp.text)
            t = title_match.group(1) if title_match else resp.text[:100]
            print(f"  ❌ {sku}: {len(resp.text)} bytes - {t[:50]}")
    except Exception as e:
        print(f"  ❌ {sku}: {e}")

# 3. Try mobile search API (different domain)
print("\n=== Step 3: JD mobile API search ===")
mobile_urls = [
    ('api.m.jd.com search', 'https://api.m.jd.com/client.action?functionId=search&body=%7B%22keyword%22%3A%22%E5%AE%A0%E7%89%A9%E7%9B%8A%E7%94%9F%E8%8F%8C%22%2C%22page%22%3A%221%22%2C%22pageSize%22%3A%2210%22%7D&appid=wh5'),
    ('api.m.jd.com ware', 'https://api.m.jd.com/client.action?functionId=wareBusiness&body=%7B%22skuId%22%3A%22100012043978%22%7D&appid=item-v3'),
    ('suggest', 'https://dd-search.jd.com/suggest?keyword=宠物益生菌&enc=utf-8'),
]

for name, url in mobile_urls:
    try:
        resp = session.get(url, timeout=10)
        final_url = str(resp.url)
        if 'risk_handler' not in final_url:
            print(f"  ✅ {name}: {resp.status_code}, {len(resp.text)} bytes")
            if len(resp.text) > 50:
                print(f"     {resp.text[:200]}")
        else:
            print(f"  ❌ {name}: blocked")
    except Exception as e:
        print(f"  ❌ {name}: {type(e).__name__}: {e}")

# 4. Try JD list/category pages (often less restricted than search)
print("\n=== Step 4: Category pages ===")
cat_urls = [
    ('Pet food', 'https://list.jd.com/list.html?cat=1949,1950,1957'),
    ('Pet health', 'https://list.jd.com/list.html?cat=1949,1951,1963'),
    ('channel', 'https://channel.jd.com/pet.html'),
]
for name, url in cat_urls:
    try:
        resp = session.get(url, timeout=10)
        final_url = str(resp.url)
        if 'risk_handler' not in final_url and len(resp.text) > 5000:
            print(f"  ✅ {name}: {resp.status_code}, {len(resp.text)} bytes")
            soup = BeautifulSoup(resp.text, 'lxml')
            skus = re.findall(r'data-sku="(\d+)"', resp.text)
            items = soup.select('[data-sku]')
            print(f"     Products: {len(skus)} SKUs, {len(items)} items")
        else:
            title_match = re.search(r'<title>(.*?)</title>', resp.text)
            t = title_match.group(1) if title_match else ''
            print(f"  ❌ {name}: {len(resp.text)} bytes - {t[:50]}")
    except Exception as e:
        print(f"  ❌ {name}: {type(e).__name__}")

# 5. Try JD shop product list
print("\n=== Step 5: Shop product list ===")
# Try a known pet shop
shop_urls = [
    ('mall.jd.com shop', 'https://mall.jd.com/view_search-10130498-0-1-24-1.html'),
    ('shop.jd.com', 'https://shop.jd.com/10130498'),
]
for name, url in shop_urls:
    try:
        resp = session.get(url, timeout=10)
        final_url = str(resp.url)
        if 'risk_handler' not in final_url and len(resp.text) > 5000:
            print(f"  ✅ {name}: {resp.status_code}, {len(resp.text)} bytes")
            # Check for products
            skus = re.findall(r'item\.jd\.com/(\d+)\.html', resp.text)
            print(f"     Found {len(skus)} product links")
            for s in skus[:5]:
                print(f"       {s}")
        else:
            title_match = re.search(r'<title>(.*?)</title>', resp.text)
            t = title_match.group(1) if title_match else ''
            print(f"  ❌ {name}: {len(resp.text)} bytes - {t[:50]}")
    except Exception as e:
        print(f"  ❌ {name}: {type(e).__name__}")
