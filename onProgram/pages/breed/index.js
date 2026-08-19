// pages/breed/index.js
const api = require('../../utils/api')
const { formatImageUrl } = require('../../utils/util')

const PLACEHOLDER = 'https://website-petcare-oss-bj.oss-cn-beijing.aliyuncs.com/images/placeholder.png'

Page({
  data: {
    breeds: [],
    loading: true
  },

  onLoad() {
    this.loadBreeds()
  },

  async loadBreeds() {
    try {
      const breeds = await api.getBreeds()
      // 处理图片URL：后端返回 image_url 是相对路径，转为完整URL
      const formattedBreeds = (breeds || []).map(breed => ({
        ...breed,
        image: formatImageUrl(breed.image_url, PLACEHOLDER)
      }))
      this.setData({ breeds: formattedBreeds, loading: false })
    } catch (err) {
      console.error('加载品种列表失败:', err)
      this.setData({ loading: false })
    }
  },

  onBreedTap(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/breed/detail?id=${id}` })
  }
})
