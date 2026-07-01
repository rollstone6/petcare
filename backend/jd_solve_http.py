"""
纯HTTP方案解决京东滑块验证码
1. curl_cffi 获取验证码图片
2. OpenCV 识别缺口位置
3. 生成人类轨迹并提交验证
4. 用验证后的cookies抓取商品数据
"""
from curl_cffi import requests
import json
import base64
import cv2
import numpy as np
from PIL import Image
import io
import random
import time
import re
from urllib.parse import quote

session = requests.Session(impersonate='chrome120')

def get_captcha_images():
    """获取验证码图片"""
    # 先触发验证码
    resp = session.get('https://search.jd.com/Search?keyword=宠物益生菌', timeout=15)
    print(f"[1] 触发验证: {resp.status_code}, URL: {str(resp.url)[:60]}...")
    
    # 获取验证码
    captcha_resp = session.get('https://iv.jd.com/slide/g.html', timeout=15)
    data = captcha_resp.json()
    
    print(f"[2] 验证码API字段: {list(data.keys())}")
    
    # 解码图片
    bg_img = None
    patch_img = None
    
    if data.get('bg'):
        try:
            bg_bytes = base64.b64decode(data['bg'])
            bg_img = Image.open(io.BytesIO(bg_bytes))
            bg_img.save('/tmp/captcha_bg.png')
            print(f"  背景图: {bg_img.size}")
        except Exception as e:
            print(f"  bg解码失败: {e}")
    
    if data.get('patch'):
        try:
            patch_bytes = base64.b64decode(data['patch'])
            patch_img = Image.open(io.BytesIO(patch_bytes))
            patch_img.save('/tmp/captcha_patch.png')
            print(f"  滑块图: {patch_img.size}")
        except Exception as e:
            print(f"  patch解码失败: {e}")
    
    return data, bg_img, patch_img


