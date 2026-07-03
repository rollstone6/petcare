# 宠物宝（PetCare）— 测试文档 v3.0

> 版本：v3.0 | 最后更新：2026-07-02

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
- [x] GET /api/products — 返回186个产品，按评分降序
- [x] GET /api/products?q=驱虫 — 搜索"驱虫"返回驱虫药
- [x] GET /api/products?type=药品 — 筛选药品（71个）
- [x] GET /api/products?category_id=1 — 按品类筛选
- [x] GET /api/products?page=2 — 分页
- [x] GET /api/products?species=猫 — 按物种筛选
- [x] GET /api/products?target_size=小型 — 按体型筛选
- [x] GET /api/products?target_age=幼年 — 按年龄筛选

### 2.2 产品详情
- [x] GET /api/products/1 — 返回大宠爱完整信息
- [x] 包含品牌、品类、成分列表、target_size、target_age
- [x] GET /api/products/999 — 返回 404

### 2.3 成分查询
- [x] GET /api/ingredients — 返回31种成分
- [x] GET /api/ingredients/1 — 成分详情含关联产品

### 2.4 品种
- [x] GET /api/breeds?species=猫 — 返回28个猫品种
- [x] GET /api/breeds?species=狗 — 返回34个狗品种
- [x] GET /api/breeds/15 — 英短详情（含size字段）
- [x] GET /api/breeds/15/products — 英短推荐产品（基于体型智能关联）

### 2.5 品牌/品类
- [x] GET /api/brands — 返回52个品牌
- [x] GET /api/categories — 返回40个品类

### 2.6 用户系统
- [x] POST /api/users/register — 注册新用户
- [x] POST /api/users/login — 登录返回JWT
- [x] GET /api/users/me — 获取用户信息（需Bearer token）
- [x] PUT /api/users/me — 更新用户信息

### 2.7 收藏功能
- [x] GET /api/favorites — 获取收藏列表（需认证）
- [x] POST /api/favorites — 添加收藏
- [x] DELETE /api/favorites/{id} — 取消收藏

### 2.8 评价功能
- [x] GET /api/products/{id}/reviews — 获取产品评价
- [x] POST /api/products/{id}/reviews — 发表评价（需认证）

### 2.9 健康记录
- [x] GET /api/records — 获取健康记录列表
- [x] POST /api/records — 添加健康记录
- [x] DELETE /api/records/{id} — 删除健康记录

### 2.10 日程提醒
- [x] GET /api/schedules — 获取日程列表
- [x] POST /api/schedules — 创建日程
- [x] PUT /api/schedules/{id} — 更新日程
- [x] DELETE /api/schedules/{id} — 删除日程

### 2.11 AI 问答
- [x] POST /api/ai/chat — AI 成分问答（需认证）

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
