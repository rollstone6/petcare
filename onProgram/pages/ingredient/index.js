// pages/ingredient/index.js
const api = require('../../utils/api')

Page({
  data: {
    searchValue: '',
    categories: [],
    currentCategory: '',
    ingredients: [],
    loading: true,
    page: 1,
    hasMore: true
  },

  onLoad() {
    this.loadCategories()
    this.loadIngredients()
  },

  // 加载分类
  async loadCategories() {
    try {
      const categories = await api.getCategories()
      this.setData({
        categories: [{ name: '全部', value: '' }, ...(categories || [])]
      })
    } catch (err) {
      console.error('加载分类失败:', err)
      // 使用默认分类
      this.setData({
        categories: [
          { name: '全部', value: '' },
          { name: '防腐剂', value: 'preservative' },
          { name: '香精', value: 'fragrance' },
          { name: '色素', value: 'colorant' },
          { name: '表面活性剂', value: 'surfactant' },
          { name: '保湿剂', value: 'moisturizer' }
        ]
      })
    }
  },

  // 加载成分列表
  async loadIngredients(reset = true) {
    if (this.data.loading && !reset) return

    if (reset) {
      this.setData({ page: 1, ingredients: [], hasMore: true })
    }

    this.setData({ loading: true })
    try {
      const params = {
        page: this.data.page,
        page_size: 20
      }
      if (this.data.currentCategory) {
        params.category = this.data.currentCategory
      }
      if (this.data.searchValue) {
        params.keyword = this.data.searchValue
      }

      const result = await api.getIngredients(params)
      const items = result.items || result || []

      this.setData({
        ingredients: reset ? items : [...this.data.ingredients, ...items],
        hasMore: items.length >= 20,
        loading: false
      })
    } catch (err) {
      console.error('加载成分失败:', err)
      this.setData({ loading: false })
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchValue: e.detail.value })
  },

  // 搜索确认
  onSearchConfirm() {
    this.loadIngredients()
  },

  // 分类切换
  onCategoryTap(e) {
    const value = e.currentTarget.dataset.value
    this.setData({ currentCategory: value })
    this.loadIngredients()
  },

  // 点击成分
  onIngredientTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/ingredient/detail?id=${id}`
    })
  },

  // 加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 })
      this.loadIngredients(false)
    }
  }
})