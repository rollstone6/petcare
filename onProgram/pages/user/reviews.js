// pages/user/reviews.js — 我的评价（对齐 PC 端 getMyReviews/deleteReview）
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    reviews: [],
    loading: true,
    page: 1,
    total: 0
  },

  onShow() {
    if (!app.globalData.isLogin) {
      this.setData({ loading: false, reviews: [] })
      return
    }
    this.setData({ page: 1, reviews: [] })
    this.loadReviews(1)
  },

  async loadReviews(page) {
    this.setData({ loading: true })
    try {
      const res = await api.getMyReviews({ page, page_size: 10 })
      const items = (res?.items || []).map((r) => ({
        ...r,
        stars: '★'.repeat(r.rating || 0) + '☆'.repeat(5 - (r.rating || 0)),
        created_at_fmt: this.formatDate(r.created_at)
      }))
      this.setData({
        reviews: page === 1 ? items : this.data.reviews.concat(items),
        total: res?.total || 0,
        page
      })
    } catch (err) {
      console.error('加载评价失败:', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  formatDate(str) {
    if (!str) return ''
    return String(str).replace('T', ' ').slice(0, 16)
  },

  onProductTap(e) {
    const { productId } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/detail?id=${productId}` })
  },

  onDeleteReview(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '提示',
      content: '确定删除这条评价吗？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.deleteReview(id)
          wx.showToast({ title: '已删除', icon: 'none' })
          this.setData({ page: 1, reviews: [] })
          this.loadReviews(1)
        } catch (err) {
          console.error('删除评价失败:', err)
        }
      }
    })
  },

  onReachBottom() {
    if (this.data.reviews.length < this.data.total) {
      this.loadReviews(this.data.page + 1)
    }
  }
})