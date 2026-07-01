"""
分析京东验证码页面结构 — 用 curl_cffi 快速获取
"""
from curl_cffi import requests
import re
import json

session = requests.Session(impersonate='chrome120')

# 1. 访问搜索页触发验证码
print("[1] 触发验证码...")
resp = session.get('https://search.jd.com/Search?keyword=宠物益生菌&enc=utf-8', timeout=15)
final_url = str(resp.url)
print(f"URL: {final_url[:100]}")
print(f"Status: {resp.status_code}, Size: {len(resp.text)} bytes")

html = resp.text

# 2. 分析验证码页面HTML
print("\n[2] 分析验证码页面...")

# 提取JS中的配置信息
configs = re.findall(r'window\.(\w+)\s*=\s*["\']([^"\']+)["\']', html)
for name, value in configs:
    print(f"  window.{name} = {value}")

# 提取所有外部JS链接
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print(f"\n外部JS ({len(scripts)}):")
for s in scripts:
    print(f"  {s}")

# 提取CSS
css_links = re.findall(r'<link[^>]+href="([^"]+)"', html)
print(f"\nCSS ({len(css_links)}):")
for c in css_links:
    print(f"  {c}")

# 3. 提取验证码相关参数
print("\n[3] 验证码参数...")
# 从URL提取参数
from urllib.parse import urlparse, parse_qs
parsed = urlparse(final_url)
params = parse_qs(parsed.query)
for k, v in params.items():
    print(f"  {k}: {v[0][:80]}")

# 4. 尝试加载验证码API
print("\n[4] 尝试验证码API...")

# JD验证码通常通过这些接口
captcha_apis = [
    'https://iv.jd.com/slide/g.html',
    'https://iv.jd.com/slide/getSlideImage',
    'https://verify.jd.com/getVerifyImage',
]

for api_url in captcha_apis:
    try:
        r = session.get(api_url, timeout=10)
        print(f"\n  {api_url.split('/')[-1]}:")
        print(f"    Status: {r.status_code}, Size: {len(r.content)} bytes")
        if r.status_code == 200 and len(r.content) > 100:
            print(f"    Content-Type: {r.headers.get('content-type', 'unknown')}")
            if 'image' in r.headers.get('content-type', ''):
                # Save image
                with open(f'/tmp/captcha_{api_url.split("/")[-1]}.png', 'wb') as f:
                    f.write(r.content)
                print(f"    ✅ Saved image!")
            elif 'json' in r.headers.get('content-type', '') or r.text.startswith('{'):
                print(f"    JSON: {r.text[:300]}")
    except Exception as e:
        print(f"  {api_url.split('/')[-1]}: Error - {e}")

# 5. 获取验证码JS，分析验证码加载逻辑
print("\n[5] 分析验证码JS...")
js_urls = [s for s in scripts if 'app.' in s or 'risk' in s]
for js_url in js_urls[:3]:
    if js_url.startswith('//'):
        js_url = 'https:' + js_url
    elif js_url.startswith('/'):
        js_url = 'https://cfe.m.jd.com' + js_url
    
    try:
        r = session.get(js_url, timeout=10)
        if r.status_code == 200:
            js_content = r.text
            print(f"\n  {js_url.split('/')[-1]}: {len(js_content)} bytes")
            
            # Look for captcha-related patterns
            patterns = [
                (r'slide|slider|滑块', 'slider'),
                (r'verify|验证', 'verify'),
                (r'captcha|验证码', 'captcha'),
                (r'getImage|loadImage|bg.*img', 'image loading'),
                (r'api.*slide|slide.*api', 'slide API'),
            ]
            
            for pat, desc in patterns:
                matches = re.findall(pat, js_content, re.IGNORECASE)
                if matches:
                    print(f"    Found '{desc}': {len(matches)} matches")
            
            # Look for API URLs in JS
            api_patterns = re.findall(r'["\'](https?://[^"\']+)["\']', js_content)
            relevant_apis = [a for a in api_patterns if any(kw in a.lower() for kw in ['slide', 'verify', 'captcha', 'image', 'challenge'])]
            if relevant_apis:
                print(f"    Relevant APIs:")
                for api in relevant_apis[:10]:
                    print(f"      {api}")
    except Exception as e:
        print(f"  JS fetch error: {e}")

# 6. 打印完整的验证码页面HTML（关键部分）
print("\n[6] 验证码页面HTML关键部分...")
# Remove JS/CSS content, keep structure
clean_html = re.sub(r'<script[^>]*>.*?</script>', '<script>...</script>', html, flags=re.DOTALL)
clean_html = re.sub(r'<style[^>]*>.*?</style>', '<style>...</style>', clean_html, flags=re.DOTALL)
print(clean_html[:3000])
