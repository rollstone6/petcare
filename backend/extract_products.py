"""从评测文章中提取宠物产品数据并导入数据库"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Articles found via Bing search
ARTICLES = [
    # 益生菌
    "https://www.toutiao.com/article/7641482100188676643/",
    "https://www.toutiao.com/article/7626212663827284543/",
    "https://zhuanlan.zhihu.com/p/623156151",
    # 狗粮
    "https://zhuanlan.zhihu.com/p/1903210634616758922",
    # 猫粮
    "https://www.chinapp.com/best/gouliang.html",
]

async def fetch_article(client, url):
    """获取文章内容"""
    try:
        resp = await client.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Remove scripts/styles
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Get title
        title = soup.title.string if soup.title else ''
        
        # Get article content
        content = ''
        for selector in ['article', '.article-content', '.Post-RichTextContainer', '.RichText', '.content', 'main']:
            el = soup.select_one(selector)
            if el:
                content = el.get_text(separator='\n', strip=True)
                break
        
        if not content:
            content = soup.get_text(separator='\n', strip=True)
        
        return {'url': url, 'title': title, 'content': content[:8000]}
    except Exception as e:
        return {'url': url, 'title': '', 'content': '', 'error': str(e)}


def extract_products_from_text(text, category):
    """从文本中提取产品/品牌信息"""
    products = []
    
    # Common pet product brand names
    brands = [
        '皇家', '渴望', '麦富迪', '伯纳天纯', '疯狂小狗', '比瑞吉',
        '冠能', '比乐', '网易严选', '高爷家', '卫仕', '红狗',
        '小壳', '朗诺', '宠幸', '雷米高', '拜宠清', '大宠爱',
        '福来恩', '海乐妙', '妙三多', '维克', '信必可', '勃欣齐',
        '普瑞纳', '雪山', '纽顿', 'GO', '爱肯拿', 'now fresh',
        '素力高', '纽翠斯', '卡比', '百利', '蓝氏', '巅峰',
        '朗士', '发育宝', '谷登', 'MAG', '卫仕', '雷米高一',
        '金赏', '优卡', '希尔斯', '处方粮', '处方',
        '豆柴', '诚实一口', '高爷家', 'pidan', '未卡',
        '小佩', '有鱼', '鲜朗', '弗列加特', '阿飞和巴弟',
    ]
    
    # Search for brand mentions with context
    for brand in brands:
        if brand.lower() in text.lower():
            # Find the context around brand mention
            idx = text.lower().find(brand.lower())
            context = text[max(0, idx-50):idx+100]
            products.append({
                'brand': brand,
                'context': context.strip(),
                'category': category,
            })
    
    return products


async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        
        all_articles = []
        for url in ARTICLES:
            print(f"\nFetching: {url[:60]}...")
            article = await fetch_article(client, url)
            if article:
                all_articles.append(article)
                print(f"  Title: {article['title'][:60]}")
                print(f"  Content: {len(article['content'])} chars")
            await asyncio.sleep(1)
        
        # Extract products from articles
        print("\n\n" + "="*60)
        print("EXTRACTED PRODUCTS")
        print("="*60)
        
        all_products = []
        categories = {
            'toutiao.com/article/764': '保健品-益生菌',
            'toutiao.com/article/762': '保健品-益生菌',
            'zhihu.com/p/623156': '保健品-益生菌',
            'zhihu.com/p/190321': '食品-狗粮',
            'chinapp.com': '食品-狗粮',
        }
        
        for article in all_articles:
            cat = '未分类'
            for pattern, c in categories.items():
                if pattern in article['url']:
                    cat = c
                    break
            
            products = extract_products_from_text(article['content'], cat)
            if products:
                print(f"\n[{cat}] From: {article['title'][:50]}")
                for p in products:
                    print(f"  品牌: {p['brand']}")
                    print(f"  上下文: {p['context'][:80]}...")
            all_products.extend(products)
        
        # Deduplicate by brand
        unique_brands = {}
        for p in all_products:
            brand = p['brand']
            cat = p['category']
            key = f"{brand}|{cat}"
            if key not in unique_brands:
                unique_brands[key] = p
        
        print(f"\n\n{'='*60}")
        print(f"UNIQUE BRANDS FOUND: {len(unique_brands)}")
        print(f"{'='*60}")
        
        results = []
        for key, p in sorted(unique_brands.items()):
            results.append(p)
            print(f"  [{p['category']}] {p['brand']}")
        
        # Save to JSON
        with open('/tmp/extracted_products.json', 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved to /tmp/extracted_products.json")


asyncio.run(main())
