<template>
  <view class="container">
    <!-- 顶部搜索栏 -->
    <view class="search-bar">
      <view class="search-input" @click="goSearch">
        <text class="iconfont">🔍</text>
        <text class="placeholder">搜索产品、品牌、成分</text>
      </view>
    </view>

    <!-- 轮播图 -->
    <swiper class="banner" indicator-dots autoplay circular>
      <swiper-item>
        <image src="/static/banner1.jpg" mode="aspectFill" class="banner-img"></image>
      </swiper-item>
      <swiper-item>
        <image src="/static/banner2.jpg" mode="aspectFill" class="banner-img"></image>
      </swiper-item>
    </swiper>

    <!-- 快捷入口 -->
    <view class="quick-entry">
      <view class="entry-item" @click="goBrands">
        <view class="entry-icon brands">🏷️</view>
        <text>品牌库</text>
      </view>
      <view class="entry-item" @click="goIngredients">
        <view class="entry-icon ingredients">🧪</view>
        <text>成分库</text>
      </view>
      <view class="entry-item" @click="goBreeds">
        <view class="entry-icon breeds">🐾</view>
        <text>品种库</text>
      </view>
      <view class="entry-item" @click="goAI">
        <view class="entry-icon ai">🤖</view>
        <text>AI问答</text>
      </view>
    </view>

    <!-- 热门品牌 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">热门品牌</text>
        <text class="section-more" @click="goBrands">更多 ></text>
      </view>
      <scroll-view scroll-x class="brand-scroll">
        <view class="brand-list">
          <view 
            v-for="brand in hotBrands" 
            :key="brand.id" 
            class="brand-item"
            @click="goBrandDetail(brand.id)"
          >
            <image :src="brand.logo || '/static/brand-default.png'" class="brand-logo" mode="aspectFill"></image>
            <text class="brand-name">{{ brand.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 推荐产品 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">推荐产品</text>
        <text class="section-more" @click="goSearch">更多 ></text>
      </view>
      <view class="product-list">
        <view 
          v-for="product in recommendProducts" 
          :key="product.id" 
          class="product-card"
          @click="goProductDetail(product.id)"
        >
          <image :src="product.image_url || '/static/product-default.png'" class="product-img" mode="aspectFill"></image>
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <text class="product-brand">{{ product.brand_name }}</text>
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
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const hotBrands = ref<any[]>([])
const recommendProducts = ref<any[]>([])

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  try {
    // 加载热门品牌
    const brandsRes = await api.brands.hot()
    if (brandsRes.code === 200) {
      hotBrands.value = brandsRes.data.slice(0, 8)
    }

    // 加载推荐产品
    const productsRes = await api.products.list({ page: 1, page_size: 6 })
    if (productsRes.code === 200) {
      recommendProducts.value = productsRes.data.items || []
    }
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const getScoreClass = (score: number) => {
  if (score >= 4) return 'score-good'
  if (score >= 3) return 'score-normal'
  return 'score-bad'
}

const goSearch = () => {
  uni.switchTab({ url: '/pages/search/index' })
}

const goBrands = () => {
  uni.navigateTo({ url: '/pages/brands/index' })
}

const goIngredients = () => {
  uni.navigateTo({ url: '/pages/ingredients/index' })
}

const goBreeds = () => {
  uni.navigateTo({ url: '/pages/breeds/index' })
}

const goAI = () => {
  uni.showToast({ title: 'AI问答功能开发中', icon: 'none' })
}

const goBrandDetail = (id: number) => {
  uni.showToast({ title: '品牌详情开发中', icon: 'none' })
}

const goProductDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/product/detail?id=${id}` })
}
</script>

<style scoped>
.container {
  padding-bottom: 120rpx;
}

.search-bar {
  padding: 20rpx 30rpx;
  background: #fff;
}

.search-input {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 20rpx 30rpx;
}

.search-input .iconfont {
  font-size: 32rpx;
  margin-right: 15rpx;
}

.search-input .placeholder {
  color: #999;
  font-size: 28rpx;
}

.banner {
  height: 300rpx;
  margin: 20rpx 0;
}

.banner-img {
  width: 100%;
  height: 100%;
}

.quick-entry {
  display: flex;
  justify-content: space-around;
  padding: 40rpx 30rpx;
  background: #fff;
  margin-bottom: 20rpx;
}

.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 26rpx;
  color: #333;
}

.entry-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  margin-bottom: 15rpx;
}

.entry-icon.brands { background: #FFE5E5; }
.entry-icon.ingredients { background: #E5F0FF; }
.entry-icon.breeds { background: #FFF5E5; }
.entry-icon.ai { background: #F0E5FF; }

.section {
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.section-more {
  font-size: 26rpx;
  color: #999;
}

.brand-scroll {
  white-space: nowrap;
}

.brand-list {
  display: inline-flex;
  gap: 20rpx;
}

.brand-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 140rpx;
}

.brand-logo {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: #f5f5f5;
  margin-bottom: 15rpx;
}

.brand-name {
  font-size: 24rpx;
  color: #666;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 140rpx;
}

.product-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.product-card {
  width: calc(50% - 10rpx);
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}

.product-img {
  width: 100%;
  height: 300rpx;
  background: #f5f5f5;
}

.product-info {
  padding: 20rpx;
}

.product-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10rpx;
}

.product-brand {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 15rpx;
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
  font-size: 32rpx;
  font-weight: bold;
}

.score-good { color: #52c41a; }
.score-normal { color: #faad14; }
.score-bad { color: #ff4d4f; }
</style>
