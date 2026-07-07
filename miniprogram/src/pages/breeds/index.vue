<template>
  <view class="container">
    <view class="tabs">
      <view class="tab" :class="{ active: tab === 'all' }" @click="tab = 'all'">全部</view>
      <view class="tab" :class="{ active: tab === '猫' }" @click="tab = '猫'">猫咪</view>
      <view class="tab" :class="{ active: tab === '狗' }" @click="tab = '狗'">狗狗</view>
    </view>
    <view class="grid">
      <view v-for="breed in filtered" :key="breed.id" class="breed-card" @click="goDetail(breed.id)">
        <image :src="breed.image_url" class="breed-img" mode="aspectFill"></image>
        <text class="breed-name">{{ breed.name }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const breeds = ref<any[]>([])
const tab = ref('all')
const filtered = computed(() => 
  tab.value === 'all' ? breeds.value : breeds.value.filter(b => b.species === tab.value)
)

onMounted(async () => {
  const res = await api.breeds.list()
  if (res.code === 200) breeds.value = res.data || []
})

const goDetail = (id: number) => {
  uni.showToast({ title: '品种详情开发中', icon: 'none' })
}
</script>

<style scoped>
.container { padding: 20rpx; }
.tabs { display: flex; gap: 20rpx; margin-bottom: 30rpx; }
.tab { flex: 1; text-align: center; padding: 20rpx; background: #fff; border-radius: 30rpx; color: #666; }
.tab.active { background: #FF6B6B; color: #fff; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20rpx; }
.breed-card { background: #fff; border-radius: 20rpx; overflow: hidden; text-align: center; }
.breed-img { width: 100%; height: 200rpx; background: #f5f5f5; }
.breed-name { padding: 15rpx; font-size: 26rpx; color: #333; }
</style>
