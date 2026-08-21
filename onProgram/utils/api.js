// API 请求封装
const BASE_URL = 'https://petcare.yjyblog.xyz/api'

// OSS 静态资源地址
const OSS_BASE_URL = 'https://website-petcare-oss-bj.oss-cn-beijing.aliyuncs.com'
const PLACEHOLDER_IMAGE = `${OSS_BASE_URL}/images/placeholder.png`

// 获取存储的 token
const getToken = () => {
  return wx.getStorageSync('token') || ''
}

// 设置 token
const setToken = (token) => {
  wx.setStorageSync('token', token)
}

// 清除 token
const clearToken = () => {
  wx.removeStorageSync('token')
}

// 统一请求方法
// options.silent = true 时失败不弹 toast（用于可降级的请求，如分类加载）
const request = (options) => {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {}, silent = false } = options

    // 统一错误处理：后端 FastAPI 的错误信息放在 detail 字段
    const failWith = (msg) => {
      if (!silent) {
        wx.showToast({ title: msg, icon: 'none' })
      }
      reject(new Error(msg))
    }

    // 添加 token
    const token = getToken()
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    header['Content-Type'] = header['Content-Type'] || 'application/json'

    wx.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success: (res) => {
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data.data)
          } else if (res.data.code === 2) {
            // 未登录，清除 token 并跳转登录
            clearToken()
            failWith('请先登录')
          } else {
            failWith(res.data.message || '请求失败')
          }
        } else if (res.statusCode === 401) {
          clearToken()
          // 优先展示后端返回的具体原因（如登录时的"用户名或密码错误"）
          const msg = (res.data && typeof res.data.detail === 'string' && res.data.detail) || '登录已过期，请重新登录'
          failWith(msg)
        } else {
          const body = res.data || {}
          const msg = (typeof body.detail === 'string' && body.detail) || body.message || `请求失败(${res.statusCode})`
          failWith(msg)
        }
      },
      fail: (err) => {
        if (!silent) {
          wx.showToast({
            title: '网络连接失败',
            icon: 'none'
          })
        }
        reject(err)
      }
    })
  })
}

// GET 请求（options 可传 { silent: true } 等 request 选项）
const get = (url, data = {}, options = {}) => {
  return request({ url, method: 'GET', data, ...options })
}

// POST 请求
const post = (url, data = {}, options = {}) => {
  return request({ url, method: 'POST', data, ...options })
}

// PUT 请求
const put = (url, data = {}, options = {}) => {
  return request({ url, method: 'PUT', data, ...options })
}

// DELETE 请求
const del = (url, data = {}, options = {}) => {
  return request({ url, method: 'DELETE', data, ...options })
}

// ===== 产品 API =====
const getProducts = (params = {}) => {
  return get('/products', params)
}

const getProductDetail = (id) => {
  return get(`/products/${id}`)
}

// ===== 成分 API =====
const getIngredients = (params = {}) => {
  return get('/ingredients', params)
}

const getIngredientDetail = (id) => {
  return get(`/ingredients/${id}`)
}

// 成分分类列表（对现有成分数据去重聚合；接口不存在时静默失败，由页面降级）
const getIngredientCategories = () => {
  return get('/ingredients/categories', {}, { silent: true })
}

// ===== 品牌 API =====
const getBrands = () => {
  return get('/brands')
}

// ===== 品类 API =====
const getCategories = (params = {}) => {
  return get('/categories', params)
}

// ===== 品种 API =====
const getBreeds = (params = {}) => {
  return get('/breeds', params)
}

const getSpecies = () => {
  return get('/breeds/species')
}

const getBreedDetail = (id) => {
  return get(`/breeds/${id}`)
}

const getBreedProducts = (id) => {
  return get(`/breeds/${id}/products`)
}

// ===== 用户 API（后端路由前缀为 /auth）=====
// 注意：login/register 均传对象 { username, password }
const login = (data) => {
  return post('/auth/login', data)
}

const register = (data) => {
  return post('/auth/register', data)
}

const getUserInfo = () => {
  return get('/auth/me')
}

const updateUserInfo = (data) => {
  // 注意：后端暂未实现「更新用户信息」接口，调用会返回 404/405
  return put('/auth/me', data)
}

// ===== 微信登录 API =====
// 获取 wx.login 临时凭证 code（Promise 化）
const getWxLoginCode = () => {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (res) => {
        if (res.code) resolve(res.code)
        else reject(new Error(res.errMsg || 'wx.login 未返回 code'))
      },
      fail: (err) => reject(new Error(err.errMsg || 'wx.login 失败'))
    })
  })
}

// 微信一键登录：code 换 token（未绑定微信的 openid 会自动注册新账号）
// 返回 { token, user, is_new }，与账密登录结构一致
// options 可传 { silent: true } 表示失败不弹 toast（调用方自行处理）
const wxLogin = (code, options = {}) => {
  return post('/auth/wx-login', { code }, options)
}

// 已登录状态下绑定微信（需带 token）
const bindWechat = (code, options = {}) => {
  return post('/auth/bind-wx', { code }, options)
}

// 设置/修改账号密码（需带 token）：微信用户设置后即可在 PC/H5 用账密登录同一账号
// data: { password, username?, old_password? }
const setPassword = (data, options = {}) => {
  return post('/auth/set-password', data, options)
}

// 带自动重试的微信登录（官方规范：code 一次性使用、有效期约 10 分钟）。
// 首次失败时静默换新 code 重试一次；第二次仍失败则把错误抛给调用方。
const wxLoginAuto = async (options = {}) => {
  try {
    return await wxLogin(await getWxLoginCode(), { ...options, silent: true })
  } catch (err) {
    return await wxLogin(await getWxLoginCode(), options)
  }
}

