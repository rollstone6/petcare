import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { createPortal } from 'react-dom'
import { api } from '../api/client'
import { getToken } from '../api/client'
import AIChat from '../components/AIChat'
import ReviewSection from '../components/ReviewSection'
import BreedCompatibility from '../components/BreedCompatibility'
import HealthWarningBanner from '../components/HealthWarningBanner'

const LEVEL_COLORS = {
  1: 'bg-green-500', 2: 'bg-green-400', 3: 'bg-green-400',
  4: 'bg-yellow-400', 5: 'bg-yellow-500', 6: 'bg-orange-400',
  7: 'bg-orange-500', 8: 'bg-red-400', 9: 'bg-red-500', 10: 'bg-red-600',
}

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showFeedingModal, setShowFeedingModal] = useState(false)
  const [pets, setPets] = useState([])
  const [feedingPets, setFeedingPets] = useState([]) // 已经在吃这个产品的宠物

  useEffect(() => {
    api.getProduct(id).then(data => {
      setProduct(data)
      setLoading(false)
    }).catch(() => setLoading(false))
    
    // 获取宠物列表和喂养状态
    if (getToken()) {
      api.getPets().then(data => setPets(data.items || []))
      api.checkProductFeeding(id).then(data => setFeedingPets(data.pets || []))
    }
  }, [id])

  if (loading) {
    return (
      <div className="px-4 md:px-8 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-2/3" />
            <div className="h-48 bg-gray-200 rounded-2xl" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="px-4 md:px-8 py-16 text-center">
        <div className="max-w-2xl mx-auto">
          <p className="text-4xl mb-3">😿</p>
          <p className="text-gray-500">产品不存在</p>
          <button onClick={() => navigate('/search')} className="mt-4 text-primary text-sm">返回搜索</button>
        </div>
      </div>
    )
  }

  const score = product.safety_score || 5
  // EWG 1-10分制
  const level = Math.min(10, Math.max(1, Math.round(score)))

  return (
    <div className="animate-fadeIn pb-4">
      {/* 头部 */}
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-6">
        <div className="max-w-2xl mx-auto">
          <button onClick={() => navigate(-1)} className="text-gray-400 text-sm mb-4 hover:text-gray-600 inline-block">← 返回</button>
          <div className="flex items-start gap-4 md:gap-6">
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-2xl md:text-3xl flex-shrink-0">
              💊
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-lg md:text-2xl font-bold text-gray-900 leading-tight">{product.name}</h1>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                {product.brand && (
                  <span className="text-xs md:text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{product.brand.name}</span>
                )}
                {product.category && (
                  <span className="text-xs md:text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{product.category.name}</span>
                )}
                <span className={`text-xs px-2 py-0.5 rounded-full text-white ${product.type === '药品' ? 'bg-blue-500' : product.type === '食品' ? 'bg-green-500' : 'bg-purple-500'}`}>
                  {product.type}
                </span>
              </div>
            </div>
          </div>

          {/* 🎯 品种契合度（第一视觉） */}
          <div className="mt-5 md:mt-6">
            <BreedCompatibility productId={parseInt(id)} />
          </div>

          {/* 🚨 健康警告横幅（仅食品） */}
          {product.type === '食品' && getToken() && (
            <div className="mt-4">
              <HealthWarningBanner productId={parseInt(id)} />
            </div>
          )}

          {/* 安全评分（折叠为次要信息） */}
          <div className="mt-3 flex items-center gap-2 p-3 bg-gray-50 rounded-xl">
            <div className={`w-9 h-9 rounded-full ${LEVEL_COLORS[level]} flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}>
              {score.toFixed(1)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-700">通用安全评分</p>
              <p className="text-[10px] text-gray-400">
                {score <= 2 ? '安全可靠' : score <= 4 ? '基本安全' : score <= 6 ? '谨慎使用' : '风险较高'}
              </p>
            </div>
            <div className="flex gap-0.5">
              {[1,2,3,4,5,6,7,8,9,10].map(i => (
                <div key={i} className={`w-1.5 h-1.5 rounded-full ${i <= level ? LEVEL_COLORS[level] : 'bg-gray-200'}`} />
              ))}
            </div>
          </div>

          {/* 🍽 我家正在吃 */}
          {product.type === '食品' && getToken() && (
            <div className="mt-3">
              {feedingPets.length > 0 ? (
                <div className="flex items-center gap-2 p-3 bg-orange-50 border border-orange-200 rounded-xl">
                  <span className="text-lg">🍽</span>
                  <div className="flex-1">
                    <p className="text-xs font-medium text-orange-800">
                      {feedingPets.join('、')} 正在吃
                    </p>
                    <p className="text-[10px] text-orange-500 mt-0.5">
                      <button onClick={() => navigate('/health')} className="underline">
                        去喂养日记查看 →
                      </button>
                    </p>
                  </div>
                  <button
                    onClick={() => setShowFeedingModal(true)}
                    className="px-3 py-1.5 bg-orange-100 text-orange-700 rounded-lg text-xs font-medium hover:bg-orange-200 transition-colors"
                  >
                    管理
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    if (pets.length === 0) {
                      alert('请先去个人中心 → 品种档案添加宠物')
                      return
                    }
                    setShowFeedingModal(true)
                  }}
                  className="w-full flex items-center justify-center gap-2 p-3 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl hover:from-orange-100 hover:to-amber-100 transition-colors"
                >
                  <span className="text-lg">🍽</span>
                  <span className="text-sm font-medium text-orange-700">我家正在吃</span>
                  <span className="text-xs text-orange-400 ml-1">记录换粮观察</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 详情 */}
      <div className="px-4 md:px-8 mt-4">
        <div className="max-w-2xl mx-auto space-y-4 md:space-y-5">
          {/* 基本信息 */}
          <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
            <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">📋 基本信息</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {product.approval_number && (
                <div>
                  <p className="text-gray-400 text-xs">批准文号</p>
                  <p className="text-gray-700 mt-0.5 text-xs md:text-sm">{product.approval_number}</p>
                </div>
              )}
              <div>
                <p className="text-gray-400 text-xs">适用物种</p>
                <p className="text-gray-700 mt-0.5 text-xs md:text-sm">{product.suitable_species || '猫狗'}</p>
              </div>
              {product.description && (
                <div className="col-span-2">
                  <p className="text-gray-400 text-xs mb-1">产品描述</p>
                  <p className="text-gray-700 text-xs md:text-sm leading-relaxed line-clamp-6">{product.description}</p>
                </div>
              )}
            </div>
          </div>

          {/* 使用说明 */}
          {product.usage_guide && (
            <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
              <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">📖 使用说明</h3>
              <p className="text-xs md:text-sm text-gray-700 leading-relaxed whitespace-pre-line">{product.usage_guide}</p>
            </div>
          )}

          {/* 成分列表 */}
          {product.ingredients && product.ingredients.length > 0 && (
            <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
              <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">🧪 成分列表 ({product.ingredients.length})</h3>
              <div className="space-y-2 md:space-y-3">
                {product.ingredients.map((ing, idx) => {
                  const hasRisk = ing.risk_tags && ing.risk_tags.length > 0
                  return (
                    <div
                      key={ing.id}
                      onClick={() => navigate(`/ingredient/${ing.id}`)}
                      className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors active:scale-[0.98] ${
                        hasRisk
                          ? 'bg-red-50 border border-red-200 hover:bg-red-100'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <span className={`text-xs w-5 flex-shrink-0 ${hasRisk ? 'text-red-400' : 'text-gray-400'}`}>{idx + 1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <p className="text-sm font-medium text-gray-800">{ing.name}</p>
                          {hasRisk && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 text-red-600 font-medium flex-shrink-0">
                              ⚠️ 风险
                            </span>
                          )}
                        </div>
                        {ing.function && <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{ing.function}</p>}
                        {hasRisk && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {ing.risk_tags.map(tag => (
                              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-red-100/60 text-red-600">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <span className={`text-sm flex-shrink-0 ${hasRisk ? 'text-red-300' : 'text-gray-300'}`}>→</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* AI 问答 */}
          <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
            <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">🤖 AI 成分问答</h3>
            <AIChat productName={product.name} ingredients={product.ingredients?.map(i => i.name) || []} />
          </div>

          {/* 用户评价 */}
          <ReviewSection productId={parseInt(id)} />
        </div>
      </div>

      {/* 喂养记录弹窗 */}
      {showFeedingModal && (
        <FeedingModal
          pets={pets}
          product={product}
          productId={parseInt(id)}
          feedingPets={feedingPets}
          onClose={() => setShowFeedingModal(false)}
          onUpdated={(pets) => setFeedingPets(pets)}
        />
      )}
    </div>
  )
}

// ===== 喂养弹窗 =====
function FeedingModal({ pets, product, productId, feedingPets, onClose, onUpdated }) {
  const [selectedPet, setSelectedPet] = useState('')
  const [saving, setSaving] = useState(false)
  const alreadyFeeding = feedingPets || []

  const handleAdd = async () => {
    if (!selectedPet) { alert('请选择宠物'); return }
    setSaving(true)
    try {
      await api.createFeedingLog({ pet_name: selectedPet, product_id: productId })
      onUpdated([...alreadyFeeding, selectedPet])
      onClose()
    } catch (e) {
      alert(e.message)
    }
    setSaving(false)
  }

  const handleRemove = async (petName) => {
    if (!confirm(`确定停止记录 ${petName} 吃这个产品吗？`)) return
    setSaving(true)
    try {
      // 找到对应的 feeding log 并停用
      const data = await api.getFeedingLogs()
      const log = data.items.find(l => l.pet_name === petName && l.product_id === productId && l.is_active === 1)
      if (log) {
        await api.updateFeedingLog(log.id, { is_active: 0 })
        onUpdated(alreadyFeeding.filter(p => p !== petName))
      }
    } catch (e) {
      alert(e.message)
    }
    setSaving(false)
  }

  return createPortal(
    <div className="fixed inset-0 z-[60] flex items-end justify-center modal-overlay" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div className="relative bg-white rounded-t-3xl w-full max-w-md p-6 pb-20 animate-fadeIn max-h-[80vh] overflow-y-auto safe-bottom" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">🍽 喂养记录</h2>
          <button onClick={onClose} className="text-gray-400 text-lg">✕</button>
        </div>

        {/* 已在吃的宠物 */}
        {alreadyFeeding.length > 0 && (
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">正在吃「{product.name}」的宠物</p>
            <div className="space-y-2">
              {alreadyFeeding.map(p => (
                <div key={p} className="flex items-center gap-2 p-3 bg-orange-50 rounded-xl">
                  <span className="text-base">🍽</span>
                  <span className="flex-1 text-sm font-medium text-gray-800">{p}</span>
                  <button onClick={() => handleRemove(p)} disabled={saving}
                    className="px-3 py-1 text-xs text-red-500 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50">
                    停止
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 添加新宠物 */}
        {pets.filter(p => !alreadyFeeding.includes(p.pet_name)).length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-2">添加新的喂养记录</p>
            <div className="flex gap-2 flex-wrap mb-4">
              {pets.filter(p => !alreadyFeeding.includes(p.pet_name)).map(p => (
                <button key={p.id} onClick={() => setSelectedPet(p.pet_name)}
                  className={`px-3 py-2 rounded-xl text-sm transition-all flex items-center gap-1.5 ${
                    selectedPet === p.pet_name
                      ? 'bg-orange-500 text-white shadow-sm'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}>
                  <span>{p.breed?.species === '猫' ? '🐱' : '🐶'}</span>
                  <span className="font-medium">{p.pet_name}</span>
                </button>
              ))}
            </div>
            <button onClick={handleAdd} disabled={saving || !selectedPet}
              className="w-full bg-orange-500 text-white py-3 rounded-xl font-medium text-sm disabled:opacity-50">
              {saving ? '保存中...' : '✅ 开始记录'}
            </button>
            <p className="text-xs text-gray-400 mt-2 text-center">
              开始后可在「健康管家 → 喂养日记」记录每天观察
            </p>
          </div>
        )}

        {pets.filter(p => !alreadyFeeding.includes(p.pet_name)).length === 0 && alreadyFeeding.length > 0 && (
          <p className="text-center text-sm text-gray-400">所有宠物都已记录 ✅</p>
        )}
      </div>
    </div>,
    document.body
  )
}
