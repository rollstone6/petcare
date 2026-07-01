"""
京东混合爬虫：Playwright处理验证码 + HTTP获取数据
"""
import asyncio
import json
import time
from playwright.async_api import async_playwright
from curl_cffi import requests as http_requests

async def main():
    print("=" * 60)
    print("京东混合爬虫：Playwright + HTTP")
    print("=" * 60)
    
    async with async_playwright() as p:
        # 启动浏览器（headless模式）
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        print("\n[1] 先访问京东首页...")
        try:
            await page.goto('https://www.jd.com/', timeout=60000, wait_until='domcontentloaded')
            print("✅ 首页加载成功")
        except Exception as e:
            print(f"❌ 首页加载失败: {e}")
            await browser.close()
            return
        
        print("[2] 等待页面稳定...")
        await asyncio.sleep(5)
        
        # 尝试通过搜索框搜索
        print("[3] 尝试搜索...")
        try:
            search_input = await page.wait_for_selector('input[name="keyword"]', timeout=10000)
            await search_input.fill('宠物益生菌')
            await asyncio.sleep(1)
            
            # 点击搜索按钮
            search_btn = await page.wait_for_selector('button.form_btn, .search-form button', timeout=5000)
            await search_btn.click()
            print("✅ 搜索已提交")
            
            # 等待搜索结果页
            await asyncio.sleep(5)
        except Exception as e:
            print(f"搜索失败: {e}")
            # 直接导航到搜索页
            print("尝试直接导航到搜索页...")
            try:
                await page.goto('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8', 
                               timeout=60000, wait_until='domcontentloaded')
            except Exception as e2:
                print(f"直接导航也失败: {e2}")
                await browser.close()
                return
        
        # 检查是否有验证码
        if 'risk_handler' in page.url or '验证' in await page.title():
            print("[3] 检测到验证码页面")
            
            # 等待验证码完成（最多60秒）
            # 验证码可能是自动的，也可能需要手动
            print("等待验证码完成...")
            
            # 监听URL变化
            start_time = time.time()
            while 'risk_handler' in page.url and time.time() - start_time < 60:
                await asyncio.sleep(1)
                print(f"  等待中... ({int(time.time() - start_time)}秒)")
            
            if 'risk_handler' not in page.url:
                print("✅ 验证码已通过！")
            else:
                print("❌ 验证码超时")
                await browser.close()
                return
        
        # 等待搜索结果加载
        print("[4] 等待搜索结果加载...")
        await asyncio.sleep(3)
        
        # 提取cookies
        print("[5] 提取cookies...")
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        print(f"  获取到 {len(cookie_dict)} 个cookies")
        
        # 保存cookies
        with open('/tmp/jd_cookies.json', 'w') as f:
            json.dump(cookie_dict, f, indent=2)
        print("  cookies已保存到 /tmp/jd_cookies.json")
        
        # 关闭浏览器
        await browser.close()
        
        # 用HTTP + cookies获取数据
        print("\n[6] 使用HTTP + cookies获取商品数据...")
        
        session = http_requests.Session(impersonate='chrome120')
        
        # 设置cookies
        for name, value in cookie_dict.items():
            session.cookies.set(name, value, domain='.jd.com')
        
        # 搜索商品
        keywords = ['宠物益生菌', '猫粮', '狗粮']
        all_products = []
        
        for keyword in keywords:
            print(f"\n搜索: {keyword}")
            
            url = f'https://search.jd.com/Search?keyword={keyword}&enc=utf-8'
            resp = session.get(url, timeout=15)
            
            print(f"  状态码: {resp.status_code}")
            print(f"  响应大小: {len(resp.text)} bytes")
            
            if resp.status_code == 200 and len(resp.text) > 50000:
                # 解析HTML
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'lxml')
                
                products = []
                items = soup.select('li.gl-item, [data-sku]')
                
                for item in items[:30]:  # 限制30个
                    sku = item.get('data-sku', '')
                    name_el = item.select_one('.p-name em, .p-name a')
                    price_el = item.select_one('.p-price strong i')
                    shop_el = item.select_one('.p-shop a')
                    
                    if sku and name_el:
                        products.append({
                            'sku_id': sku,
                            'name': name_el.get_text(strip=True),
                            'price': price_el.get_text(strip=True) if price_el else '',
                            'shop': shop_el.get_text(strip=True) if shop_el else '',
                            'url': f'https://item.jd.com/{sku}.html',
                            'keyword': keyword,
                        })
                
                print(f"  找到 {len(products)} 个商品")
                all_products.extend(products)
                
                # 打印前5个
                for i, p in enumerate(products[:5], 1):
                    print(f"    {i}. {p['name'][:40]} ¥{p['price']}")
                
                # 延迟避免触发反爬
                time.sleep(2)
            else:
                print(f"  ❌ 获取失败")
        
        # 保存结果
        if all_products:
            with open('/tmp/jd_products_hybrid.json', 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 成功获取 {len(all_products)} 个商品")
            print(f"已保存到 /tmp/jd_products_hybrid.json")
        else:
            print("\n❌ 未获取到任何商品")

if __name__ == '__main__':
    asyncio.run(main())
