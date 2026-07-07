import { useState, useEffect } from 'react'
import { api } from '../api/client'

/**
 * 品种契合度组件
 * 显示产品与用户宠物的品种契合度指数
 */
export default function BreedCompatibility({ productId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pets, setPets] = useState([])
  const [selectedPetId, setSelectedPetId] = useState(null)

  // 获取用户的宠物列表
  useEffect(() => {
    api.getPets().then(res => {
      const petList = res?.items || []
      setPets(petList)
      // 默认选第一个有品种的宠物
      const firstWithBreed = petList.find(p => p.breed_id)
      if (firstWithBreed) {
        setSelectedPetId(firstWithBreed.id)
      } else if (petList.length > 0) {
        setSelectedPetId(petList[0].id)
      }
    }).catch(() => {
      // 未登录或获取失败
      setLoading(false)
    })
  }, [])

  // 获取契合度数据
  useEffect(() => {
    if (!productId) return
    setLoading(true)
    api.getBreedCompatibility(productId, selectedPetId).then(res => {
      setData(res)
      setLoading(false)
    }).catch(err => {
      setError(err.message)
      setLoading(false)
    })
  }, [productId, selectedPetId])

  // 获取分数颜色
  const getScoreColor = (score) => {
    if (score === null || score === undefined) return '#9ca3af'
    if (score >= 80) return '#10b981' // green
    if (score >= 60) return '#f59e0b' // amber
    if (score >= 40) return '#f97316' // orange
    return '#ef4444' // red
  }

  const getScoreBg = (score) => {
    if (score === null || score === undefined) return 'bg-gray-50'
    if (score >= 80) return 'bg-green-50'
    if (score >= 60) return 'bg-amber-50'
    if (score >= 40) return 'bg-orange-50'
    return 'bg-red-50'
  }

  const getScoreLabel = (score) => {
    if (score === null || score === undefined) return '未分析'
    if (score >= 80) return '高度契合'
    if (score >= 60) return '基本契合'
    if (score >= 40) return '谨慎使用'
    return '不推荐'
  }

  if (loading) {
    return (
      <div className="rounded-2xl p-4 md:p-5 bg-gray-50 animate-pulse">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-1/3" />
            <div className="h-3 bg-gray-200 rounded w-2/3" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return null // 静默失败，不影响页面
  }

  // 未登录或无宠物
  if (!data || (data.compatibility_score === null && (!data.warnings || data.warnings.length === 0))) {
    return (
      <div className="rounded-2xl p-4 md:p-5 bg-blue-50 border border-blue-100">
        <div className="flex items-start gap-3">
          <div className="text-2xl flex-shrink-0">🐾</div>
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">
              {data?.message || '绑定宠物品种，获取个性化契合度分析'}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              在「宠物档案」中添加你的宠物，即可看到品种专属的成分风险提示
            </p>
          </div>
        </div>
      </div>
    )
  }

  const score = data.compatibility_score
  const color = getScoreColor(score)

  return (
    <div className={`rounded-2xl p-4 md:p-5 ${getScoreBg(score)} border`} style={{ borderColor: color + '30' }}>
      {/* 宠物选择器（如果有多个宠物） */}
      {pets.length > 1 && (
        <div className="mb-3 flex items-center gap-2 flex-wrap">
          <span className="text-xs text-gray-500">为哪个宠物分析：</span>
          {pets.map(pet => (
            <button
              key={pet.id}
              onClick={() => setSelectedPetId(pet.id)}
              className={`px-2.5 py-1 rounded-full text-xs transition-colors ${
                selectedPetId === pet.id
                  ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                  : 'text-gray-500 hover:bg-white/50'
              }`}
            >
              {pet.pet_name}
            </button>
          ))}
        </div>
      )}

      {/* 分数展示 */}
      <div className="flex items-center gap-3 md:gap-4">
        <div
          className="w-14 h-14 md:w-16 md:h-16 rounded-full flex items-center justify-center text-white text-xl md:text-2xl font-bold flex-shrink-0 shadow-sm"
          style={{ backgroundColor: color }}
        >
          {score !== null ? score : '?'}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-sm md:text-base text-gray-900">品种契合度</p>
            <span
              className="text-xs px-2 py-0.5 rounded-full text-white"
              style={{ backgroundColor: color }}
            >
              {getScoreLabel(score)}
            </span>
          </div>
          {data.pet_name && data.breed_name && (
            <p className="text-xs text-gray-500 mt-0.5">
              {data.pet_name}（{data.breed_name}）的专属分析
            </p>
          )}
          {data.breed_health_tags && data.breed_health_tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {data.breed_health_tags.map(tag => (
                <span
                  key={tag}
                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                    data.matched_health_tags?.includes(tag)
                      ? 'bg-red-100 text-red-700 font-medium'
                      : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 警告列表 */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="mt-3 space-y-1.5">
          {data.warnings.map((warning, idx) => (
            <p key={idx} className="text-xs text-gray-700 bg-white/70 rounded-lg px-3 py-2 leading-relaxed">
              {warning}
            </p>
          ))}
        </div>
      )}

      {/* 风险提示（无风险时） */}
      {score === 100 && (
        <p className="mt-3 text-xs text-green-700 bg-green-100/50 rounded-lg px-3 py-2">
          ✅ 该产品的成分与{data.breed_name}的常见健康风险无冲突，可以放心使用
        </p>
      )}
    </div>
  )
}
