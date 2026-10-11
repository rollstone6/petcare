import undetected_chromedriver as uc
import time
import random

print("=== undetected-chromedriver with fixed binary ===")

options = uc.ChromeOptions()
options.binary_location = '/usr/bin/chromium-browser'
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

try:
    driver = uc.Chrome(options=options, use_subprocess=False)
    driver.set_page_load_timeout(30)
    
    print("✅ Browser started")
    
    # Visit homepage
    driver.get('https://www.jd.com/')
    time.sleep(3)
    print(f"Homepage: {driver.title}")
    
    # Try search
    driver.get('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8')
    time.sleep(5)
    print(f"Search: {driver.title}")
    print(f"URL: {driver.current_url}")
    
    if 'risk_handler' not in driver.current_url and '验证' not in driver.title:
        print("✅ SUCCESS!")
        
        # Extract products
        products = driver.execute_script('''
            return Array.from(document.querySelectorAll('.gl-item, [data-sku]')).map(el => ({
                sku: el.getAttribute('data-sku'),
                name: (el.querySelector('.p-name em') || {}).innerText || '',
                price: (el.querySelector('.p-price strong i') || {}).innerText || '',
            })).filter(p => p.sku);
        ''')
        print(f"Products: {len(products)}")
        for p in products[:5]:
            print(f"  {p}")
    else:
        print("❌ Blocked")
        
        # Check for captcha
        page_source = driver.page_source
        if '滑块' in page_source or 'slide' in page_source.lower():
            print("Slider captcha detected")
            
            # Try to find slider
            try:
                slider = driver.find_element('css selector', '.JDJRV-slide-btn, .slide_btn, [class*=slide-inner]')
                print(f"Found slider: {slider}")
                
                # Try to drag
                from selenium.webdriver.common.action_chains import ActionChains
                action = ActionChains(driver)
                action.click_and_hold(slider).perform()
                
                for i in range(30):
                    action.move_by_offset(random.randint(5, 15), random.randint(-2, 2)).perform()
                    time.sleep(0.05)
                
                action.release().perform()
                time.sleep(3)
                
                print(f"After drag: {driver.current_url}")
                if 'risk_handler' not in driver.current_url:
                    print("✅ Slider bypassed!")
            except Exception as e:
                print(f"Slider handling error: {e}")
        
        driver.save_screenshot('/tmp/jd_undetected.png')
    
    # Try detail page
    driver.get('https://item.jd.com/100012043978.html')
    time.sleep(3)
    print(f"\nDetail: {driver.title}")
    print(f"URL: {driver.current_url}")
    
    driver.quit()
    print("\nDone")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
