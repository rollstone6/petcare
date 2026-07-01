import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/SearchBar'
import QuickTags from '../components/QuickTags'
import ProductCard from '../components/ProductCard'
import { SkeletonList } from '../components/Skeleton'
import { api } from '../api/client'

const quickLinks = [
  { label: '药品查询', icon: '💊', path: '/search?type=药品' },
  { label: '食品查询', icon: '🍖', path: '/search?type=食品' },
  { label: '保健品', icon: '✨', path: '/search?type=保健品' },
  { label: '品种百科', icon: '🐾', path: '/breeds' },
]

export default function Home() {
  const navigate = useNavigate()
  const [hotProducts, setHotProducts] = useState([])
  const [breeds, setBreeds] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.searchProducts({ page_size: 12 }),
      api.getBreeds(),
    ]).then(([products, breeds]) => {
      setHotProducts(products.items || [])
      setBreeds((breeds.items || []).slice(0, 8))
      setLoading(false)
    }).catch((err) => {
      console.error('首页加载失败:', err)
      setLoading(false)
    })
  }, [])

  return (
    <div className="animate-fadeIn pb-2">
      {/* 搜索 */}
      <div className="px-4 md:px-8 pt-6 md:pt-10 pb-4">
        <div className="max-w-4xl mx-auto">
          <SearchBar />
        </div>
      </div>

      {/* 快捷标签 */}
      <div className="px-4 md:px-8 mb-4">
        <div className="max-w-4xl mx-auto">
          <QuickTags mode="home" />
        </div>
      </div>

      {/* 快捷入口 */}
      <div className="px-4 md:px-8 mb-6">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-4 gap-2 md:gap-4">
            {quickLinks.map(link => (
              <button
                key={link.path}
                onClick={() => navigate(link.path)}
                className="flex flex-col items-center justify-center bg-white rounded-xl md:rounded-2xl p-3 md:p-5 shadow-sm hover:shadow-md transition-all active:scale-95 touch-target"
              >
                <span className="text-2xl md:text-4xl mb-1 md:mb-2">{link.icon}</span>
                <span className="text-xs md:text-sm font-medium text-gray-700">{link.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 热门产品 */}
      <div className="px-4 md:px-8 mb-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <h2 className="text-base md:text-lg font-bold text-gray-900">🔥 热门产品</h2>
            <button onClick={() => navigate('/search')} className="text-xs md:text-sm text-primary">查看更多 →</button>
          </div>
          {loading ? (
            <SkeletonList count={4} />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 md:gap-4">
              {hotProducts.slice(0, 8).map(p => (
                <ProductCard key={p.id} product={p} compact />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 品种百科预览 */}
      <div className="px-4 md:px-8 mb-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <h2 className="text-base md:text-lg font-bold text-gray-900">🐾 品种百科</h2>
            <button onClick={() => navigate('/breeds')} className="text-xs md:text-sm text-primary">查看全部 →</button>
          </div>
          {loading ? (
            <div className="grid grid-cols-4 gap-3 md:gap-4">
              {[1,2,3,4,5,6,7,8].map(i => (
                <div key={i} className="bg-white rounded-xl md:rounded-2xl p-3 md:p-4 animate-pulse">
                  <div className="aspect-square bg-gray-200 rounded-lg mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-3/4 mx-auto" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-2 md:gap-4">
              {breeds.map(b => (
                <button
                  key={b.id}
                  onClick={() => navigate(`/breed/${b.id}`)}
                  className="flex flex-col items-center bg-white rounded-xl md:rounded-2xl p-2 md:p-4 shadow-sm hover:shadow-md transition-all active:scale-95 touch-target"
                >
                  <div className="w-full aspect-square rounded-lg md:rounded-xl overflow-hidden bg-gray-100 mb-1.5 md:mb-2">
                    <img
                      src={b.image_url || '/placeholder-breed.svg'}
                      alt={b.name}
                      loading="lazy"
                      className="w-full h-full object-cover"
                      onError={(e) => { e.target.style.display = 'none' }}
                    />
                  </div>
                  <span className="text-xs md:text-sm font-medium text-gray-800 text-center line-clamp-1">{b.name}</span>
                  <span className="text-[10px] md:text-xs text-gray-400">{b.species}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
