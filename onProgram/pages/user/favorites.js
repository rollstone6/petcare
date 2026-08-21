// pages/user/favorites.js — 我的收藏（对齐 PC 端收藏功能）
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    favorites: [],
    loading: true,
    placeholder: api.PLACEHOLDER_IMAGE
  },

  onShow() {
    if (!app.globalData.isLogin) {
      this.setData({ loading: false, favorites: [] })
      return
    }
    this.loadFavorites()
  },

  async loadFavorites() {
    this.setData({ loading: true })
    try {
      const res = await api.getFavorites()
      this.setData({ favorites: res?.items || [] })
    } catch (err) {
      console.error('加载收藏失败:', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  },

  // 首页是自定义 tab-bar 页面（app.json 无 tabBar 配置），不能用 switchTab，与 tab-bar 组件一致用 redirectTo
  onGoHome() {
    wx.redirectTo({ url: '/pages/index/index' })
  },

  onRemoveFavorite(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '提示',
      content: '确定取消收藏吗？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.removeFavorite(id)
          wx.showToast({ title: '已取消收藏', icon: 'none' })
          this.loadFavorites()
        } catch (err) {
          console.error('取消收藏失败:', err)
        }
      }
    })
  }
})