# 宠物宝（PetCare）— 技术文档 v2.0

> 对标：美丽修行 (bevol.cn) | 版本：v2.0 | 最后更新：2026-06-23

---

## 1. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + Vite + Tailwind CSS 3 | SPA，移动端优先，PWA 可安装 |
| **路由** | React Router v6 | 客户端路由 |
| **状态管理** | React Context + useReducer | 轻量级，够用 |
| **HTTP 客户端** | fetch / axios | API 调用 |
| **后端** | Python FastAPI | 自动 OpenAPI 文档 |
| **ORM** | SQLAlchemy 2.0 | 数据库操作 |
| **数据库** | SQLite → PostgreSQL | MVP 用 SQLite |
| **认证** | JWT (python-jose) | 用户系统 |
| **部署** | Nginx + Let's Encrypt | petcare.yjyblog.xyz |
| **HTTPS** | Certbot 自动续期 | 90天自动续 |

---

## 2. 前端项目结构

```
frontend/
├── public/
│   ├── manifest.json        # PWA 配置
│   └── icons/               # App 图标
├── src/
│   ├── main.jsx             # 入口
│   ├── App.jsx              # 根组件 + 路由
│   ├── index.css            # Tailwind + 全局样式
│   ├── api/
│   │   └── client.js        # API 客户端封装
│   ├── context/
│   │   └── AppContext.jsx   # 全局状态
│   ├── pages/
│   │   ├── Home.jsx         # 首页
│   │   ├── Search.jsx       # 搜索页
│   │   ├── ProductDetail.jsx # 产品详情
│   │   ├── IngredientDetail.jsx # 成分详情
│   │   ├── BreedDetail.jsx  # 品种详情
│   │   ├── Compare.jsx      # 产品对比
│   │   └── Profile.jsx      # 个人中心
│   ├── components/
│   │   ├── Layout.jsx       # 布局（顶部导航+底部Tab）
│   │   ├── SearchBar.jsx    # 搜索栏
│   │   ├── ProductCard.jsx  # 产品卡片
│   │   ├── IngredientTag.jsx # 成分标签
│   │   ├── SafetyScore.jsx  # 安全评分组件
│   │   ├── CategoryGrid.jsx # 分类宫格
│   │   └── BottomNav.jsx    # 底部导航栏
│   └── utils/
│       └── helpers.js       # 工具函数
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## 3. 后端项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 模型
│   ├── seed.py              # 种子数据
│   ├── auth.py              # JWT 认证
│   └── routers/
│       ├── products.py      # 产品 API
│       ├── ingredients.py   # 成分 API
│       ├── brands.py        # 品牌 API
│       ├── categories.py    # 品类 API
│       ├── breeds.py        # 品种 API
│       ├── users.py         # 用户 API
│       └── favorites.py     # 收藏 API
├── requirements.txt
└── petcare.db               # SQLite 数据库
```

---

## 4. 数据库设计

### 现有表（已实现）
- `brands` — 品牌（52个）
- `categories` — 品类（40个：药品17 + 食品7 + 保健品9）
- `ingredients` — 成分（31种药品成分）
- `products` — 产品（186个，含target_size/target_age字段）
- `pet_breeds` — 品种（62个：狗34 + 猫28，含size/age_stage字段）
- `product_ingredient` — 产品-成分关联
- `breed_product` — 品种-产品推荐（9149条，按物种+体型智能关联）
- `users` — 用户
- `favorites` — 收藏
- `reviews` — 评价
- `browse_history` — 浏览历史
- `pet_profiles` — 用户宠物档案
- `health_records` — 健康记录（便便/饮水/呕吐/体重等）
- `schedules` — 日程提醒（驱虫/疫苗/体检）

### 关键字段说明
- `Product.suitable_species` — 物种：猫/狗/猫狗（标准化，无变体）
- `Product.target_size` — 体型：全部/小型/中型/大型/小型中型/中大型
- `Product.target_age` — 年龄：全部/幼年/成年/老年/成年老年
- `PetBreed.size` — 品种体型：小型/中型/大型（狗），中型（猫）
- `Product.approval_number` — JD:{wareId}（京东商品溯源）

---

## 5. 部署架构

```
                     Internet
                        │
                        ▼
              ┌─────────────────┐
              │  Nginx :443      │
              │  petcare.yjyblog │
              │  (Let's Encrypt) │
              └──────┬──────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   /api/*       /docs       / (静态文件)
   FastAPI      Swagger     React SPA
   :8000        :8000       /frontend/dist
```

---

## 6. PWA 配置

```json
{
  "name": "宠物宝 PetCare",
  "short_name": "宠物宝",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#10B981",
  "background_color": "#ffffff",
  "icons": [...]
}
```

---

## 7. 移动端适配策略

- **Tailwind 响应式断点**：sm(640) / md(768) / lg(1024)
- **底部 Tab 导航**（移动端固定底部，5个Tab）
- **触摸优化**：大按钮、滑动操作
- **PWA**：可添加到手机主屏幕，离线缓存
