// pages/product/detail.js
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    product: null,
    reviews: [],
    isFavorite: false,
    loading: true,
    reviewPage: 1,
    hasMoreReviews: true
  },

  onLoad(options) {
    if (options.id) {
      this.productId = options.id
      this.loadProduct()
      this.loadReviews()
    }
  },

  // 加载产品详情
  async loadProduct() {
    try {
      const product = await api.getProductDetail(this.productId)
      
      // 检查是否已收藏
      let isFavorite = false
      if (app.globalData.isLogin) {
        try {
          const favorites = await api.getFavorites()
          isFavorite = favorites.some(f => f.product_id == this.productId)
        } catch (e) {}
      }
      
      this.setData({ 
        product, 
        isFavorite,
        loading: false 
      })
    } catch (err) {
      console.error('加载产品详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  // 加载评价
  async loadReviews(reset = true) {
    if (reset) {
      this.setData({ reviewPage: 1, reviews: [], hasMoreReviews: true })
    }
    
    try {
      const result = await api.getProductReviews(this.productId, {
        page: this.data.reviewPage,
        page_size: 10
      })
      const items = result.items || result || []
      
      this.setData({
        reviews: reset ? items : [...this.data.reviews, ...items],
        hasMoreReviews: items.length >= 10
      })
    } catch (err) {
      console.error('加载评价失败:', err)
    }
  },

  // 加载更多评价
  onLoadMoreReviews() {
    if (this.data.hasMoreReviews) {
      this.setData({ reviewPage: this.data.reviewPage + 1 })
      this.loadReviews(false)
    }
  },

  // 收藏/取消收藏
  async onToggleFavorite() {
    if (!app.globalData.isLogin) {
      wx.navigateTo({ url: '/pages/user/login' })
      return
    }

    try {
      if (this.data.isFavorite) {
        const favorites = await api.getFavorites()
        const fav = favorites.find(f => f.product_id == this.productId)
        if (fav) {
          await api.removeFavorite(fav.id)
        }
        this.setData({ isFavorite: false })
        wx.showToast({ title: '已取消收藏', icon: 'none' })
      } else {
        await api.addFavorite({ product_id: this.productId })
        this.setData({ isFavorite: true })
        wx.showToast({ title: '已收藏', icon: 'none' })
      }
    } catch (err) {
      console.error('收藏操作失败:', err)
      wx.showToast({ title: '操作失败', icon: 'none' })
    }
  },

  // 分享
  onShareAppMessage() {
    const { product } = this.data
    return {
      title: product ? `${product.name} - 安全评分 ${product.safety_score}` : '宠物宝',
      path: `/pages/product/detail?id=${this.productId}`
    }
  },

  // 查看成分详情
  onIngredientTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/ingredient/detail?id=${id}`
    })
  },

  // 查看品牌详情
  onBrandTap() {
    const brand = this.data.product?.brand
    if (brand) {
      wx.navigateTo({
        url: `/pages/search/search?brand=${encodeURIComponent(brand)}`
      })
    }
  },

  // 写评价
  onWriteReview() {
    if (!app.globalData.isLogin) {
      wx.navigateTo({ url: '/pages/user/login' })
      return
    }
    wx.showToast({ title: '评价功能开发中', icon: 'none' })
  }
})