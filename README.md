# 🐾 宠物宝 PetCare

> 专业的宠物食品/药品/保健品成分查询与安全评分平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)

## 📖 项目简介

**宠物宝（PetCare）**是一个对标"美丽修行"的宠物版成分查询与安全评分平台。通过 AI 驱动的智能分析系统，帮助宠物主人快速了解宠物食品、药品、保健品的成分安全性，做出更明智的选择。

### 🌟 核心特性

- **📊 安全评分系统**：基于成分分析的智能安全评分（1-10分制），涵盖毒性、刺激性、致癌风险等多维度评估
- **🔍 智能搜索**：支持按成分、品牌、品种、体型等多维度筛选，快速找到适合的宠物产品
- **🤖 AI 问答**：集成大语言模型，提供专业的宠物营养咨询和成分解读
- **🐕 品种百科**：收录 92 个常见宠物品种（62犬种+30猫种），配备专业漫画头像
- **📈 数据驱动**：整合京东等电商平台真实销售数据，持续更新产品信息
- **🎯 个性化推荐**：根据宠物品种、体型、年龄提供定制化产品推荐
- **📱 多端支持**：Web 端（React）+ 微信小程序（uni-app）
- **🔒 隐私保护**：支持匿名评论，用户数据本地化存储

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Web (React) │  │ 微信小程序   │  │  PWA 离线    │       │
│  │  Vite + TS   │  │  uni-app     │  │  Service Worker│     │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                          │
│              (SSL终止 / 静态资源 / 限流)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 后端服务                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  RESTful API │  │  JWT 认证    │  │  AI 集成     │       │
│  │  60+ 端点    │  │  OAuth2      │  │  OpenAI/Gemini│      │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  SQLite      │  │  静态文件    │  │  图片资源    │       │
│  │  10张核心表  │  │  前端构建    │  │  漫画头像    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈详情

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端 Web** | React 18 + Vite + TypeScript + Tailwind CSS | 现代化 SPA，支持 PWA |
| **前端小程序** | uni-app + Vue 3 + TypeScript | 跨平台，支持微信/支付宝/H5 |
| **后端框架** | FastAPI + Pydantic | 高性能异步 API，自动生成 OpenAPI 文档 |
| **数据库** | SQLite | 轻量级，支持全文搜索（FTS5） |
| **认证授权** | JWT + OAuth2 | 支持邮箱登录 + 微信小程序登录 |
| **AI 集成** | OpenAI API / Gemini API | 成分分析、智能问答 |
| **部署** | Nginx + Let's Encrypt | HTTPS、静态资源缓存、反向代理 |
| **监控** | Cron Jobs + 日志系统 | 自动化任务、错误追踪 |

## 📁 项目结构

