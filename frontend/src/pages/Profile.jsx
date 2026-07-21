import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { api } from '../api/client'
import { getToken } from '../api/client'
import HealthTracker from './HealthTracker'

export default function Profile() {
  const { state, dispatch } = useApp()
  const navigate = useNavigate()
  const [mainTab, setMainTab] = useState('profile')
  const [showLogin, setShowLogin] = useState(false)
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  // 统计数据
  const [stats, setStats] = useState({
    petCount: 0,
    scheduleCount: 0,
    reviewCount: 0,
  })
  const [myReviews, setMyReviews] = useState([])
  const [showReviews, setShowReviews] = useState(false)
  const [pets, setPets] = useState([])
  const [petsLoading, setPetsLoading] = useState(true)

  useEffect(() => {
    if (state.user) {
      api.getPets()
        .then(d => {
          setStats(s => ({ ...s, petCount: d.items?.length || 0 }))
          setPets(d.items || [])
        })
        .catch(() => {})
        .finally(() => setPetsLoading(false))
      api.getSchedules().then(d => setStats(s => ({ ...s, scheduleCount: d.items?.length || 0 }))).catch(() => {})
      api.getMyReviews(1).then(d => {
        setStats(s => ({ ...s, reviewCount: d.total || 0 }))
        setMyReviews(d.items || [])
      }).catch(() => {})
    } else {
      setPetsLoading(false)
    }
  }, [state.user])

  const handleAuth = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const fn = isRegister ? api.register : api.login
      const data = await fn(username, password)
      localStorage.setItem('petcare_token', data.token)
      dispatch({ type: 'SET_USER', payload: data.user })
      const favs = await api.getFavorites()
      dispatch({ type: 'SET_FAVORITES', payload: (favs.items || []).map(f => f.id) })
      setShowLogin(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    dispatch({ type: 'LOGOUT' })
  }

  // 快捷功能入口
  const quickActions = [
    { icon: '🐱', label: '宠物档案', path: '/pets', desc: '管理宠物信息 + 健康标签' },
    { icon: '💬', label: '我的评论', action: () => setShowReviews(true), desc: '查看我的评价' },
    { icon: '🔖', label: '我的收藏', count: state.favorites.length, action: null, disabled: true, desc: '已收藏产品' },
  ]

  // 菜单项
  const menuItems = [
    { icon: '🔖', label: '我的收藏', count: state.favorites.length, path: null, disabled: true },
    { icon: '🕐', label: '浏览历史', count: null, path: null, disabled: true },
    { icon: '⚙️', label: '设置', count: null, path: null, disabled: true },
  ]

  const handleItemClick = (item) => {
    if (item.action) {
      item.action()
    } else if (item.path) {
      if (!state.user) {
        setShowLogin(true)
        setIsRegister(false)
        setError('')
      } else {
        navigate(item.path)
      }
    }
  }

  return (
    <div className="animate-fadeIn pb-4">
      {/* 顶部 Tab 切换 */}
      <div className="bg-white px-4 pt-4 pb-2 sticky top-0 z-30 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-1 bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setMainTab('profile')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                mainTab === 'profile' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'
              }`}
            >
              👤 个人中心
            </button>
            <button
              onClick={() => setMainTab('health')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                mainTab === 'health' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'
              }`}
            >
              🏥 宠物管家
            </button>
          </div>
        </div>
      </div>

      {/* 登录/注册弹窗 */}
      {showLogin && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl" onClick={e => e.stopPropagation()}>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-5">
              <button
                type="button"
                onClick={() => { setIsRegister(false); setError('') }}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                  !isRegister 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                登录
              </button>
              <button
                type="button"
                onClick={() => { setIsRegister(true); setError('') }}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                  isRegister 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                注册
              </button>
            </div>
            <form onSubmit={handleAuth} className="space-y-3">
              <input
                type="text" value={username} onChange={e => setUsername(e.target.value)}
                placeholder="用户名" required minLength={2}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
              />
              <input
                type="password" value={password} onChange={e => setPassword(e.target.value)}
                placeholder={isRegister ? "密码（至少8位，含字母和数字）" : "密码"} required minLength={isRegister ? 8 : 4}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
              />
              {isRegister && (
                <p className="text-xs text-gray-400 -mt-1">密码需至少8位，包含字母和数字</p>
              )}
              {error && <p className="text-red-500 text-xs bg-red-50 p-2 rounded-lg">{error}</p>}
              <button type="submit" disabled={loading}
                className="w-full bg-primary text-white py-2.5 rounded-xl font-medium text-sm disabled:opacity-50 hover:bg-primary/90 transition-colors"
              >
                {loading ? '请稍候...' : isRegister ? '立即注册' : '登录'}
              </button>
            </form>
            {!isRegister && (
              <p className="text-xs text-center text-gray-400 mt-4">没有账号？点击上方"注册"创建账号</p>
            )}
            {isRegister && (
              <p className="text-xs text-center text-gray-400 mt-4">已有账号？点击上方"登录"</p>
            )}
            <button onClick={() => setShowLogin(false)} className="w-full text-center text-sm text-gray-300 mt-2 hover:text-gray-500">关闭</button>
          </div>
        </div>
      )}

      {mainTab === 'profile' ? (
        <>
          {/* 用户头像和基本信息 */}
          <div className="bg-primary px-4 md:px-8 pt-8 md:pt-10 pb-8 md:pb-10 md:rounded-b-3xl">
            <div className="max-w-4xl mx-auto flex items-center gap-4 md:gap-6">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-white/20 rounded-full flex items-center justify-center text-3xl md:text-4xl">
                {state.user ? '🐾' : '👤'}
              </div>
              <div className="text-white flex-1">
                <h1 className="text-lg md:text-xl font-bold">{state.user ? state.user.nickname || state.user.username : '宠物主'}</h1>
                {state.user ? (
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-green-100 text-sm md:text-base">@{state.user.username}</p>
                    <button onClick={handleLogout} className="text-green-200 text-xs hover:text-white">退出登录</button>
                  </div>
                ) : (
                  <button
                    onClick={() => { setShowLogin(true); setIsRegister(false); setError('') }}
                    className="text-green-100 text-sm md:text-base mt-1 hover:text-white"
                  >
                    登录 / 注册 →
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* 统计卡片 */}
          {state.user && (
            <div className="px-4 md:px-8 -mt-4">
              <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-2xl shadow-sm p-4 md:p-5">
                  <div className="grid grid-cols-4 gap-2 md:gap-4">
                    <div className="text-center">
                      <div className="text-2xl md:text-3xl font-bold text-primary">{stats.petCount}</div>
                      <div className="text-xs md:text-sm text-gray-500 mt-1">宠物</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl md:text-3xl font-bold text-primary">{state.favorites.length}</div>
                      <div className="text-xs md:text-sm text-gray-500 mt-1">收藏</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl md:text-3xl font-bold text-primary">{stats.scheduleCount}</div>
                      <div className="text-xs md:text-sm text-gray-500 mt-1">提醒</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl md:text-3xl font-bold text-primary">{stats.reviewCount}</div>
                      <div className="text-xs md:text-sm text-gray-500 mt-1">评论</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 快捷功能 */}
          {state.user && (
            <div className="px-4 md:px-8 mt-4 md:mt-6">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-base md:text-lg font-semibold text-gray-900 mb-3">⚡ 快捷功能</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3">
                  {quickActions.map((item, i) => (
                    <div
                      key={item.label}
                      onClick={() => handleItemClick(item)}
                      className="bg-white rounded-xl p-3 md:p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                    >
                      <div className="text-2xl md:text-3xl mb-2">{item.icon}</div>
                      <div className="text-sm md:text-base font-medium text-gray-900">{item.label}</div>
                      <div className="text-xs text-gray-400 mt-1 hidden md:block">{item.desc}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 菜单列表 */}
          <div className="px-4 md:px-8 mt-4 md:mt-6">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-base md:text-lg font-semibold text-gray-900 mb-3">📋 其他</h2>
              <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
                {menuItems.map((item, i) => (
                  <div
                    key={item.label}
                    onClick={() => handleItemClick(item)}
                    className={`flex items-center justify-between px-4 md:px-6 py-4 md:py-5 hover:bg-gray-50 cursor-pointer transition-colors ${
                      i < menuItems.length - 1 ? 'border-b border-gray-50' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3 md:gap-4">
                      <span className="text-xl md:text-2xl">{item.icon}</span>
                      <span className="text-sm md:text-base text-gray-900">{item.label}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {item.count !== null && (
                        <span className="text-sm text-gray-400">{item.count}</span>
                      )}
                      <span className="text-gray-300">→</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 关于宠物宝 */}
          <div className="px-4 md:px-8 mt-6 md:mt-8">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
                <h2 className="font-semibold text-gray-900 mb-2 md:mb-3">📊 关于宠物宝</h2>
                <p className="text-sm md:text-base text-gray-500 leading-relaxed">
                  宠物宝是宠物版的"美丽修行"，帮助宠物主查询宠物药品、食品、保健品的成分和安全评分。
                  目前已收录 15 个品牌、16 款产品、31 种成分、24 个品种。
                </p>
                <p className="text-xs md:text-sm text-gray-400 mt-3 md:mt-4">版本 1.0.0 · Made with ❤️</p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <HealthTracker pets={pets} petsLoading={petsLoading} embed />
      )}

      {/* 我的评论弹窗 */}
      {showReviews && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 modal-overlay" onClick={() => setShowReviews(false)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-xl max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-gray-900 mb-4">💬 我的评论</h2>
            {myReviews.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">📝</div>
                <p className="text-gray-500 text-sm">还没有评论</p>
              </div>
            ) : (
              <div className="space-y-3">
                {myReviews.map(r => (
                  <div key={r.id} className="border border-gray-100 rounded-xl p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">{r.product_name}</span>
                      <span className="text-xs text-gray-400">{r.created_at?.split('T')[0]}</span>
                    </div>
                    <div className="flex items-center gap-1 mb-1">
                      {[1,2,3,4,5].map(s => (
                        <span key={s} className="text-sm">{s <= r.rating ? '⭐' : '☆'}</span>
                      ))}
                    </div>
                    {r.content && <p className="text-sm text-gray-600">{r.content}</p>}
                  </div>
                ))}
              </div>
            )}
            <button onClick={() => setShowReviews(false)} className="w-full text-center text-sm text-gray-400 mt-4">
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
