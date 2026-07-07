import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface User {
  id: number
  username: string
  email?: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')

  // 初始化
  const init = () => {
    const storedToken = uni.getStorageSync('token')
    const storedUser = uni.getStorageSync('user')
    
    if (storedToken) {
      token.value = storedToken
    }
    
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse user:', e)
      }
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    const res = await api.auth.login({ username, password })
    if (res.code === 200) {
      token.value = res.data.access_token
      uni.setStorageSync('token', res.data.access_token)
      await fetchUser()
    }
    return res
  }

  // 注册
  const register = async (username: string, password: string, email?: string) => {
    const res = await api.auth.register({ username, password, email })
    if (res.code === 200) {
      // 注册成功后自动登录
      await login(username, password)
    }
    return res
  }

  // 获取用户信息
  const fetchUser = async () => {
    try {
      const res = await api.auth.getMe()
      if (res.code === 200) {
        user.value = res.data
        uni.setStorageSync('user', JSON.stringify(res.data))
      }
    } catch (e) {
      console.error('Failed to fetch user:', e)
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = ''
    uni.removeStorageSync('token')
    uni.removeStorageSync('user')
  }

  // 是否已登录
  const isLoggedIn = () => {
    return !!token.value
  }

  return {
    user,
    token,
    init,
    login,
    register,
    fetchUser,
    logout,
    isLoggedIn,
  }
})
