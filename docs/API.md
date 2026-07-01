# 宠物宝（PetCare）— API 文档 v2.0

> Base URL: `https://petcare.yjyblog.xyz/api`
> 版本：v2.0 | 最后更新：2026-06-23

---

## 通用规范

- **格式**: JSON
- **分页**: `?page=1&page_size=20`
- **统一响应**: `{"code": 0, "data": {...}, "message": "ok"}`
- **错误码**: 0=成功, 1=参数错误, 2=未登录, 3=无权限, 4=不存在

---

## 一、产品 API

### GET /api/products — 产品搜索/列表
| 参数 | 类型 | 说明 |
|------|------|------|
| q | string | 搜索关键词 |
| category_id | int | 品类ID |
| brand_id | int | 品牌ID |
| type | string | 药品/食品/保健品 |
| page | int | 页码 |
| page_size | int | 每页数量 |

### GET /api/products/{id} — 产品详情
返回完整产品信息 + 成分列表 + 品牌/品类信息

---

## 二、成分 API

### GET /api/ingredients — 成分搜索
### GET /api/ingredients/{id} — 成分详情（含关联产品）

---

## 三、品牌 API

### GET /api/brands — 品牌列表

---

## 四、品类 API

### GET /api/categories — 品类列表（支持 type 筛选）

---

## 五、品种 API

### GET /api/breeds — 品种列表（支持 species 筛选：猫/狗）
### GET /api/breeds/{id} — 品种详情
### GET /api/breeds/{id}/products — 品种推荐产品

---

## 六、用户 API（Phase 4 待实现）

### POST /api/users/register — 注册
### POST /api/users/login — 登录
### GET /api/users/me — 当前用户信息
### PUT /api/users/me — 更新用户信息

---

## 七、收藏 API（Phase 4 待实现）

### GET /api/favorites — 我的收藏
### POST /api/favorites — 添加收藏
### DELETE /api/favorites/{id} — 取消收藏

---

## 八、评价 API（Phase 5 待实现）

### GET /api/products/{id}/reviews — 产品评价列表
### POST /api/products/{id}/reviews — 发表评价

---

## 九、对比 API（Phase 5 待实现）

### GET /api/compare?ids=1,2,3 — 产品对比