```
petcare/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── routers/           # API 路由模块
│   │   │   ├── products.py    # 产品管理（CRUD、搜索、评分）
│   │   │   ├── ingredients.py # 成分库（查询、危害等级）
│   │   │   ├── brands.py      # 品牌管理
│   │   │   ├── breeds.py      # 品种百科
│   │   │   ├── users.py       # 用户系统（注册、登录、资料）
│   │   │   ├── favorites.py   # 收藏功能
│   │   │   ├── reviews.py     # 评论系统
│   │   │   ├── schedules.py   # 日程管理（驱虫、疫苗、体检）
│   │   │   ├── records.py     # 健康记录
│   │   │   ├── feeding.py     # 喂食记录
│   │   │   ├── suggestions.py # UGC 产品建议
│   │   │   └── ai.py          # AI 问答 + VLM 图片解析
│   │   ├── crawler/           # 数据采集模块
│   │   │   ├── jd_browseruse_scraper.py       # 京东爬虫（Browser Use）
│   │   │   └── jd_vlm_ingredient_parser.py    # VLM 配料表解析
│   │   ├── models.py          # 数据库模型（SQLAlchemy）
│   │   ├── schemas.py         # Pydantic 数据验证
│   │   ├── scoring.py         # 安全评分算法 v2
│   │   ├── auth.py            # JWT 认证逻辑
│   │   └── config.py          # 配置管理
│   ├── tests/                 # 单元测试
│   ├── requirements.txt       # Python 依赖
│   └── petcare.db            # SQLite 数据库
│
├── frontend/                  # Web 前端（React）
│   ├── src/
│   │   ├── pages/            # 页面组件（13个主要页面）
│   │   │   ├── Home.jsx      # 首页（推荐、热门品牌）
│   │   │   ├── ProductDetail.jsx  # 产品详情
│   │   │   ├── IngredientList.jsx # 成分库
│   │   │   ├── BrandList.jsx      # 品牌库
│   │   │   ├── BreedList.jsx      # 品种百科
│   │   │   ├── Search.jsx         # 高级搜索
│   │   │   ├── Compare.jsx        # 产品对比
│   │   │   ├── HealthTracker.jsx  # 健康追踪
│   │   │   └── ...
│   │   ├── components/       # 通用组件
│   │   │   ├── BreedCompatibility.jsx  # 品种兼容性
│   │   │   ├── ProductSuggestion.jsx   # 产品建议
│   │   │   └── ...
│   │   └── api/              # API 客户端
│   ├── public/               # 静态资源
│   │   └── avatars/          # 品种漫画头像（哈希命名）
│   ├── package.json
│   └── vite.config.js        # Vite 构建配置 + PWA
│
├── miniprogram/               # 微信小程序（uni-app）
│   ├── src/
│   │   ├── pages/            # 小程序页面（8个）
│   │   ├── components/       # 小程序组件
│   │   ├── api/              # API 封装
│   │   ├── stores/           # Pinia 状态管理
│   │   └── App.vue           # 应用入口
│   ├── package.json
│   └── README.md             # 小程序独立文档
│
├── scripts/                   # 工具脚本
│   ├── hash_avatars.py       # 图片哈希命名工具
│   ├── gen_anime_avatars.py  # AI 生成漫画头像
│   ├── test_vlm_parser.py    # VLM 解析器测试
│   └── ...
│
├── docs/                      # 项目文档
│   ├── PRD.md                # 产品需求文档
│   ├── TECH.md               # 技术架构文档
│   ├── API.md                # API 接口文档
│   └── DATA_RULES.md         # 数据管理规范
│
├── PROJECT.md                 # 项目主文档（开发状态）
├── DEPLOYMENT.md              # 部署指南
├── DATA_RULES.md              # 数据治理规则
└── README.md                  # 本文件（项目概览）
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Nginx（生产环境）

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev
# http://localhost:5173

# 生产构建
npm run build
# 输出到 dist/，自动复制到 /var/www/petcare/
```

### 小程序开发

```bash
cd miniprogram

# 安装依赖
npm install

# 微信小程序开发
npm run dev:mp-weixin
# 用微信开发者工具打开 dist/dev/mp-weixin

# H5 开发
npm run dev:h5
```

详细部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 📊 数据规模

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| **产品** | 186 | 药品71 + 食品60 + 保健品55 |
| **成分** | 90 | 常见宠物食品/药品成分 |
| **品牌** | 52 | 国内外知名品牌（含京东店铺） |
| **品类** | 40 | 药品17 + 食品7 + 保健品9 |
| **品种** | 92 | 狗62个 + 猫30个 |
| **品种关联** | 9,149 | 基于物种+体型的智能关联 |
| **漫画头像** | 92 | 每个品种专属动漫风格头像 |

## 🎯 核心功能

### 1. 产品查询与评分
- **多维搜索**：支持按成分、品牌、品种、体型、年龄筛选
- **安全评分**：1-10 分制，综合考虑成分毒性、刺激性、致癌风险
- **成分解读**：每个成分的详细危害说明和安全等级

### 2. AI 智能助手
- **成分问答**：基于大语言模型的专业咨询
- **VLM 配料表解析**：上传图片，自动识别并解析配料表
- **个性化推荐**：根据宠物特征推荐适合的产品

### 3. 品种百科
- **专业资料**：92 个品种的详细介绍（性格、健康、护理）
- **漫画头像**：每个品种配备独特的动漫风格头像
- **产品推荐**：根据品种特征推荐合适的产品

### 4. 用户系统
- **账号管理**：注册、登录、资料编辑
- **收藏功能**：收藏感兴趣的产品
- **评论系统**：分享使用体验，支持匿名评论
- **健康记录**：记录宠物的体重、用药、就诊历史

### 5. 日程管理
- **驱虫提醒**：定期驱虫提醒
- **疫苗接种**：疫苗计划管理
- **体检安排**：定期体检提醒
- **日历导出**：支持导出为 .ics 文件

### 6. 多端支持
- **Web 端**：完整的 React 单页应用，支持 PWA
- **微信小程序**：轻量级小程序版本（开发中）
- **移动端优化**：响应式设计，完美适配手机访问

