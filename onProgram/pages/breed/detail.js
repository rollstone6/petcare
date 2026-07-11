// pages/breed/detail.js
const api = require('../../utils/api')

Page({
  data: {
    breed: null,
    products: [],
    loading: true
  },

  onLoad(options) {
    if (options.id) {
      this.breedId = options.id
      this.loadDetail()
      this.loadProducts()
    }
  },

  async loadDetail() {
    try {
      const breed = await api.getBreedDetail(this.breedId)
      this.setData({ breed, loading: false })
    } catch (err) {
      console.error('加载品种详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  async loadProducts() {
    try {
      const products = await api.getBreedProducts(this.breedId)
      this.setData({ products: products || [] })
    } catch (err) {
      console.error('加载品种产品失败:', err)
    }
  },

  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})