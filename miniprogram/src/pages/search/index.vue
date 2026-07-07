<template>
  <view class="container">
    <!-- 搜索框 -->
    <view class="search-box">
      <input 
        v-model="keyword" 
        class="search-input" 
        placeholder="搜索产品名称、品牌、成分"
        @confirm="doSearch"
      />
      <button class="search-btn" @click="doSearch">搜索</button>
    </view>

    <!-- 筛选条件 -->
    <view class="filter-bar">
      <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="setFilter('all')">
        全部
      </view>
      <view class="filter-item" :class="{ active: activeFilter === 'brand' }" @click="setFilter('brand')">
        按品牌
      </view>
      <view class="filter-item" :class="{ active: activeFilter === 'category' }" @click="setFilter('category')">
        按分类
      </view>
    </view>

    <!-- 搜索结果 -->
    <view class="result-section" v-if="searchResults.length > 0">
      <view 
        v-for="product in searchResults" 
        :key="product.id" 
        class="product-card"
        @click="goDetail(product.id)"
      >
        <image :src="product.image_url || '/static/product-default.png'" class="product-img" mode="aspectFill"></image>
        <view class="product-info">
          <text class="product-name">{{ product.name }}</text>
          <text class="product-brand">{{ product.brand_name }}</text>
          <view class="product-meta">
            <text class="product-category">{{ product.category_name }}</text>
            <view class="product-score">
              <text class="score-label">安全评分</text>
              <text class="score-value" :class="getScoreClass(product.safety_score)">
                {{ product.safety_score?.toFixed(1) || '0.0' }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="searchResults.length === 0 && hasSearched">
      <text class="empty-icon">🔍</text>
      <text class="empty-text">未找到相关产品</text>
      <text class="empty-hint">试试其他关键词</text>
    </view>

    <!-- 加载提示 -->
    <view class="loading-more" v-if="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'

const keyword = ref('')
const activeFilter = ref('all')
const searchResults = ref<any[]>([])
const hasSearched = ref(false)
const loading = ref(false)

const doSearch = async () => {
  if (!keyword.value.trim()) {
    uni.showToast({ title: '请输入搜索关键词', icon: 'none' })
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const res = await api.products.list({ 
      keyword: keyword.value,
      page: 1,
      page_size: 20
    })
    
    if (res.code === 200) {
      searchResults.value = res.data.items || []
    }
  } catch (e) {
    console.error('Search failed:', e)
    uni.showToast({ title: '搜索失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const setFilter = (filter: string) => {
  activeFilter.value = filter
  if (filter === 'brand') {
    uni.showToast({ title: '品牌筛选开发中', icon: 'none' })
  } else if (filter === 'category') {
    uni.showToast({ title: '分类筛选开发中', icon: 'none' })
  }
}

const getScoreClass = (score: number) => {
  if (score >= 4) return 'score-good'
  if (score >= 3) return 'score-normal'
  return 'score-bad'
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/product/detail?id=${id}` })
}
</script>

<style scoped>
.container {
  padding: 20rpx 30rpx;
  padding-bottom: 120rpx;
}

.search-box {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.search-input {
  flex: 1;
  background: #fff;
  border-radius: 40rpx;
  padding: 20rpx 30rpx;
  font-size: 28rpx;
}

.search-btn {
  background: #FF6B6B;
  color: #fff;
  border-radius: 40rpx;
  padding: 0 40rpx;
  font-size: 28rpx;
  line-height: 80rpx;
}

.filter-bar {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.filter-item {
  padding: 15rpx 30rpx;
  background: #fff;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}

.filter-item.active {
  background: #FF6B6B;
  color: #fff;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.product-card {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}

.product-img {
  width: 200rpx;
  height: 200rpx;
  background: #f5f5f5;
}

.product-info {
  flex: 1;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 30rpx;
  color: #333;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10rpx;
}

.product-brand {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 15rpx;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-category {
  font-size: 24rpx;
  color: #FF6B6B;
  background: #FFE5E5;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.product-score {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.score-label {
  font-size: 24rpx;
  color: #666;
}

.score-value {
  font-size: 36rpx;
  font-weight: bold;
}

.score-good { color: #52c41a; }
.score-normal { color: #faad14; }
.score-bad { color: #ff4d4f; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 15rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #999;
}

.loading-more {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}
</style>
