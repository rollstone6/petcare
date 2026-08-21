# 跨端结构互通说明（PC 端 ↔ 小程序）

本文档定义 PC 端（`frontend/`，React）与微信小程序（`onProgram/`）的结构对齐规则，
保证两端功能同步、接口一致、可对照维护。

## 1. 总体架构

```
petcare/
├── backend/     FastAPI 后端（两端唯一数据源，路由统一挂在 /api 下）
├── frontend/    PC/移动端网页（React + Vite + Tailwind）
├── onProgram/   微信小程序（原生 WXML/WXSS）
└── docs/        本文档等跨端约定
```

两端不直接共享代码（小程序无法引用 miniprogramRoot 之外的文件，React 有独立构建链），
互通依靠三个契约层：**同一套后端接口** + **同构的 API 客户端** + **同名映射的页面结构**。

## 2. 页面结构映射

| 功能 | PC 路由（frontend/src/pages） | 小程序页面（onProgram/pages） | 状态 |
|------|------|------|------|
| 首页 | `/` Home | `pages/index/index` | ✅ 双端 |
| 综合搜索 | `/search` Search | `pages/search/search` | ✅ 双端 |
| 产品详情 | `/product/:id` ProductDetail | `pages/product/detail` | ✅ 双端 |
| 成分列表 | IngredientList（内嵌于搜索） | `pages/ingredient/index` | ✅ 双端 |
| 成分详情 | `/ingredient/:id` IngredientDetail | `pages/ingredient/detail` | ✅ 双端 |
| 品种列表 | `/breeds` BreedList | `pages/breed/index` | ✅ 双端 |
| 品种详情 | `/breed/:id` BreedDetail | `pages/breed/detail` | ✅ 双端 |
| 个人中心 | `/profile` Profile | `pages/user/index` | ✅ 双端 |
| 登录 | Profile 内弹窗 | `pages/user/login` | ✅ 双端 |
| 宠物档案 | `/pets` PetProfiles | `pages/user/pets` | ✅ 双端 |
| 健康记录（日程提醒） | `/health` HealthTracker | `pages/health/index` | ✅ 双端 |
| 我的收藏 | Profile 内 Tab | `pages/user/favorites` | ✅ 双端 |
| 我的评价 | Profile 内 Tab | `pages/user/reviews` | ✅ 双端 |
| 设置 | — | `pages/user/settings` | 小程序独有 |
| 喂养日记 | HealthTracker 内 Tab | 待同步（api 层已就绪：feeding 组） | ⏳ |
| 健康标签 | HealthTagsTab 组件 | 待同步（api 层已就绪：health-tags 组） | ⏳ |
| AI 配料分析 | AIChat 组件 | 待同步（api 层已就绪：analyzeIngredients） | ⏳ |
| 产品对比 | Compare（重定向至搜索） | —（PC 已下线） | — |

## 3. API 层对应规范（互通核心）

**规则：`onProgram/utils/api.js` 与 `frontend/src/api/client.js` 保持同名、同参数、同端点。**

| PC（client.js） | 小程序（api.js） | 后端端点 |
|------|------|------|
| register / login / getMe | register / login / getUserInfo | `/auth/*` |
| —（PC 无需调用） | getWxLoginCode / wxLogin / bindWechat | `/auth/wx-login`、`/auth/bind-wx` |
| getFavorites / addFavorite / removeFavorite | 同名 | `/favorites` |
| searchProducts / getProduct | getProducts / getProductDetail | `/products` |
| searchIngredients / getIngredient | getIngredients / getIngredientDetail | `/ingredients` |
| getIngredientCategories / getDangerousIngredients | 同名 | `/ingredients/categories`、`/ingredients/dangerous` |
| getBrands / getHotBrands | 同名 | `/brands`、`/brands/hot` |
| getCategories | 同名 | `/categories` |
| getSpecies / getBreeds / getBreed / getBreedProducts | getSpecies / getBreeds / getBreedDetail / getBreedProducts | `/breeds*` |
| getBreedCompatibility | 同名 | `/products/{id}/breed-compatibility` |
| getSchedules / createSchedule / updateSchedule / markScheduleDone / deleteSchedule | 同名 | `/schedules*` |
| getProductReviews / createReview / deleteReview / getMyReviews | getProductReviews / createReview / deleteReview / getMyReviews | `/reviews*` |
| getPets / createPet / updatePet / deletePet | 同名 | `/pets*` |
| getFeedingLogs / createFeedingLog / … / getFeedingDiaries / … | 同名 | `/feeding/*` |
| getHealthTags / updatePetHealthTags / checkProductWarnings | 同名 | `/health-tags*` |
| analyzeIngredients | 同名 | `/ai/analyze-ingredients` |

命名差异仅限小程序历史习惯（getProductDetail vs getProduct 等），新接口一律与 PC 同名。

## 4. 数据契约

- **响应包装**：所有接口统一返回 `{ "code": 0, "data": ..., "message": "..." }`；
  `code !== 0` 或 HTTP 非 2xx 视为失败，错误信息取 `detail`/`message`。
- **认证**：`Authorization: Bearer <token>`；登录返回 `{ token, user }`（`user` 含 `has_wx_bind`）。
  两端均把 token 存本地（PC: localStorage `petcare_token`；小程序: storage `token`）。
  401 处理一致：登录接口 401 = 用户名/密码错误；其他接口 401 = 登录过期，清 token 提示重新登录。
