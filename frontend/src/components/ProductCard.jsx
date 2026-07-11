import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { api } from '../api/client'

export default function ProductCard({ product, compact = false }) {
  const navigate = useNavigate()
  const { state, dispatch } = useApp()
  const isFav = state.favorites.includes(product.id)

  const toggleFav = async (e) => {
    e.stopPropagation()
    if (!state.user) {
      navigate('/profile')
      return
    }
    try {
      if (isFav) {
        await api.removeFavorite(product.id)
        dispatch({ type: 'REMOVE_FAVORITE', payload: product.id })
      } else {
        await api.addFavorite(product.id)
        dispatch({ type: 'ADD_FAVORITE', payload: product.id })
      }
    } catch (err) {
      console.error(err)
    }
  }

  const score = product.safety_score || 5
  // EWG 1-10分制：低分=安全，高分=风险
  const isSafe = score <= 3
  const isMedium = score > 3 && score <= 6
  const isHigh = score > 6

  return (
    <div
      onClick={() => navigate(`/product/${product.id}`)}
      className={`bg-white rounded-xl md:rounded-2xl shadow-sm hover:shadow-md transition-all cursor-pointer active:scale-[0.98] touch-target overflow-hidden ${
        compact ? 'p-3 md:p-4' : 'p-4 md:p-5'
      }`}
    >
      <div className="flex items-start gap-2 md:gap-3">
        {/* 类型图标 */}
        <div className={`rounded-lg md:rounded-xl flex items-center justify-center flex-shrink-0 ${
          compact ? 'w-10 h-10 md:w-12 md:h-12 text-lg md:text-xl' : 'w-12 h-12 md:w-14 md:h-14 text-xl md:text-2xl'
        } bg-gradient-to-br from-primary/10 to-primary/5`}>
          {product.type === '药品' ? '💊' : product.type === '食品' ? '🍖' : '✨'}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-gray-900 line-clamp-2 leading-snug ${
            compact ? 'text-sm md:text-base' : 'text-base md:text-lg'
          }`}>
            {product.name}
          </h3>
          <div className="flex items-center gap-1.5 mt-1">
            {product.brand && (
              <span className={`text-gray-400 truncate ${compact ? 'text-[10px] md:text-xs' : 'text-xs md:text-sm'}`}>
                {product.brand}
              </span>
            )}
            {product.category && (
              <span className={`text-gray-300 ${compact ? 'text-[10px] md:text-xs' : 'text-xs md:text-sm'}`}>
                · {product.category}
              </span>
            )}
          </div>
        </div>

        {/* 收藏 */}
        <button onClick={toggleFav} className={`flex-shrink-0 ${compact ? 'text-base md:text-lg' : 'text-lg md:text-xl'} ${isFav ? '' : 'opacity-30'} hover:opacity-100 transition-opacity touch-target`}>
          {isFav ? '❤️' : '🤍'}
        </button>
      </div>

      {/* 评分条 - EWG 1-10分制 */}
      <div className={`flex items-center gap-2 ${compact ? 'mt-2 md:mt-3' : 'mt-3 md:mt-4'}`}>
        <div className="flex-1 bg-gray-100 rounded-full h-1.5 md:h-2 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isSafe ? 'bg-green-500' : isMedium ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${(score / 10) * 100}%` }}
          />
        </div>
        <span className={`font-bold flex-shrink-0 ${
          isSafe ? 'text-green-500' : isMedium ? 'text-yellow-500' : 'text-red-500'
        } ${compact ? 'text-xs md:text-sm' : 'text-sm md:text-base'}`}>
          {score.toFixed(1)}
        </span>
      </div>
    </div>
  )
}
