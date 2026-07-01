"""通过Bing搜索获取京东产品信息"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        
        # 1. Search for pet probiotics on Bing
        print("=== [1] Bing search for 宠物益生菌 ===")
        keywords = ['宠物益生菌', '猫驱虫药', '狗粮推荐']
        
        for keyword in keywords:
            print(f"\n--- {keyword} ---")
            url = f'https://cn.bing.com/search?q={keyword}+site:item.jd.com'
            try:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'lxml')
                    results = soup.select('li.b_algo')
                    print(f"Found {len(results)} results")
                    
                    for i, r in enumerate(results[:5], 1):
                        title_el = r.select_one('h2 a')
                        if title_el:
                            title = title_el.get_text()
                            link = title_el.get('href', '')
                            print(f"{i}. {title}")
                            print(f"   {link[:80]}")
                            
                            # Extract SKU from JD URL
                            sku_match = re.search(r'/(\d{8,12})\.html', link)
                            if sku_match:
                                sku = sku_match.group(1)
                                print(f"   SKU: {sku}")
                            
                            # Get snippet
                            snippet = r.select_one('.b_caption p')
                            if snippet:
                                print(f"   {snippet.get_text()[:100]}")
                            
                            print()
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(1)
        
        # 2. Search for product review articles
        print("\n\n=== [2] Search for product review articles ===")
        review_keywords = [
            '宠物益生菌推荐',
            '猫驱虫药哪个牌子好',
            '2024猫粮推荐',
        ]
        
        for keyword in review_keywords:
            print(f"\n--- {keyword} ---")
            url = f'https://cn.bing.com/search?q={keyword}'
            try:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'lxml')
                    results = soup.select('li.b_algo')
                    
                    # Filter for Zhihu/Toutiao/review sites
                    for r in results[:8]:
                        title_el = r.select_one('h2 a')
                        if title_el:
                            title = title_el.get_text()
                            link = title_el.get('href', '')
                            # Check if it's from a review site
                            if any(site in link for site in ['zhihu.com', 'toutiao.com', 'xiaohongshu.com', 'smzdm.com']):
                                print(f"- {title}")
                                print(f"  {link[:80]}")
                                snippet = r.select_one('.b_caption p')
                                if snippet:
                                    print(f"  {snippet.get_text()[:120]}")
                                print()
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(1)

asyncio.run(main())
