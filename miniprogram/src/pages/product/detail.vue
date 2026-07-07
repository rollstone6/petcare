<template>
  <view class="container">
    <!-- 产品图片 -->
    <view class="product-header">
      <image :src="product.image_url || '/static/product-default.png'" class="product-img" mode="aspectFit"></image>
    </view>

    <!-- 基本信息 -->
    <view class="product-info">
      <text class="product-name">{{ product.name }}</text>
      <view class="product-tags">
        <text class="tag brand">{{ product.brand_name }}</text>
        <text class="tag category">{{ product.category_name }}</text>
      </view>
      <view class="score-section">
        <text class="score-label">安全评分</text>
        <text class="score-value" :class="getScoreClass(product.safety_score)">
          {{ product.safety_score?.toFixed(1) || '0.0' }}
        </text>
        <text class="score-unit">/ 5.0</text>
      </view>
    </view>

    <!-- 产品描述 -->
    <view class="section" v-if="product.description">
      <text class="section-title">产品描述</text>
      <text class="section-content">{{ product.description }}</text>
    </view>

    <!-- 成分列表 -->
    <view class="section" v-if="product.ingredients && product.ingredients.length > 0">
      <text class="section-title">成分列表</text>
      <view class="ingredient-list">
        <view 
          v-for="ingredient in product.ingredients" 
          :key="ingredient.id"
          class="ingredient-item"
        >
          <text class="ingredient-name">{{ ingredient.name }}</text>
          <text class="ingredient-safety" :class="getSafetyClass(ingredient.safety_level)">
            {{ ingredient.safety_level }}/5
          </text>
        </view>
      </view>
    </view>

    <!-- 使用说明 -->
    <view class="section" v-if="product.usage_guide">
      <text class="section-title">使用说明</text>
      <text class="section-content">{{ product.usage_guide }}</text>
    </view>

    <!-- 适用对象 -->
    <view class="section">
      <text class="section-title">适用对象</text>
      <view class="apply-info">
        <view class="info-item">
          <text class="info-label">适用物种</text>
          <text class="info-value">{{ product.suitable_species || '猫狗' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">适用体型</text>
          <text class="info-value">{{ product.target_size || '全部' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">适用年龄</text>
          <text class="info-value">{{ product.target_age || '全部' }}</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-bar">
      <button class="action-btn favorite" @click="toggleFavorite">
        {{ isFavorite ? '❤️ 已收藏' : '🤍 收藏' }}
      </button>
      <button class="action-btn share" open-type="share">
        📤 分享
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import api from '@/api'

const product = ref<any>({})
const isFavorite = ref(false)
const productId = ref<number>(0)

onLoad((options) => {
  if (options?.id) {
    productId.value = parseInt(options.id)
    loadProduct()
  }
})

const loadProduct = async () => {
  uni.showLoading({ title: '加载中...' })
  
  try {
    const res = await api.products.detail(productId.value)
    if (res.code === 200) {
      product.value = res.data
    }
  } catch (e) {
    console.error('Failed to load product:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

const getScoreClass = (score: number) => {
  if (score >= 4) return 'score-good'
  if (score >= 3) return 'score-normal'
  return 'score-bad'
}

const getSafetyClass = (level: number) => {
  if (level >= 4) return 'safety-good'
  if (level >= 3) return 'safety-normal'
  return 'safety-bad'
}

const toggleFavorite = async () => {
  try {
    if (isFavorite.value) {
      await api.favorites.remove(productId.value)
      isFavorite.value = false
      uni.showToast({ title: '已取消收藏', icon: 'success' })
    } else {
      await api.favorites.add(productId.value)
      isFavorite.value = true
      uni.showToast({ title: '已收藏', icon: 'success' })
    }
  } catch (e) {
    console.error('Failed to toggle favorite:', e)
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}
</script>

<style scoped>
.container {
  padding-bottom: 180rpx;
}

.product-header {
  background: #fff;
  padding: 40rpx;
  text-align: center;
}

.product-img {
  width: 400rpx;
  height: 400rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
}

.product-info {
  background: #fff;
  padding: 30rpx;
  margin-top: 20rpx;
}

.product-name {
  font-size: 36rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.product-tags {
  display: flex;
  gap: 15rpx;
  margin-bottom: 30rpx;
}

.tag {
  padding: 10rpx 25rpx;
  border-radius: 25rpx;
  font-size: 24rpx;
}

.tag.brand {
  background: #E5F0FF;
  color: #1890FF;
}

.tag.category {
  background: #FFF5E5;
  color: #FA8C16;
}

.score-section {
  display: flex;
  align-items: baseline;
  gap: 15rpx;
}

.score-label {
  font-size: 28rpx;
  color: #666;
}

.score-value {
  font-size: 56rpx;
  font-weight: bold;
}

.score-unit {
  font-size: 28rpx;
  color: #999;
}

.score-good { color: #52c41a; }
.score-normal { color: #faad14; }
.score-bad { color: #ff4d4f; }

.section {
  background: #fff;
  padding: 30rpx;
  margin-top: 20rpx;
}

.section-title {
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.section-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  display: block;
}

.ingredient-list {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 20rpx;
  background: #f9f9f9;
  border-radius: 15rpx;
}

.ingredient-name {
  font-size: 28rpx;
  color: #333;
}

.ingredient-safety {
  font-size: 24rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.safety-good { background: #F6FFED; color: #52c41a; }
.safety-normal { background: #FFFBE6; color: #faad14; }
.safety-bad { background: #FFF1F0; color: #ff4d4f; }

.apply-info {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: #666;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  display: flex;
  gap: 20rpx;
  box-shadow: 0 -4rpx 12rpx rgba(0,0,0,0.08);
}

.action-btn {
  flex: 1;
  padding: 25rpx 0;
  border-radius: 40rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.action-btn.favorite {
  background: #FFE5E5;
  color: #FF6B6B;
}

.action-btn.share {
  background: #E5F0FF;
  color: #1890FF;
}
</style>
