import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { getToken } from '../api/client'

const SEVERITY_STYLES = {
  high: {
    bg: 'bg-red-50 border-red-300',
    icon: '🚨',
    title: '严重警告',
    text: 'text-red-800',
    badge: 'bg-red-600 text-white',
  },
  medium: {
    bg: 'bg-amber-50 border-amber-300',
    icon: '⚠️',
    title: '注意事项',
    text: 'text-amber-800',
    badge: 'bg-amber-600 text-white',
  },
  low: {
    bg: 'bg-blue-50 border-blue-300',
    icon: '💡',
    title: '温馨提示',
    text: 'text-blue-800',
    badge: 'bg-blue-600 text-white',
  },
  info: {
    bg: 'bg-green-50 border-green-300',
    icon: '✨',
    title: '推荐匹配',
    text: 'text-green-800',
    badge: 'bg-green-600 text-white',
  },
}

export default function HealthWarningBanner({ productId }) {
  const [warnings, setWarnings] = useState([])
  const [loading, setLoading] = useState(true)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    api.checkProductWarnings(productId)
      .then(data => {
        setWarnings(data.warnings || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [productId])

  if (loading || warnings.length === 0 || dismissed) return null

  // 按严重程度分组
  const highWarnings = warnings.filter(w => w.severity === 'high')
  const mediumWarnings = warnings.filter(w => w.severity === 'medium')
  const otherWarnings = warnings.filter(w => w.severity === 'low' || w.severity === 'info')

  return (
    <div className="space-y-2 mb-4">
      {/* 高严重度警告 */}
      {highWarnings.map((w, i) => (
        <WarningCard key={`high-${i}`} warning={w} severity="high" onDismiss={highWarnings.length === 1 && mediumWarnings.length === 0 && otherWarnings.length === 0 ? () => setDismissed(true) : null} />
      ))}
      {/* 中严重度警告 */}
      {mediumWarnings.map((w, i) => (
        <WarningCard key={`medium-${i}`} warning={w} severity="medium" />
      ))}
      {/* 低严重度/信息 */}
      {otherWarnings.map((w, i) => (
        <WarningCard key={`other-${i}`} warning={w} severity={w.severity} />
      ))}
    </div>
  )
}

function WarningCard({ warning, severity, onDismiss }) {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.medium
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`${style.bg} border rounded-xl p-3 animate-slideDown`}>
      <div className="flex items-start gap-2">
        <span className="text-lg flex-shrink-0 mt-0.5">{style.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.badge}`}>
              {style.title}
            </span>
            <span className={`text-xs ${style.text} opacity-70`}>
              🐾 {warning.pet_name}
            </span>
          </div>
          <p className={`text-sm ${style.text} leading-relaxed`}>
            {warning.message}
          </p>
          {warning.matched_tag_labels && warning.matched_tag_labels.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {warning.matched_tag_labels.map(label => (
                <span key={label} className={`text-[10px] px-1.5 py-0.5 rounded ${style.bg} ${style.text} border`}>
                  {label}
                </span>
              ))}
            </div>
          )}
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className={`${style.text} opacity-50 hover:opacity-100 text-sm flex-shrink-0`}>
            ✕
          </button>
        )}
      </div>
    </div>
  )
}
