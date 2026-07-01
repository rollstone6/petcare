"""用 nodriver (undetected-chromedriver的继任者) 尝试绕过"""
import asyncio
import nodriver as uc

async def main():
    print("=== nodriver attempt ===")
    
    browser = await uc.start(
        headless=True,
        browser_args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
        ]
    )
    
    page = await browser.get('https://www.jd.com/')
    await asyncio.sleep(3)
    
    print(f"Homepage URL: {page.url}")
    title = await page.get_title()
    print(f"Title: {title}")
    
    # Try search
    page2 = await browser.get('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8')
    await asyncio.sleep(5)
    
    print(f"\nSearch URL: {page2.url}")
    title2 = await page2.get_title()
    print(f"Title: {title2}")
    
    if 'risk_handler' not in page2.url and '验证' not in (title2 or ''):
        print("✅ Search page accessible!")
        content = await page2.get_content()
        print(f"Content length: {len(content)}")
        
        # Try to find products
        products = await page2.evaluate('''
            Array.from(document.querySelectorAll('.gl-item, [data-sku]')).map(el => ({
                sku: el.getAttribute('data-sku'),
                name: el.querySelector('.p-name em')?.innerText || '',
                price: el.querySelector('.p-price strong i')?.innerText || '',
            })).filter(p => p.sku)
        ''')
        print(f"Products: {len(products) if products else 0}")
        if products:
            for p in products[:5]:
                print(f"  {p}")
    else:
        print("❌ Blocked")
        
        # Screenshot
        await page2.save_screenshot('/tmp/jd_nodriver.png')
        print("Screenshot: /tmp/jd_nodriver.png")
        
        # Check if there's a captcha to solve
        content = await page2.get_content()
        if '滑块' in content or 'slide' in content.lower():
            print("Slider captcha detected, trying to solve...")
            
            # Try to find and drag slider
            try:
                slider = await page2.select('.JDJRV-slide-btn, .slide_btn, [class*=slide-inner], [class*=drag]')
                if slider:
                    print(f"Found slider: {slider}")
                    # Get bounding box and drag
                    box = await slider.get_box()
                    print(f"Box: {box}")
            except Exception as e:
                print(f"Slider handling error: {e}")
    
    # Try detail page
    page3 = await browser.get('https://item.jd.com/100012043978.html')
    await asyncio.sleep(3)
    print(f"\nDetail URL: {page3.url}")
    title3 = await page3.get_title()
    print(f"Title: {title3}")
    
    browser.stop()

asyncio.run(main())
