// pages/index/index.js
const api = require('../../utils/api')

Page({
  data: {
    searchValue: '',
    categories: [],
    hotProducts: [],
    loading: true
  },

  onLoad() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      // 并行加载品类和热门产品
      const [categories, products] = await Promise.all([
        api.getCategories(),
        api.getProducts({ page: 1, page_size: 10 })
      ])
      
      this.setData({
        categories: categories || [],
        hotProducts: products.items || products || [],
        loading: false
      })
    } catch (err) {
      console.error('加载数据失败:', err)
      this.setData({ loading: false })
    }
  },

  // 搜索框点击
  onSearchTap() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchValue: e.detail.value })
  },

  // 搜索确认
  onSearchConfirm() {
    const value = this.data.searchValue.trim()
    if (value) {
      wx.navigateTo({
        url: `/pages/search/search?q=${encodeURIComponent(value)}`
      })
    }
  },

  // 分类点击
  onCategoryTap(e) {
    const { type, name } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/search/search?type=${encodeURIComponent(type)}&name=${encodeURIComponent(name)}`
    })
  },

  // 产品点击
  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product/detail?id=${id}`
    })
  },

  // 查看更多
  onMoreTap() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  },

  // 获取安全评分颜色
  getSafetyClass(score) {
    if (score >= 4.5) return 'safety-5'
    if (score >= 3.5) return 'safety-4'
    if (score >= 2.5) return 'safety-3'
    if (score >= 1.5) return 'safety-2'
    return 'safety-1'
  }
})