<template>
  <view class="container">
    <view class="user-card">
      <image :src="user?.avatar || '/static/avatar-default.png'" class="avatar"></image>
      <view class="user-info" v-if="isLoggedIn">
        <text class="username">{{ user?.username }}</text>
        <text class="user-email">{{ user?.email }}</text>
      </view>
      <view class="user-info" v-else @click="goLogin">
        <text class="username">点击登录</text>
        <text class="user-email">登录体验更多功能</text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" @click="goPage('/pages/pets/index')">
        <text class="menu-icon">🐾</text>
        <text class="menu-text">我的宠物</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item">
        <text class="menu-icon">❤️</text>
        <text class="menu-text">我的收藏</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item">
        <text class="menu-icon">📝</text>
        <text class="menu-text">我的评论</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item">
        <text class="menu-icon">📊</text>
        <text class="menu-text">健康记录</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于我们</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" v-if="isLoggedIn" @click="handleLogout">
        <text class="menu-icon">🚪</text>
        <text class="menu-text">退出登录</text>
        <text class="menu-arrow">></text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const isLoggedIn = computed(() => userStore.isLoggedIn())

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}

const goPage = (url: string) => {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.showToast({ title: '已退出', icon: 'success' })
      }
    }
  })
}
</script>

<style scoped>
.container { padding: 20rpx; }
.user-card { display: flex; align-items: center; background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); padding: 40rpx; border-radius: 20rpx; color: #fff; gap: 30rpx; margin-bottom: 20rpx; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; border: 4rpx solid rgba(255,255,255,0.5); background: #f5f5f5; }
.user-info { flex: 1; }
.username { font-size: 36rpx; font-weight: bold; display: block; margin-bottom: 10rpx; }
.user-email { font-size: 26rpx; opacity: 0.8; }
.menu-list { background: #fff; border-radius: 20rpx; margin-bottom: 20rpx; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 30rpx; border-bottom: 1rpx solid #f5f5f5; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 40rpx; margin-right: 20rpx; }
.menu-text { flex: 1; font-size: 30rpx; color: #333; }
.menu-arrow { font-size: 28rpx; color: #ccc; }
</style>
