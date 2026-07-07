import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Swiper, SwiperSlide } from 'swiper/react'
import { FreeMode, Mousewheel } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/free-mode'
import { SkeletonBreedCard } from '../components/Skeleton'
import { api } from '../api/client'

const SPECIES_ICONS = {
  '全部': '🐾', '狗': '🐕', '猫': '🐈', '兔子': '🐇', '仓鼠': '🐹',
  '鸟类': '🐦', '鱼类': '🐟', '爬行类': '🦎', '刺猬': '🦔',
  '雪貂': '🦦', '豚鼠': '🐹', '龙猫': '🐭', '蜜袋鼯': '🐿️',
}

const SORT_OPTIONS = [
  { key: 'name', label: '按名字', icon: '🔤' },
  { key: 'species', label: '按种类', icon: '🏷️' },
]

const PAGE_SIZE = 24

export default function BreedList() {
  const navigate = useNavigate()
  const [breeds, setBreeds] = useState([])
  const [species, setSpecies] = useState('')
  const [speciesList, setSpeciesList] = useState(['全部', '狗', '猫'])
  const [sortBy, setSortBy] = useState('name')
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [page, setPage] = useState(1)
  const observerRef = useRef(null)
  const loadMoreRef = useRef(null)

  useEffect(() => {
    api.getSpecies().then(data => {
      if (Array.isArray(data)) {
        setSpeciesList(['全部', ...data.map(s => s.name)])
      }
    }).catch(() => {})
  }, [])

  // 重置并加载第一页
  useEffect(() => {
    setLoading(true)
    setBreeds([])
    setPage(1)
    setHasMore(true)
    api.getBreeds(species || undefined, sortBy, 1, PAGE_SIZE).then(data => {
      setBreeds(data.items || [])
      setHasMore(data.total > PAGE_SIZE)
      setLoading(false)
    })
  }, [species, sortBy])

  // 加载更多
  const loadMore = useCallback(() => {
    if (loadingMore || !hasMore) return
    setLoadingMore(true)
    const nextPage = page + 1
    api.getBreeds(species || undefined, sortBy, nextPage, PAGE_SIZE).then(data => {
      setBreeds(prev => [...prev, ...(data.items || [])])
      setPage(nextPage)
      setHasMore(breeds.length + (data.items || []).length < data.total)
      setLoadingMore(false)
    })
  }, [loadingMore, hasMore, page, species, sortBy, breeds.length])

  // IntersectionObserver 监听滚动到底部
  useEffect(() => {
    if (loading) return
    observerRef.current = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          loadMore()
        }
      },
      { threshold: 0.1 }
    )
    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current)
    }
    return () => observerRef.current?.disconnect()
  }, [loading, hasMore, loadingMore, loadMore])

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-4 sticky top-0 z-40 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">🐾 品种百科</h1>
          <p className="text-sm md:text-base text-gray-500 mt-1">{breeds.length} 个品种</p>
        </div>
      </div>

      <div className="px-4 md:px-8 py-3">
        <div className="max-w-4xl mx-auto">
          <Swiper
            modules={[FreeMode, Mousewheel]}
            slidesPerView="auto"
            freeMode={true}
            mousewheel={true}
            spaceBetween={8}
            className="species-swiper"
          >
            {speciesList.map(s => (
              <SwiperSlide key={s} className="!w-auto">
                <button
                  onClick={() => setSpecies(s === '全部' ? '' : s)}
                  className={`px-3 md:px-4 py-1.5 md:py-2 rounded-full text-sm whitespace-nowrap transition-colors flex items-center gap-1 ${
                    (s === '全部' && !species) || s === species
                      ? 'bg-primary text-white shadow-sm'
                      : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <span>{SPECIES_ICONS[s] || '🐾'}</span>
                  <span>{s}</span>
                </button>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
      </div>

      <div className="px-4 md:px-8 pb-2">
        <div className="max-w-4xl mx-auto flex items-center gap-2">
          <span className="text-xs text-gray-400 whitespace-nowrap">排序：</span>
          {SORT_OPTIONS.map(opt => (
            <button
              key={opt.key}
              onClick={() => setSortBy(opt.key)}
              className={`px-2.5 py-1 rounded-full text-xs transition-colors flex items-center gap-1 ${
                sortBy === opt.key
                  ? 'bg-amber-100 text-amber-700 border border-amber-300'
                  : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              <span>{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          {loading ? (
            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 md:gap-4">
              {Array.from({length: 12}).map((_, i) => <SkeletonBreedCard key={i} />)}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 md:gap-4">
                {breeds.map(b => (
                  <button
                    key={b.id}
                    onClick={() => navigate(`/breed/${b.id}`)}
                    className="group flex flex-col items-center bg-white rounded-xl md:rounded-2xl p-2 md:p-3 shadow-sm hover:shadow-md hover:scale-105 transition-all duration-300 active:scale-95 touch-target"
                  >
                    <div className="w-full aspect-square rounded-full overflow-hidden bg-amber-50 mb-1.5 md:mb-2 border-2 border-white ring-4 ring-amber-100/50">
                      {b.image_url ? (
                        <img
                          src={b.image_url}
                          alt={b.name}
                          loading="lazy"
                          className="w-full h-full object-cover group-hover:rotate-6 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-2xl group-hover:rotate-6 transition-transform duration-300">
                          {b.species === '猫' ? '🐱' : b.species === '狗' ? '🐶' : '🐾'}
                        </div>
                      )}
                    </div>
                    <span className="text-xs md:text-sm font-bold text-gray-700 text-center line-clamp-1 w-full">{b.name}</span>
                    <span className="text-[10px] md:text-xs text-gray-400">{b.species}</span>
                  </button>
                ))}
              </div>
              {loadingMore && (
                <div className="flex justify-center py-8">
                  <div className="flex items-center gap-2 text-gray-400">
                    <div className="w-4 h-4 border-2 border-gray-300 border-t-amber-500 rounded-full animate-spin"></div>
                    <span className="text-sm">加载更多...</span>
                  </div>
                </div>
              )}
              {hasMore && <div ref={loadMoreRef} className="h-10"></div>}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
