const BASE = '/api'

function getToken() {
  return localStorage.getItem('petcare_token')
}

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, { headers, ...options })
  if (res.status === 401) {
    // 登录接口的 401 是用户名或密码错误，不走过期逻辑
    if (path.includes('/auth/login')) {
      let msg = '用户名或密码错误'
      try {
        const err = await res.json()
        msg = err.detail || msg
      } catch {}
      throw new Error(msg)
    }
    // 其他接口的 401 才是 token 过期
    localStorage.removeItem('petcare_token')
    throw new Error('登录已过期，请重新登录')
  }
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const err = await res.json()
      msg = err.detail || err.message || msg
    } catch {}
    throw new Error(msg)
  }
  let json
  try {
    json = await res.json()
  } catch {
    throw new Error('服务器响应异常')
  }
  if (json.code !== 0) throw new Error(json.message || '请求失败')
  return json.data
}

export const api = {
  // 用户
  register: (username, password, email = '') =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ username, password, email }) }),
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  getMe: () => request('/auth/me'),

  // 收藏
  getFavorites: () => request('/favorites'),
  addFavorite: (productId) =>
    request('/favorites', { method: 'POST', body: JSON.stringify({ product_id: productId }) }),
  removeFavorite: (productId) =>
    request(`/favorites/${productId}`, { method: 'DELETE' }),

  // 产品
  searchProducts: (params) => request(`/products?${new URLSearchParams(params)}`),
  getProduct: (id) => request(`/products/${id}`),

  // 成分
  searchIngredients: (params) => request(`/ingredients?${new URLSearchParams(params)}`),
  getIngredient: (id, page = 1) => request(`/ingredients/${id}?page=${page}`),

  // 品牌
  getBrands: () => request('/brands'),
  getHotBrands: (limit = 8) => request(`/brands/hot?limit=${limit}`),

  // 高危成分
  getDangerousIngredients: (limit = 8) => request(`/ingredients/dangerous?limit=${limit}`),

  // 品类
  getCategories: (type) => request(`/categories${type ? `?type=${type}` : ''}`),

  // 品种
  getBreeds: (species) => request(`/breeds${species ? `?species=${species}` : ''}`),
  getBreed: (id) => request(`/breeds/${id}`),
  getBreedProducts: (id) => request(`/breeds/${id}/products`),

  // 日程提醒
  getSchedules: () => request('/schedules'),
  getSchedulePresets: () => request('/schedules/presets/list'),
  createSchedule: (data) => request('/schedules', { method: 'POST', body: JSON.stringify(data) }),
  markScheduleDone: (id) => request(`/schedules/${id}/done`, { method: 'POST' }),
  deleteSchedule: (id) => request(`/schedules/${id}`, { method: 'DELETE' }),
  // ics 需要带 token 请求
  downloadIcs: async (id) => {
    const token = getToken()
    const res = await fetch(`${BASE}/schedules/${id}/ics`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    if (!res.ok) throw new Error('导出失败')
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `schedule_${id}.ics`
    a.click()
    URL.revokeObjectURL(url)
  },

  // 评论
  getProductReviews: (productId, page = 1) => request(`/reviews/product/${productId}?page=${page}`),
  createReview: (data) => request('/reviews', { method: 'POST', body: JSON.stringify(data) }),
  deleteReview: (id) => request(`/reviews/${id}`, { method: 'DELETE' }),
  getMyReviews: (page = 1) => request(`/reviews/my?page=${page}`),

  // 宠物档案
  getPets: () => request('/pets'),
  createPet: (data) => request('/pets', { method: 'POST', body: JSON.stringify(data) }),
  updatePet: (id, data) => request(`/pets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePet: (id) => request(`/pets/${id}`, { method: 'DELETE' }),
}

export { getToken }
