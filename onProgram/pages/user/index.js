// pages/user/index.js
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    isLogin: false,
    userInfo: null,
    favorites: [],
    menuList: [
      { icon: '❤️', title: '我的收藏', url: '/pages/user/favorites' },
      { icon: '📝', title: '我的评价', url: '/pages/user/reviews' },
      { icon: '🐾', title: '我的宠物', url: '/pages/user/pets' },
      { icon: '⚙️', title: '设置', url: '/pages/user/settings' }
    ]
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    this.checkLogin()
  },

  checkLogin() {
    const isLogin = app.globalData.isLogin
    this.setData({ isLogin })
    if (isLogin) {
      this.loadUserInfo()
    }
  },

  async loadUserInfo() {
    try {
      const userInfo = await api.getUserInfo()
      this.setData({ userInfo })
    } catch (err) {
      console.error('加载用户信息失败:', err)
    }
  },

  onLoginTap() {
    wx.navigateTo({ url: '/pages/user/login' })
  },

  onMenuTap(e) {
    const { url } = e.currentTarget.dataset
    if (!this.data.isLogin) {
      wx.navigateTo({ url: '/pages/user/login' })
      return
    }
    wx.navigateTo({ url })
  },

  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          api.clearToken()
          app.globalData.isLogin = false
          this.setData({ isLogin: false, userInfo: null })
          wx.showToast({ title: '已退出登录', icon: 'none' })
        }
      }
    })
  }
})