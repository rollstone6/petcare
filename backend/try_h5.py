"""手动 stealth + 多种方式尝试突破京东反爬"""
import asyncio
import json
import re
import random

STEALTH_JS = """
// Override webdriver detection
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
// Override languages
Object.defineProperty(navigator, 'languages', {get: () => Object.freeze(['zh-CN', 'zh', 'en'])});
// Override plugins
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
// Chrome runtime
window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
// Permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);
// Hide automation
delete navigator.__proto__.webdriver;
// Platform
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
// Hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
"""

async def main():
    from playwright.async_api import async_playwright

    print("=== JD Anti-bot Bypass Attempts ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080',
            ]
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        page = await context.new_page()
        await page.add_init_script(STEALTH_JS)

        # === Approach 1: Homepage → Search (with cookies) ===
        print("--- [1] Homepage first, then search ---")
        try:
            resp = await page.goto('https://www.jd.com/', wait_until='domcontentloaded', timeout=20000)
            print(f"Homepage: {resp.status}")
            await page.wait_for_timeout(1500)
            cookies = await context.cookies()
            print(f"Cookies acquired: {len(cookies)}")

            resp2 = await page.goto('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8',
                                     wait_until='domcontentloaded', timeout=20000)
            print(f"Search: {resp2.status}, URL: {page.url[:80]}")

            if 'risk_handler' not in page.url:
                await page.wait_for_timeout(2000)
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 600)")
                    await page.wait_for_timeout(400)

                prods = await page.evaluate('''() => {
                    let items = document.querySelectorAll('.gl-item');
                    return Array.from(items).map(i => ({
                        name: i.querySelector('.p-name em')?.innerText || '',
                        price: i.querySelector('.p-price strong i')?.innerText || '',
                        sku: i.getAttribute('data-sku') || '',
                    })).filter(p => p.name);
                }''')
                print(f"✅ Products: {len(prods)}")
                for pr in prods[:5]:
                    print(f"   {pr['name'][:50]} ¥{pr['price']}")
            else:
                print("❌ Blocked")
                await page.screenshot(path='/tmp/jd_stealth2.png')
                # Try slider
                await try_slider(page)
        except Exception as e:
            print(f"Error: {e}")

        # === Approach 2: Try via httpx with specific headers (no browser fingerprint) ===
        print("\n--- [2] httpx with browser-like headers ---")
        import httpx
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            # JD product detail - sometimes accessible without auth
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.jd.com/',
            }

            # Try several known JD public endpoints
            endpoints = [
                ("search.jd.com", "https://search.jd.com/Search?keyword=猫粮&enc=utf-8"),
                ("list.jd.com", "https://list.jd.com/list.html?cat=1949,1950,1957"),
                ("so.m.jd.com", "https://so.m.jd.com/ware/search.action?keyword=猫粮"),
            ]

            for name, url in endpoints:
                try:
                    resp = await client.get(url, headers=headers)
                    blocked = 'risk_handler' in str(resp.url) or '验证' in resp.text[:1000]
                    print(f"  {name}: {resp.status_code} {'❌ blocked' if blocked else '✅ ok'} ({len(resp.text)} bytes)")
                    if not blocked and '宠物' in resp.text:
                        print(f"    Contains pet content!")
                except Exception as e:
                    print(f"  {name}: error - {type(e).__name__}")

        # === Approach 3: Try third-party price/product APIs ===
        print("\n--- [3] Third-party APIs ---")
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            apis = [
                ("慢慢买", "http://tool.manmanbuy.com/historyLowest.aspx?jsoncallback=cb&url=https://item.jd.com/100012043978.html"),
                ("什么值得买搜索", "https://post.smzdm.com/search/json/?s=宠物益生菌&order=score&limit=10"),
            ]
            for name, url in apis:
                try:
                    resp = await client.get(url, headers=headers)
                    print(f"  {name}: {resp.status_code} ({len(resp.text)} bytes)")
                    if resp.status_code == 200 and len(resp.text) > 50:
                        print(f"    Preview: {resp.text[:200]}")
                except Exception as e:
                    print(f"  {name}: {type(e).__name__}")

        await browser.close()


async def try_slider(page):
    """尝试处理滑块"""
    print("  Attempting slider bypass...")
    try:
        for sel in ['.JDJRV-slide-btn', '.slide_btn', '[class*=slide-inner]', '[class*=drag]', '#nc_1_n1z']:
            slider = await page.query_selector(sel)
            if slider:
                print(f"  Found slider: {sel}")
                box = await slider.bounding_box()
                if not box:
                    continue
                sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
                await page.mouse.move(sx, sy)
                await asyncio.sleep(0.2)
                await page.mouse.down()

                total = random.randint(260, 300)
                cur = 0
                while cur < total:
                    step = random.uniform(2, 12)
                    cur = min(cur + step, total)
                    await page.mouse.move(sx + cur, sy + random.uniform(-2, 2))
                    await asyncio.sleep(random.uniform(0.008, 0.04))

                await page.mouse.up()
                await asyncio.sleep(3)
                print(f"  After slider: {'✅' if 'risk_handler' not in page.url else '❌'} {page.url[:80]}")
                return
        print("  No slider element found")
    except Exception as e:
        print(f"  Slider error: {e}")


asyncio.run(main())
