# 宠物宝（PetCare）— 测试文档 v2.0

> 版本：v2.0 | 最后更新：2026-06-23

---

## 1. 测试策略

| 测试类型 | 工具 | 覆盖范围 |
|---------|------|---------|
| 后端单元测试 | pytest | 数据模型、评分算法 |
| API 集成测试 | pytest + httpx | 所有 API 端点 |
| 前端组件测试 | Vitest + React Testing Library | 组件渲染、交互 |
| E2E 测试 | Playwright（后续） | 完整用户流程 |
| 手动测试 | Swagger UI + 浏览器 | 探索性测试 |

---

## 2. API 测试用例

### 2.1 产品搜索
- [x] GET /api/products — 返回16条产品，按评分降序
- [ ] GET /api/products?q=驱虫 — 搜索"驱虫"返回驱虫药
- [ ] GET /api/products?type=药品 — 筛选药品
- [ ] GET /api/products?category_id=1 — 按品类筛选
- [ ] GET /api/products?page=2 — 分页

### 2.2 产品详情
- [x] GET /api/products/1 — 返回大宠爱完整信息
- [x] 包含品牌、品类、成分列表
- [ ] GET /api/products/999 — 返回 404

### 2.3 成分查询
- [x] GET /api/ingredients — 返回31种成分
- [ ] GET /api/ingredients/1 — 成分详情含关联产品

### 2.4 品种
- [x] GET /api/breeds?species=猫 — 返回猫品种
- [ ] GET /api/breeds/15 — 英短详情
- [ ] GET /api/breeds/15/products — 英短推荐产品

### 2.5 品牌/品类
- [x] GET /api/brands — 返回15个品牌
- [x] GET /api/categories — 返回18个品类

---

## 3. 前端测试用例

### 3.1 首页
- [ ] 搜索框渲染正常
- [ ] 分类宫格（药品/食品/保健品/品种）可点击
- [ ] 热门产品卡片渲染
- [ ] 底部导航栏（首页/搜索/品种/我的）

### 3.2 搜索页
- [ ] 输入关键词实时搜索
- [ ] 分类/品牌筛选生效
- [ ] 搜索结果列表渲染

### 3.3 产品详情页
- [ ] 产品基本信息展示
- [ ] 安全评分组件渲染
- [ ] 成分列表按排序展示
- [ ] 收藏按钮可点击

### 3.4 移动端
- [ ] 底部 Tab 导航固定
- [ ] 触摸滑动正常
- [ ] PWA 可安装

---

## 4. 性能指标

| 指标 | 目标 |
|------|------|
| API 响应时间 | < 200ms |
| 首页加载 | < 2s (3G) |
| 详情页加载 | < 1s |
| Lighthouse 评分 | > 80 |
| PWA 离线可用 | ✅ |

---

## 5. 验收标准

- [ ] 所有 API 返回正确数据
- [ ] 前端 6 个页面全部渲染正常
- [ ] 移动端适配（375px - 1024px）
- [ ] HTTPS 正常
- [ ] PWA 可安装
