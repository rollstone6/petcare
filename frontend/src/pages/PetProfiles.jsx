import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function PetProfiles() {
  const navigate = useNavigate()
  const [pets, setPets] = useState([])
  const [breeds, setBreeds] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingPet, setEditingPet] = useState(null)
  const [selectedSpecies, setSelectedSpecies] = useState('')
  const [healthTagsData, setHealthTagsData] = useState({ tags: [], categories: {} })
  const [showTagsModal, setShowTagsModal] = useState(null) // pet object or null
  const [tagsDraft, setTagsDraft] = useState([])
  const [tagsSaving, setTagsSaving] = useState(false)
  const [tagsToast, setTagsToast] = useState(null)
  const [formData, setFormData] = useState({
    pet_name: '',
    breed_id: '',
    age: '',
    gender: '',
    weight: '',
    birthday: '',
    body_condition: '',
  })

  // 按物种分组的品种列表
  const breedsBySpecies = breeds.reduce((acc, breed) => {
    if (!acc[breed.species]) acc[breed.species] = []
    acc[breed.species].push(breed)
    return acc
  }, {})
  
  const filteredBreeds = selectedSpecies ? (breedsBySpecies[selectedSpecies] || []) : []

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [petsData, breedsData, tagsData] = await Promise.all([
        api.getPets(),
        api.getBreeds(),
        api.getHealthTags(),
      ])
      setPets(petsData.items || [])
      setBreeds(breedsData.items || [])
      setHealthTagsData(tagsData)
    } catch (err) {
      console.error('加载数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const openTagsModal = (pet) => {
    setShowTagsModal(pet)
    setTagsDraft(pet.health_tags || [])
  }

  const handleSaveTags = async () => {
    if (!showTagsModal) return
    setTagsSaving(true)
    try {
      await api.updatePetHealthTags(showTagsModal.id, tagsDraft)
      setTagsToast(`✅ ${showTagsModal.pet_name} 的健康标签已更新`)
      setTimeout(() => setTagsToast(null), 3000)
      setShowTagsModal(null)
      loadData()
    } catch (err) {
      alert(err.message)
    } finally {
      setTagsSaving(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        breed_id: formData.breed_id ? parseInt(formData.breed_id) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
        body_condition: formData.body_condition || '',
      }

      if (editingPet) {
        await api.updatePet(editingPet.id, data)
      } else {
        await api.createPet(data)
      }
      
      setShowForm(false)
      setEditingPet(null)
      setFormData({ pet_name: '', breed_id: '', age: '', gender: '', weight: '', birthday: '', body_condition: '' })
      loadData()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleEdit = (pet) => {
    setEditingPet(pet)
    setFormData({
      pet_name: pet.pet_name,
      breed_id: pet.breed?.id || '',
      age: pet.age || '',
      gender: pet.gender || '',
      weight: pet.weight?.toString() || '',
      birthday: pet.birthday || '',
      body_condition: pet.body_condition || '',
    })
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('确定删除这个宠物档案吗？')) return
    try {
      await api.deletePet(id)
      loadData()
    } catch (err) {
      alert(err.message)
    }
  }

  const getGenderIcon = (gender) => {
    if (gender === '公') return '♂️'
    if (gender === '母') return '♀️'
    return '🐾'
  }

  if (loading) {
    return (
      <div className="px-4 md:px-8 py-8">
        <div className="max-w-2xl mx-auto animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/2" />
          <div className="space-y-3">
            <div className="h-24 bg-gray-200 rounded-2xl" />
            <div className="h-24 bg-gray-200 rounded-2xl" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-4 sticky top-0 z-40 shadow-sm">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div>
            <button onClick={() => navigate(-1)} className="text-gray-400 text-sm mb-2 hover:text-gray-600">
              ← 返回
            </button>
            <h1 className="text-xl md:text-2xl font-bold text-gray-900">🐱 品种档案</h1>
            <p className="text-sm md:text-base text-gray-500 mt-1">管理你的宠物</p>
          </div>
          <button
            onClick={() => {
              setEditingPet(null)
              setFormData({ pet_name: '', breed_id: '', age: '', gender: '', weight: '', birthday: '', body_condition: '' })
              setShowForm(true)
            }}
            className="bg-primary text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            + 添加宠物
          </button>
        </div>
      </div>

      <div className="px-4 md:px-8 py-4">
        <div className="max-w-2xl mx-auto space-y-3">
          {pets.length === 0 ? (
            <div className="bg-white rounded-2xl p-8 text-center shadow-sm">
              <div className="text-5xl mb-3">🐾</div>
              <p className="text-gray-500 text-sm">还没有添加宠物</p>
              <p className="text-gray-400 text-xs mt-1">点击右上角添加你的宠物档案</p>
            </div>
          ) : (
            pets.map(pet => (
              <div key={pet.id} className="bg-white rounded-2xl p-4 shadow-sm">
                <div className="flex items-start gap-3">
                  {pet.breed?.image_url ? (
                    <img
                      src={pet.breed.image_url}
                      alt={pet.breed.name}
                      loading="lazy"
                      className="w-16 h-16 rounded-xl object-cover flex-shrink-0"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center text-3xl flex-shrink-0">
                      {pet.breed?.species === '猫' ? '🐱' : '🐶'}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{pet.pet_name}</h3>
                      <span className="text-sm">{getGenderIcon(pet.gender)}</span>
                    </div>
                    {pet.breed && (
                      <p className="text-sm text-gray-600">{pet.breed.name} · {pet.breed.size}</p>
                    )}
                    <div className="flex gap-3 mt-2 text-xs text-gray-500">
                      {pet.age_category && (
                        <span className={`px-2 py-0.5 rounded-full ${
                          pet.age_category === '幼崽' ? 'bg-pink-100 text-pink-600' :
                          pet.age_category === '幼年' ? 'bg-blue-100 text-blue-600' :
                          pet.age_category === '成年' ? 'bg-green-100 text-green-600' :
                          'bg-purple-100 text-purple-600'
                        }`}>
                          {pet.age_category}
                        </span>
                      )}
                      {pet.weight && <span>{pet.weight}kg</span>}
                      {pet.body_condition && (
                        <span className={`px-2 py-0.5 rounded-full ${
                          pet.body_condition === 'thin' ? 'bg-cyan-100 text-cyan-700' :
                          pet.body_condition === 'standard' ? 'bg-emerald-100 text-emerald-700' :
                          pet.body_condition === 'chubby' ? 'bg-amber-100 text-amber-700' :
                          'bg-rose-100 text-rose-700'
                        }`}>
                          {pet.body_condition === 'thin' ? '🦴 骨感型' :
                           pet.body_condition === 'standard' ? '🐕 标准体型' :
                           pet.body_condition === 'chubby' ? '🍞 略微发福' :
                           '🎈 圆滚滚'}
                        </span>
                      )}
                    </div>
                    {/* 健康标签展示 */}
                    {pet.health_tags && pet.health_tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {pet.health_tags.slice(0, 4).map(tagId => {
                          const tag = healthTagsData.tags.find(t => t.id === tagId)
                          return tag ? (
                            <span key={tagId} className="text-[10px] px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-700">
                              {tag.icon} {tag.label}
                            </span>
                          ) : null
                        })}
                        {pet.health_tags.length > 4 && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500">
                            +{pet.health_tags.length - 4}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => openTagsModal(pet)}
                      className="text-gray-400 hover:text-orange-500 p-3 text-sm touch-target"
                      title="健康标签"
                    >
                      🏷️
                    </button>
                    <button
                      onClick={() => handleEdit(pet)}
                      className="text-gray-400 hover:text-primary p-3 text-sm touch-target"
                      title="编辑"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(pet.id)}
                      className="text-gray-400 hover:text-red-500 p-3 text-sm touch-target"
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 modal-overlay" onClick={() => setShowForm(false)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              {editingPet ? '编辑宠物' : '添加宠物'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-sm text-gray-700 mb-1">名字 *</label>
                <input
                  type="text"
                  value={formData.pet_name}
                  onChange={e => setFormData({ ...formData, pet_name: e.target.value })}
                  placeholder="宠物名字"
                  required
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">品种 <span className="text-red-500">*</span></label>
                
                {/* 第一步：选择物种 */}
                <div className="mb-2">
                  <div className="text-xs text-gray-500 mb-1.5">先选物种：</div>
                  <div className="flex gap-2 flex-wrap">
                    {Object.keys(breedsBySpecies).map(species => (
                      <button
                        key={species}
                        type="button"
                        onClick={() => {
                          setSelectedSpecies(species === selectedSpecies ? '' : species)
                          setFormData({ ...formData, breed_id: '' })
                        }}
                        className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          selectedSpecies === species
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {species === '猫' ? '🐱' : species === '狗' ? '🐶' : species === '兔' ? '🐰' : '🐾'} {species}
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* 第二步：选择品种 */}
                {selectedSpecies && (
                  <div>
                    <div className="text-xs text-gray-500 mb-1.5">再选品种：</div>
                    <select
                      value={formData.breed_id}
                      onChange={e => setFormData({ ...formData, breed_id: e.target.value })}
                      required
                      className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary bg-white"
                    >
                      <option value="">请选择品种</option>
                      {filteredBreeds.map(b => (
                        <option key={b.id} value={b.id}>{b.name}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">生日 🎂 <span className="text-red-500">*</span></label>
                <input
                  type="date"
                  value={formData.birthday}
                  onChange={e => setFormData({ ...formData, birthday: e.target.value })}
                  required
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full min-w-0 px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                />
                {formData.birthday && (
                  <p className="text-xs text-gray-500 mt-1">
                    {(() => {
                      const birth = new Date(formData.birthday)
                      const now = new Date()
                      const years = now.getFullYear() - birth.getFullYear()
                      const months = now.getMonth() - birth.getMonth()
                      const totalMonths = years * 12 + months
                      if (totalMonths < 12) {
                        return `${totalMonths} 个月`
                      } else {
                        const y = Math.floor(totalMonths / 12)
                        const m = totalMonths % 12
                        return `${y} 岁${m > 0 ? ` ${m} 个月` : ''}`
                      }
                    })()}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">性别</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: '公', icon: '♂️', label: '帅小伙' },
                    { value: '母', icon: '♀️', label: '小公主' },
                    { value: '保密', icon: '🐾', label: '保密' },
                  ].map(opt => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, gender: formData.gender === opt.value ? '' : opt.value })}
                      className={`flex flex-col items-center p-3 rounded-xl border-2 transition-all ${
                        formData.gender === opt.value
                          ? 'border-primary bg-primary/5 shadow-sm'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                    >
                      <span className="text-xl mb-1">{opt.icon}</span>
                      <span className="text-xs text-gray-700">{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">体型 🎨</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'thin', icon: '🦴', label: '骨感型', desc: '苗条轻盈' },
                    { value: 'standard', icon: '🐕', label: '标准体型', desc: '健康匀称' },
                    { value: 'chubby', icon: '🍞', label: '略微发福', desc: '软萌圆润' },
                    { value: 'round', icon: '🎈', label: '圆滚滚', desc: '煤气罐罐' },
                  ].map(opt => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, body_condition: formData.body_condition === opt.value ? '' : opt.value })}
                      className={`flex items-center gap-2 p-3 rounded-xl border-2 transition-all text-left ${
                        formData.body_condition === opt.value
                          ? 'border-primary bg-primary/5 shadow-sm'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                    >
                      <span className="text-xl flex-shrink-0">{opt.icon}</span>
                      <div>
                        <div className="text-xs font-medium text-gray-800">{opt.label}</div>
                        <div className="text-[10px] text-gray-500">{opt.desc}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">体重 (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.weight}
                  onChange={e => setFormData({ ...formData, weight: e.target.value })}
                  placeholder="如：5.5"
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-primary text-white py-2.5 rounded-xl font-medium text-sm hover:bg-primary/90 transition-colors"
              >
                {editingPet ? '保存修改' : '添加宠物'}
              </button>
            </form>
            <button onClick={() => setShowForm(false)} className="w-full text-center text-sm text-gray-400 mt-3">
              取消
            </button>
          </div>
        </div>
      )}

      {/* 健康标签管理弹窗 */}
      {showTagsModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 modal-overlay" onClick={() => setShowTagsModal(null)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-gray-900 mb-1">🏷️ 健康标签</h2>
            <p className="text-xs text-gray-500 mb-4">
              {showTagsModal.pet_name} · 勾选当前健康状况，浏览食品时会自动提醒
            </p>

            {/* 已选标签 */}
            {tagsDraft.length > 0 && (
              <div className="mb-4 p-3 bg-primary/5 rounded-xl">
                <p className="text-xs text-gray-600 mb-2">已选 {tagsDraft.length} 个标签</p>
                <div className="flex flex-wrap gap-1.5">
                  {tagsDraft.map(tagId => {
                    const tag = healthTagsData.tags.find(t => t.id === tagId)
                    return tag ? (
                      <span key={tagId}
                        onClick={() => setTagsDraft(prev => prev.filter(t => t !== tagId))}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-primary text-white rounded-full text-xs cursor-pointer hover:bg-primary/90 transition-colors"
                      >
                        <span>{tag.icon}</span>
                        <span>{tag.label}</span>
                        <span className="ml-0.5 opacity-70">✕</span>
                      </span>
                    ) : null
                  })}
                </div>
              </div>
            )}

            {/* 标签分类列表 */}
            <div className="space-y-3">
              {Object.entries(healthTagsData.categories).map(([category, tags]) => (
                <div key={category} className="border border-gray-100 rounded-xl p-3">
                  <h4 className="font-semibold text-xs text-gray-700 mb-2">{category}</h4>
                  <div className="space-y-1.5">
                    {tags.map(tag => {
                      const isSelected = tagsDraft.includes(tag.id)
                      return (
                        <button key={tag.id}
                          onClick={() => setTagsDraft(prev => 
                            prev.includes(tag.id) ? prev.filter(t => t !== tag.id) : [...prev, tag.id]
                          )}
                          className={`w-full flex items-center gap-2 p-2 rounded-lg transition-all text-left ${
                            isSelected
                              ? 'bg-primary/10 border-2 border-primary'
                              : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                          }`}
                        >
                          <span className="text-base flex-shrink-0">{tag.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1.5">
                              <span className={`text-xs font-medium ${isSelected ? 'text-primary' : 'text-gray-800'}`}>
                                {tag.label}
                              </span>
                              {isSelected && (
                                <span className="text-[10px] bg-primary text-white px-1 py-0.5 rounded">✓</span>
                              )}
                            </div>
                            <p className="text-[10px] text-gray-500 mt-0.5 line-clamp-1">{tag.description}</p>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* 保存按钮 */}
            <button onClick={handleSaveTags} disabled={tagsSaving}
              className="w-full bg-primary text-white py-2.5 rounded-xl font-medium text-sm mt-4 disabled:opacity-50 hover:bg-primary/90 transition-colors"
            >
              {tagsSaving ? '保存中...' : '💾 保存标签'}
            </button>
            <button onClick={() => setShowTagsModal(null)} className="w-full text-center text-sm text-gray-400 mt-2">
              取消
            </button>
          </div>
        </div>
      )}

      {/* Toast */}
      {tagsToast && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-[70] animate-slideDown">
          <div className="bg-gray-800 text-white px-6 py-3 rounded-xl shadow-lg text-sm">
            {tagsToast}
          </div>
        </div>
      )}
    </div>
  )
}
