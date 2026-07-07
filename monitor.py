#!/usr/bin/env python3
"""宠物宝 PetCare 健康监控脚本"""
import json
import time
import subprocess
import sys

SITE = "https://petcare.yjyblog.xyz"
API = "http://localhost:8000"
REPORT = []
ISSUES = []

def check(name, fn):
    try:
        ok, detail = fn()
        status = "✅" if ok else "❌"
        REPORT.append(f"  {status} {name}: {detail}")
        if not ok:
            ISSUES.append(f"{name}: {detail}")
    except Exception as e:
        REPORT.append(f"  ❌ {name}: 异常 - {e}")
        ISSUES.append(f"{name}: {e}")

def curl(url, timeout=10, want_json=False):
    cmd = ["curl", "-s", "-L", "-o", "/dev/null", "-w", "%{http_code}|%{time_total}|%{size_download}", "--max-time", str(timeout), url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    parts = r.stdout.strip().split("|")
    code = int(parts[0]) if parts[0].isdigit() else 0
    t = float(parts[1]) if len(parts) > 1 else 0
    size = int(parts[2]) if len(parts) > 2 else 0
    return code, t, size

def curl_body(url, timeout=10):
    cmd = ["curl", "-s", "-L", "--max-time", str(timeout), url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    return r.stdout

# === 1. Nginx ===
def check_nginx():
    r = subprocess.run(["pgrep", "-c", "nginx"], capture_output=True, text=True)
    count = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    return count > 0, f"{count} 个进程运行中"

# === 2. 后端 API 基础连通 ===
def check_api_root():
    code, t, _ = curl(f"{API}/")
    return code == 200, f"HTTP {code}, {t:.2f}s"

# === 3. 前端页面 (HTTPS) ===
def check_frontend():
    code, t, size = curl(SITE)
    return code == 200 and size > 500, f"HTTP {code}, {size} bytes, {t:.2f}s"

# === 4. 商品数据 API ===
def check_products():
    body = curl_body(f"{API}/api/products?page=1&size=5")
    data = json.loads(body)
    # API 返回 {"code":0,"data":{"items":[],"total":N}}
    inner = data.get("data", data)
    total = inner.get("total", 0)
    items = inner.get("items", [])
    return total > 0 and len(items) > 0, f"共 {total} 个商品, 返回 {len(items)} 条"

# === 5. 品牌数据 ===
def check_brands():
    body = curl_body(f"{API}/api/brands")
    data = json.loads(body)
    inner = data.get("data", data)
    items = inner.get("items", inner) if isinstance(inner, dict) else inner
    count = len(items) if isinstance(items, list) else inner.get("total", 0)
    return count > 0, f"{count} 个品牌"

# === 6. 分类数据 ===
def check_categories():
    body = curl_body(f"{API}/api/categories")
    data = json.loads(body)
    inner = data.get("data", data)
    items = inner.get("items", inner) if isinstance(inner, dict) else inner
    count = len(items) if isinstance(items, list) else inner.get("total", 0)
    return count > 0, f"{count} 个分类"

# === 7. 品种数据 ===
def check_breeds():
    body = curl_body(f"{API}/api/breeds")
    data = json.loads(body)
    inner = data.get("data", data)
    items = inner.get("items", inner) if isinstance(inner, dict) else inner
    count = len(items) if isinstance(items, list) else inner.get("total", 0)
    return count > 0, f"{count} 个品种"

# === 8. 商品图片可访问 ===
def check_images():
    body = curl_body(f"{API}/api/products?page=1&size=3")
    data = json.loads(body)
    inner = data.get("data", data)
    items = inner.get("items", [])
    for p in items:
        img = p.get("image_url", "")
        if img and img.startswith("http"):
            code, t, _ = curl(img, timeout=5)
            if code != 200:
                return False, f"图片不可访问: {img[:60]}... (HTTP {code})"
    return True, f"商品图片正常 ({len(items)} 张测试)"

# === 9. SSL 证书有效期 ===
def check_ssl():
    cmd = ["openssl", "s_client", "-connect", "petcare.yjyblog.xyz:443", "-servername", "petcare.yjyblog.xyz"]
    r = subprocess.run(cmd, input="", capture_output=True, text=True, timeout=10)
    cmd2 = ["openssl", "x509", "-noout", "-enddate"]
    r2 = subprocess.run(cmd2, input=r.stdout, capture_output=True, text=True, timeout=10)
    endline = r2.stdout.strip()
    if "notAfter" in endline:
        datestr = endline.split("=")[1].strip()
        return True, f"到期: {datestr}"
    return False, "无法读取证书信息"

# === 10. API 响应时间 ===
def check_api_speed():
    code, t, _ = curl(f"{API}/api/products/?page=1&size=5")
    ok = code == 200 and t < 2.0
    return ok, f"{t:.2f}s ({'正常' if t < 2 else '偏慢'})"

# === 11. Nginx HTTPS 代理 ===
def check_https_proxy():
    code, t, size = curl(f"{SITE}/api/products/?page=1&size=1")
    return code == 200, f"HTTP {code}, {t:.2f}s"

# 执行所有检查
check("Nginx 进程", check_nginx)
check("后端 API 基础", check_api_root)
check("前端页面(HTTPS)", check_frontend)
check("商品数据", check_products)
check("品牌数据", check_brands)
check("分类数据", check_categories)
check("品种数据", check_breeds)
check("商品图片", check_images)
check("SSL 证书", check_ssl)
check("API 响应速度", check_api_speed)
check("HTTPS 代理", check_https_proxy)

# 输出报告
ts = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"🐾 宠物宝监控报告 [{ts}]")
print("=" * 50)
for line in REPORT:
    print(line)
print("=" * 50)

if ISSUES:
    print(f"\n⚠️ 发现 {len(ISSUES)} 个问题:")
    for i in ISSUES:
        print(f"  - {i}")
    
    # 尝试自动修复后端
    for issue in ISSUES:
        if "后端" in issue or "API" in issue:
            print("\n🔧 尝试重启后端...")
            subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
            time.sleep(1)
            subprocess.Popen(
                "cd /root/workspace/petcare/backend && source browseract-env/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000",
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            code, t, _ = curl(f"http://localhost:8000/")
            if code == 200:
                print("  ✅ 后端已恢复")
            else:
                print(f"  ❌ 后端重启失败 (HTTP {code})")
            break
else:
    print("\n✅ 所有服务正常运行")

sys.exit(1 if ISSUES else 0)
