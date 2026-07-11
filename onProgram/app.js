// app.js
const api = require('./utils/api')

App({
  onLaunch() {
    // 检查登录状态
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
          // token 无效，清除
          api.clearToken()
          this.globalData.userInfo = null
          this.globalData.isLogin = false
        })
    }
  },

  // 全局数据
  globalData: {
    userInfo: null,
    isLogin: false
  }
})