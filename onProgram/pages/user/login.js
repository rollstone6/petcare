// pages/user/login.js
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    username: '',
    password: '',
    isRegister: false,
    loading: false
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  toggleRegister() {
    this.setData({ isRegister: !this.data.isRegister })
  },

  async onSubmit() {
    const { username, password, isRegister } = this.data

    if (!username.trim()) {
      wx.showToast({ title: '请输入用户名', icon: 'none' })
      return
    }
    if (!password.trim()) {
      wx.showToast({ title: '请输入密码', icon: 'none' })
      return
    }
    if (password.length < 6) {
      wx.showToast({ title: '密码至少6位', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    try {
      let res
      if (isRegister) {
        res = await api.register(username, password)
        wx.showToast({ title: '注册成功', icon: 'success' })
      } else {
        res = await api.login(username, password)
        wx.showToast({ title: '登录成功', icon: 'success' })
      }

      if (res && res.token) {
        api.setToken(res.token)
        app.globalData.isLogin = true
        setTimeout(() => {
          wx.navigateBack()
        }, 1000)
      }
    } catch (err) {
      console.error('登录/注册失败:', err)
      wx.showToast({ title: err.message || '操作失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  onWechatLogin() {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        console.log('获取用户信息成功:', res.userInfo)
        wx.showToast({ title: '微信登录功能开发中', icon: 'none' })
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err)
      }
    })
  }
})