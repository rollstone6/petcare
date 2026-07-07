import { useState, useMemo } from 'react'

// 品类图标映射
const categoryIcons = {
  // 药品
  '驱虫药': '🪱', '体内外同驱': '🪱', '体内驱虫': '💊', '体外驱虫': '🧴',
  '疫苗': '💉', '犬用疫苗': '💉', '猫用疫苗': '💉',
  '皮肤病药': '🧴', '皮肤真菌药': '🧴', '药浴护理': '🛁',
  '抗生素': '💊', '消炎止痛': '💊',
  '心脏/肾脏用药': '❤️', '心脏肾脏': '❤️',
  '眼耳用药': '👁️', '眼部用药': '👁️', '耳部用药': '👂',
  '消化系统用药': '🫁', '肠胃调理': '🫁', '止泻药': '🫁', '止吐药': '🫁',
  '泌尿系统': '🫘',
  '口腔护理': '🦷',
  '感冒呼吸道': '🤧',
  '肝胆保健': '🫁',
  '癫痫神经': '🧠',
  '猫鼻支': '🐱',
  '益生菌类': '🦠',
  '护理用品': '🧹',
  // 食品
  '猫粮': '🐱', '猫干粮': '🐱',
  '狗粮': '🐶', '狗干粮': '🐶',
  '猫零食': '🐟', '狗零食': '🦴',
  '处方粮': '🏥', '处方食品': '🏥',
  // 保健品
  '关节保护': '🦴', '健骨补钙': '🦴',
  '营养膏': '🍯', '综合营养': '🌟',
  '益生菌': '🦠', '化毛膏': '🐱',
  '美毛护肤': '✨', '增强免疫': '🛡️',
  '保健用品': '💪',
}

function getIcon(name) {
  return categoryIcons[name] || '📦'
}

// 根据类型获取主题色
const typeColors = {
  '药品': { bg: 'bg-blue-50', active: 'bg-blue-500', border: 'border-blue-200', text: 'text-blue-700' },
  '食品': { bg: 'bg-amber-50', active: 'bg-amber-500', border: 'border-amber-200', text: 'text-amber-700' },
  '保健品': { bg: 'bg-emerald-50', active: 'bg-emerald-500', border: 'border-emerald-200', text: 'text-emerald-700' },
}

export default function CategoryGrid({ categories, activeCategoryId, onCategoryChange }) {
  const [expanded, setExpanded] = useState(false)
  const MAX_VISIBLE = 6

  // 按类型分组排序：药品(蓝) → 食品(黄) → 保健品(绿)，同色聚在一起
  const typeOrder = { '药品': 0, '食品': 1, '保健品': 2 }
  const sorted = useMemo(() =>
    [...categories].sort((a, b) => {
      const ta = typeOrder[a.type] ?? 9
      const tb = typeOrder[b.type] ?? 9
      return ta - tb
    }),
    [categories]
  )

  // 只展示有产品的品类
  const visible = expanded ? sorted : sorted.slice(0, MAX_VISIBLE)
  const hasMore = sorted.length > MAX_VISIBLE

  return (
    <div>
      {/* 标题行 */}
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-gray-400 font-medium">📋 品类筛选</span>
        {activeCategoryId !== null && (
          <button
            onClick={() => onCategoryChange(null)}
            className="text-xs text-gray-400 hover:text-blue-500 transition-colors"
          >
            ✕ 清除品类
          </button>
        )}
      </div>

      {/* 网格布局 */}
      <div className="flex flex-wrap gap-1.5">
        {visible.map(c => {
          const isActive = activeCategoryId === c.id
          const colors = typeColors[c.type] || typeColors['药品']
          return (
            <button
              key={c.id}
              onClick={() => onCategoryChange(c.id)}
              className={`
                inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium
                transition-all duration-200 shrink-0
                ${isActive
                  ? `${colors.active} text-white shadow-sm scale-105`
                  : `${colors.bg} ${colors.text} border ${colors.border} hover:shadow-sm`
                }
              `}
            >
              <span className="text-sm">{getIcon(c.name)}</span>
              <span>{c.name}</span>
              <span className={`
                ml-0.5 px-1.5 py-0 rounded-full text-[10px] leading-tight
                ${isActive ? 'bg-white/25 text-white' : 'bg-white/80 text-gray-500'}
              `}>
                {c.product_count}
              </span>
            </button>
          )
        })}

        {/* 展开/收起 */}
        {hasMore && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs
              bg-gray-50 text-gray-400 border border-gray-200 hover:bg-gray-100 transition-colors shrink-0"
          >
            {expanded ? '收起 ↑' : `+${categories.length - MAX_VISIBLE} 更多 ↓`}
          </button>
        )}
      </div>
    </div>
  )
}
