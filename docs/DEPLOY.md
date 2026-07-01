# 宠物宝（PetCare）— 部署文档

> 版本：v1.0 | 最后更新：2026-06-23

---

## 1. 部署架构

```
                     Internet
                        │
                        ▼
              Nginx (HTTPS :443)
              petcare.yjyblog.xyz
                │           │
        /api/*  │           │  /* (静态文件)
                ▼           ▼
        FastAPI :8000    React dist/
        SQLite DB
```

## 2. 服务器信息

| 项目 | 值 |
|------|-----|
| 公网 IP | 101.200.146.234 |
| 域名 | petcare.yjyblog.xyz |
| HTTPS | Let's Encrypt（自动续期） |
| 系统 | Ubuntu |
| 面板 | 宝塔 (8888) |

## 3. 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80/443 | 反向代理 + HTTPS |
| FastAPI | 8000 | 后端 API |
| Hugo 博客 | 8080 | 本地开发 |

## 4. 目录结构

```
/root/workspace/petcare/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── seed.py
│   │   └── routers/
│   ├── petcare.db        # SQLite 数据库
│   └── requirements.txt
├── frontend/             # React 前端
│   ├── src/
│   ├── dist/             # 构建产物
│   └── package.json
└── docs/                 # 文档
    ├── PRD.md
    ├── TECH.md
    ├── UI.md
    ├── API.md
    ├── TEST.md
    └── DEPLOY.md
```

## 5. 启动命令

### 后端
```bash
cd /root/workspace/petcare/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd /root/workspace/petcare/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 前端构建
```bash
cd /root/workspace/petcare/frontend
npm run build
```

## 6. Nginx 配置

```nginx
server {
    listen 443 ssl;
    server_name petcare.yjyblog.xyz;

    ssl_certificate     /etc/letsencrypt/live/petcare.yjyblog.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/petcare.yjyblog.xyz/privkey.pem;

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }

    # 前端静态文件
    root /root/workspace/petcare/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

server {
    listen 80;
    server_name petcare.yjyblog.xyz;
    return 301 https://$host$request_uri;
}
```

## 7. 维护命令

### 重启后端
```bash
kill $(lsof -ti:8000)
cd /root/workspace/petcare/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### 重新导入数据
```bash
cd /root/workspace/petcare/backend && PYTHONPATH=. python3 app/seed.py
```

### 重新构建前端
```bash
cd /root/workspace/petcare/frontend && npm run build
```

### 证书续期
```bash
certbot renew --dry-run  # 测试
certbot renew            # 正式续期（自动 crontab）
```

## 8. 防火墙

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 8080/tcp
```
