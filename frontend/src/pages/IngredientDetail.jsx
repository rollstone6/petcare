import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function IngredientDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [products, setProducts] = useState([])
  const [totalProducts, setTotalProducts] = useState(0)
  const [page, setPage] = useState(1)
  const [loadingMore, setLoadingMore] = useState(false)

  useEffect(() => {
    api.getIngredient(id).then(d => {
      setData(d)
      const prods = d.products || {}
      setProducts(prods.items || [])
      setTotalProducts(prods.total || 0)
      setPage(prods.page || 1)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  const loadMore = () => {
    setLoadingMore(true)
    const nextPage = page + 1
    api.getIngredient(id, nextPage).then(d => {
      const newItems = (d.products || {}).items || []
      setProducts(prev => [...prev, ...newItems])
      setPage(nextPage)
      setLoadingMore(false)
    }).catch(() => setLoadingMore(false))
  }

  if (loading) return <div className="px-4 md:px-8 py-16 text-center"><p className="text-gray-400">加载中...</p></div>
  if (!data) return <div className="px-4 md:px-8 py-16 text-center"><p className="text-4xl mb-3">😿</p><p className="text-gray-500">成分不存在</p><button onClick={() => navigate(-1)} className="mt-4 text-primary text-sm">返回</button></div>

  const ing = data.ingredient
  const level = ing.safety_level || 3
  const levelLabels = { 1: '高风险', 2: '谨慎使用', 3: '一般', 4: '较安全', 5: '安全' }
  const levelColors = {
    5: 'bg-green-500', 4: 'bg-green-400',
    3: 'bg-yellow-400', 2: 'bg-orange-400', 1: 'bg-red-500',
  }

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-6">
        <div className="max-w-2xl mx-auto">
          <button onClick={() => navigate(-1)} className="text-gray-400 text-sm mb-4 hover:text-gray-600 inline-block">← 返回</button>
          
          <div className="flex items-start gap-4 md:gap-5">
            <div className={`w-14 h-14 md:w-16 md:h-16 rounded-2xl ${levelColors[level]} flex items-center justify-center text-white text-xl md:text-2xl font-bold flex-shrink-0`}>
              {level}
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-lg md:text-2xl font-bold text-gray-900">{ing.name}</h1>
              {ing.alias && (
                <p className="text-xs md:text-sm text-gray-400 mt-1">别名: {ing.alias}</p>
              )}
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <span className={`text-xs px-2 py-0.5 rounded-full text-white ${levelColors[level]}`}>
                  {levelLabels[level]}
                </span>
                {ing.category && (
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{ing.category}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 md:px-8 mt-4">
        <div className="max-w-2xl mx-auto space-y-4 md:space-y-5">
          {ing.function && (
            <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
              <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-2">💡 功效</h3>
              <p className="text-sm md:text-base text-gray-700 leading-relaxed">{ing.function}</p>
            </div>
          )}

          {ing.description && (
            <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
              <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-2">📝 详细说明</h3>
              <p className="text-sm md:text-base text-gray-700 leading-relaxed line-clamp-6">{ing.description}</p>
            </div>
          )}

          {/* 含有该成分的产品 */}
          {products.length > 0 && (
            <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
              <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">📦 含有该成分的产品 ({totalProducts})</h3>
              <div className="space-y-2">
                {products.map(p => (
                  <div key={p.id} onClick={() => navigate(`/product/${p.id}`)}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors active:scale-[0.98]">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{p.name}</p>
                      <p className="text-xs text-gray-400">{p.brand} · {p.category}</p>
                    </div>
                    <span className="text-gray-300 text-sm">→</span>
                  </div>
                ))}
              </div>
              {products.length < totalProducts && (
                <button
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="w-full mt-3 py-2.5 text-sm text-primary bg-primary/5 hover:bg-primary/10 rounded-xl transition-colors disabled:opacity-50"
                >
                  {loadingMore ? '加载中...' : `加载更多（已显示 ${products.length}/${totalProducts}）`}
                </button>
              )}
            </div>
          )}

          {/* 安全等级说明 */}
          <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
            <h3 className="font-semibold text-sm md:text-base text-gray-900 mb-3">🔰 安全等级</h3>
            <div className="flex items-center gap-1.5 md:gap-2 mb-3">
              {[1,2,3,4,5].map(i => (
                <div key={i} className={`flex-1 h-2 md:h-2.5 rounded-full ${i <= level ? levelColors[level] : 'bg-gray-200'}`} />
              ))}
            </div>
            <div className="flex justify-between text-[10px] md:text-xs text-gray-400">
              <span>高风险</span>
              <span>谨慎</span>
              <span>一般</span>
              <span>较安全</span>
              <span>安全</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
