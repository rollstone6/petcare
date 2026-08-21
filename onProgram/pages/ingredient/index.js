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

  // 加载成分分类
  async loadCategories() {
    try {
      const result = await api.getIngredientCategories()
      const items = (result && result.items) || result || []
      this.setData({
        categories: [{ name: '全部', value: '' }].concat(
          items.map(c => ({ name: c.name, value: c.value != null ? c.value : c.name }))
        )
      })
    } catch (err) {
      console.error('加载成分分类失败:', err)
      // 兜底：后端暂未提供 /ingredients/categories 时使用库内现有分类
      this.setData({
        categories: [
          { name: '全部', value: '' },
          { name: '营养', value: '营养' },
          { name: '食品成分', value: '食品成分' },
          { name: '保健品成分', value: '保健品成分' },
          { name: '矿物质', value: '矿物质' },
          { name: '蛋白质', value: '蛋白质' },
          { name: '维生素', value: '维生素' },
          { name: '驱虫', value: '驱虫' },
          { name: '疫苗', value: '疫苗' },
          { name: '防腐剂', value: '防腐剂' },
          { name: '抗生素', value: '抗生素' }
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
        params.q = this.data.searchValue
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