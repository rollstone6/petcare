// pages/health/index.js — 健康记录（对齐 PC 端 /health HealthTracker 的日程提醒）
const api = require('../../utils/api')
const app = getApp()

const TYPE_ICONS = { '体外驱虫': '🦟', '体内驱虫': '💊', '疫苗': '💉', '体检': '🩺', '自定义': '📝' }
const STATUS_LABELS = { overdue: '已过期', urgent: '紧急', warning: '临近', normal: '正常' }
const SCHEDULE_TYPES = ['体外驱虫', '体内驱虫', '疫苗', '体检', '自定义']

Page({
  data: {
    pets: [],
    schedules: [],
    filteredSchedules: [],
    loading: true,
    filterPet: '',
    // 添加表单
    showForm: false,
    scheduleTypes: SCHEDULE_TYPES,
    formData: { petIndex: 0, typeIndex: 0, title: '', interval: '' }
  },

  onShow() {
    if (!app.globalData.isLogin) {
      wx.redirectTo({ url: '/pages/user/login' })
      return
    }
    this.loadData()
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const [petsRes, schedulesRes] = await Promise.all([
        api.getPets(),
        api.getSchedules()
      ])
      const pets = petsRes?.items || []
      const schedules = (schedulesRes?.items || []).map((s) => ({
        ...s,
        type_icon: TYPE_ICONS[s.schedule_type] || '📝',
        status_label: STATUS_LABELS[s.status] || '',
        next_due_fmt: s.next_due_at ? String(s.next_due_at).slice(0, 10) : ''
      }))
      this.setData({ pets, schedules })
      this.applyFilter()
    } catch (err) {
      console.error('加载健康数据失败:', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  applyFilter() {
    const { schedules, filterPet } = this.data
    this.setData({
      filteredSchedules: filterPet ? schedules.filter((s) => s.pet_name === filterPet) : schedules
    })
  },

  onFilterTap(e) {
    this.setData({ filterPet: e.currentTarget.dataset.pet || '' })
    this.applyFilter()
  },

  // ===== 标记完成 / 删除 =====
  async onMarkDone(e) {
    const { id } = e.currentTarget.dataset
    try {
      await api.markScheduleDone(id)
      wx.showToast({ title: '已完成，倒计时重置', icon: 'none' })
      this.loadData()
    } catch (err) {
      console.error('标记完成失败:', err)
    }
  },

  onDeleteSchedule(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '提示',
      content: '确定删除这条提醒吗？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.deleteSchedule(id)
          wx.showToast({ title: '已删除', icon: 'none' })
          this.loadData()
        } catch (err) {
          console.error('删除提醒失败:', err)
        }
      }
    })
  },

  // ===== 添加表单 =====
  onAddTap() {
    if (this.data.pets.length === 0) {
      wx.showModal({
        title: '提示',
        content: '请先添加宠物档案，才能创建提醒哦',
        confirmText: '去添加',
        success: (res) => {
          if (res.confirm) wx.navigateTo({ url: '/pages/user/pets' })
        }
      })
      return
    }
    this.setData({
      showForm: true,
      formData: { petIndex: 0, typeIndex: 0, title: '', interval: '' }
    })
  },

  onCancelForm() {
    this.setData({ showForm: false })
  },

  onFormPetChange(e) {
    this.setData({ 'formData.petIndex': Number(e.detail.value) })
  },

  onFormTypeChange(e) {
    this.setData({ 'formData.typeIndex': Number(e.detail.value) })
  },

  onFormTitleInput(e) {
    this.setData({ 'formData.title': e.detail.value })
  },

  onFormIntervalInput(e) {
    this.setData({ 'formData.interval': e.detail.value })
  },

  async onSubmitSchedule() {
    const { formData, pets, scheduleTypes } = this.data
    const type = scheduleTypes[formData.typeIndex]
    const pet = pets[formData.petIndex]
    if (!pet) {
      wx.showToast({ title: '请选择宠物', icon: 'none' })
      return
    }
    const data = { pet_name: pet.pet_name, schedule_type: type }
    if (type === '自定义') {
      const title = (formData.title || '').trim()
      if (!title) {
        wx.showToast({ title: '请填写提醒标题', icon: 'none' })
        return
      }
      data.title = title
      data.interval_days = formData.interval ? parseInt(formData.interval, 10) : 30
    }
    try {
      await api.createSchedule(data)
      wx.showToast({ title: '创建成功', icon: 'success' })
      this.setData({ showForm: false })
      this.loadData()
    } catch (err) {
      console.error('创建提醒失败:', err)
    }
  },

  onGoPets() {
    wx.navigateTo({ url: '/pages/user/pets' })
  }
})