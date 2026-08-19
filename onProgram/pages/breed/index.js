// pages/breed/index.js
const api = require('../../utils/api')
const { formatImageUrl } = require('../../utils/util')
const { SPECIES_ICONS, SORT_OPTIONS, PAGE_SIZE } = require('../../utils/constants')

const PLACEHOLDER = 'https://website-petcare-oss-bj.oss-cn-beijing.aliyuncs.com/images/placeholder.png'

Page({
  data: {
    breeds: [],
    loading: true,
    loadingMore: false,
    hasMore: true,
    page: 1,
    species: '',
    speciesList: ['全部'],
    sortBy: 'name',
    sortOptions: SORT_OPTIONS,
    speciesIcons: SPECIES_ICONS
  },

  onLoad() {
    this.loadSpecies()
    this.loadBreeds()
  },

  // 加载物种分类
  async loadSpecies() {
    try {
      const speciesData = await api.getSpecies()
      if (Array.isArray(speciesData)) {
        const speciesNames = speciesData.map(s => s.name)
        this.setData({
          speciesList: ['全部', ...speciesNames]
        })
      }
    } catch (err) {
      console.error('加载物种分类失败:', err)
      // 使用默认分类
      this.setData({
        speciesList: ['全部', '狗', '猫']
      })
    }
  },

  // 加载品种列表
  async loadBreeds(reset = true) {
    if (reset) {
      this.setData({ page: 1, breeds: [], hasMore: true })
    }

    if (this.data.loading && !reset) return
    this.setData({ loading: true })

    try {
      const params = {
        page: this.data.page,
        page_size: PAGE_SIZE,
        sort_by: this.data.sortBy
      }

      if (this.data.species) {
        params.species = this.data.species
      }

      const result = await api.getBreeds(params)
      const items = (result.items || result || []).map(breed => ({
        ...breed,
        image: formatImageUrl(breed.image_url, PLACEHOLDER)
      }))

      this.setData({
        breeds: reset ? items : [...this.data.breeds, ...items],
        hasMore: items.length >= PAGE_SIZE,
        loading: false,
        loadingMore: false
      })
    } catch (err) {
      console.error('加载品种列表失败:', err)
      this.setData({ loading: false, loadingMore: false })
    }
  },

  // 切换物种筛选
  onSpeciesChange(e) {
    const species = e.currentTarget.dataset.species
    if (species === this.data.species) return

    this.setData({ species: species === '全部' ? '' : species })
    this.loadBreeds(true)
  },

  // 切换排序
  onSortChange(e) {
    const sortBy = e.currentTarget.dataset.sort
    if (sortBy === this.data.sortBy) return

    this.setData({ sortBy })
    this.loadBreeds(true)
  },

  // 点击品种卡片
  onBreedTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/breed/detail?id=${id}` })
  },

  // 上拉加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loadingMore) {
      this.setData({
        page: this.data.page + 1,
        loadingMore: true
      })
      this.loadBreeds(false)
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadBreeds(true).then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
