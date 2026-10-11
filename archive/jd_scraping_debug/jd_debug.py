"""尝试访问京东商品详情页 + 备选数据源"""
import asyncio
import json
import re
import httpx

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.jd.com/',
}

# Known JD pet product SKUs (from previous crawling or public data)
KNOWN_SKUS = [
    '100012043978',  # 某宠物产品
    '100008062498',  # 皇家猫粮
    '100008379588',  # 渴望猫粮
    '100012100488',  # 宠物益生菌
    '100004025432',  # 驱虫药
]

async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        
        # 1. Try item.jd.com detail pages
        print("=== [1] Product detail pages ===")
        for sku in KNOWN_SKUS[:3]:
            try:
                url = f'https://item.jd.com/{sku}.html'
                resp = await client.get(url, headers=HEADERS)
                final_url = str(resp.url)
                blocked = 'risk_handler' in final_url or '验证' in resp.text[:500]
                print(f"\n  SKU {sku}: {resp.status_code}, {len(resp.text)} bytes")
                print(f"  URL: {final_url[:80]}")
                if not blocked and len(resp.text) > 5000:
                    print(f"  ✅ Accessible!")
                    # Extract title
                    title_match = re.search(r'<title>(.*?)</title>', resp.text)
                    if title_match:
                        print(f"  Title: {title_match.group(1)}")
                    # Save first accessible page
                    with open('/tmp/jd_detail.html', 'w') as f:
                        f.write(resp.text)
                else:
                    print(f"  ❌ {'Blocked' if blocked else 'Too small'}")
            except Exception as e:
                print(f"  Error: {e}")
            await asyncio.sleep(1)

        # 2. Try JD mobile product API (different domain)
        print("\n\n=== [2] Alternative JD endpoints ===")
        alt_urls = [
            ("JD callback API", "https://callback.51buy.com/callback.php?jsoncallback=j&skuId=100012043978&type=1"),
            ("JD comment", "https://sclub.jd.com/comment/productPageComments.action?productId=100012043978&score=0&sortType=5&page=0&pageSize=10"),
            ("JD price history", "https://p.3.cn/prices/mgets?skuIds=J_100012043978"),
            ("JD recommend", "https://cd.jd.com/recommendation/getProductByWare?wareId=100012043978&lid=1&limit=5&callback=cb"),
            ("JD shop products", "https://mall.jd.com/view_search-12085499-0-1-24-1.html"),
        ]
        for name, url in alt_urls:
            try:
                resp = await client.get(url, headers=HEADERS)
                final_url = str(resp.url)
                blocked = 'risk_handler' in final_url
                print(f"\n  {name}: {resp.status_code}, {len(resp.text)} bytes, {'❌' if blocked else '✅'}")
                if not blocked and resp.status_code == 200:
                    print(f"  Preview: {resp.text[:300]}")
            except Exception as e:
                print(f"  {name}: {type(e).__name__}: {e}")

        # 3. Try Google cached JD pages
        print("\n\n=== [3] Google cache / web archive ===")
        cache_urls = [
            ("Wayback Machine", f"https://web.archive.org/web/2024/https://search.jd.com/Search?keyword=宠物益生菌"),
            ("Wayback item", f"https://web.archive.org/web/2024/https://item.jd.com/100012043978.html"),
        ]
        for name, url in cache_urls:
            try:
                resp = await client.get(url, headers=HEADERS, timeout=20)
                print(f"\n  {name}: {resp.status_code}, {len(resp.text)} bytes")
                if resp.status_code == 200 and len(resp.text) > 5000:
                    # Check if it has product data
                    if '宠物' in resp.text or '猫' in resp.text or '狗' in resp.text:
                        print(f"  ✅ Contains pet data!")
                        with open(f'/tmp/jd_{name.replace(" ", "_")}.html', 'w') as f:
                            f.write(resp.text)
            except Exception as e:
                print(f"  {name}: {type(e).__name__}")

asyncio.run(main())
