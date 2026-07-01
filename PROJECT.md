# 宠物宝（PetCare）— 项目主文档

> 对标：美丽修行 (bevol.cn) — 宠物版成分查询与安全评分平台
> 本地路径：`/root/workspace/petcare/`

---

## 📋 项目概览

| 项目 | 内容 |
|------|------|
| **产品名** | 宠物宝（PetCare） |
| **域名** | `https://petcare.yjyblog.xyz` |
| **定位** | 宠物药品/食品/保健品成分查询与安全评分平台 |
| **对标** | 美丽修行 (bevol.cn) |
| **技术栈** | React + FastAPI + SQLite + Nginx |
| **部署** | 本机 Nginx + Let's Encrypt HTTPS |

---

## 🚩 当前状态

```
Phase 1 数据层 ✅ → Phase 2 后端 API ✅ → Phase 3 前端 ✅ → Phase 4 用户系统 ✅ → Phase 5 优化 ✅
```

### ✅ 已完成

- [x] 项目调研（宠物药品/食品/市场分析）
- [x] 项目文档体系（PRD/TECH/API/TEST/PROJECT）
- [x] 数据库模型设计（10张表：products/ingredients/brands/categories/pet_breeds/users/favorites/reviews/health_records/schedules）
- [x] 种子数据（20品牌/18品类/65成分/24品种/47产品）
- [x] FastAPI 后端 API（产品/成分/品牌/品类/品种/用户/收藏/评论/日程/健康记录/AI）
- [x] Nginx + Let's Encrypt HTTPS 部署
- [x] 子域名 petcare.yjyblog.xyz 配置
- [x] 前端 MVP（React + Vite + Tailwind CSS）
- [x] 用户系统（注册/登录/JWT/收藏）
- [x] 安全评分算法 v2（成分排序权重 + 相互作用 + 高风险惩罚 + 类型系数）
- [x] 产品对比功能（整合进搜索页）
- [x] 用户评价/评论（评分+评论+匿名+删除）
- [x] AI 成分问答
- [x] 安全加固（端口收敛 + Nginx 限流 + 爬虫拦截）
- [x] 日程看板（驱虫/疫苗/体检倒计时 + .ics 日历导出）
- [x] PWA 离线支持（Service Worker + manifest + 图标）
- [x] 搜索"全部"修复（点击类型tab即触发搜索）
- [x] 移动端/桌面端适配优化

### 📊 数据规模

| 数据类型 | 数量 | 说明 |
|----------|------|------|
| 产品 | 47 | 药品13 + 食品22 + 保健品12 |
| 成分 | 65 | 药品成分31 + 食品成分34 |
| 品牌 | 20 | 国内外知名品牌 |
| 品类 | 18 | 药品7 + 食品5 + 保健品6 |
| 品种 | 24 | 犬猫各12个品种（含kawaii头像） |

### ⏳ 待办

- [ ] 扩充产品数据（更多品牌/产品导入）
- [ ] 阿里云 OSS + CDN 迁移（待创建 Bucket）

---

## 📁 项目结构

```
petcare/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库
│   │   ├── models.py        # 数据模型
│   │   ├── schemas.py       # Pydantic 模型
│   │   ├── scoring.py       # 安全评分算法 v2
│   │   ├── auth.py          # JWT 认证
│   │   ├── seed.py          # 种子数据
│   │   └── routers/         # API 路由
│   │       ├── products.py
│   │       ├── ingredients.py
│   │       ├── brands.py
│   │       ├── categories.py
│   │       ├── breeds.py
│   │       ├── users.py
│   │       ├── favorites.py
│   │       ├── reviews.py
│   │       ├── schedules.py
│   │       ├── records.py
│   │       └── ai.py
│   ├── requirements.txt
│   └── petcare.db           # SQLite 数据库
├── frontend/                # React 前端
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   └── api/             # API 客户端
│   ├── public/              # 静态资源
│   └── vite.config.js       # Vite + PWA 配置
├── docs/                    # 文档
│   ├── PRD.md
│   ├── TECH.md
│   ├── API.md
│   └── TEST.md
└── PROJECT.md               # 本文件
```

---

## 🔧 常用命令

```bash
# 启动后端（生产环境用 nohup 或 systemd）
cd /root/workspace/petcare/backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 重新计算安全评分
cd /root/workspace/petcare/backend
python3 -c "from app.database import SessionLocal; from app.scoring import recalculate_all_scores; db=SessionLocal(); recalculate_all_scores(db); db.close()"

# 构建前端
cd /root/workspace/petcare/frontend
npm run build  # 自动复制到 /var/www/petcare/

# 测试 API
curl https://petcare.yjyblog.xyz/api/products

# 重启 nginx
systemctl reload nginx

# 证书续期
certbot renew
```

---

## 🔗 相关链接

- 网站：https://petcare.yjyblog.xyz
- API：https://petcare.yjyblog.xyz/api/
- 文档：https://petcare.yjyblog.xyz/docs
- 博客：https://yjyblog.xyz
