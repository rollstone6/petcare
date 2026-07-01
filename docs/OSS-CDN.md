# 宠物宝 — 静态资源 OSS + CDN 迁移方案

> 版本：v1.0 | 目标：将全部静态资源迁移到阿里云 OSS，开启 CDN 加速

---

## 一、当前架构 vs 目标架构

```
当前：
  用户 → Nginx(ECS) → 静态文件(/var/www/petcare/)
                    → API(/api/* → FastAPI:8000)

目标：
  用户 → CDN(aliyuncs.com) → OSS(静态文件)
       → Nginx(ECS) → API(/api/* → FastAPI:8000)
```

---

## 二、需要迁移的静态资源

| 类型 | 路径 | 大小 | 迁移优先级 |
|------|------|------|-----------|
| 品种头像 PNG | `/avatars/*.png` | ~800KB (24个) | ⭐⭐⭐ 高 |
| JS Bundle | `/assets/*.js` | ~200KB | ⭐⭐⭐ 高 |
| CSS | `/assets/*.css` | ~20KB | ⭐⭐ 中 |
| PWA 文件 | `/sw.js`, `/workbox-*.js` | ~15KB | ⭐ 低 |
| SVG 图标 | `/*.svg` | ~15KB | ⭐ 低 |
| HTML | `/index.html` | ~1KB | ❌ 不迁移(Nginx直出) |

**关键**：HTML 入口文件保留在 ECS，其余全部上 OSS。

---

## 三、阿里云 OSS 配置步骤

### 1. 创建 OSS Bucket
```
控制台: https://oss.console.aliyun.com/
Bucket 名称: petcare-static
区域: 与 ECS 同区域（减少内网流量费用）
存储类型: 标准存储
读写权限: 公共读（Public Read）
```

### 2. 配置 CDN 加速
```
控制台: https://cdn.console.aliyun.com/
添加域名: cdn.petcare.yjyblog.xyz（或 static.petcare.yjyblog.xyz）
源站: petcare-static.oss-cn-{region}.aliyuncs.com
加速区域: 仅中国大陆（或全球）
```

### 3. DNS 配置
```
类型: CNAME
主机记录: cdn（或 static）
记录值: {CDN 提供的 CNAME 地址}
```

---

## 四、自动上传脚本

```bash
#!/bin/bash
# deploy-static.sh — 构建并上传静态资源到 OSS

BUCKET="petcare-static"
OSS_ENDPOINT="oss-cn-beijing.aliyuncs.com"  # 根据实际区域修改
CDN_URL="https://cdn.petcare.yjyblog.xyz"

# 1. 构建前端
cd /root/workspace/petcare/frontend
npm run build

# 2. 上传到 OSS（排除 index.html）
ossutil cp -r dist/ oss://${BUCKET}/ \
  --exclude "index.html" \
  --exclude "*.map" \
  --update

# 3. 刷新 CDN 缓存
aliyun cdn RefreshObjectCaches \
  --ObjectPath "https://cdn.petcare.yjyblog.xyz/" \
  --ObjectType Directory

echo "✅ 静态资源已上传到 OSS + CDN"
```

### 安装 ossutil
```bash
wget https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil64
chmod +x ossutil64
./ossutil64 config  # 输入 AccessKey ID / Secret / Endpoint
```

---

## 五、前端构建配置修改

### vite.config.js 添加 base 配置

```js
export default defineConfig({
  base: process.env.CDN_URL || '/',  // 生产环境使用 CDN
  // ...
})
```

### package.json 添加脚本

```json
{
  "scripts": {
    "build:cdn": "CDN_URL=https://cdn.petcare.yjyblog.xyz vite build",
    "deploy:cdn": "npm run build:cdn && bash deploy-static.sh"
  }
}
```

---

## 六、Nginx 配置修改

```nginx
server {
    listen 443 ssl;
    server_name petcare.yjyblog.xyz;

    # API 代理（不变）
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
    }

    # HTML 入口 — 从本地读取
    location = /index.html {
        root /var/www/petcare;
    }

    # 静态资源 — 301 重定向到 CDN
    # （或者保持本地读取作为回源，CDN 在前端代码中通过 base 配置）
}
```

**推荐方案**：使用 `vite.config.js` 的 `base` 配置，让前端代码中的资源路径自动指向 CDN，无需改 Nginx。

---

## 七、成本估算

| 项目 | 月费用估算 |
|------|-----------|
| OSS 存储（1GB） | ¥0.12 |
| OSS 外网流量（100GB/月） | ¥50 |
| CDN 流量（100GB/月） | ¥24 |
| CDN HTTPS 请求 | ¥0.05/万次 |
| **合计** | **约 ¥75/月** |

---

## 八、执行清单

- [ ] 创建 OSS Bucket（阿里云控制台）
- [ ] 获取 AccessKey（RAM 子账号，仅 OSS 权限）
- [ ] 安装 ossutil 并配置
- [ ] 创建 CDN 加速域名
- [ ] 添加 DNS CNAME 记录
- [ ] 修改 vite.config.js base 配置
- [ ] 运行首次上传
- [ ] 验证 CDN 可访问
- [ ] 更新前端代码中硬编码的静态路径
