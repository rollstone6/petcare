// API 配置
const BASE_URL = 'http://localhost:8000' // 开发环境，生产环境需要替换

// 通用请求方法
interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
  showLoading?: boolean
}

interface ApiResponse<T = any> {
  code: number
  data: T
  message?: string
}

export async function request<T = any>(options: RequestOptions): Promise<ApiResponse<T>> {
  const { url, method = 'GET', data, header = {}, showLoading = true } = options
  
  if (showLoading) {
    uni.showLoading({ title: '加载中...' })
  }

  // 从本地存储获取 token
  const token = uni.getStorageSync('token')
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await new Promise<UniApp.RequestSuccessCallbackResult>((resolve, reject) => {
      uni.request({
        url: `${BASE_URL}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res)
          } else if (res.statusCode === 401) {
            // Token 过期，跳转登录
            uni.removeStorageSync('token')
            uni.removeStorageSync('user')
            uni.showToast({
              title: '请重新登录',
              icon: 'none'
            })
            setTimeout(() => {
              uni.navigateTo({ url: '/pages/login/index' })
            }, 1500)
            reject(new Error('未授权'))
          } else {
            reject(new Error(`请求失败: ${res.statusCode}`))
          }
        },
        fail: (err) => {
          reject(new Error(`网络错误: ${err.errMsg}`))
        }
      })
    })

    return response.data as ApiResponse<T>
  } catch (error) {
    console.error('Request error:', error)
    throw error
  } finally {
    if (showLoading) {
      uni.hideLoading()
    }
  }
}

// API 方法
export const api = {
  // 用户认证
  auth: {
    login: (data: { username: string; password: string }) =>
      request({ url: '/api/auth/login', method: 'POST', data }),
    
    register: (data: { username: string; password: string; email?: string }) =>
      request({ url: '/api/auth/register', method: 'POST', data }),
    
    getMe: () =>
      request({ url: '/api/auth/me' }),
  },

  // 产品相关
  products: {
    list: (params?: { page?: number; page_size?: number; keyword?: string; brand_id?: number; category_id?: number }) =>
      request({ url: '/api/products', data: params }),
    
    detail: (id: number) =>
      request({ url: `/api/products/${id}` }),
    
    recalculateScores: () =>
      request({ url: '/api/products/recalculate-scores', method: 'POST' }),
  },

  // 品牌相关
  brands: {
    list: () =>
      request({ url: '/api/brands' }),
    
    hot: () =>
      request({ url: '/api/brands/hot' }),
  },

  // 成分相关
  ingredients: {
    list: () =>
      request({ url: '/api/ingredients' }),
    
    dangerous: () =>
      request({ url: '/api/ingredients/dangerous' }),
    
    detail: (id: number) =>
      request({ url: `/api/ingredients/${id}` }),
  },

  // 品种相关
  breeds: {
    list: () =>
      request({ url: '/api/breeds' }),
    
    detail: (id: number) =>
      request({ url: `/api/breeds/${id}` }),
    
    products: (id: number) =>
      request({ url: `/api/breeds/${id}/products` }),
  },

  // AI 问答
  ai: {
    ask: (data: { question: string }) =>
      request({ url: '/api/ai/ask', method: 'POST', data }),
    
    analyzeIngredients: (data: { ingredients: string[] }) =>
      request({ url: '/api/ai/analyze-ingredients', method: 'POST', data }),
  },

  // 评论
  reviews: {
    product: (productId: number) =>
      request({ url: `/api/reviews/product/${productId}` }),
    
    my: () =>
      request({ url: '/api/reviews/my' }),
    
    create: (data: { product_id: number; rating: number; content: string }) =>
      request({ url: '/api/reviews/', method: 'POST', data }),
    
    delete: (id: number) =>
      request({ url: `/api/reviews/${id}`, method: 'DELETE' }),
  },

  // 宠物档案
  pets: {
    list: () =>
      request({ url: '/api/pets' }),
    
    create: (data: { name: string; breed_id: number; birth_date?: string; gender?: string }) =>
      request({ url: '/api/pets', method: 'POST', data }),
    
    update: (id: number, data: any) =>
      request({ url: `/api/pets/${id}`, method: 'PUT', data }),
    
    delete: (id: number) =>
      request({ url: `/api/pets/${id}`, method: 'DELETE' }),
  },

  // 健康计算器
  health: {
    calculate: (data: { pet_id: number; product_id: number; daily_amount: number }) =>
      request({ url: '/api/health/calculate', method: 'POST', data }),
  },

  // 收藏
  favorites: {
    list: () =>
      request({ url: '/api/favorites' }),
    
    add: (productId: number) =>
      request({ url: '/api/favorites', method: 'POST', data: { product_id: productId } }),
    
    remove: (productId: number) =>
      request({ url: `/api/favorites/${productId}`, method: 'DELETE' }),
  },
}

export default api
