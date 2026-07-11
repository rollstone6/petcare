import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Swiper, SwiperSlide } from 'swiper/react'
import { FreeMode, Mousewheel } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/free-mode'
import { api } from '../api/client'

export default function Compare() {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState([])
  const [showCompare, setShowCompare] = useState(false)

  useEffect(() => {
    api.searchProducts({ page_size: 50 }).then(data => setProducts(data.items || []))
  }, [])

  const toggleSelect = (id) => {
    if (selected.includes(id)) {
      setSelected(selected.filter(s => s !== id))
    } else if (selected.length < 4) {
      setSelected([...selected, id])
    }
  }

  const selectedProducts = products.filter(p => selected.includes(p.id))

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-white px-4 md:px-8 pt-8 md:pt-10 pb-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">⚖️ 产品对比</h1>
          <p className="text-sm md:text-base text-gray-500 mt-1">选择 2-4 款产品进行对比（已选 {selected.length}/4）</p>
        </div>
      </div>

      <div className="px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          {/* 已选产品 */}
          {selected.length > 0 && (
            <div className="mt-3">
              <Swiper
                modules={[FreeMode, Mousewheel]}
                spaceBetween={8}
                slidesPerView="auto"
                freeMode={true}
                mousewheel={true}
                className="pb-2"
              >
                {selectedProducts.map(p => (
                  <SwiperSlide key={p.id} className="!w-auto">
                    <div className="bg-primary/10 text-primary rounded-full px-3 py-1 text-sm flex items-center gap-1 whitespace-nowrap">
                      {p.name.split(' ')[0]}
                      <button onClick={() => toggleSelect(p.id)} className="ml-1">✕</button>
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
              {selected.length >= 2 && (
                <button
                  onClick={() => setShowCompare(!showCompare)}
                  className="mt-3 w-full bg-primary text-white py-3 rounded-xl font-medium hover:bg-primary-dark transition-colors"
                >
                  {showCompare ? '收起对比' : '开始对比'}
                </button>
              )}
            </div>
          )}

          {/* 对比结果 */}
          {showCompare && selectedProducts.length >= 2 && (
            <div className="mt-4">
              <div className="bg-white rounded-2xl shadow-sm overflow-x-auto">
                <table className="w-full text-sm md:text-base">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="p-3 md:p-4 text-left text-gray-500 font-medium">项目</th>
                      {selectedProducts.map(p => (
                        <th key={p.id} className="p-3 md:p-4 text-center font-medium text-gray-900 min-w-[100px]">{p.name.split(' ')[0]}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-3 md:p-4 text-gray-500">品牌</td>
                      {selectedProducts.map(p => <td key={p.id} className="p-3 md:p-4 text-center">{p.brand}</td>)}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 md:p-4 text-gray-500">品类</td>
                      {selectedProducts.map(p => <td key={p.id} className="p-3 md:p-4 text-center">{p.category}</td>)}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 md:p-4 text-gray-500">类型</td>
                      {selectedProducts.map(p => <td key={p.id} className="p-3 md:p-4 text-center">{p.type}</td>)}
                    </tr>
                    <tr>
                      <td className="p-3 md:p-4 text-gray-500">安全评分</td>
                      {selectedProducts.map(p => (
                        <td key={p.id} className="p-3 md:p-4 text-center">
                          <span className={`font-bold ${p.safety_score <= 3 ? 'text-green-500' : p.safety_score <= 6 ? 'text-yellow-500' : 'text-red-500'}`}>
                            ⭐ {p.safety_score}
                          </span>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 产品选择列表 */}
          <div className="mt-6">
            <h2 className="font-semibold text-gray-900 mb-3 md:mb-4">选择产品</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3">
              {products.map(p => (
                <div
                  key={p.id}
                  onClick={() => toggleSelect(p.id)}
                  className={`flex items-center gap-3 p-3 md:p-4 rounded-xl cursor-pointer transition-all ${
                    selected.includes(p.id) ? 'bg-primary/5 border border-primary/30 shadow-sm' : 'bg-white border border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    selected.includes(p.id) ? 'border-primary bg-primary' : 'border-gray-300'
                  }`}>
                    {selected.includes(p.id) && <span className="text-white text-xs">✓</span>}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm md:text-base font-medium text-gray-900 truncate">{p.name}</div>
                    <div className="text-xs md:text-sm text-gray-400">{p.brand} · {p.category}</div>
                  </div>
                  <span className={`text-sm md:text-base font-bold ${p.safety_score <= 3 ? 'text-green-500' : 'text-yellow-500'}`}>
                    {p.safety_score}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
