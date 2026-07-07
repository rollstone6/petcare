# 宠物宝小程序 🐾

基于 uni-app (Vue 3 + TypeScript) 开发的宠物宝微信小程序客户端。

## 功能特性

- ✅ 产品展示：浏览宠物食品，查看安全评分
- ✅ 智能搜索：按关键词、品牌、成分搜索产品
- ✅ 品牌库：浏览 52 个宠物食品品牌
- ✅ 成分库：查看 90 种成分的安全等级
- ✅ 品种库：62 个宠物品种（猫咪/狗狗）
- ✅ 个人中心：用户登录、收藏、评论管理
- ✅ AI 问答：智能解答宠物营养问题（开发中）

## 技术栈

- **框架**: uni-app 3.0 + Vue 3
- **语言**: TypeScript
- **状态管理**: Pinia
- **UI**: 自定义组件
- **API**: 复用宠物宝后端 API

## 项目结构

```
miniprogram/
├── src/
│   ├── api/              # API 请求封装
│   ├── components/       # 公共组件
│   ├── pages/            # 页面
│   │   ├── index/        # 首页
│   │   ├── search/       # 搜索页
│   │   ├── product/      # 产品详情
│   │   ├── brands/       # 品牌库
│   │   ├── ingredients/  # 成分库
│   │   ├── breeds/       # 品种库
│   │   ├── profile/      # 个人中心
│   │   └── login/        # 登录页
│   ├── static/           # 静态资源
│   │   ├── tab/          # 底部导航图标
│   │   └── images/       # 占位图片
│   ├── stores/           # Pinia 状态管理
│   ├── App.vue           # 应用入口
│   ├── main.ts           # 主入口
│   ├── manifest.json     # 应用配置
│   └── pages.json        # 页面配置
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 开发指南

### 1. 安装依赖

```bash
cd miniprogram
npm install
```

### 2. 配置 API 地址

编辑 `src/api/index.ts`，修改 `BASE_URL`：

```typescript
const BASE_URL = 'https://your-backend-domain.com'  // 生产环境
// const BASE_URL = 'http://localhost:8000'  // 开发环境
```

**注意**: 微信小程序只允许 HTTPS 域名，开发时需要在微信开发者工具中关闭"不校验合法域名"。

### 3. 配置微信小程序 AppID

编辑 `src/manifest.json`，填写你的小程序 AppID：

```json
{
  "mp-weixin": {
    "appid": "你的小程序AppID",
    ...
  }
}
```

### 4. 启动开发服务器

```bash
# H5 开发（浏览器调试）
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

### 5. 微信开发者工具

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开微信开发者工具
3. 导入项目，选择 `dist/dev/mp-weixin` 目录
4. 在"详情" → "本地设置"中勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"

## 构建发布

```bash
# 构建微信小程序
npm run build:mp-weixin
```

构建完成后，使用微信开发者工具上传代码到微信小程序后台。

## 后端 API 要求

本小程序复用宠物宝后端 API，需要后端提供以下接口：

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 产品相关
- `GET /api/products` - 产品列表（支持分页、搜索、筛选）
- `GET /api/products/{id}` - 产品详情
- `GET /api/products/recalculate-scores` - 重新计算安全评分

### 品牌相关
- `GET /api/brands` - 品牌列表
- `GET /api/brands/hot` - 热门品牌

### 成分相关
- `GET /api/ingredients` - 成分列表
- `GET /api/ingredients/dangerous` - 危险成分列表
- `GET /api/ingredients/{id}` - 成分详情

### 品种相关
- `GET /api/breeds` - 品种列表
- `GET /api/breeds/{id}` - 品种详情
- `GET /api/breeds/{id}/products` - 品种推荐产品

### AI 问答
- `POST /api/ai/ask` - AI 问答
- `POST /api/ai/analyze-ingredients` - 成分分析

### 用户相关
- `GET /api/reviews/my` - 我的评论
- `POST /api/reviews/` - 发表评论
- `DELETE /api/reviews/{id}` - 删除评论
- `GET /api/favorites` - 我的收藏
- `POST /api/favorites` - 添加收藏
- `DELETE /api/favorites/{product_id}` - 取消收藏

### 宠物档案
- `GET /api/pets` - 我的宠物列表
- `POST /api/pets` - 添加宠物
- `PUT /api/pets/{id}` - 更新宠物信息
- `DELETE /api/pets/{id}` - 删除宠物

### 健康计算
- `POST /api/health/calculate` - 健康评分计算

详细 API 文档见：`http://your-backend-domain.com/docs`

## 待开发功能

- [ ] AI 问答功能
- [ ] 宠物档案管理
- [ ] 健康记录追踪
- [ ] 评论功能
- [ ] 微信登录
- [ ] 分享功能
- [ ] 产品对比功能

## 图标资源

当前使用占位图标，正式部署前需要替换为设计好的图标：

- `static/tab/` - 底部导航栏图标（6 个）
- `static/avatar-default.png` - 默认头像
- `static/brand-default.png` - 默认品牌 logo
- `static/product-default.png` - 默认产品图片
- `static/banner1.jpg` / `banner2.jpg` - 首页轮播图

建议使用 [iconfont](https://www.iconfont.cn/) 或 [iconpark](https://iconpark.oceanengine.com/) 获取图标资源。

## 性能优化建议

1. **图片懒加载**: 产品列表页使用 `<image lazy-load>` 属性
2. **分包加载**: 将不常用页面（如品种详情）放入分包
3. **数据缓存**: 使用 `uni.setStorage` 缓存品牌、成分等静态数据
4. **请求优化**: 合并请求，减少 API 调用次数
5. **代码分割**: 使用动态 import 按需加载组件

## 常见问题

### Q: 开发时提示"不在以下 request 合法域名列表中"
A: 在微信开发者工具中关闭域名校验：详情 → 本地设置 → 勾选"不校验合法域名"

### Q: 页面白屏，控制台报错
A: 检查 `src/api/index.ts` 中的 `BASE_URL` 是否正确，确保后端服务已启动

### Q: TabBar 图标不显示
A: 检查 `static/tab/` 目录下是否有对应的图标文件，确保文件名与 `pages.json` 中配置一致

### Q: 构建失败提示 TypeScript 错误
A: 运行 `npm install` 重新安装依赖，或删除 `node_modules` 和 `package-lock.json` 后重新安装

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
