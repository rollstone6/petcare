<template>
  <view class="container">
    <view class="list">
      <view v-for="brand in brands" :key="brand.id" class="brand-card">
        <image :src="brand.logo || '/static/brand-default.png'" class="brand-logo" mode="aspectFill"></image>
        <view class="brand-info">
          <text class="brand-name">{{ brand.name }}</text>
          <text class="brand-country">{{ brand.country || '未知' }}</text>
        </view>
      </view>
    </view>
    <view v-if="brands.length === 0" class="empty">暂无品牌数据</view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const brands = ref<any[]>([])

onMounted(async () => {
  const res = await api.brands.list()
  if (res.code === 200) brands.value = res.data || []
})
</script>

<style scoped>
.container { padding: 20rpx; }
.list { display: flex; flex-direction: column; gap: 20rpx; }
.brand-card { display: flex; align-items: center; background: #fff; padding: 20rpx; border-radius: 20rpx; gap: 20rpx; }
.brand-logo { width: 120rpx; height: 120rpx; border-radius: 60rpx; background: #f5f5f5; }
.brand-info { flex: 1; }
.brand-name { font-size: 32rpx; color: #333; font-weight: 500; display: block; margin-bottom: 10rpx; }
.brand-country { font-size: 26rpx; color: #999; }
.empty { text-align: center; padding: 100rpx 0; color: #999; }
</style>
