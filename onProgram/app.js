// app.js
const api = require('./utils/api')

App({
  onLaunch() {
    // 检查登录状态（无 token 时尝试微信静默登录）
    this.checkLoginStatus()
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = api.getToken()
    if (token) {
      // 尝试获取用户信息验证 token 是否有效
      api.getUserInfo()
        .then(userInfo => {
          this.globalData.userInfo = userInfo
          this.globalData.isLogin = true
        })
        .catch(() => {
          // token 无效，清除后走静默登录兜底
          api.clearToken()
          this.globalData.userInfo = null
          this.globalData.isLogin = false
          this.silentWxLogin()
        })
    } else {
      // 无 token：尝试微信静默登录（wx.login 无需用户授权，用户无感知）
      this.silentWxLogin()
    }
  },

  // 微信静默登录：已绑定过微信的用户打开小程序即自动恢复登录态；
  // 从未用过微信登录的新用户也会被自动注册（与手动点「微信快捷登录」等效）。
  // 任何环节失败都静默降级为未登录，不打扰用户。
  silentWxLogin() {
    api.wxLoginAuto({ silent: true })
      .then(res => {
        if (res && res.token) {
          api.setToken(res.token)
          this.globalData.userInfo = res.user || null
          this.globalData.isLogin = true
        }
      })
      .catch(() => {
        // 静默失败：保持未登录状态
      })
  },

  // 全局数据
  globalData: {
    userInfo: null,
    isLogin: false
  }
})