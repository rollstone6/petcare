import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

/**
 * 快捷标签组件 - 展示热门品牌和高危成分
 * @param {string} mode - 'home' 或 'search'，不同页面样式不同
 */
export default function QuickTags({ mode = 'search' }) {
  const navigate = useNavigate()
  const [hotBrands, setHotBrands] = useState([])
  const [dangerousIngredients, setDangerousIngredients] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getHotBrands(8),
      api.getDangerousIngredients(8),
    ])
      .then(([brands, ingredients]) => {
        setHotBrands(brands.items || [])
        setDangerousIngredients(ingredients.items || [])
      })
      .catch(err => {
        console.error('加载快捷标签失败:', err)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="animate-pulse space-y-3">
        <div className="h-8 bg-gray-100 rounded" />
        <div className="h-8 bg-gray-100 rounded" />
      </div>
    )
  }

  const handleBrandClick = (brandName) => {
    navigate(`/search?q=${encodeURIComponent(brandName)}`)
  }

  const handleIngredientClick = (ingredientId) => {
    navigate(`/ingredient/${ingredientId}`)
  }

  // 首页模式：更紧凑
  if (mode === 'home') {
    return (
      <div className="space-y-2">
        {/* 热门品牌 */}
        {hotBrands.length > 0 && (
          <div>
            <div className="text-xs text-gray-500 mb-1.5">🔥 热门品牌</div>
            <div className="flex flex-wrap gap-1.5">
              {hotBrands.slice(0, 6).map(brand => (
                <button
                  key={brand.id}
                  onClick={() => handleBrandClick(brand.name)}
                  className="px-2.5 py-1 bg-white hover:bg-blue-50 text-xs text-gray-700 rounded-full border border-gray-200 hover:border-blue-300 transition-colors"
                >
                  {brand.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 高危成分 */}
        {dangerousIngredients.length > 0 && (
          <div>
            <div className="text-xs text-gray-500 mb-1.5">⚠️ 高危成分</div>
            <div className="flex flex-wrap gap-1.5">
              {dangerousIngredients.slice(0, 6).map(ing => (
                <button
                  key={ing.id}
                  onClick={() => handleIngredientClick(ing.id)}
                  className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-xs text-red-700 rounded-full border border-red-200 hover:border-red-400 transition-colors"
                >
                  {ing.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // 搜索页模式：更详细
  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-4">
      {/* 热门品牌 */}
      {hotBrands.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">🔥 热门品牌</h3>
            <button 
              onClick={() => navigate('/brands')}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              查看全部 →
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {hotBrands.map(brand => (
              <button
                key={brand.id}
                onClick={() => handleBrandClick(brand.name)}
                className="px-3 py-1.5 bg-white hover:bg-blue-50 text-sm text-gray-700 rounded-full border border-gray-200 hover:border-blue-400 transition-all hover:shadow-sm"
              >
                {brand.name}
                {brand.product_count > 0 && (
                  <span className="ml-1 text-xs text-gray-400">
                    ({brand.product_count})
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 高危成分 */}
      {dangerousIngredients.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">⚠️ 高危成分</h3>
            <span className="text-xs text-gray-500">EWG评分 ≥ 7</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {dangerousIngredients.map(ing => (
              <button
                key={ing.id}
                onClick={() => handleIngredientClick(ing.id)}
                className="group px-3 py-1.5 bg-red-50 hover:bg-red-100 text-sm text-red-700 rounded-full border border-red-200 hover:border-red-400 transition-all hover:shadow-sm"
              >
                <span className="flex items-center gap-1">
                  {ing.name}
                  <span className="text-xs opacity-60 group-hover:opacity-100">
                    ({ing.category})
                  </span>
                </span>
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            💡 点击成分名称可查看详细信息和含该成分的产品
          </p>
        </div>
      )}

      {/* 空状态 */}
      {hotBrands.length === 0 && dangerousIngredients.length === 0 && (
        <p className="text-center text-gray-400 text-sm py-2">
          暂无推荐标签
        </p>
      )}
    </div>
  )
}
