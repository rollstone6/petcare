import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/search', label: '搜索', icon: '🔍' },
  { path: '/breeds', label: '品种百科', icon: '🐾' },
  { path: '/profile', label: '个人中心', icon: '👤' },
]

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [keyboardHeight, setKeyboardHeight] = useState(0)

  // 虚拟键盘适配：监听 visualViewport 变化
  useEffect(() => {
    const viewport = window.visualViewport
    if (!viewport) return

    const handleResize = () => {
      const heightDiff = window.innerHeight - viewport.height - viewport.offsetTop
      setKeyboardHeight(Math.max(0, heightDiff))
    }

    viewport.addEventListener('resize', handleResize)
    viewport.addEventListener('scroll', handleResize)
    return () => {
      viewport.removeEventListener('resize', handleResize)
      viewport.removeEventListener('scroll', handleResize)
    }
  }, [])

  const isActive = (tab) =>
    location.pathname === tab.path ||
    (tab.path !== '/' && location.pathname.startsWith(tab.path))

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* 桌面端侧边栏 */}
      <aside className="hidden md:flex md:flex-col md:w-56 md:min-h-screen md:bg-white md:border-r md:border-gray-200 md:flex-shrink-0 md:fixed md:top-0 md:left-0 md:bottom-0 md:z-40">
        <div className="p-5 border-b border-gray-100">
          <h1 className="text-lg font-bold text-primary">🐾 宠物宝</h1>
          <p className="text-xs text-gray-400 mt-1">PetCare</p>
        </div>
        <nav className="flex-1 py-3 overflow-y-auto">
          {tabs.map(tab => {
            const active = isActive(tab)
            return (
              <button key={tab.path} onClick={() => navigate(tab.path)}
                className={`w-full flex items-center gap-3 px-5 py-3 text-sm transition-colors ${
                  active
                    ? 'bg-primary/5 text-primary font-medium border-r-2 border-primary'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
        <div className="p-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">宠物药品/食品成分查询平台</p>
          <p className="text-xs text-gray-300 mt-1">v1.0.0</p>
        </div>
      </aside>

      {/* 手机端顶部导航栏 */}
      <header className="md:hidden sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-4 h-12">
          <h1 className="text-base font-bold text-primary">🐾 宠物宝</h1>
          <span className="text-[10px] text-gray-400">PetCare</span>
        </div>
      </header>

      {/* 主内容区 */}
      <main
        className="flex-1 md:ml-56 pb-20 md:pb-0"
      >
        <div className="max-w-4xl mx-auto">
          <Outlet />
        </div>
      </main>

      {/* 手机端底部导航 */}
      <nav
        className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 transition-transform duration-200"
        style={{
          paddingBottom: 'env(safe-area-inset-bottom, 0px)',
          transform: `translateY(-${keyboardHeight}px)`,
        }}
      >
        <div className="flex justify-around items-center h-14">
          {tabs.map(tab => {
            const active = isActive(tab)
            return (
              <button
                key={tab.path}
                onClick={() => navigate(tab.path)}
                className={`flex flex-col items-center justify-center flex-1 h-full min-w-0 transition-colors ${
                  active ? 'text-primary' : 'text-gray-400'
                }`}
              >
                <span className="text-lg leading-none">{tab.icon}</span>
                <span className={`text-[10px] mt-0.5 leading-tight truncate max-w-full px-0.5 ${
                  active ? 'font-medium' : ''
                }`}>
                  {tab.label}
                </span>
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
