// pages/index/index.js
const api = require('../../utils/api')
const { formatImageUrl } = require('../../utils/util')

Page({
  data: {
    searchValue: '',
    categories: [],
    hotProducts: [],
    loading: true,
    placeholder: api.PLACEHOLDER_IMAGE
  },

  onLoad() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      // 并行加载品类和热门产品
      const [categories, products] = await Promise.all([
        api.getCategories(),
        api.getProducts({ page: 1, page_size: 10 })
      ])
      
      // 处理产品图片URL：后端返回 image_url 是相对路径，转为完整URL
      const items = products.items || products || []
      const formattedProducts = items.map(item => ({
        ...item,
        image: formatImageUrl(item.image_url, api.PLACEHOLDER_IMAGE)
      }))
      
      this.setData({
        categories: categories || [],
        hotProducts: formattedProducts,
        loading: false
      })
    } catch (err) {
      console.error('加载数据失败:', err)
      this.setData({ loading: false })
    }
  },

  // 搜索框点击
  onSearchTap() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchValue: e.detail.value })
  },

  // 搜索确认
  onSearchConfirm() {
    const value = this.data.searchValue.trim()
    if (value) {
      wx.navigateTo({
        url: `/pages/search/search?q=${encodeURIComponent(value)}`
      })
    }
  },

  // 分类点击
  onCategoryTap(e) {
    const { type, name } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/search/search?type=${encodeURIComponent(type)}&name=${encodeURIComponent(name)}`
    })
  },

  // 产品点击
  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product/detail?id=${id}`
    })
  },

  // 查看更多
  onMoreTap() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  }
})
