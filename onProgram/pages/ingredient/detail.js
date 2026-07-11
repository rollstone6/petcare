// pages/ingredient/detail.js
const api = require('../../utils/api')

Page({
  data: {
    ingredient: null,
    relatedProducts: [],
    loading: true
  },

  onLoad(options) {
    if (options.id) {
      this.ingredientId = options.id
      this.loadDetail()
    }
  },

  async loadDetail() {
    try {
      const ingredient = await api.getIngredientDetail(this.ingredientId)
      this.setData({ ingredient, loading: false })
    } catch (err) {
      console.error('加载成分详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})