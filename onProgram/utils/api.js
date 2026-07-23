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
const request = (options) => {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {} } = options
    
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
            wx.showToast({
              title: '请先登录',
              icon: 'none'
            })
            reject(new Error('未登录'))
          } else {
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(new Error(res.data.message))
          }
        } else if (res.statusCode === 401) {
          clearToken()
          wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          })
          reject(new Error('登录过期'))
        } else {
          wx.showToast({
            title: '网络请求失败',
            icon: 'none'
          })
          reject(new Error('网络请求失败'))
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// GET 请求
const get = (url, data = {}) => {
  return request({ url, method: 'GET', data })
}

// POST 请求
const post = (url, data = {}) => {
  return request({ url, method: 'POST', data })
}

// PUT 请求
const put = (url, data = {}) => {
  return request({ url, method: 'PUT', data })
}

// DELETE 请求
const del = (url, data = {}) => {
  return request({ url, method: 'DELETE', data })
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

const getBreedDetail = (id) => {
  return get(`/breeds/${id}`)
}

const getBreedProducts = (id) => {
  return get(`/breeds/${id}/products`)
}

// ===== 用户 API =====
const login = (data) => {
  return post('/users/login', data)
}

const register = (data) => {
  return post('/users/register', data)
}

const getUserInfo = () => {
  return get('/users/me')
}

const updateUserInfo = (data) => {
  return put('/users/me', data)
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

// ===== 评价 API =====
const getProductReviews = (productId, params = {}) => {
  return get(`/products/${productId}/reviews`, params)
}

const addProductReview = (productId, data) => {
  return post(`/products/${productId}/reviews`, data)
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
  // 品牌
  getBrands,
  // 品类
  getCategories,
  // 品种
  getBreeds,
  getBreedDetail,
  getBreedProducts,
  // 用户
  login,
  register,
  getUserInfo,
  updateUserInfo,
  // 收藏
  getFavorites,
  addFavorite,
  removeFavorite,
  // 评价
  getProductReviews,
  addProductReview,
  // 对比
  compareProducts
}