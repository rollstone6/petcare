"""
京东验证码自动解决方案
步骤：
1. Playwright 打开京东搜索页 → 触发验证码
2. 截取验证码图片
3. ddddocr 识别滑块缺口位置
4. 模拟人类拖拽滑块
5. 验证通过后继续爬取
"""
import asyncio
import json
import re
import random
import time
import os
import io

from playwright.async_api import async_playwright
from PIL import Image
import numpy as np

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => Object.freeze(['zh-CN', 'zh', 'en'])});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
"""


async def solve_captcha(page, max_attempts=3):
    """尝试解决当前页面的验证码"""
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Captcha attempt {attempt}/{max_attempts} ---")
        
        # Wait for page to stabilize
        await page.wait_for_timeout(3000)
        
        # Check if we're still on captcha page
        current_url = page.url
        if 'risk_handler' not in current_url:
            print("✅ Already passed verification!")
            return True
        
        # Step 1: Analyze the captcha page structure
        try:
            captcha_info = await analyze_captcha_page(page)
        except Exception as e:
            print(f"Error analyzing captcha: {e}")
            # Wait and retry
            await page.wait_for_timeout(2000)
            continue
        print(f"Captcha type: {captcha_info['type']}")
        print(f"Elements found: {list(captcha_info['elements'].keys())}")
        
        if captcha_info['type'] == 'slider':
            success = await solve_slider_captcha(page, captcha_info)
        elif captcha_info['type'] == 'image_select':
            success = await solve_image_select_captcha(page, captcha_info)
        elif captcha_info['type'] == 'unknown':
            # Take full screenshot and try to identify
            await page.screenshot(path=f'/tmp/jd_captcha_attempt{attempt}.png', full_page=False)
            print(f"Unknown captcha, screenshot saved")
            
            # Try to find any interactive elements
            success = await solve_unknown_captcha(page, captcha_info)
        else:
            print(f"Unsupported captcha type: {captcha_info['type']}")
            success = False
        
        if success:
            await page.wait_for_timeout(3000)
            if 'risk_handler' not in page.url:
                print("✅ CAPTCHA SOLVED! Verification passed!")
                return True
            else:
                print("❌ Still on verification page after attempt")
        else:
            print("❌ Attempt failed")
            # Wait before retry
            await page.wait_for_timeout(2000)
    
    return False


async def analyze_captcha_page(page):
    """分析验证码页面的结构"""
    info = {
        'type': 'unknown',
        'elements': {},
        'images': [],
    }
    
    # Check for slider captcha elements
    slider_selectors = {
        'slider_btn': '.JDJRV-slide-btn, .slide_btn, [class*=slide-inner], [class*=slide_btn]',
        'slider_track': '.JDJRV-slide, .slide-track, [class*=slide]',
        'bg_image': '.JDJRV-bigimg, .captcha_bg, [class*=bg-img], img[class*=big]',
        'slide_image': '.JDJRV-smallimg, .captcha_slide, [class*=slide-img], img[class*=small]',
        'canvas': 'canvas',
    }
    
    for name, selector in slider_selectors.items():
        elements = await page.query_selector_all(selector)
        if elements:
            info['elements'][name] = len(elements)
    
    # Check for image select captcha
    select_selectors = {
        'select_items': '[class*=click-item], [class*=select-item], [class*=verify-item]',
        'prompt_text': '[class*=prompt], [class*=tip], [class*=hint]',
    }
    
    for name, selector in select_selectors.items():
        elements = await page.query_selector_all(selector)
        if elements:
            info['elements'][name] = len(elements)
    
    # Get all images on page
    images = await page.query_selector_all('img')
    for img in images:
        src = await img.get_attribute('src') or ''
        cls = await img.get_attribute('class') or ''
        width = await img.get_attribute('width') or ''
        height = await img.get_attribute('height') or ''
        info['images'].append({
            'src': src[:100],
            'class': cls,
            'width': width,
            'height': height,
        })
    
    # Determine captcha type
    if info['elements'].get('slider_btn') or info['elements'].get('slider_track'):
        info['type'] = 'slider'
    elif info['elements'].get('canvas'):
        info['type'] = 'slider'  # JD often uses canvas for slider
    elif info['elements'].get('select_items'):
        info['type'] = 'image_select'
    
    # Also check page content for clues
    content = await page.content()
    if '滑块' in content or '拖动' in content or 'slide' in content.lower():
        info['type'] = 'slider'
    elif '点选' in content or '点击' in content or '按顺序' in content:
        info['type'] = 'image_select'
    
    return info


async def solve_slider_captcha(page, captcha_info):
    """解决滑块验证码"""
    print("Solving slider captcha...")
    
    # Step 1: Find and screenshot the background image (with the gap)
    bg_image = None
    slide_image = None
    
    # Try to get captcha images
    bg_selectors = ['.JDJRV-bigimg', '.captcha_bg', '[class*=bg-img]', 'img[class*=big]', 'canvas']
    for sel in bg_selectors:
        el = await page.query_selector(sel)
        if el:
            try:
                bg_bytes = await el.screenshot()
                bg_image = Image.open(io.BytesIO(bg_bytes))
                print(f"  Got bg image from {sel}: {bg_image.size}")
                bg_image.save('/tmp/captcha_bg.png')
                break
            except Exception as e:
                print(f"  Screenshot {sel} failed: {e}")
    
    # Try to get the slide piece image
    slide_selectors = ['.JDJRV-smallimg', '.captcha_slide', '[class*=slide-img]', 'img[class*=small]']
    for sel in slide_selectors:
        el = await page.query_selector(sel)
        if el:
            try:
                slide_bytes = await el.screenshot()
                slide_image = Image.open(io.BytesIO(slide_bytes))
                print(f"  Got slide image from {sel}: {slide_image.size}")
                slide_image.save('/tmp/captcha_slide.png')
                break
            except Exception as e:
                print(f"  Screenshot {sel} failed: {e}")
    
    # If we couldn't get individual images, screenshot the whole captcha area
    if not bg_image:
        # Screenshot the full verification area
        captcha_area = await page.query_selector('[class*=verify], [class*=captcha], [class*=risk], #app')
        if captcha_area:
            try:
                area_bytes = await captcha_area.screenshot()
                bg_image = Image.open(io.BytesIO(area_bytes))
                bg_image.save('/tmp/captcha_area.png')
                print(f"  Got captcha area screenshot: {bg_image.size}")
            except:
                pass
    
    # Full page screenshot as fallback
    await page.screenshot(path='/tmp/captcha_full.png', full_page=False)
    
    # Step 2: Calculate the slider distance
    distance = 0
    
    if bg_image and slide_image:
        # Use template matching to find the gap position
        distance = find_gap_position(bg_image, slide_image)
        print(f"  Template matching distance: {distance}px")
    elif bg_image:
        # Use edge detection to find the gap
        distance = find_gap_by_edge_detection(bg_image)
        print(f"  Edge detection distance: {distance}px")
    
    if distance == 0:
        # Try ddddocr
        distance = try_ddddocr()
        print(f"  ddddocr distance: {distance}px")
    
    if distance == 0:
        # Fallback: random distance (typical JD slider is 100-300px)
        distance = random.randint(150, 280)
        print(f"  Random fallback distance: {distance}px")
    
    # Step 3: Find the slider button and drag it
    slider_btn = None
    btn_selectors = [
        '.JDJRV-slide-btn', '.slide_btn', '[class*=slide-inner]',
        '[class*=drag]', '.nc_iconfont', '#nc_1_n1z',
        '[class*=slider-btn]', '[class*=handler]',
    ]
    
    for sel in btn_selectors:
        slider_btn = await page.query_selector(sel)
        if slider_btn:
            print(f"  Found slider button: {sel}")
            break
    
    if not slider_btn:
        # Try to find any draggable element
        all_elements = await page.query_selector_all('div, span, button')
        for el in all_elements:
            cls = await el.get_attribute('class') or ''
            if any(kw in cls.lower() for kw in ['slide', 'drag', 'handler', 'btn', 'knob']):
                slider_btn = el
                print(f"  Found slider by class: {cls}")
                break
    
    if not slider_btn:
        print("  ❌ Could not find slider button")
        # Print page structure for debugging
        structure = await page.evaluate('''() => {
            function getStructure(el, depth) {
                if (depth > 4) return null;
                let children = Array.from(el.children).map(c => getStructure(c, depth + 1)).filter(Boolean);
                return {
                    tag: el.tagName,
                    class: el.className?.toString()?.substring(0, 60) || '',
                    id: el.id || '',
                    children: children.length ? children : undefined,
                };
            }
            return getStructure(document.body, 0);
        }''')
        # Print relevant parts
        print(f"  Page structure saved to /tmp/captcha_structure.json")
        with open('/tmp/captcha_structure.json', 'w') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        return False
    
    # Step 4: Perform human-like drag
    box = await slider_btn.bounding_box()
    if not box:
        print("  ❌ Slider has no bounding box")
        return False
    
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2
    
    print(f"  Dragging from ({start_x:.0f}, {start_y:.0f}) distance={distance}px")
    
    await human_like_drag(page, start_x, start_y, distance)
    
    # Step 5: Check result
    await page.wait_for_timeout(3000)
    
    current_url = page.url
    if 'risk_handler' not in current_url:
        return True
    
    # Check if we need to retry (page might show "retry" message)
    content = await page.content()
    if '重试' in content or 'retry' in content.lower():
        print("  Server says retry, clicking...")
        retry_btn = await page.query_selector('button, [class*=retry], a:has-text("重试")')
        if retry_btn:
            await retry_btn.click()
            await page.wait_for_timeout(2000)
    
    return 'risk_handler' not in page.url


async def human_like_drag(page, start_x, start_y, distance):
    """模拟人类拖拽行为"""
    await page.mouse.move(start_x, start_y)
    await asyncio.sleep(random.uniform(0.1, 0.3))
    await page.mouse.down()
    await asyncio.sleep(random.uniform(0.1, 0.2))
    
    # Generate human-like movement curve (accelerate → decelerate → slight overshoot → correct)
    steps = []
    current = 0
    total = distance
    
    # Phase 1: Acceleration (0-60%)
    while current < total * 0.6:
        step = random.uniform(8, 20)
        current = min(current + step, total)
        steps.append((step, random.uniform(-1, 1)))
    
    # Phase 2: Deceleration (60-90%)
    while current < total * 0.9:
        step = random.uniform(3, 10)
        current = min(current + step, total)
        steps.append((step, random.uniform(-1, 1)))
    
    # Phase 3: Overshoot slightly
    overshoot = random.uniform(5, 15)
    current += overshoot
    steps.append((overshoot, random.uniform(-1, 1)))
    
    # Phase 4: Correct back
    steps.append((-overshoot + (total - current + overshoot), random.uniform(-0.5, 0.5)))
    
    # Execute movement
    for dx, dy in steps:
        await page.mouse.move(start_x + current, start_y + dy)
        current_after = current  # Track position
        
        # Actually we need to track cumulative position
        pass
    
    # Simpler approach with cumulative tracking
    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    await asyncio.sleep(0.1)
    
    pos = 0
    target = distance
    
    # Generate smooth trajectory
    trajectory = generate_trajectory(target)
    
    for dx, dy, dt in trajectory:
        pos += dx
        await page.mouse.move(start_x + pos, start_y + dy)
        await asyncio.sleep(dt)
    
    # Final position
    await page.mouse.move(start_x + target, start_y + random.uniform(-0.5, 0.5))
    await asyncio.sleep(random.uniform(0.1, 0.3))
    await page.mouse.up()


def generate_trajectory(distance):
    """生成人类拖拽轨迹"""
    trajectory = []
    current = 0
    t = 0
    
    # Total steps based on distance
    total_steps = random.randint(25, 45)
    
    for i in range(total_steps):
        # Progress ratio (0 to 1)
        progress = (i + 1) / total_steps
        
        # Ease-in-out curve
        if progress < 0.5:
            # Accelerating
            speed_factor = 2 * progress * progress
        else:
            # Decelerating
            speed_factor = 1 - (-2 * progress + 2) ** 2 / 2
        
        target_pos = distance * speed_factor
        dx = target_pos - current
        current = target_pos
        
        # Add some noise
        dy = random.uniform(-1.5, 1.5)
        dt = random.uniform(0.008, 0.04)
        
        # Slow down near the end
        if progress > 0.85:
            dt *= 2
            dy *= 0.5
        
        if abs(dx) > 0.5:
            trajectory.append((dx, dy, dt))
    
    # Add overshoot and correction at the end
    overshoot = random.uniform(3, 10)
    trajectory.append((overshoot, random.uniform(-0.5, 0.5), 0.03))
    trajectory.append((-overshoot, random.uniform(-0.3, 0.3), 0.05))
    
    return trajectory


def find_gap_position(bg_image, slide_image):
    """用模板匹配找到缺口位置"""
    import cv2
    
    bg_cv = cv2.cvtColor(np.array(bg_image), cv2.COLOR_RGB2GRAY)
    slide_cv = cv2.cvtColor(np.array(slide_image), cv2.COLOR_RGB2GRAY)
    
    # Resize if needed
    if slide_cv.shape[0] > bg_cv.shape[0]:
        scale = bg_cv.shape[0] / slide_cv.shape[0]
        slide_cv = cv2.resize(slide_cv, None, fx=scale, fy=scale)
    
    # Template matching
    result = cv2.matchTemplate(bg_cv, slide_cv, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    # max_loc[0] is the x position of the gap
    return max_loc[0]


def find_gap_by_edge_detection(image):
    """用边缘检测找到缺口位置"""
    import cv2
    
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(img_cv, 100, 200)
    
    # Look for vertical edges (gap boundaries are vertical lines)
    # Sum along y-axis to find x positions with many vertical edges
    col_sums = np.sum(edges, axis=0)
    
    # Skip the first 20% (slide piece is usually on the left)
    start_idx = len(col_sums) // 5
    
    # Find the x position with maximum edge density after start
    if start_idx < len(col_sums):
        remaining = col_sums[start_idx:]
        gap_x = start_idx + np.argmax(remaining)
        return int(gap_x)
    
    return 0


def try_ddddocr():
    """使用 ddddocr 识别滑块距离"""
    try:
        import ddddocr
        
        # Check if we have the images
        if not os.path.exists('/tmp/captcha_bg.png'):
            return 0
        
        # ddddocr has a slider detection model
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        
        if os.path.exists('/tmp/captcha_slide.png'):
            # Use slider detection
            with open('/tmp/captcha_bg.png', 'rb') as f:
                bg_bytes = f.read()
            with open('/tmp/captcha_slide.png', 'rb') as f:
                slide_bytes = f.read()
            
            result = det.slide_match(slide_bytes, bg_bytes)
            if result:
                print(f"    ddddocr slide_match result: {result}")
                # Result is typically {'target': [x, y]}
                if isinstance(result, dict) and 'target' in result:
                    return result['target'][0]
        else:
            # Try with just the background image
            with open('/tmp/captcha_bg.png', 'rb') as f:
                bg_bytes = f.read()
            
            # Use detection model to find the gap
            det2 = ddddocr.DdddOcr(det=True, ocr=False, show_ad=False)
            result = det2.detection(bg_bytes)
            if result:
                print(f"    ddddocr detection result: {result}")
                # Parse detection result
                if isinstance(result, list) and result:
                    # Each item is [x1, y1, x2, y2, confidence]
                    for item in result:
                        if len(item) >= 4:
                            return item[0]  # x1 position
        
    except Exception as e:
        print(f"    ddddocr error: {e}")
    
    return 0


async def solve_image_select_captcha(page, captcha_info):
    """解决图片点选验证码"""
    print("Solving image select captcha...")
    # TODO: implement
    return False


async def solve_unknown_captcha(page, captcha_info):
    """处理未知类型验证码"""
    print("Trying to solve unknown captcha type...")
    
    # List all interactive elements
    elements = await page.evaluate('''() => {
        let interactive = document.querySelectorAll('button, a, input, [onclick], [class*=btn], [class*=click], [role=button]');
        return Array.from(interactive).map(el => ({
            tag: el.tagName,
            class: el.className?.toString()?.substring(0, 80) || '',
            id: el.id || '',
            text: el.innerText?.substring(0, 50) || '',
            rect: el.getBoundingClientRect(),
        }));
    }''')
    
    print(f"  Interactive elements: {len(elements)}")
    for el in elements[:10]:
        print(f"    {el['tag']}.{el['class'][:40]} - '{el['text'][:30]}'")
    
    return False


async def main():
    print("=" * 60)
    print("京东验证码自动解决 + 数据抓取")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-gpu',
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
        
        # 直接访问搜索页（会触发验证码）
        print("\n[1] Navigating to search page (expect captcha)...")
        try:
            await page.goto('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8',
                            wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"    Navigation error (might be ok): {e}")
        
        await page.wait_for_timeout(3000)
        current_url = page.url
        
        if 'risk_handler' in current_url:
            print("    Captcha triggered as expected")
            
            # Solve captcha
            solved = await solve_captcha(page, max_attempts=5)
            
            if solved:
                print("\n[3] ✅ Verification passed! Extracting data...")
                
                # Wait for page to load
                await page.wait_for_timeout(3000)
                
                # Scroll and extract products
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await page.wait_for_timeout(500)
                
                products = await page.evaluate('''() => {
                    let items = document.querySelectorAll('.gl-item, [data-sku]');
                    return Array.from(items).map(item => ({
                        sku: item.getAttribute('data-sku'),
                        name: (item.querySelector('.p-name em') || {}).innerText || '',
                        price: (item.querySelector('.p-price strong i') || {}).innerText || '',
                        shop: (item.querySelector('.p-shop a') || {}).innerText || '',
                        img: (item.querySelector('.p-img img'))?.getAttribute('data-lazy-img') || 
                             (item.querySelector('.p-img img'))?.src || '',
                    })).filter(p => p.sku && p.name);
                }''')
                
                print(f"    Found {len(products)} products!")
                for i, p_item in enumerate(products[:10], 1):
                    print(f"    {i}. [{p_item['sku']}] {p_item['name'][:40]} ¥{p_item['price']}")
                
                if products:
                    with open('/tmp/jd_products_solved.json', 'w') as f:
                        json.dump(products, f, ensure_ascii=False, indent=2)
                    print(f"\n    Saved {len(products)} products to /tmp/jd_products_solved.json")
            else:
                print("\n[3] ❌ Failed to solve captcha after all attempts")
                await page.screenshot(path='/tmp/jd_final_failure.png')
        else:
            print(f"    No captcha! URL: {current_url}")
            title = await page.title()
            print(f"    Title: {title}")
        
        await browser.close()


asyncio.run(main())
