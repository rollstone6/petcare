<template>
  <view class="container">
    <view class="search-box">
      <input v-model="keyword" class="search-input" placeholder="搜索成分" @input="filter" />
    </view>
    <view class="list">
      <view v-for="ing in filtered" :key="ing.id" class="ing-card">
        <text class="ing-name">{{ ing.name }}</text>
        <text class="ing-safety" :class="'level-' + ing.safety_level">安全等级: {{ ing.safety_level }}/5</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const ingredients = ref<any[]>([])
const keyword = ref('')
const filtered = computed(() => 
  ingredients.value.filter(i => !keyword.value || i.name.includes(keyword.value))
)

onMounted(async () => {
  const res = await api.ingredients.list()
  if (res.code === 200) ingredients.value = res.data || []
})

const filter = () => {}
</script>

<style scoped>
.container { padding: 20rpx; }
.search-box { margin-bottom: 20rpx; }
.search-input { background: #fff; border-radius: 40rpx; padding: 20rpx 30rpx; }
.list { display: flex; flex-direction: column; gap: 20rpx; }
.ing-card { background: #fff; padding: 30rpx; border-radius: 20rpx; display: flex; justify-content: space-between; align-items: center; }
.ing-name { font-size: 30rpx; color: #333; }
.ing-safety { font-size: 24rpx; padding: 8rpx 20rpx; border-radius: 20rpx; }
.level-5, .level-4 { background: #F6FFED; color: #52c41a; }
.level-3 { background: #FFFBE6; color: #faad14; }
.level-2, .level-1 { background: #FFF1F0; color: #ff4d4f; }
</style>
