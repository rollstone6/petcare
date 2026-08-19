// pages/breed/detail.js
const api = require('../../utils/api')
const { formatImageUrl } = require('../../utils/util')
const { SPECIES_ICONS } = require('../../utils/constants')

const PLACEHOLDER = 'https://website-petcare-oss-bj.oss-cn-beijing.aliyuncs.com/images/placeholder.png'

Page({
  data: {
    breed: null,
    products: [],
    loading: true,
    speciesIcons: SPECIES_ICONS
  },

  onLoad(options) {
    if (options.id) {
      this.breedId = options.id
      this.loadDetail()
      this.loadProducts()
    }
  },

  async loadDetail() {
    try {
      const breed = await api.getBreedDetail(this.breedId)
      
      // 处理图片URL
      breed.image = formatImageUrl(breed.image_url, PLACEHOLDER)
      
      // 处理性格标签（后端用顿号分隔）
      if (breed.temperament) {
        breed.temperamentTags = breed.temperament.split('、').filter(Boolean)
      } else {
        breed.temperamentTags = []
      }
      
      // 处理基础信息卡片
      breed.infoCards = [
        breed.lifespan && { icon: '⏳', label: '寿命', value: breed.lifespan },
        breed.weight_range && { icon: '⚖️', label: '体重', value: breed.weight_range },
        breed.origin && { icon: '🌍', label: '产地', value: breed.origin },
        { icon: breed.hypoallergenic ? '🌿' : '🤧', label: '低敏性', value: breed.hypoallergenic ? '低敏' : '普通' }
      ].filter(Boolean)
      
      this.setData({ breed, loading: false })
    } catch (err) {
      console.error('加载品种详情失败:', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  async loadProducts() {
    try {
      const result = await api.getBreedProducts(this.breedId)
      const products = (result.items || result || []).map(product => ({
        ...product,
        image: formatImageUrl(product.image_url, PLACEHOLDER)
      }))
      this.setData({ products })
    } catch (err) {
      console.error('加载品种产品失败:', err)
    }
  },

  onProductTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})
