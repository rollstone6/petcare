// pages/user/settings.js — 设置
const api = require('../../utils/api')
const app = getApp()

const APP_VERSION = '1.0.0'

Page({
  data: {
    version: APP_VERSION,
    isLogin: false,
    username: '',
    hasWxBind: false,
    binding: false
  },

  onShow() {
    const isLogin = app.globalData.isLogin
    this.setData({
      isLogin,
      username: app.globalData.userInfo?.username || '',
      hasWxBind: !!app.globalData.userInfo?.has_wx_bind
    })
  },

  // 绑定微信：把当前微信绑定到已登录账号（实现与 PC/小程序微信登录互通）
  async onBindWechat() {
    if (this.data.binding) return
    if (!app.globalData.isLogin) {
      wx.navigateTo({ url: '/pages/user/login' })
      return
    }
    this.setData({ binding: true })
    try {
      // bindWechatAuto：code 失效时自动换新 code 重试一次（code 一次性使用）
      const res = await api.bindWechatAuto({ silent: true })
      if (res && res.has_wx_bind) {
        app.globalData.userInfo = res
        this.setData({ hasWxBind: true })
        wx.showToast({ title: '绑定成功', icon: 'success' })
      }
    } catch (err) {
      console.error('绑定微信失败:', err)
      wx.showToast({ title: err.message || '绑定失败', icon: 'none' })
    } finally {
      this.setData({ binding: false })
    }
  },

  onClearCache() {
    wx.showModal({
      title: '提示',
      content: '清除本地缓存？（不会影响登录状态）',
      success: (res) => {
        if (!res.confirm) return
        const token = wx.getStorageSync('token')
        wx.clearStorageSync()
        if (token) wx.setStorageSync('token', token)
        wx.showToast({ title: '缓存已清除', icon: 'success' })
      }
    })
  },

  onAbout() {
    wx.showModal({
      title: '关于宠物宝',
      content: '宠物宝 v' + APP_VERSION + '\n科学养宠，从成分开始。提供产品安全评分、成分查询、品种百科、喂养提醒等服务。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  onFeedback() {
    wx.showToast({ title: '感谢您的反馈', icon: 'none' })
  }
})