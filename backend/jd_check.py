"""检查店铺页面和推荐API的实际内容"""
import asyncio
import httpx
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.jd.com/',
}

async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        
        # 1. Check mall.jd.com shop page
        print("=== [1] mall.jd.com shop page ===")
        url = 'https://mall.jd.com/view_search-12085499-0-1-24-1.html'
        resp = await client.get(url, headers=HEADERS)
        print(f"Status: {resp.status_code}, Size: {len(resp.text)} bytes")
        
        soup = BeautifulSoup(resp.text, 'lxml')
        title = soup.title.string if soup.title else 'No title'
        print(f"Title: {title}")
        
        # Check if it's a verification page
        if '验证' in resp.text or 'risk_handler' in resp.text:
            print("❌ This is a verification page")
        else:
            print("✅ Not a verification page")
            # Try to find products
            products = soup.select('.gl-item, .J_goodsList li, [data-sku]')
            print(f"Products found: {len(products)}")
            
            # Check what's in the page
            text = soup.get_text()[:1000]
            print(f"Page text preview:\n{text[:500]}")
        
        # 2. Check recommend API
        print("\n\n=== [2] JD recommend API ===")
        url2 = 'https://cd.jd.com/recommendation/getProductByWare?wareId=100012043978&lid=1&limit=5&callback=cb'
        resp2 = await client.get(url2, headers=HEADERS)
        print(f"Status: {resp2.status_code}, Size: {len(resp2.text)} bytes")
        
        soup2 = BeautifulSoup(resp2.text, 'lxml')
        title2 = soup2.title.string if soup2.title else 'No title'
        print(f"Title: {title2}")
        
        if '验证' in resp2.text or 'risk_handler' in resp2.text:
            print("❌ Verification page")
        else:
            print("✅ Not verification")
            # Check if it has JSON data
            import re
            json_match = re.search(r'cb\((.*?)\)', resp2.text, re.DOTALL)
            if json_match:
                print(f"JSON callback found: {json_match.group(1)[:500]}")
            else:
                print(f"Content preview: {resp2.text[:500]}")
        
        # 3. Try a different approach: use Bing China cache
        print("\n\n=== [3] Try Bing China ===")
        bing_url = 'https://cn.bing.com/search?q=site:item.jd.com+宠物益生菌'
        try:
            resp3 = await client.get(bing_url, headers=HEADERS, timeout=10)
            print(f"Bing: {resp3.status_code}, {len(resp3.text)} bytes")
            if resp3.status_code == 200:
                soup3 = BeautifulSoup(resp3.text, 'lxml')
                results = soup3.select('li.b_algo')
                print(f"Search results: {len(results)}")
                for r in results[:3]:
                    title = r.select_one('h2 a')
                    if title:
                        print(f"  - {title.get_text()}")
                        print(f"    {title.get('href', '')[:80]}")
        except Exception as e:
            print(f"Bing error: {e}")

asyncio.run(main())
