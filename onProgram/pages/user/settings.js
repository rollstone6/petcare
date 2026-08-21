// pages/user/settings.js — 设置
const api = require('../../utils/api')
const app = getApp()

const APP_VERSION = '1.0.0'

function toast(msg, icon = 'none') {
  wx.showToast({ title: msg, icon, duration: 2500 })
}

Page({
  data: {
    version: APP_VERSION,
    isLogin: false,
    username: '',
    hasWxBind: false,
    binding: false,
    hasPassword: false,
    // 设置/修改密码表单
    showPasswordForm: false,
    submitting: false,
    newUsername: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  },

  onShow() {
    const isLogin = app.globalData.isLogin
    this.setData({
      isLogin,
      username: app.globalData.userInfo?.username || '',
      hasWxBind: !!app.globalData.userInfo?.has_wx_bind,
      hasPassword: !!app.globalData.userInfo?.has_password
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

  // ===== 设置/修改账号密码 =====

  onTogglePasswordForm() {
    if (!app.globalData.isLogin) {
      wx.navigateTo({ url: '/pages/user/login' })
      return
    }
    this.setData({ showPasswordForm: !this.data.showPasswordForm })
  },

  onNewUsernameInput(e) { this.setData({ newUsername: e.detail.value }) },
  onOldPasswordInput(e) { this.setData({ oldPassword: e.detail.value }) },
  onNewPasswordInput(e) { this.setData({ newPassword: e.detail.value }) },
  onConfirmPasswordInput(e) { this.setData({ confirmPassword: e.detail.value }) },

  async onSubmitPassword() {
    const { hasPassword, oldPassword, newPassword, confirmPassword, newUsername, submitting } = this.data
    if (submitting) return

    if (hasPassword && !oldPassword) { toast('请输入原密码'); return }
    if (newPassword.length < 8 || !/[a-zA-Z]/.test(newPassword) || !/\d/.test(newPassword)) {
      toast('新密码至少8位且包含字母和数字')
      return
    }
    if (newPassword !== confirmPassword) { toast('两次输入的密码不一致'); return }

    this.setData({ submitting: true })
    try {
      const payload = { password: newPassword }
      if (!hasPassword && newUsername.trim()) payload.username = newUsername.trim()
      if (hasPassword) payload.old_password = oldPassword
      const res = await api.setPassword(payload, { silent: true })
      app.globalData.userInfo = res
      this.setData({
        hasPassword: true,
        showPasswordForm: false,
        username: res.username || this.data.username,
        newUsername: '',
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
      wx.showToast({ title: hasPassword ? '密码已修改' : '设置成功', icon: 'success' })
    } catch (err) {
      wx.showToast({ title: err.message || '设置失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
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