import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { getToken } from '../api/client'

export default function HealthTags() {
  const navigate = useNavigate()
  const [availableTags, setAvailableTags] = useState({ tags: [], categories: {} })
  const [pets, setPets] = useState([])
  const [selectedPet, setSelectedPet] = useState(null)
  const [selectedTags, setSelectedTags] = useState([])
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 检查登录状态
    if (!getToken()) {
      alert('请先登录')
      navigate('/profile')
      return
    }

    // 加载数据
    Promise.all([
      api.getHealthTags(),
      api.getPets()
    ])
      .then(([tagsData, petsData]) => {
        setAvailableTags(tagsData)
        setPets(petsData.items || [])
        if (petsData.items && petsData.items.length > 0) {
          setSelectedPet(petsData.items[0])
        }
      })
      .catch(e => alert(e.message))
      .finally(() => setLoading(false))
  }, [navigate])

  useEffect(() => {
    if (selectedPet) {
      setSelectedTags(selectedPet.health_tags || [])
    }
  }, [selectedPet])

  const handleToggleTag = (tagId) => {
    setSelectedTags(prev => 
      prev.includes(tagId) ? prev.filter(t => t !== tagId) : [...prev, tagId]
    )
  }

  const handleSave = async () => {
    if (!selectedPet) return
    setSaving(true)
    try {
      await api.updatePetHealthTags(selectedPet.id, selectedTags)
      // 更新本地 pets 数据
      setPets(prev => prev.map(p => 
        p.id === selectedPet.id ? { ...p, health_tags: selectedTags } : p
      ))
      setToast(`✅ ${selectedPet.pet_name} 的健康标签已更新`)
      setTimeout(() => setToast(null), 3000)
    } catch (e) {
      alert(e.message)
    }
    setSaving(false)
  }

  if (loading) {
    return <div className="text-center py-10 text-gray-400">加载中...</div>
  }

  if (pets.length === 0) {
    return (
      <div className="text-center py-10">
        <div className="text-5xl mb-3">🏷️</div>
        <p className="text-gray-400">请先添加宠物</p>
        <p className="text-sm text-gray-300 mt-1 mb-4">去个人中心 → 品种档案添加宠物后，可在此设置健康标签</p>
        <button onClick={() => navigate('/pets')} className="text-primary">去添加宠物 →</button>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn pb-20">
      {/* 顶部 */}
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-8 pb-4 sticky top-0 z-30 shadow-sm">
        <div className="max-w-2xl mx-auto">
          <button onClick={() => navigate(-1)} className="text-gray-400 text-sm mb-2 hover:text-gray-600 inline-block">← 返回</button>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">🏷️ 健康标签</h1>
          <p className="text-sm text-gray-500 mt-1">设置宠物的健康状况，浏览食品时会自动提醒</p>
        </div>
      </div>

      {/* 内容区 */}
      <div className="px-4 md:px-8 mt-4">
        <div className="max-w-2xl mx-auto">
          {/* 宠物选择 */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">选择宠物</p>
            <div className="flex gap-2 flex-wrap">
              {pets.map(p => (
                <button key={p.id} onClick={() => setSelectedPet(p)}
                  className={`px-4 py-2 rounded-xl text-sm transition-all flex items-center gap-2 ${
                    selectedPet?.id === p.id
                      ? 'bg-primary text-white shadow-sm'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span>{p.breed?.species === '猫' ? '🐱' : '🐶'}</span>
                  <span className="font-medium">{p.pet_name}</span>
                  {p.health_tags && p.health_tags.length > 0 && (
                    <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                      selectedPet?.id === p.id ? 'bg-white/20' : 'bg-primary/10 text-primary'
                    }`}>
                      {p.health_tags.length}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {selectedPet && (
            <>
              {/* 说明 */}
              <div className="bg-blue-50 rounded-xl p-3 mb-4">
                <p className="text-xs text-blue-700 leading-relaxed">
                  💡 勾选宠物当前的健康状况，浏览食品时会自动弹出相关警告提醒
                </p>
              </div>

              {/* 已选标签 */}
              {selectedTags.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-2">
                    已选 {selectedTags.length} 个标签
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {selectedTags.map(tagId => {
                      const tag = availableTags.tags.find(t => t.id === tagId)
                      if (!tag) return null
                      return (
                        <span key={tagId} 
                          onClick={() => handleToggleTag(tagId)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary text-white rounded-full text-xs cursor-pointer hover:bg-primary/90 transition-colors"
                        >
                          <span>{tag.icon}</span>
                          <span>{tag.label}</span>
                          <span className="ml-1 opacity-70">✕</span>
                        </span>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* 标签分类列表 */}
              <div className="space-y-4">
                {Object.entries(availableTags.categories).map(([category, tags]) => (
                  <div key={category} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <h4 className="font-semibold text-sm text-gray-800 mb-3">{category}</h4>
                    <div className="space-y-2">
                      {tags.map(tag => {
                        const isSelected = selectedTags.includes(tag.id)
                        return (
                          <button key={tag.id} onClick={() => handleToggleTag(tag.id)}
                            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all text-left ${
                              isSelected
                                ? 'bg-primary/10 border-2 border-primary'
                                : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                            }`}
                          >
                            <span className="text-xl flex-shrink-0">{tag.icon}</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className={`text-sm font-medium ${isSelected ? 'text-primary' : 'text-gray-800'}`}>
                                  {tag.label}
                                </span>
                                {isSelected && (
                                  <span className="text-xs bg-primary text-white px-1.5 py-0.5 rounded">✓</span>
                                )}
                              </div>
                              <p className="text-xs text-gray-500 mt-0.5">{tag.description}</p>
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>

              {/* 保存按钮 */}
              <div className="sticky bottom-4 mt-6 bg-white p-3 rounded-xl shadow-lg border border-gray-100">
                <button onClick={handleSave} disabled={saving}
                  className="w-full bg-primary text-white py-3 rounded-xl font-medium text-sm disabled:opacity-50 hover:bg-primary/90 transition-colors"
                >
                  {saving ? '保存中...' : `💾 保存 ${selectedPet.pet_name} 的健康标签`}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {toast && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-[70] animate-slideDown">
          <div className="bg-gray-800 text-white px-6 py-3 rounded-xl shadow-lg text-sm">
            {toast}
          </div>
        </div>
      )}
    </div>
  )
}
