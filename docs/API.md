# 宠物宝（PetCare）— API 文档 v3.0

> Base URL: `https://petcare.yjyblog.xyz/api`
> 版本：v3.0 | 最后更新：2026-07-02

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
| species | string | 猫/狗/猫狗 |
| target_size | string | 全部/小型/中型/大型/小型中型/中大型 |
| target_age | string | 全部/幼年/成年/老年/成年老年 |
| page | int | 页码 |
| page_size | int | 每页数量 |

### GET /api/products/{id} — 产品详情
返回完整产品信息 + 成分列表 + 品牌/品类信息 + 适用体型/年龄标签

---

## 二、成分 API

### GET /api/ingredients — 成分搜索
### GET /api/ingredients/{id} — 成分详情（含关联产品）

---

## 三、品牌 API

### GET /api/brands — 品牌列表（当前52个品牌）

---

## 四、品类 API

### GET /api/categories — 品类列表（支持 type 筛选）
当前40个品类：药品17 + 食品7 + 保健品9

---

## 五、品种 API

### GET /api/breeds — 品种列表
| 参数 | 类型 | 说明 |
|------|------|------|
| species | string | 猫/狗（当前62个品种：狗34+猫28） |

### GET /api/breeds/{id} — 品种详情
### GET /api/breeds/{id}/products — 品种推荐产品（基于体型过滤的智能关联）

---

## 六、用户 API ✅

### POST /api/users/register — 注册
### POST /api/users/login — 登录（返回JWT）
### GET /api/users/me — 当前用户信息（需Authorization: Bearer token）
### PUT /api/users/me — 更新用户信息

---

## 七、收藏 API ✅

### GET /api/favorites — 我的收藏（需认证）
### POST /api/favorites — 添加收藏
### DELETE /api/favorites/{id} — 取消收藏

---

## 八、评价 API ✅

### GET /api/products/{id}/reviews — 产品评价列表
### POST /api/products/{id}/reviews — 发表评价（需认证）

---

## 九、对比 API ✅

### GET /api/compare?ids=1,2,3 — 产品对比

---

## 十、健康记录 API ✅

### GET /api/records — 健康记录列表（便便/饮水/呕吐/体重等）
### POST /api/records — 添加记录
### DELETE /api/records/{id} — 删除记录

---

## 十一、日程提醒 API ✅

### GET /api/schedules — 日程列表（驱虫/疫苗/体检）
### POST /api/schedules — 创建日程
### PUT /api/schedules/{id} — 更新日程
### DELETE /api/schedules/{id} — 删除日程

---

## 十二、AI 问答 API ✅

### POST /api/ai/chat — AI 成分问答（需认证）
