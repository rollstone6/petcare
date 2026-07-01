import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import AIChat from '../components/AIChat'
import ReviewSection from '../components/ReviewSection'

const LEVEL_COLORS = {
  5: 'bg-green-500', 4: 'bg-green-400',
  3: 'bg-yellow-400', 2: 'bg-orange-400', 1: 'bg-red-500',
}

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getProduct(id).then(data => {
      setProduct(data)
      setLoading(false)
    }).catch(() => setLoading(false))
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

  const score = product.safety_score || 0
  const level = Math.min(5, Math.max(1, Math.round(score)))

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

          {/* 安全评分 */}
          <div className="mt-5 md:mt-6 flex items-center gap-3 md:gap-4 p-4 md:p-5 bg-gray-50 rounded-2xl">
            <div className={`w-14 h-14 md:w-16 md:h-16 rounded-full ${LEVEL_COLORS[level]} flex items-center justify-center text-white text-xl md:text-2xl font-bold flex-shrink-0`}>
              {score.toFixed(1)}
            </div>
            <div>
              <p className="font-semibold text-sm md:text-base text-gray-900">安全评分</p>
              <p className="text-xs md:text-sm text-gray-500 mt-0.5">
                {score >= 4 ? '安全可靠，推荐使用' : score >= 3 ? '基本安全，注意用量' : score >= 2 ? '谨慎使用，咨询兽医' : '风险较高，遵医嘱使用'}
              </p>
              <div className="flex gap-1 mt-2">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className={`w-3 h-3 md:w-4 md:h-4 rounded-full ${i <= level ? LEVEL_COLORS[level] : 'bg-gray-200'}`} />
                ))}
              </div>
            </div>
          </div>
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
                  <p className="text-gray-700 text-xs md:text-sm leading-relaxed">{product.description}</p>
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
                {product.ingredients.map((ing, idx) => (
                  <div
                    key={ing.id}
                    onClick={() => navigate(`/ingredient/${ing.id}`)}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors active:scale-[0.98]"
                  >
                    <span className="text-xs text-gray-400 w-5 flex-shrink-0">{idx + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800">{ing.name}</p>
                      {ing.function && <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{ing.function}</p>}
                    </div>
                    <span className="text-gray-300 text-sm">→</span>
                  </div>
                ))}
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
    </div>
  )
}
