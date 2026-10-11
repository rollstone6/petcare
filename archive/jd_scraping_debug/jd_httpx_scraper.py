"""用 httpx 抓取京东搜索结果并解析商品数据"""
import asyncio
import json
import re
from bs4 import BeautifulSoup
import httpx

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.jd.com/',
}

async def search_jd(keyword, page_num=1):
    """搜索京东商品"""
    # JD search pagination: page=1,3,5,7... (odd numbers)
    page = page_num * 2 - 1
    url = f'https://search.jd.com/Search?keyword={keyword}&enc=utf-8&page={page}&s={1 + (page_num-1)*60}'
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        resp = await client.get(url, headers=HEADERS)
        print(f"[{keyword}] page {page_num}: status={resp.status_code}, size={len(resp.text)} bytes")
        
        if resp.status_code != 200:
            return []
        
        html = resp.text
        soup = BeautifulSoup(html, 'lxml')
        
        products = []
        
        # Method 1: Parse from HTML DOM
        items = soup.select('li.gl-item')
        if not items:
            items = soup.select('div.gl-i-wrap')
        if not items:
            # Try broader selectors
            items = soup.select('[data-sku]')
        
        for item in items:
            try:
                product = {}
                
                # SKU ID
                sku = item.get('data-sku', '')
                if sku:
                    product['sku_id'] = sku
                    product['url'] = f'https://item.jd.com/{sku}.html'
                
                # Name
                name_el = item.select_one('.p-name em') or item.select_one('.p-name a')
                if name_el:
                    product['name'] = name_el.get_text(strip=True)
                
                # Price
                price_el = item.select_one('.p-price strong i')
                if price_el:
                    product['price'] = price_el.get_text(strip=True)
                
                # Image
                img_el = item.select_one('.p-img img')
                if img_el:
                    img_src = img_el.get('data-lazy-img') or img_el.get('src', '')
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    product['image_url'] = img_src
                
                # Comments
                comment_el = item.select_one('.p-commit strong a')
                if comment_el:
                    product['comment_count'] = comment_el.get_text(strip=True)
                
                # Shop
                shop_el = item.select_one('.p-shop a') or item.select_one('.p-shopnum a')
                if shop_el:
                    product['shop'] = shop_el.get_text(strip=True)
                
                if product.get('name') and product.get('sku_id'):
                    product['source'] = '京东'
                    products.append(product)
                    
            except Exception as e:
                continue
        
        # Method 2: Extract from JSON in script tags
        if not products:
            print("  DOM parsing failed, trying JSON extraction...")
            json_patterns = [
                r'g_page_config\s*=\s*({.*?});',
                r'pageConfig\s*=\s*({.*?});',
            ]
            for pat in json_patterns:
                match = re.search(pat, html, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        # Try to find skuList or wareList
                        for key in ['skuList', 'wareList', 'goodsList', 'list']:
                            if key in data:
                                items = data[key]
                                for item in items:
                                    products.append({
                                        'sku_id': str(item.get('wareId', item.get('skuId', ''))),
                                        'name': item.get('wname', item.get('name', '')),
                                        'price': str(item.get('jdPrice', item.get('price', ''))),
                                        'image_url': item.get('imageurl', ''),
                                        'source': '京东',
                                    })
                                break
                    except json.JSONDecodeError:
                        continue
        
        # Method 3: Extract from data attributes using regex
        if not products:
            print("  JSON extraction failed, trying regex...")
            sku_pattern = re.findall(r'data-sku="(\d+)"', html)
            name_pattern = re.findall(r'<em>([^<]{10,})</em>', html)
            
            for i, sku in enumerate(sku_pattern[:30]):
                name = name_pattern[i] if i < len(name_pattern) else ''
                if name:
                    products.append({
                        'sku_id': sku,
                        'name': name,
                        'url': f'https://item.jd.com/{sku}.html',
                        'source': '京东',
                    })
        
        return products


async def get_product_detail(sku_id):
    """获取商品详情（配料/成分信息）"""
    url = f'https://item.jd.com/{sku_id}.html'
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        resp = await client.get(url, headers=HEADERS)
        if resp.status_code != 200:
            return {}
        
        html = resp.text
        soup = BeautifulSoup(html, 'lxml')
        detail = {'sku_id': sku_id, 'source': '京东'}
        
        # Title
        title_el = soup.select_one('.sku-name') or soup.select_one('h1.title')
        if title_el:
            detail['name'] = title_el.get_text(strip=True)
        
        # Brand
        brand_el = soup.select_one('#parameter-brand li a') or soup.select_one('.p-parameter-list li a')
        if brand_el:
            detail['brand'] = brand_el.get_text(strip=True)
        
        # Parameters
        params = soup.select('.p-parameter-list li')
        for param in params:
            text = param.get_text(strip=True)
            parts = re.split(r'[：:]', text, maxsplit=1)
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                if '配料' in key or '成分' in key or '原料' in key:
                    detail['ingredients_text'] = value
                elif '品牌' in key:
                    detail['brand'] = value
                elif '适用' in key:
                    detail['suitable_species'] = value
                elif '批准文号' in key:
                    detail['approval_number'] = value
        
        # Image
        img_el = soup.select_one('#spec-img') or soup.select_one('.main-img')
        if img_el:
            img_src = img_el.get('src', '')
            if img_src.startswith('//'):
                img_src = 'https:' + img_src
            detail['image_url'] = img_src
        
        return detail


async def main():
    keywords = ['宠物益生菌', '猫驱虫药', '狗零食', '猫粮']
    
    all_products = []
    
    for keyword in keywords:
        print(f"\n{'='*60}")
        print(f"搜索: {keyword}")
        print(f"{'='*60}")
        
        products = await search_jd(keyword, page_num=1)
        print(f"找到 {len(products)} 个商品")
        
        for i, p in enumerate(products[:5], 1):
            print(f"  {i}. [{p.get('sku_id')}] {p.get('name', '?')[:50]}")
            print(f"     ¥{p.get('price', '?')} | {p.get('shop', '?')}")
        
        all_products.extend(products)
        
        # Rate limiting
        await asyncio.sleep(2)
    
    # Save results
    output_file = '/tmp/jd_search_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"总计: {len(all_products)} 个商品")
    print(f"已保存到: {output_file}")
    
    # Try getting detail for first product
    if all_products:
        sku = all_products[0].get('sku_id')
        if sku:
            print(f"\n--- Fetching detail for {sku} ---")
            detail = await get_product_detail(sku)
            print(json.dumps(detail, ensure_ascii=False, indent=2))


asyncio.run(main())
