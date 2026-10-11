"""
最小化测试：只截图看看京东验证码
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("启动浏览器...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        print("访问搜索页...")
        try:
            await page.goto(
                'https://search.jd.com/Search?keyword=iPhone',
                timeout=45000,
                wait_until='domcontentloaded'
            )
        except Exception as e:
            print(f"导航异常: {e}")
        
        # 等待页面稳定
        print("等待页面加载...")
        await page.wait_for_timeout(5000)
        
        # 截图
        print("截图...")
        await page.screenshot(path='/tmp/jd_captcha_test.png', full_page=True)
        
        # 获取页面信息
        url = page.url
        title = await page.title()
        content = await page.content()
        
        print(f"\n当前URL: {url}")
        print(f"页面标题: {title}")
        print(f"页面大小: {len(content)} bytes")
        
        # 检查是否是验证码页面
        if 'risk_handler' in url:
            print("\n✅ 检测到验证码页面")
            
            # 尝试获取验证码类型
            if '滑块' in content or 'slider' in content.lower():
                print("类型: 滑块验证码")
            elif '点选' in content or 'select' in content.lower():
                print("类型: 点选验证码")
            else:
                print("类型: 未知")
            
            # 列出页面中的所有 img 和 canvas 元素
            print("\n页面元素:")
            elements = await page.evaluate('''() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const canvases = Array.from(document.querySelectorAll('canvas'));
                const buttons = Array.from(document.querySelectorAll('button, [role="button"], .btn'));
                
                return {
                    images: imgs.map(img => ({
                        src: img.src,
                        class: img.className,
                        id: img.id,
                        width: img.width,
                        height: img.height
                    })),
                    canvases: canvases.map(c => ({
                        class: c.className,
                        id: c.id,
                        width: c.width,
                        height: c.height
                    })),
                    buttons: buttons.map(b => ({
                        text: b.innerText,
                        class: b.className,
                        id: b.id
                    }))
                };
            }''')
            
            print(f"  图片: {len(elements['images'])} 个")
            for img in elements['images'][:5]:
                print(f"    - {img}")
            
            print(f"  Canvas: {len(elements['canvases'])} 个")
            for canvas in elements['canvases'][:5]:
                print(f"    - {canvas}")
            
            print(f"  按钮: {len(elements['buttons'])} 个")
            for btn in elements['buttons'][:5]:
                print(f"    - {btn}")
        else:
            print("\n⚠️ 未检测到验证码页面")
        
        await browser.close()

asyncio.run(main())
