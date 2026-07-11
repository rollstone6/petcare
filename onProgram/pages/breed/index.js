// pages/breed/index.js
const api = require('../../utils/api')

Page({
  data: {
    breeds: [],
    loading: true
  },

  onLoad() {
    this.loadBreeds()
  },

  async loadBreeds() {
    try {
      const breeds = await api.getBreeds()
      this.setData({ breeds: breeds || [], loading: false })
    } catch (err) {
      console.error('加载品种列表失败:', err)
      this.setData({ loading: false })
    }
  },

  onBreedTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/breed/detail?id=${id}` })
  }
})