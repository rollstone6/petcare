// pages/search/search.js
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    filterType: '',
    sortBy: 'default',
    products: [],
    loading: false,
    hasMore: true,
    page: 1
  },

  onLoad(options) {
    if (options.q) {
      this.setData({ keyword: decodeURIComponent(options.q) })
    }
    if (options.type) {
      this.setData({ filterType: decodeURIComponent(options.type) })
    }
    this.loadProducts()
  },

  // 输入搜索关键词
  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  // 清空输入
  onClear() {
    this.setData({ keyword: '' })
  },

  // 确认搜索
  onSearch() {
    this.setData({ page: 1, products: [], hasMore: true })
    this.loadProducts()
  },

  // 类型筛选
  onTypeFilter(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ filterType: type, page: 1, products: [], hasMore: true })
    this.loadProducts()
  },

  // 排序
  onSort(e) {
    const sort = e.currentTarget.dataset.sort
    this.setData({ sortBy: sort, page: 1, products: [], hasMore: true })
    this.loadProducts()
  },

  // 加载产品列表
  async loadProducts() {
    if (this.data.loading) return

    this.setData({ loading: true })
    try {
      const params = {
        page: this.data.page,
        page_size: 20
      }
      if (this.data.keyword) {
        params.keyword = this.data.keyword
      }
      if (this.data.filterType) {
        params.type = this.data.filterType
      }
      if (this.data.sortBy !== 'default') {
        params.sort = this.data.sortBy
      }

      const result = await api.getProducts(params)
      const items = result.items || result || []

      this.setData({
        products: this.data.page === 1 ? items : [...this.data.products, ...items],
        hasMore: items.length >= 20,
        loading: false
      })
    } catch (err) {
      console.error('加载产品失败:', err)
      this.setData({ loading: false })
    }
  },

  // 点击产品
  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product/detail?id=${id}`
    })
  },

  // 加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 })
      this.loadProducts()
    }
  }
})