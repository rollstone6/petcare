import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import ProductCard from '../components/ProductCard'

export default function BreedDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [breed, setBreed] = useState(null)
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getBreed(id),
      api.getBreedProducts(id),
    ]).then(([breedData, productData]) => {
      setBreed(breedData)
      setProducts(productData.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="px-4 md:px-8 py-8">
        <div className="max-w-2xl mx-auto animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/2" />
          <div className="aspect-video bg-gray-200 rounded-2xl" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
    )
  }

  if (!breed) {
    return (
      <div className="px-4 md:px-8 py-16 text-center">
        <p className="text-4xl mb-3">😿</p>
        <p className="text-gray-500">品种不存在</p>
        <button onClick={() => navigate('/breeds')} className="mt-4 text-primary text-sm">返回品种列表</button>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn pb-4">
      {/* 头部 */}
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-6">
        <div className="max-w-2xl mx-auto">
          <button onClick={() => navigate(-1)} className="text-gray-400 text-sm mb-4 hover:text-gray-600 inline-block">← 返回</button>
          
          <div className="flex flex-col md:flex-row md:items-start gap-4 md:gap-6">
            <div className="w-full md:w-48 aspect-square md:aspect-[3/4] rounded-2xl overflow-hidden bg-gray-100 flex-shrink-0">
              {breed.image_url ? (
                <img
                  src={breed.image_url}
                  alt={breed.name}
                  loading="eager"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-6xl">
                  {breed.species === '猫' ? '🐱' : breed.species === '狗' ? '🐶' : '🐾'}
                </div>
              )}
            </div>
            <div className="flex-1">
              <h1 className="text-xl md:text-2xl font-bold text-gray-900">{breed.name}</h1>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs md:text-sm bg-primary/10 text-primary px-2 py-0.5 rounded-full">{breed.species}</span>
                <span className="text-xs md:text-sm bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{breed.size || '中型'}</span>
              </div>
              {breed.description && (
                <p className="text-sm md:text-base text-gray-600 mt-4 leading-relaxed line-clamp-6">{breed.description}</p>
              )}
              {breed.common_issues && (
                <div className="mt-4 p-3 md:p-4 bg-amber-50 rounded-xl">
                  <p className="text-xs md:text-sm font-medium text-amber-800 mb-1">⚠️ 常见健康问题</p>
                  <p className="text-xs md:text-sm text-amber-700">{breed.common_issues}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 推荐产品 */}
      {products.length > 0 && (
        <div className="px-4 md:px-8 mt-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-base md:text-lg font-bold text-gray-900 mb-3 md:mb-4">💊 推荐产品</h2>
            <div className="grid grid-cols-2 gap-2 md:gap-4">
              {products.slice(0, 6).map(p => (
                <ProductCard key={p.id} product={p} compact />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