- **登录互通（三端同一账号体系）**：后端用户表通过 `wx_openid` 关联微信身份，
  账密账号与微信账号可互认为同一用户：
  - `POST /api/auth/wx-login { code }`：小程序 `wx.login` 的 code 换 token；
    未绑定过的微信自动注册新账号（随机用户名，无需密码），返回 `is_new` 标识。
  - `POST /api/auth/bind-wx { code }`（需登录）：把当前微信绑定到已登录账密账号；
    openid 已被其他账号占用时返回 400。
  - 典型互通路径：用户在 PC 用账密注册 → 小程序登录后在「设置」绑定微信 →
    之后小程序打开即静默微信登录直达同一账号，收藏/宠物档案等数据三端同步。
  - 服务端需配置 `WX_APPID` / `WX_APP_SECRET`（后端 `.env`），session_key 不下发前端。
  - 实现细节与安全规范见下文「4.1 微信登录实现规范」。
- **分页**：`page` 从 1 开始；列表响应统一 `{ items: [...], total? }`。
- **字段命名**：一律 snake_case（product_id、image_url、pet_name…），两端均不做转换，直接消费。
- **图片兜底**：统一占位图 `https://website-petcare-oss-bj.oss-cn-beijing.aliyuncs.com/images/placeholder.png`
  （小程序中为 `api.PLACEHOLDER_IMAGE`）。

## 4.1 微信登录实现规范（依据微信开放文档《微信登录开发指南》）

参考：https://developers.weixin.qq.com/doc/oplatform/Mobile_App/WeChat_Login/Development_Guide.html
（本项目为小程序形态，使用 `wx.login` + `jscode2session`，与文档中 OAuth2.0 授权码模式同源）

**架构决策（均为官方推荐做法）：**
- **自管业务登录态**：后端只向微信换取 openid，随后签发自己的 JWT；
  不保存/不刷新微信的 access_token，避免维护 2 小时有效期的第三方凭证。
- **不调用 /sns/userinfo**：code2session 已直接返回 openid/unionid，
  用户头像昵称不作为登录关键路径（官方建议：userinfo 数据可缓存、勿放关键路径）。

**安全红线：**
- `AppSecret` 只允许存服务端 `.env`（`WX_APP_SECRET`），**严禁出现在任何客户端文件/git 仓库**
  （历史上曾误入 `project.config.json`，已移除；泄漏过的 secret 必须在微信后台重置）。
- `session_key` 仅服务端使用（解密手机号等），绝不下发前端。
- `code` 一次性使用、有效期约 10 分钟：前端每次登录/绑定都重新 `wx.login` 获取，
  失败时由 `wxLoginAuto` / `bindWechatAuto` 自动换新 code 重试一次。

**微信错误码 → HTTP 状态映射（后端 `code2session`）：**

| 微信 errcode | 含义 | 后端响应 | 客户端策略 |
|---|---|---|---|
| 40029 / 40163 / 41008 | code 无效 / 已使用 | 400 | 换新 code 重试（已自动） |
| 45011 | 频率限制（同一用户 1 分钟合计 ≤180 次） | 503 | 稍后重试，勿立即重试 |
| 40125 | AppSecret 配置错误 | 500 | 服务端修配置，客户端不重试 |
| -1 | 微信系统繁忙 | 502 | 稍后重试 |
| 其他 | — | 400（带 errcode） | 提示失败 |

**unionid 机制：**
- openid 按应用隔离（同一用户在不同小程序/App 下 openid 不同）；
  unionid 在同一微信开放平台账号下的所有应用间一致。
- `jscode2session` **仅当小程序绑定到微信开放平台账号后**才返回 unionid。
- 后端 `users.wx_unionid` 列已就绪：登录时若微信返回 unionid 会自动补记，
  未来多端（App/公众号）打通可直接以 unionid 匹配同一用户。

**上线注意：**
- 未上架小程序的微信登录有 **100 次/天** 限制，超出报 errcode 10060
  （见官方文档 FAQ）；正式发布前在微信后台确认上架状态。
- 部署检查清单：`.env` 配置 `WX_APPID`/`WX_APP_SECRET` → 运行 `migrate_wx_login.py` → 重启服务。

## 5. 环境地址

| 端 | 基址 | 位置 |
|------|------|------|
| PC | `/api`（Vite dev 代理到后端） | `frontend/vite.config.js` |
| 小程序 | `https://petcare.yjyblog.xyz/api`（上线）/ `http://127.0.0.1:8000/api`（本地调试） | `onProgram/utils/api.js` `BASE_URL` |
| 后端 | `http://127.0.0.1:8000`，全部路由前缀 `/api` | `backend/app/main.py` |

## 6. 同步维护流程

1. **新增接口**：先在后端 `backend/app/routers/` 实现 → 同时在 PC `client.js` 与小程序 `api.js`
   添加同名函数（参考第 3 节表格分组）。
2. **新增页面**：按第 2 节映射规则放置（PC 路由名 ↔ 小程序目录名保持语义一致），
   并在本文档登记状态。
3. **修改字段**：后端字段变更必须同时检查两端消费点（全局搜索 snake_case 字段名即可定位）。
4. **联调**：后端本地起服务后，PC 用 `npm run dev`，小程序在开发者工具切换 `BASE_URL`
   为本地地址；上线统一走部署域名。