def find_gap_position(bg_img, patch_img):
    """用OpenCV模板匹配找到缺口X坐标"""
    bg_cv = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2GRAY)
    patch_cv = cv2.cvtColor(np.array(patch_img), cv2.COLOR_RGB2GRAY)
    
    # Canny边缘检测增强
    bg_edges = cv2.Canny(bg_cv, 100, 200)
    patch_edges = cv2.Canny(patch_cv, 100, 200)
    
    # 模板匹配
    result = cv2.matchTemplate(bg_edges, patch_edges, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    gap_x = max_loc[0]
    print(f"  模板匹配: gap_x={gap_x}px, confidence={max_val:.3f}")
    
    return gap_x


def find_gap_by_edge(bg_img):
    """用边缘检测找缺口"""
    bg_cv = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(bg_cv, 100, 200)
    
    # 按列求和，找垂直边缘最密集的位置
    col_sums = np.sum(edges, axis=0)
    
    # 跳过左边20%（滑块初始位置）
    start = len(col_sums) // 5
    if start < len(col_sums):
        gap_x = start + np.argmax(col_sums[start:])
        print(f"  边缘检测: gap_x={gap_x}px")
        return int(gap_x)
    return 0


def try_ddddocr_slide(bg_bytes, patch_bytes):
    """用ddddocr识别滑块位置"""
    try:
        import ddddocr
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        result = det.slide_match(patch_bytes, bg_bytes)
        if result and isinstance(result, dict) and 'target' in result:
            gap_x = result['target'][0]
            print(f"  ddddocr: gap_x={gap_x}px")
            return gap_x
    except Exception as e:
        print(f"  ddddocr失败: {e}")
    return 0


def generate_trajectory(distance):
    """生成人类拖拽轨迹（JSON格式）"""
    trajectory = []
    t = 0
    current = 0
    
    steps = random.randint(30, 50)
    
    for i in range(steps):
        progress = (i + 1) / steps
        
        # Ease-in-out
        if progress < 0.5:
            speed = 2 * progress * progress
        else:
            speed = 1 - (-2 * progress + 2) ** 2 / 2
        
        target_pos = int(distance * speed)
        dx = target_pos - current
        current = target_pos
        
        dy = random.randint(-2, 2)
        t += random.randint(8, 40)
        
        trajectory.append([dx, dy, t])
    
    # Overshoot + correction
    overshoot = random.randint(3, 12)
    t += random.randint(10, 30)
    trajectory.append([overshoot, 0, t])
    t += random.randint(20, 50)
    trajectory.append([-overshoot, 0, t])
    
    return trajectory


def submit_captcha(data, gap_x, trajectory):
    """提交验证码答案"""
    challenge = data.get('challenge', '')
    api_server = data.get('api_server', '//iv.jd.com/')
    
    # 构建完整的API地址
    if api_server.startswith('//'):
        api_server = 'https:' + api_server
    
    # 尝试多个可能的提交端点
    endpoints = [
        f'{api_server}slide/a.html',
        f'{api_server}slide/verify',
        f'{api_server}verify',
    ]
    
    print(f"\n[5] 提交验证...")
    print(f"  challenge: {challenge[:40]}...")
    print(f"  gap_x: {gap_x}")
    print(f"  轨迹步数: {len(trajectory)}")
    
    # 尝试不同的参数格式
    params_list = [
        # 格式1: 原始格式
        {
            'd': json.dumps(trajectory),
            'challenge': challenge,
            'w': data.get('width', 360),
            'x': gap_x,
            'y': data.get('y', 0),
            'o': data.get('o', ''),
        },
        # 格式2: 简化格式
        {
            'challenge': challenge,
            'x': gap_x,
            'y': data.get('y', 0),
            'd': json.dumps(trajectory),
        },
    ]
    
    for endpoint in endpoints:
        for params in params_list:
            try:
                # 尝试GET
                resp = session.get(endpoint, params=params, timeout=10)
                print(f"  GET {endpoint}: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"    响应: {resp.text[:200]}")
                    try:
                        result = resp.json()
                        if result.get('success'):
                            print(f"  ✅ 验证成功!")
                            return True
                    except:
                        pass
                
                # 尝试POST
                resp = session.post(endpoint, data=params, timeout=10)
                print(f"  POST {endpoint}: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"    响应: {resp.text[:200]}")
                    try:
                        result = resp.json()
                        if result.get('success'):
                            print(f"  ✅ 验证成功!")
                            return True
                    except:
                        pass
            except Exception as e:
                print(f"  错误: {e}")
    
    print("  ❌ 所有提交方式都失败")
    return False


def search_products(keyword):
    """用验证后的session搜索商品"""
    url = f'https://search.jd.com/Search?keyword={keyword}&enc=utf-8'
    resp = session.get(url, timeout=15)
    
    if 'risk_handler' not in str(resp.url) and len(resp.text) > 10000:
        # 解析商品数据
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'lxml')
        
        products = []
        items = soup.select('li.gl-item, [data-sku]')
        for item in items:
            sku = item.get('data-sku', '')
            name_el = item.select_one('.p-name em')
            price_el = item.select_one('.p-price strong i')
            
            if sku and name_el:
                products.append({
                    'sku_id': sku,
                    'name': name_el.get_text(strip=True),
                    'price': price_el.get_text(strip=True) if price_el else '',
                    'url': f'https://item.jd.com/{sku}.html',
                })
        
        return products
    return []


def main():
    print("=" * 60)
    print("京东滑块验证码自动解决方案（纯HTTP）")
    print("=" * 60)
    
    # 多尝试几次
    for attempt in range(1, 6):
        print(f"\n{'='*40}")
        print(f"尝试 #{attempt}")
        print(f"{'='*40}")
        
        # 1. 获取验证码
        data, bg_img, patch_img = get_captcha_images()
        
        if not bg_img:
            print("  ❌ 无法获取背景图，跳过")
            time.sleep(2)
            continue
        
        # 2. 识别缺口位置
        print(f"\n[3] 识别缺口位置...")
        gap_x = 0
        
        # 方法1: 模板匹配
        if bg_img and patch_img:
            gap_x = find_gap_position(bg_img, patch_img)
        
        # 方法2: ddddocr
        if gap_x == 0:
            bg_bytes = base64.b64decode(data['bg'])
            patch_bytes = base64.b64decode(data.get('patch', ''))
            gap_x = try_ddddocr_slide(bg_bytes, patch_bytes)
        
        # 方法3: 边缘检测
        if gap_x == 0:
            gap_x = find_gap_by_edge(bg_img)
        
        if gap_x == 0:
            print("  ❌ 所有方法都找不到缺口")
            time.sleep(2)
            continue
        
        # 3. 生成轨迹
        print(f"\n[4] 生成拖拽轨迹...")
        trajectory = generate_trajectory(gap_x)
        print(f"  轨迹: {len(trajectory)} 步, 终点={sum(t[0] for t in trajectory)}px")
        
        # 4. 提交验证
        success = submit_captcha(data, gap_x, trajectory)
        
        if success:
            print(f"\n🎉 验证码解决成功！")
            
            # 5. 搜索商品
            print(f"\n[6] 搜索商品...")
            products = search_products('宠物益生菌')
            print(f"  找到 {len(products)} 个商品")
            
            for i, p in enumerate(products[:10], 1):
                print(f"  {i}. [{p['sku_id']}] {p['name'][:40]} ¥{p['price']}")
            
            if products:
                with open('/tmp/jd_products_solved.json', 'w') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"\n  已保存到 /tmp/jd_products_solved.json")
            return
        else:
            print(f"  ❌ 验证失败，重试...")
            time.sleep(2)
    
    print("\n❌ 5次尝试均失败")


if __name__ == '__main__':
    main()