// 带自动重试的微信绑定（规则同 wxLoginAuto）
const bindWechatAuto = async (options = {}) => {
  try {
    return await bindWechat(await getWxLoginCode(), { ...options, silent: true })
  } catch (err) {
    return await bindWechat(await getWxLoginCode(), options)
  }
}

// ===== 收藏 API =====
const getFavorites = () => {
  return get('/favorites')
}

const addFavorite = (data) => {
  return post('/favorites', data)
}

const removeFavorite = (id) => {
  return del(`/favorites/${id}`)
}

// ===== 评价 API（后端路由前缀为 /reviews）=====
const getProductReviews = (productId, params = {}) => {
  return get(`/reviews/product/${productId}`, params)
}

// 创建评论（data 自带 product_id，签名对齐 PC 端 createReview）
const createReview = (data) => {
  return post('/reviews/', data)
}

// 我的评论列表
const getMyReviews = (params = {}) => {
  return get('/reviews/my', params)
}

// 删除自己的评论
const deleteReview = (id) => {
  return del(`/reviews/${id}`)
}

// ===== 宠物档案 API（对齐 PC 端 pets） =====
const getPets = () => {
  return get('/pets')
}

const createPet = (data) => {
  return post('/pets', data)
}

const updatePet = (id, data) => {
  return put(`/pets/${id}`, data)
}

const deletePet = (id) => {
  return del(`/pets/${id}`)
}

// ===== 日程提醒 API（对齐 PC 端 schedules） =====
const getSchedules = () => {
  return get('/schedules')
}

const createSchedule = (data) => {
  return post('/schedules', data)
}

const updateSchedule = (id, data) => {
  return put(`/schedules/${id}`, data)
}

const markScheduleDone = (id) => {
  return post(`/schedules/${id}/done`)
}

const deleteSchedule = (id) => {
  return del(`/schedules/${id}`)
}

// ===== 喂养日记 API（对齐 PC 端 feeding） =====
const getFeedingLogs = (params = {}) => {
  return get('/feeding/logs', params)
}

const createFeedingLog = (data) => {
  return post('/feeding/logs', data)
}

const updateFeedingLog = (id, data) => {
  return put(`/feeding/logs/${id}`, data)
}

const deleteFeedingLog = (id) => {
  return del(`/feeding/logs/${id}`)
}

const checkProductFeeding = (productId) => {
  return get(`/feeding/check/${productId}`)
}

const getFeedingDiaries = (params = {}) => {
  return get('/feeding/diaries', params)
}

const createFeedingDiary = (data) => {
  return post('/feeding/diaries', data)
}

const deleteFeedingDiary = (id) => {
  return del(`/feeding/diaries/${id}`)
}

// ===== 健康标签 API（对齐 PC 端 health-tags） =====
const getHealthTags = () => {
  return get('/health-tags')
}

const updatePetHealthTags = (petId, tags) => {
  return put(`/health-tags/pets/${petId}`, { tags })
}

const checkProductWarnings = (productId) => {
  return post(`/health-tags/check/${productId}`)
}

// ===== 品种契合度 API（对齐 PC 端 breed-compatibility） =====
const getBreedCompatibility = (productId, petId) => {
  return get(`/products/${productId}/breed-compatibility`, petId ? { pet_id: petId } : {})
}

// ===== 其他（对齐 PC 端） =====
// 热门品牌
const getHotBrands = (limit = 8) => {
  return get('/brands/hot', { limit })
}

// 高危成分
const getDangerousIngredients = (limit = 8) => {
  return get('/ingredients/dangerous', { limit })
}

// AI 配料分析
const analyzeIngredients = (data) => {
  return post('/ai/analyze-ingredients', data)
}

// ===== 对比 API =====
const compareProducts = (ids) => {
  return get('/compare', { ids })
}

module.exports = {
  BASE_URL,
  OSS_BASE_URL,
  PLACEHOLDER_IMAGE,
  getToken,
  setToken,
  clearToken,
  request,
  get,
  post,
  put,
  del,
  // 产品
  getProducts,
  getProductDetail,
  // 成分
  getIngredients,
  getIngredientDetail,
  getIngredientCategories,
  // 品牌
  getBrands,
  // 品类
  getCategories,
  // 品种
  getBreeds,
  getSpecies,
  getBreedDetail,
  getBreedProducts,
  // 用户
  login,
  register,
  getUserInfo,
  updateUserInfo,
  getWxLoginCode,
  wxLogin,
  wxLoginAuto,
  bindWechat,
  bindWechatAuto,
  setPassword,
  // 收藏
  getFavorites,
  addFavorite,
  removeFavorite,
  // 评价
  getProductReviews,
  createReview,
  getMyReviews,
  deleteReview,
  // 宠物档案
  getPets,
  createPet,
  updatePet,
  deletePet,
  // 日程提醒
  getSchedules,
  createSchedule,
  updateSchedule,
  markScheduleDone,
  deleteSchedule,
  // 喂养日记
  getFeedingLogs,
  createFeedingLog,
  updateFeedingLog,
  deleteFeedingLog,
  checkProductFeeding,
  getFeedingDiaries,
  createFeedingDiary,
  deleteFeedingDiary,
  // 健康标签
  getHealthTags,
  updatePetHealthTags,
  checkProductWarnings,
  // 品种契合度
  getBreedCompatibility,
  // 其他
  getHotBrands,
  getDangerousIngredients,
  analyzeIngredients,
  // 对比
  compareProducts
}