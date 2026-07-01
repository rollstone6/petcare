"""
直接调用京东滑块验证码API，获取图片并分析
"""
from curl_cffi import requests
import re
import json
import base64

session = requests.Session(impersonate='chrome120')

print("[1] 获取验证码图片...")
# 先访问搜索触发验证
resp = session.get('https://search.jd.com/Search?keyword=宠物益生菌', timeout=15)
print(f"触发验证: {resp.url[:80]}...")

# 获取验证码
captcha_resp = session.get('https://iv.jd.com/slide/g.html', timeout=15)
print(f"\n验证码API状态: {captcha_resp.status_code}")
print(f"Content-Type: {captcha_resp.headers.get('content-type')}")
print(f"响应大小: {len(captcha_resp.text)} bytes")

# 尝试解析为JSON
try:
    data = captcha_resp.json()
    print(f"\nJSON字段: {list(data.keys())}")
    
    # 保存完整响应
    with open('/tmp/captcha_response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("完整响应已保存到 /tmp/captcha_response.json")
    
    # 提取图片
    if 'patch' in data:
        patch_b64 = data['patch']
        print(f"\npatch字段长度: {len(patch_b64)}")
        
        # 解码base64图片
        try:
            img_data = base64.b64decode(patch_b64)
            with open('/tmp/captcha_patch.png', 'wb') as f:
                f.write(img_data)
            print(f"✅ 背景图已保存: /tmp/captcha_patch.png ({len(img_data)} bytes)")
        except Exception as e:
            print(f"解码失败: {e}")
    
    if 'y' in data:
        y_b64 = data['y']
        print(f"\ny字段长度: {len(y_b64)}")
        
        try:
            img_data = base64.b64decode(y_b64)
            with open('/tmp/captcha_y.png', 'wb') as f:
                f.write(img_data)
            print(f"✅ 滑块图已保存: /tmp/captcha_y.png ({len(img_data)} bytes)")
        except Exception as e:
            print(f"解码失败: {e}")
    
    # 打印其他关键字段
    for key in ['challenge', 'token', 'width', 'height']:
        if key in data:
            print(f"{key}: {data[key]}")
    
    # 打印前500字符看看结构
    print(f"\n响应预览:")
    print(json.dumps(data, ensure_ascii=False)[:500])
    
except Exception as e:
    print(f"JSON解析失败: {e}")
    print(f"响应内容: {captcha_resp.text[:500]}")
