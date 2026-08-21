// pages/user/pets.js — 宠物档案（对齐 PC 端 PetProfiles：增删改）
const api = require('../../utils/api')
const app = getApp()

const GENDERS = ['公', '母']
const BODY_CONDITIONS = ['偏瘦', '标准', '偏胖']
const SPECIES_ICONS = { '猫': '🐱', '狗': '🐶' }

Page({
  data: {
    pets: [],
    loading: true,
    showForm: false,
    editingId: null,
    breeds: [],
    breedOptions: [],
    genders: GENDERS,
    bodyConditions: BODY_CONDITIONS,
    formData: {
      pet_name: '',
      breedIndex: -1,
      age: '',
      genderIndex: -1,
      weight: '',
      birthday: '',
      bodyIndex: -1
    }
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
      const [petsRes, breedsRes] = await Promise.all([
        api.getPets(),
        api.getBreeds({ page_size: 500 })
      ])
      const breeds = breedsRes?.items || []
      const pets = (petsRes?.items || []).map((p) => ({
        ...p,
        species_icon: SPECIES_ICONS[p.breed?.species] || '🐾',
        age_category: p.age_category || ''
      }))
      this.setData({
        pets,
        breeds,
        breedOptions: breeds.map((b) => `${b.species} · ${b.name}`)
      })
    } catch (err) {
      console.error('加载宠物数据失败:', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  // ===== 表单交互 =====
  onAddTap() {
    this.setData({
      showForm: true,
      editingId: null,
      formData: { pet_name: '', breedIndex: -1, age: '', genderIndex: -1, weight: '', birthday: '', bodyIndex: -1 }
    })
  },

  onEditTap(e) {
    const { id } = e.currentTarget.dataset
    const pet = this.data.pets.find((p) => p.id === id)
    if (!pet) return
    const breedIndex = pet.breed ? this.data.breeds.findIndex((b) => b.id === pet.breed.id) : -1
    this.setData({
      showForm: true,
      editingId: id,
      formData: {
        pet_name: pet.pet_name || '',
        breedIndex,
        age: pet.age || '',
        genderIndex: GENDERS.indexOf(pet.gender),
        weight: pet.weight != null ? String(pet.weight) : '',
        birthday: pet.birthday || '',
        bodyIndex: BODY_CONDITIONS.indexOf(pet.body_condition)
      }
    })
  },

  onCancelForm() {
    this.setData({ showForm: false })
  },

  onNameInput(e) {
    this.setData({ 'formData.pet_name': e.detail.value })
  },

  onAgeInput(e) {
    this.setData({ 'formData.age': e.detail.value })
  },

  onWeightInput(e) {
    this.setData({ 'formData.weight': e.detail.value })
  },

  onBreedChange(e) {
    this.setData({ 'formData.breedIndex': Number(e.detail.value) })
  },

  onGenderChange(e) {
    this.setData({ 'formData.genderIndex': Number(e.detail.value) })
  },

  onBodyChange(e) {
    this.setData({ 'formData.bodyIndex': Number(e.detail.value) })
  },

  onBirthdayChange(e) {
    this.setData({ 'formData.birthday': e.detail.value })
  },

  async onSubmitForm() {
    const { formData, editingId, breeds } = this.data
    const petName = (formData.pet_name || '').trim()
    if (!petName) {
      wx.showToast({ title: '请填写宠物名字', icon: 'none' })
      return
    }
    const data = {
      pet_name: petName,
      breed_id: formData.breedIndex >= 0 ? breeds[formData.breedIndex].id : null,
      age: formData.age || '',
      gender: formData.genderIndex >= 0 ? GENDERS[formData.genderIndex] : '',
      weight: formData.weight ? parseFloat(formData.weight) : null,
      birthday: formData.birthday || null,
      body_condition: formData.bodyIndex >= 0 ? BODY_CONDITIONS[formData.bodyIndex] : ''
    }
    try {
      if (editingId) {
        await api.updatePet(editingId, data)
        wx.showToast({ title: '已更新', icon: 'success' })
      } else {
        await api.createPet(data)
        wx.showToast({ title: '添加成功', icon: 'success' })
      }
      this.setData({ showForm: false })
      this.loadData()
    } catch (err) {
      console.error('保存宠物失败:', err)
    }
  },

  onDeleteTap(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '提示',
      content: '确定删除这个宠物档案吗？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.deletePet(id)
          wx.showToast({ title: '已删除', icon: 'none' })
          this.loadData()
        } catch (err) {
          console.error('删除宠物失败:', err)
        }
      }
    })
  }
})