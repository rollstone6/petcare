<template>
  <view class="container">
    <view class="logo-section">
      <text class="logo-emoji">🐾</text>
      <text class="logo-text">宠物宝</text>
      <text class="logo-slogan">专业的宠物食品安全评分平台</text>
    </view>

    <view class="form-section">
      <view class="tabs">
        <view class="tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</view>
        <view class="tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</view>
      </view>

      <view class="input-group">
        <text class="label">用户名</text>
        <input v-model="username" class="input" placeholder="请输入用户名" />
      </view>
      <view class="input-group">
        <text class="label">密码</text>
        <input v-model="password" class="input" type="password" placeholder="请输入密码" />
      </view>
      <view class="input-group" v-if="mode === 'register'">
        <text class="label">邮箱</text>
        <input v-model="email" class="input" placeholder="请输入邮箱（选填）" />
      </view>

      <button class="submit-btn" @click="submit">
        {{ mode === 'login' ? '登录' : '注册' }}
      </button>

      <view class="wx-login" @click="wxLogin">
        <text class="wx-icon">💚</text>
        <text>微信一键登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const email = ref('')

const submit = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }

  try {
    if (mode.value === 'login') {
      await userStore.login(username.value, password.value)
    } else {
      await userStore.register(username.value, password.value, email.value)
    }
    uni.showToast({ title: '成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 1500)
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

const wxLogin = () => {
  uni.showToast({ title: '微信登录待接入', icon: 'none' })
}
</script>

<style scoped>
.container { padding: 60rpx 40rpx; }
.logo-section { text-align: center; margin-bottom: 80rpx; }
.logo-emoji { font-size: 120rpx; display: block; margin-bottom: 20rpx; }
.logo-text { font-size: 48rpx; font-weight: bold; color: #333; display: block; margin-bottom: 15rpx; }
.logo-slogan { font-size: 26rpx; color: #999; }
.form-section { background: #fff; padding: 40rpx; border-radius: 20rpx; }
.tabs { display: flex; margin-bottom: 40rpx; border-bottom: 1rpx solid #f0f0f0; }
.tab { flex: 1; text-align: center; padding: 20rpx; color: #999; font-size: 30rpx; }
.tab.active { color: #FF6B6B; border-bottom: 4rpx solid #FF6B6B; }
.input-group { margin-bottom: 30rpx; }
.label { font-size: 26rpx; color: #666; display: block; margin-bottom: 15rpx; }
.input { background: #f9f9f9; padding: 25rpx; border-radius: 15rpx; font-size: 28rpx; }
.submit-btn { background: #FF6B6B; color: #fff; border-radius: 40rpx; padding: 25rpx 0; font-size: 32rpx; margin-top: 40rpx; }
.wx-login { display: flex; align-items: center; justify-content: center; gap: 15rpx; margin-top: 40rpx; padding: 25rpx; border: 1rpx solid #eee; border-radius: 40rpx; color: #666; font-size: 28rpx; }
.wx-icon { font-size: 32rpx; }
</style>