## 🗺️ 未来规划

### Phase 1：数据增强（进行中）
- [x] 京东数据爬虫（Browser Use + Playwright）
- [x] VLM 配料表图片解析
- [ ] 接入 EWG Skin Deep 成分数据库（1-10 分制）
- [ ] 天猫/淘宝数据源接入
- [ ] 成分数据库扩充（目标 500+ 成分）

### Phase 2：功能完善（规划中）
- [ ] 宠物档案管理（多宠物支持）
- [ ] 健康趋势图表（体重、饮食、用药趋势）
- [ ] 产品对比功能（多产品横向对比）
- [ ] 社区功能（用户交流、问答）
- [ ] 专家咨询（付费咨询兽医/营养师）

### Phase 3：商业化探索（远期）
- [ ] 会员订阅（高级功能解锁）
- [ ] 广告系统（品牌合作推广）
- [ ] 电商导购（跳转购买链接，佣金分成）
- [ ] 数据报告（行业分析报告）
- [ ] API 开放平台（第三方接入）

### Phase 4：技术优化（持续）
- [ ] 阿里云 OSS + CDN 迁移（图片加速）
- [ ] 数据库迁移（SQLite → PostgreSQL，支持高并发）
- [ ] 微服务架构（拆分 AI、爬虫、推荐服务）
- [ ] 国际化支持（多语言）
- [ ] 性能监控（APM、错误追踪）

### Phase 5：生态扩展（愿景）
- [ ] 宠物医院合作（数据共享、转诊系统）
- [ ] 宠物食品厂商合作（新品首发、定制配方）
- [ ] 宠物保险对接（健康数据 → 保费计算）
- [ ] 智能硬件联动（智能喂食器、体重秤）
- [ ] 宠物社交（附近宠物、活动组织）

## 📈 技术亮点

### 1. 安全评分算法 v2
```python
# 综合评分 = 基础分 + 成分排序权重 + 相互作用 + 高风险惩罚 + 类型系数
score = (
    base_score * 0.6 +                    # 基础安全评分（60%）
    order_weight_bonus * 0.2 +            # 成分排序权重（20%）
    interaction_bonus * 0.1 +             # 成分相互作用（10%）
    high_risk_penalty * 0.1               # 高风险成分惩罚（10%）
) * product_type_coefficient              # 产品类型系数
```

### 2. VLM 配料表解析
- 使用多模态大模型（Vision Language Model）解析商品图片
- 自动识别配料表、营养成分表、添加剂信息
- 结构化输出，直接导入数据库

### 3. 智能品种关联
- 基于物种（猫/狗）+ 体型（小/中/大）的智能过滤
- 小型犬产品仅关联小型犬品种，避免误推荐
- 支持品种兼容性查询

### 4. 图片版本化管理
- 使用内容哈希命名：`柴犬_a3f5c8d2.webp`
- 更新图片自动变更文件名，客户端自动刷新
- 配合 Nginx `immutable` 缓存策略，性能最优

### 5. PWA 离线支持
- Service Worker 缓存静态资源
- 离线状态下仍可访问已浏览的产品
- 支持添加到主屏幕

## 🛡️ 安全与隐私

- **数据加密**：所有 API 通信使用 HTTPS
- **JWT 认证**：无状态 token，支持刷新机制
- **密码安全**：bcrypt 加盐哈希存储
- **匿名评论**：支持匿名发表，保护用户隐私
- **限流保护**：Nginx 限流防止恶意请求
- **爬虫拦截**：User-Agent 黑名单 + 请求频率限制

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发流程
1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 代码规范
- Python：遵循 PEP 8，使用 Black 格式化
- JavaScript/TypeScript：使用 ESLint + Prettier
- 提交信息：遵循 [Conventional Commits](https://www.conventionalcommits.org/)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 🔗 相关链接

- **官方网站**：https://petcare.yjyblog.xyz
- **API 文档**：https://petcare.yjyblog.xyz/docs
- **个人博客**：https://yjyblog.xyz
- **问题反馈**：https://github.com/yourusername/petcare/issues

## 📞 联系我们

- **作者**：rollstone6
- **邮箱**：593614984@qq.com
- **GitHub**：https://github.com/rollstone6

---

<p align="center">
  <strong>🐾 让每一只宠物都能吃到安全、健康的食物 🐾</strong>
</p>
