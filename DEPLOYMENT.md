# 宠物宝 (PetCare) 部署运维手册

## 📋 项目架构

```
宠物宝 (PetCare)
├── 后端 (FastAPI)     → http://localhost:8000
├── 前端 (React)       → /var/www/petcare/
├── 数据库 (SQLite)    → backend/data/petcare.db
└── 定时任务 (Cron)    → 2个自动化任务
```

**访问地址**: https://petcare.yjyblog.xyz

---

## 🚀 启动服务

### 1. 启动后端 API 服务

```bash
cd /root/workspace/petcare/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**后台运行**（推荐）:
```bash
cd /root/workspace/petcare/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/petcare.log 2>&1 &
```

**验证启动成功**:
```bash
# 检查进程
ps aux | grep "uvicorn app.main:app" | grep -v grep

# 测试 API
curl http://localhost:8000/api/products?page_size=1
```

### 2. 前端部署

前端已编译部署到 `/var/www/petcare/`，通过 Nginx 提供服务。

**重新构建前端**:
```bash
cd /root/workspace/petcare/frontend
npm run build
```

构建脚本会自动复制 dist 目录到 `/var/www/petcare/`。

### 3. Nginx 配置

Nginx 配置文件: `/etc/nginx/sites-available/petcare`

```nginx
server {
    listen 80;
    server_name petcare.yjyblog.xyz;

    root /var/www/petcare;
    index index.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**重启 Nginx**:
```bash
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

---

## 🔄 日常运维

### 检查服务状态

```bash
# 检查后端进程
ps aux | grep "uvicorn app.main:app" | grep -v grep

# 检查后端日志
tail -f /tmp/petcare.log

# 检查 Nginx 状态
sudo systemctl status nginx

# 测试 API 响应
curl -s http://localhost:8000/api/products?page_size=1 | jq
```

### 重启后端服务

```bash
# 停止旧进程
pkill -f "uvicorn app.main:app"

# 重新启动
cd /root/workspace/petcare/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/petcare.log 2>&1 &

# 等待启动
sleep 3

# 验证
curl http://localhost:8000/api/products?page_size=1
```

### 更新代码并重新部署

```bash
# 1. 拉取最新代码
cd /root/workspace/petcare
git pull origin main

# 2. 安装后端依赖（如有更新）
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. 构建前端
cd ../frontend
npm install
npm run build

# 4. 重启后端
pkill -f "uvicorn app.main:app"
cd ../backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/petcare.log 2>&1 &

# 5. 验证部署
sleep 3
curl http://localhost:8000/api/products?page_size=1
```

---

## 📊 数据库维护

### 查看数据库统计

```bash
cd /root/workspace/petcare/backend
source venv/bin/activate
python3 << 'EOF'
from app.database import SessionLocal
from app import models
from sqlalchemy import func

db = SessionLocal()
products = db.query(models.Product).count()
brands = db.query(models.Brand).count()
categories = db.query(models.Category).count()
ingredients = db.query(models.Ingredient).count()

print(f"产品: {products}")
print(f"品牌: {brands}")
print(f"品类: {categories}")
print(f"成分: {ingredients}")
db.close()
EOF
```

### 数据库备份

```bash
# 创建备份目录
mkdir -p /root/workspace/petcare/backups

# 备份数据库
cp backend/data/petcare.db backups/petcare_$(date +%Y%m%d_%H%M%S).db

# 保留最近7天的备份
find backups/ -name "petcare_*.db" -mtime +7 -delete
```

### 数据库迁移

**注意**: 当前使用手动 ALTER TABLE 方式，不使用 Alembic。

```bash
cd /root/workspace/petcare/backend
source venv/bin/activate
python3 << 'EOF'
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 示例：添加新字段
try:
    db.execute(text("ALTER TABLE products ADD COLUMN new_field TEXT"))
    db.commit()
    print("迁移成功")
except Exception as e:
    print(f"迁移失败: {e}")
    db.rollback()

db.close()
EOF
```

---

## ⏰ 定时任务

已配置 2 个 Cron 任务：

### 1. 计划检查（每小时）

- **任务ID**: `124cbce4bfbd`
- **频率**: 每小时
- **功能**: 检查数据库统计、构建状态、头像文件
- **日志**: `/root/workspace/petcare/logs/plan-check.log`

**查看任务**:
```bash
hermes cron list
```

### 2. 每日总结（8:00推送微信）

- **任务ID**: `cf08f3cfbdc7`
- **频率**: 每天早上 8:00
- **功能**: 生成变更总结并推送到微信
- **推送目标**: `weixin:o9cq80wqnbrl9dNQzKokNIvVSRK0@im.wechat`

**手动触发**:
```bash
hermes cron run cf08f3cfbdc7
```

---

## 🛠️ 常见问题

### 1. 后端服务无法启动

**症状**: 启动后立即退出

**排查步骤**:
```bash
# 查看详细错误
cd /root/workspace/petcare/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 检查端口占用
lsof -i :8000

# 检查 Python 版本
python3 --version  # 需要 3.12+
```

### 2. API 返回 500 错误

**排查步骤**:
```bash
# 查看后端日志
tail -100 /tmp/petcare.log

# 检查数据库连接
cd /root/workspace/petcare/backend
source venv/bin/activate
python3 -c "from app.database import SessionLocal; print(SessionLocal())"
```

### 3. 前端页面白屏

**排查步骤**:
```bash
# 检查 Nginx 错误日志
sudo tail -50 /var/log/nginx/error.log

# 检查前端文件是否存在
ls -la /var/www/petcare/index.html

# 检查浏览器控制台错误
# 打开 https://petcare.yjyblog.xyz 按 F12 查看 Console
```

### 4. SSH 连接断开

**解决方案**: 已配置 SSH KeepAlive

```bash
# 服务端配置（已设置）
ClientAliveInterval 30
ClientAliveCountMax 3

# 客户端配置（~/.ssh/config）
Host *
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

---

## 📝 开发工作流

### 本地开发

```bash
# 1. 启动后端（开发模式，自动重载）
cd /root/workspace/petcare/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. 启动前端（开发模式）
cd /root/workspace/petcare/frontend
npm run dev
```

访问: http://localhost:5173

### 提交代码

```bash
cd /root/workspace/petcare
git add .
git commit -m "feat: 描述你的更改"
git push origin main
```

---

## 📚 相关资源

- **项目文档**: `/root/workspace/petcare/PROJECT.md`
- **API 文档**: https://petcare.yjyblog.xyz/docs
- **数据规则**: `/root/workspace/petcare/DATA_RULES.md`
- **监控脚本**: `/root/workspace/petcare/scripts/`
- **日志文件**: `/root/workspace/petcare/logs/`

---

## 🔐 安全注意事项

1. **数据库文件**: `backend/data/petcare.db` 包含用户数据，定期备份
2. **API 密钥**: 存储在 `.env` 文件中，不要提交到 Git
3. **JWT 密钥**: 在 `.env` 中配置，生产环境使用强随机字符串
4. **Nginx 限流**: 已配置 API 20r/s + 静态 100r/s + 连接数 20/IP

---

## 📞 联系支持

如有问题，查看日志或联系开发者。

**最后更新**: 2026-07-03
