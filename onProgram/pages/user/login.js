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
    // 注册时与后端校验规则保持一致：密码至少8位且包含字母和数字
    if (isRegister) {
      if (password.length < 8) {
        wx.showToast({ title: '注册密码至少8位', icon: 'none' })
        return
      }
      if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
        wx.showToast({ title: '密码需包含字母和数字', icon: 'none' })
        return
      }
    }

    this.setData({ loading: true })

    try {
      let res
      if (isRegister) {
        // 临时兼容：线上旧版后端 email 列 default=""+unique 会让无邮箱用户撞唯一约束(500)。
        // 用用户名派生唯一占位邮箱规避；用户名本身唯一，邮箱必唯一。部署新版后端后此参数保留也无害。
        res = await api.register({ username, password, email: `${username}@petcare.app` })
        wx.showToast({ title: '注册成功', icon: 'success' })
      } else {
        res = await api.login({ username, password })
        wx.showToast({ title: '登录成功', icon: 'success' })
      }

      if (res && res.token) {
        api.setToken(res.token)
        app.globalData.isLogin = true
        app.globalData.userInfo = res.user || null
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

  // 微信一键登录：wx.login 拿 code → 后端换 token（未绑定的微信自动注册新账号）
  // wxLoginAuto 会在 code 失效时自动换新 code 重试一次（code 一次性使用）
  async onWechatLogin() {
    if (this.data.loading) return
    this.setData({ loading: true })
    try {
      const res = await api.wxLoginAuto({ silent: true })
      if (res && res.token) {
        api.setToken(res.token)
        app.globalData.isLogin = true
        app.globalData.userInfo = res.user || null
        wx.showToast({ title: res.is_new ? '已自动注册并登录' : '登录成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1000)
      }
    } catch (err) {
      console.error('微信登录失败:', err)
      wx.showToast({ title: err.message || '微信登录失败，请用账号密码登录', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  }
})