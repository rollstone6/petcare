import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import QuickTags from '../components/QuickTags'
import CategoryGrid from '../components/CategoryGrid'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'

const typeTabs = ['全部', '药品', '食品', '保健品']
const typeMap = { '药品': '药品', '食品': '食品', '保健品': '保健品' }
const sortOptions = [
  { key: 'score', label: '评分最高', icon: '⭐' },
  { key: 'name', label: '名称', icon: '🔤' },
  { key: 'newest', label: '最新', icon: '🆕' },
]
const PAGE_SIZE = 20

function safetyLabel(score) {
  if (score >= 4.5) return { text: '优秀', cls: 'bg-emerald-100 text-emerald-700' }
  if (score >= 3.5) return { text: '良好', cls: 'bg-green-100 text-green-700' }
  if (score >= 2.5) return { text: '一般', cls: 'bg-yellow-100 text-yellow-700' }
  if (score >= 1.5) return { text: '慎用', cls: 'bg-orange-100 text-orange-700' }
  return { text: '高危', cls: 'bg-red-100 text-red-700' }
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { state, dispatch } = useApp()

  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [type, setType] = useState(searchParams.get('type') || '')
  const [sort, setSort] = useState('score')
  const [activeType, setActiveType] = useState(() => {
    const t = searchParams.get('type')
    return t && typeTabs.includes(t) ? t : typeTabs[0]
  })
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [compareMode, setCompareMode] = useState(false)
  const [selected, setSelected] = useState([])
  const [hasSearched, setHasSearched] = useState(!!searchParams.get('q') || !!searchParams.get('type'))

  // 品类筛选
  const [categories, setCategories] = useState([])
  const [activeCategoryId, setActiveCategoryId] = useState(null)

  // 品牌筛选
  const [brands, setBrands] = useState([])
  const [activeBrandId, setActiveBrandId] = useState(null)
  const [showAllBrands, setShowAllBrands] = useState(false)

  // 搜索联想建议
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const debounceRef = useRef(null)
  const inputRef = useRef(null)

  // 加载品类列表（随类型 tab 变化）
  useEffect(() => {
    const typeVal = activeType === '全部' ? '' : activeType
    api.getCategories(typeVal).then(data => {
      setCategories(data.items || [])
      // 切换类型时重置品类选择
      setActiveCategoryId(null)
    }).catch(() => setCategories([]))
  }, [activeType])

  // 加载品牌列表（随类型 tab 变化）
  useEffect(() => {
    const typeVal = activeType === '全部' ? '' : activeType
    api.getBrands(typeVal).then(data => {
      setBrands(data.items || [])
      setActiveBrandId(null)
    }).catch(() => setBrands([]))
  }, [activeType])

  // 监听 URL 参数变化
  useEffect(() => {
    const urlQ = searchParams.get('q') || ''
    const urlT = searchParams.get('type') || ''
    if (urlQ !== query || urlT !== type) {
      setQuery(urlQ)
      setType(urlT)
      setActiveType(urlT && typeTabs.includes(urlT) ? urlT : urlQ ? '全部' : typeTabs[0])
      setHasSearched(true)
      setPage(1)
    }
  }, [searchParams])

  const doSearch = useCallback(async (q, t, s, p, catId, brandId, append = false) => {
    if (append) setLoadingMore(true)
    else setLoading(true)
    try {
      const params = { page_size: PAGE_SIZE, page: p, sort: s }
      if (q) params.q = q
      if (t && t !== '全部') params.type = t
      if (catId) params.category_id = catId
      if (brandId) params.brand_id = brandId
      const data = await api.searchProducts(params)
      const items = data.items || []
      setResults(prev => append ? [...prev, ...items] : items)
      setTotal(data.total || 0)
      setHasMore((data.page || 1) * PAGE_SIZE < (data.total || 0))
    } catch (e) {
      console.error(e)
      if (!append) setResults([])
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [])

  // 搜索触发器（query/type/sort/page/activeCategoryId/activeBrandId 变化且是首页时重新搜索）
  useEffect(() => {
    if (query || hasSearched) doSearch(query, type, sort, page, activeCategoryId, activeBrandId, false)
  }, [query, type, sort, hasSearched, doSearch, page, activeCategoryId, activeBrandId])

  // 输入联想（debounce）
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!query.trim() || query.trim().length < 1) {
      setSuggestions([])
      return
    }
    debounceRef.current = setTimeout(async () => {
      try {
        const data = await api.searchProducts({ q: query.trim(), page_size: 5, sort: 'score' })
        setSuggestions((data.items || []).map(p => p.name))
      } catch {
        setSuggestions([])
      }
    }, 250)
    return () => clearTimeout(debounceRef.current)
  }, [query])

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (query.trim()) dispatch({ type: 'ADD_HISTORY', payload: query.trim() })
    setHasSearched(true)
    setPage(1)
    setSearchParams({ q: query, type })
    setShowSuggestions(false)
    doSearch(query, type, sort, 1, activeCategoryId, activeBrandId, false)
  }

  const handleTypeChange = (t) => {
    setType(t === '全部' ? '' : t)
    setActiveType(t)
    setActiveCategoryId(null)
    setActiveBrandId(null)
    setHasSearched(true)
    setPage(1)
  }

  const handleCategoryChange = (catId) => {
    setActiveCategoryId(catId === activeCategoryId ? null : catId)
    setHasSearched(true)
    setPage(1)
  }

  const handleBrandChange = (brandId) => {
    setActiveBrandId(brandId === activeBrandId ? null : brandId)
    setHasSearched(true)
    setPage(1)
  }

  const loadMore = () => {
    const next = page + 1
    setPage(next)
    doSearch(query, type, sort, next, activeCategoryId, activeBrandId, true)
  }

  const toggleSelect = (id) => {
    if (selected.includes(id)) setSelected(selected.filter(s => s !== id))
    else if (selected.length < 4) setSelected([...selected, id])
  }

  const pickSuggestion = (s) => {
    setQuery(s)
    setShowSuggestions(false)
    dispatch({ type: 'ADD_HISTORY', payload: s })
    setHasSearched(true)
    setPage(1)
    setSearchParams({ q: s, type })
    doSearch(s, type, sort, 1, activeCategoryId, activeBrandId, false)
  }

  const selectedProducts = results.filter(p => selected.includes(p.id))

  // 对比表：收集每个产品的关键成分（从 results 已有字段 + 懒加载详情）
  const [detailMap, setDetailMap] = useState({})
  useEffect(() => {
    if (!compareMode || selectedProducts.length < 2) return
    selectedProducts.forEach(p => {
      if (!detailMap[p.id]) {
        api.getProduct(p.id).then(d => {
          setDetailMap(prev => ({ ...prev, [p.id]: d }))
        }).catch(() => {})
      }
    })
  }, [compareMode, selectedProducts.length])

  const getTopIngredients = (productId) => {
    const d = detailMap[productId]
    if (!d?.ingredients) return null
    return d.ingredients.slice(0, 5).map(i => i.name)
  }

  return (
    <div className="animate-fadeIn">
      {/* 搜索栏 - 移动端紧凑版 */}
      <div className="bg-white px-3 md:px-8 pt-4 md:pt-10 pb-3 sticky top-0 z-40 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center gap-2 mb-2">
            <div className="flex-1 flex items-center bg-gray-100 rounded-full px-3 md:px-4 py-2 md:py-2.5 relative">
              <span className="text-gray-400 mr-2 text-sm">🔍</span>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={e => { setQuery(e.target.value); setShowSuggestions(true) }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                placeholder="搜索药品、食品、品牌..."
                className="bg-transparent flex-1 outline-none text-sm md:text-base"
              />
              {query && (
                <button type="button" onClick={() => { setQuery(''); setSuggestions([]) }} className="text-gray-400 ml-1 text-sm">✕</button>
              )}
              {/* 联想建议下拉 */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      type="button"
                      onMouseDown={(e) => { e.preventDefault(); pickSuggestion(s) }}
                      className="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 flex items-center gap-2 border-b border-gray-50 last:border-0"
                    >
                      <span className="text-gray-300">🔍</span>
                      <span className="truncate">{s}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button type="submit" className="bg-primary text-white px-4 md:px-5 py-2 md:py-2.5 rounded-full text-sm font-medium shrink-0">
              搜索
            </button>
          </form>
          {/* 操作条：对比开关 */}
          <div className="flex items-center justify-between gap-2">
            <button
              onClick={() => { setCompareMode(!compareMode); setSelected([]); setDetailMap({}) }}
              className={`text-xs px-3 py-1 rounded-full transition-colors ${
                compareMode ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              ⚖️ {compareMode ? '退出对比' : '对比模式'}
            </button>
          </div>
        </div>
      </div>

      {/* 搜索历史 - 紧跟搜索框 */}
      {!query && !compareMode && state.searchHistory.length > 0 && (
        <div className="px-3 md:px-8 pt-3 mb-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">🕐 搜索历史</span>
              <button onClick={() => dispatch({ type: 'CLEAR_HISTORY' })} className="text-xs text-gray-400 hover:text-red-400 transition-colors">清除</button>
            </div>
            <div className="flex flex-wrap gap-2">
              {state.searchHistory.map((h, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(h)
                    setHasSearched(true)
                    setPage(1)
                    setSearchParams({ q: h, type })
                    dispatch({ type: 'ADD_HISTORY', payload: h })
                  }}
                  className="bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full text-sm hover:bg-gray-200 transition-colors"
                >
                  {h}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 快捷标签 - 搜索历史下方 */}
      {!query && !hasSearched && !compareMode && (
        <div className="px-3 md:px-8 mb-4">
          <div className="max-w-4xl mx-auto">
            <QuickTags mode="search" />
          </div>
        </div>
      )}

      {/* 类型筛选 */}
      {hasSearched && (
        <div className="px-3 md:px-8 pt-3 pb-1">
          <div className="max-w-4xl mx-auto flex gap-2 overflow-x-auto scrollbar-hide">
            {typeTabs.map(t => (
              <button
                key={t}
                onClick={() => handleTypeChange(t)}
                className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                  t === activeType
                    ? 'bg-primary text-white shadow-sm'
                    : 'bg-white text-gray-600 border border-gray-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 品类筛选 - 网格布局优化版 */}
      {hasSearched && categories.filter(c => c.product_count > 0).length > 0 && (
        <div className="px-3 md:px-8 pt-1 pb-2">
          <div className="max-w-4xl mx-auto">
            <CategoryGrid
              categories={categories.filter(c => c.product_count > 0)}
              activeCategoryId={activeCategoryId}
              onCategoryChange={handleCategoryChange}
            />
          </div>
        </div>
      )}

      {/* 品牌筛选 - 横向滚动，带展开/收起 */}
      {hasSearched && brands.length > 0 && (
        <div className="px-3 md:px-8 pt-1 pb-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-gray-500 font-medium">品牌</span>
              {brands.length > 8 && (
                <button
                  onClick={() => setShowAllBrands(!showAllBrands)}
                  className="text-xs text-primary hover:underline"
                >
                  {showAllBrands ? '收起' : `全部 ${brands.length}`}
                </button>
              )}
              {activeBrandId && (
                <button
                  onClick={() => { setActiveBrandId(null); setHasSearched(true); setPage(1) }}
                  className="text-xs text-red-400 hover:text-red-500 ml-auto"
                >
                  清除品牌 ✕
                </button>
              )}
            </div>
            <div className={`flex gap-1.5 overflow-x-auto scrollbar-hide pb-1 ${showAllBrands ? 'flex-wrap' : ''}`}>
              {(showAllBrands ? brands : brands.slice(0, 8)).map(b => (
                <button
                  key={b.id}
                  onClick={() => handleBrandChange(b.id)}
                  className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors shrink-0 ${
                    activeBrandId === b.id
                      ? 'bg-purple-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {b.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 筛选摘要栏 - 显示当前激活的筛选条件 */}
      {hasSearched && (activeCategoryId !== null || activeBrandId !== null) && (
        <div className="px-3 md:px-8 py-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">当前筛选:</span>
              {activeCategoryId !== null && (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">
                  {categories.find(c => c.id === activeCategoryId)?.name}
                  <button
                    onClick={() => handleCategoryChange(null)}
                    className="hover:text-blue-900 transition-colors"
                  >
                    ✕
                  </button>
                </span>
              )}
              {activeBrandId !== null && (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-700">
                  {brands.find(b => b.id === activeBrandId)?.name}
                  <button
                    onClick={() => handleBrandChange(null)}
                    className="hover:text-purple-900 transition-colors"
                  >
                    ✕
                  </button>
                </span>
              )}
              <button
                onClick={() => {
                  setActiveCategoryId(null)
                  setActiveBrandId(null)
                  setHasSearched(true)
                  setPage(1)
                }}
                className="text-xs text-gray-400 hover:text-red-500 transition-colors ml-auto"
              >
                清除所有筛选
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 排序条 - 搜索后才显示 */}
      {hasSearched && results.length > 1 && !compareMode && (
        <div className="px-3 md:px-8 py-2">
          <div className="max-w-4xl mx-auto flex items-center gap-2 overflow-x-auto scrollbar-hide">
            <span className="text-xs text-gray-400 shrink-0">排序</span>
            {sortOptions.map(o => (
              <button
                key={o.key}
                onClick={() => { setSort(o.key); setPage(1) }}
                className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                  sort === o.key
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {o.icon} {o.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 对比：已选产品条 */}
      {compareMode && selected.length > 0 && (
        <div className="px-3 md:px-8 mb-2">
          <div className="max-w-4xl mx-auto flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-400">{selected.length}/4</span>
            {selectedProducts.map(p => (
              <span key={p.id} className="bg-primary/10 text-primary rounded-full px-3 py-1 text-xs flex items-center gap-1">
                {p.name.length > 10 ? p.name.slice(0, 10) + '...' : p.name}
                <button onClick={() => toggleSelect(p.id)}>✕</button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 对比表格 */}
      {compareMode && selectedProducts.length >= 2 && (
        <div className="px-3 md:px-8 mb-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-sm overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="p-3 text-left text-gray-500 font-medium">对比项</th>
                    {selectedProducts.map(p => (
                      <th key={p.id} className="p-3 text-center font-medium text-gray-900 min-w-[110px]">
                        {p.image_url && (
                          <img src={p.image_url} alt="" className="w-12 h-12 object-cover rounded-lg mx-auto mb-1.5" />
                        )}
                        <div className="truncate">{p.name}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="p-3 text-gray-500">品牌</td>
                    {selectedProducts.map(p => <td key={p.id} className="p-3 text-center">{p.brand || '-'}</td>)}
                  </tr>
                  <tr className="border-b">
                    <td className="p-3 text-gray-500">品类</td>
                    {selectedProducts.map(p => <td key={p.id} className="p-3 text-center">{p.category || '-'}</td>)}
                  </tr>
                  <tr className="border-b">
                    <td className="p-3 text-gray-500">类型</td>
                    {selectedProducts.map(p => <td key={p.id} className="p-3 text-center">{p.type}</td>)}
                  </tr>
                  <tr className="border-b">
                    <td className="p-3 text-gray-500">安全评分</td>
                    {selectedProducts.map(p => {
                      const s = safetyLabel(p.safety_score)
                      return (
                        <td key={p.id} className="p-3 text-center">
                          <div className="font-bold text-base">{p.safety_score.toFixed(1)}</div>
                          <span className={`inline-block text-xs px-2 py-0.5 rounded-full mt-0.5 ${s.cls}`}>{s.text}</span>
                        </td>
                      )
                    })}
                  </tr>
                  <tr>
                    <td className="p-3 text-gray-500 align-top">主要成分</td>
                    {selectedProducts.map(p => {
                      const ings = getTopIngredients(p.id)
                      return (
                        <td key={p.id} className="p-3 text-center text-xs align-top">
                          {ings === null ? (
                            <span className="text-gray-300">加载中...</span>
                          ) : ings.length === 0 ? (
                            <span className="text-gray-300">-</span>
                          ) : (
                            <div className="flex flex-col gap-1">
                              {ings.map((n, i) => (
                                <span key={i} className="bg-gray-100 rounded px-1.5 py-0.5">{n}</span>
                              ))}
                            </div>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                  <tr className="border-t">
                    <td className="p-3"></td>
                    {selectedProducts.map(p => (
                      <td key={p.id} className="p-3 text-center">
                        <button
                          onClick={() => navigate(`/product/${p.id}`)}
                          className="text-primary text-xs hover:underline"
                        >
                          查看详情 →
                        </button>
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 结果 */}
      <div className="px-3 md:px-8 pb-24">
        <div className="max-w-4xl mx-auto">
          {loading && results.length === 0 ? (
            <div className="text-center py-10 text-gray-400">搜索中...</div>
          ) : hasSearched ? (
            <>
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-gray-500">
                  共 <span className="font-medium text-gray-700">{total}</span> 个产品
                  {compareMode && <span className="ml-2 text-primary text-xs">· 点击勾选对比</span>}
                </p>
              </div>
              {compareMode ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {results.map(p => (
                    <div
                      key={p.id}
                      onClick={() => toggleSelect(p.id)}
                      className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all ${
                        selected.includes(p.id)
                          ? 'bg-primary/5 border border-primary/30 shadow-sm'
                          : 'bg-white border border-gray-100'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                        selected.includes(p.id) ? 'border-primary bg-primary' : 'border-gray-300'
                      }`}>
                        {selected.includes(p.id) && <span className="text-white text-xs">✓</span>}
                      </div>
                      {p.image_url && (
                        <img src={p.image_url} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
                      )}
                      <div className="flex-1 min-w-0" onClick={(e) => { e.stopPropagation(); navigate(`/product/${p.id}`) }}>
                        <div className="text-sm font-medium text-gray-900 truncate">{p.name}</div>
                        <div className="text-xs text-gray-400">{p.brand} · {p.category}</div>
                      </div>
                      <span className={`text-sm font-bold ${p.safety_score >= 4 ? 'text-green-500' : p.safety_score >= 2.5 ? 'text-yellow-500' : 'text-red-500'}`}>
                        {p.safety_score.toFixed(1)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {results.map(p => <ProductCard key={p.id} product={p} />)}
                </div>
              )}

              {/* 加载更多 */}
              {hasMore && !compareMode && (
                <div className="text-center mt-6">
                  <button
                    onClick={loadMore}
                    disabled={loadingMore}
                    className="px-6 py-2 rounded-full bg-white border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {loadingMore ? '加载中...' : '加载更多'}
                  </button>
                </div>
              )}

              {results.length === 0 && (
                <div className="text-center py-10 text-gray-400">
                  <div className="text-4xl mb-2">🔍</div>
                  <p>未找到相关产品</p>
                  <p className="text-sm mt-1">试试其他关键词</p>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-10 text-gray-400">
              <div className="text-4xl mb-2">🔍</div>
              <p>输入关键词或选择类型开始搜索</p>
              <p className="text-sm mt-1">药品、食品、保健品、品牌...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
