import { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { useApp } from '../context/AppContext'
import { api } from '../api/client'
import { getToken } from '../api/client'

// ===== 常量 =====
const TYPE_ICONS = { '便便': '💩', '饮水': '💧', '呕吐': '🤮', '体重': '⚖️', '食欲': '🍖', '精神': '😊', '用药': '💊', '其他': '📝' }
const TYPE_COLORS = { '便便': 'bg-amber-100 text-amber-700', '饮水': 'bg-blue-100 text-blue-700', '呕吐': 'bg-red-100 text-red-700', '体重': 'bg-purple-100 text-purple-700', '食欲': 'bg-green-100 text-green-700', '精神': 'bg-yellow-100 text-yellow-700', '用药': 'bg-indigo-100 text-indigo-700', '其他': 'bg-gray-100 text-gray-700' }
const SEVERITY_BADGE = { 'normal': '', 'warning': '⚠️', 'danger': '🚨' }

const STATUS_COLORS = {
  overdue: { bg: 'bg-red-500', text: 'text-red-600', label: '已过期' },
  urgent: { bg: 'bg-orange-500', text: 'text-orange-600', label: '紧急' },
  warning: { bg: 'bg-yellow-500', text: 'text-yellow-600', label: '临近' },
  normal: { bg: 'bg-green-500', text: 'text-green-600', label: '正常' },
}
const SCHEDULE_ICONS = { '体外驱虫': '🦟', '体内驱虫': '💊', '疫苗': '💉', '体检': '🩺' }

// ===== 宠物选择器组件 =====
function PetSelector({ pets, value, onChange, label = '选择宠物' }) {
  if (pets.length === 0) {
    return (
      <div className="mb-3">
        <label className="text-xs text-gray-500 mb-1 block">{label}</label>
        <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-400">
          暂无宠物，请先去个人中心添加
        </div>
      </div>
    )
  }
  return (
    <div className="mb-3">
      <label className="text-xs text-gray-500 mb-1 block">{label}</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary bg-white"
      >
        <option value="">全部宠物</option>
        {pets.map(p => (
          <option key={p.id} value={p.pet_name}>
            {p.breed?.species === '猫' ? '🐱' : '🐶'} {p.pet_name}
            {p.breed ? ` (${p.breed.name})` : ''}
          </option>
        ))}
      </select>
    </div>
  )
}

// 表单里用的宠物选择器（必选，有默认值）
function PetPicker({ pets, value, onChange }) {
  if (pets.length === 0) {
    return (
      <div className="mb-4">
        <label className="text-xs text-gray-500 mb-1 block">选择宠物</label>
        <div className="px-4 py-2.5 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700">
          ⚠️ 请先去个人中心 → 品种档案 添加宠物
        </div>
      </div>
    )
  }
  return (
    <div className="mb-4">
      <label className="text-xs text-gray-500 mb-1 block">选择宠物</label>
      <div className="flex gap-2 flex-wrap">
        {pets.map(p => (
          <button key={p.id} onClick={() => onChange(p.pet_name)}
            className={`px-3 py-2 rounded-xl text-sm transition-all flex items-center gap-1.5 ${
              value === p.pet_name
                ? 'bg-primary text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>{p.breed?.species === '猫' ? '🐱' : '🐶'}</span>
            <span className="font-medium">{p.pet_name}</span>
            {p.breed && <span className="text-xs opacity-70">({p.breed.name})</span>}
          </button>
        ))}
      </div>
    </div>
  )
}

// ===== 倒计时圆环 =====
function CountdownCircle({ daysLeft, status }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS.normal
  const isOverdue = status === 'overdue'
  return (
    <div className="relative w-16 h-16 flex-shrink-0">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle cx="50" cy="50" r="42" fill="none"
          stroke={isOverdue ? '#ef4444' : daysLeft <= 3 ? '#f97316' : daysLeft <= 7 ? '#eab308' : '#22c55e'}
          strokeWidth="8" strokeLinecap="round"
          strokeDasharray={`${2 * Math.PI * 42}`}
          strokeDashoffset={`${2 * Math.PI * 42 * (1 - Math.min((daysLeft || 0) / 30, 1))}`}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-base font-bold ${c.text}`}>
          {isOverdue ? `+${Math.abs(daysLeft)}` : daysLeft ?? '--'}
        </span>
        <span className="text-[9px] text-gray-400">{isOverdue ? '天超' : '天后'}</span>
      </div>
    </div>
  )
}

// ===== 健康日记 Tab =====
function HealthTab({ state, pets }) {
  const [records, setRecords] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [filter, setFilter] = useState('')
  const [petFilter, setPetFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchRecords = useCallback(async () => {
    if (!state.user) { setLoading(false); return }
    try {
      const params = new URLSearchParams({ page_size: '100' })
      if (filter) params.set('record_type', filter)
      if (petFilter) params.set('pet_name', petFilter)
      const res = await fetch(`/api/records?${params}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      })
      const data = await res.json()
      if (data.code === 0) setRecords(data.data.items || [])
    } catch (e) { console.error(e) }
    setLoading(false)
  }, [state.user, filter, petFilter])

  useEffect(() => { fetchRecords() }, [fetchRecords])

  const grouped = {}
  records.forEach(r => {
    const date = r.recorded_at?.split('T')[0] || '未知'
    if (!grouped[date]) grouped[date] = []
    grouped[date].push(r)
  })

  return (
    <div>
      {/* 宠物筛选 + 类型筛选 */}
      <div className="space-y-2 pb-3">
        {pets.length > 1 && (
          <div className="flex gap-2 overflow-x-auto scrollbar-hide">
            <button onClick={() => setPetFilter('')}
              className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                !petFilter ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
              }`}>
              🐾 全部
            </button>
            {pets.map(p => (
              <button key={p.id} onClick={() => setPetFilter(p.pet_name)}
                className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                  petFilter === p.pet_name ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
                }`}>
                {p.breed?.species === '猫' ? '🐱' : '🐶'} {p.pet_name}
              </button>
            ))}
          </div>
        )}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide">
          {['', '便便', '饮水', '呕吐', '体重', '食欲', '用药'].map(t => (
            <button key={t || '全部'} onClick={() => setFilter(t)}
              className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                filter === t ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'
              }`}
            >
              {t ? `${TYPE_ICONS[t]} ${t}` : '📋 全部'}
            </button>
          ))}
        </div>
      </div>

      {/* 时间线 */}
      {loading ? (
        <div className="text-center py-10 text-gray-400">加载中...</div>
      ) : Object.keys(grouped).length === 0 ? (
        <div className="text-center py-10">
          <div className="text-5xl mb-3">📋</div>
          <p className="text-gray-400">{petFilter ? `${petFilter} 还没有记录` : '还没有记录'}</p>
          <p className="text-sm text-gray-300 mt-1">点击右下角按钮开始记录</p>
        </div>
      ) : (
        <div className="relative pl-6 border-l-2 border-gray-100 mt-2">
          {Object.entries(grouped).map(([date, items]) => (
            <div key={date} className="mb-6 relative">
              <div className="absolute -left-[29px] top-0 w-4 h-4 rounded-full bg-primary border-2 border-white" />
              <div className="text-xs text-gray-400 mb-2 ml-2">{date}</div>
              <div className="space-y-2">
                {items.map(r => (
                  <div key={r.id} className="bg-white rounded-xl p-3 shadow-sm border border-gray-50 ml-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${TYPE_COLORS[r.record_type] || 'bg-gray-100'}`}>
                        {TYPE_ICONS[r.record_type]} {r.record_type}
                      </span>
                      <span className="text-xs text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded">
                        {r.pet_name}
                      </span>
                      {r.severity !== 'normal' && (
                        <span className="text-xs">{SEVERITY_BADGE[r.severity]}</span>
                      )}
                      <span className="text-xs text-gray-300 ml-auto">
                        {r.recorded_at?.split('T')[1]?.substring(0, 5) || ''}
                      </span>
                    </div>
                    {r.record_type === '便便' && (r.poop_color || r.poop_shape) && (
                      <div className="mt-1.5 flex gap-2 text-xs text-gray-500">
                        {r.poop_color && <span>🟤 {r.poop_color}</span>}
                        {r.poop_shape && <span>· {r.poop_shape}</span>}
                      </div>
                    )}
                    {r.record_type === '饮水' && r.value && (
                      <div className="mt-1.5 text-xs text-blue-600">{r.value}ml</div>
                    )}
                    {r.record_type === '呕吐' && r.vomit_type && (
                      <div className="mt-1.5 text-xs text-red-500">{r.vomit_type}</div>
                    )}
                    {r.value && !['饮水'].includes(r.record_type) && (
                      <div className="mt-1.5 text-xs text-gray-600">{r.value}</div>
                    )}
                    {r.note && (
                      <div className="mt-1.5 text-xs text-gray-500">{r.note}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* FAB */}
      <button
        onClick={() => {
          if (pets.length === 0) {
            alert('请先去个人中心 → 品种档案添加宠物')
            return
          }
          setShowForm(true)
        }}
        className="fixed bottom-24 md:bottom-8 right-4 md:right-8 w-14 h-14 bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg shadow-primary/30 flex items-center justify-center text-2xl z-40 active:scale-95 transition-all"
      >
        ＋
      </button>

      {showForm && <RecordForm pets={pets} onClose={() => setShowForm(false)} onSaved={fetchRecords} />}
    </div>
  )
}

// ===== 记录表单 =====
function RecordForm({ pets, onClose, onSaved }) {
  const [petName, setPetName] = useState(pets[0]?.pet_name || '')
  const [type, setType] = useState('便便')
  const [note, setNote] = useState('')
  const [value, setValue] = useState('')
  const [poopColor, setPoopColor] = useState('')
  const [poopShape, setPoopShape] = useState('')
  const [vomitType, setVomitType] = useState('')
  const [severity, setSeverity] = useState('normal')
  const [saving, setSaving] = useState(false)
  const recordTypes = ['便便', '饮水', '呕吐', '体重', '食欲', '精神', '用药']

  const handleSubmit = async () => {
    if (!petName) { alert('请选择宠物'); return }
    setSaving(true)
    try {
      const res = await fetch('/api/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` },
        body: JSON.stringify({
          pet_name: petName, record_type: type, note, value,
          poop_color: poopColor, poop_shape: poopShape, vomit_type: vomitType, severity,
        }),
      })
      const data = await res.json()
      if (data.code === 0) { onSaved(); onClose() }
    } catch (e) { console.error(e) }
    setSaving(false)
  }

  return createPortal(
    <div className="fixed inset-0 z-[60] flex items-end justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div className="relative bg-white rounded-t-3xl w-full max-w-md p-6 pb-20 animate-fadeIn max-h-[90vh] overflow-y-auto safe-bottom" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">新建记录</h2>
          <button onClick={onClose} className="text-gray-400 text-lg">✕</button>
        </div>

        {/* 宠物选择 */}
        <PetPicker pets={pets} value={petName} onChange={setPetName} />

        {/* 类型选择 */}
        <div className="flex gap-2 mb-4 flex-wrap">
          {recordTypes.map(t => (
            <button key={t} onClick={() => setType(t)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${type === t ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'}`}
            >{TYPE_ICONS[t]} {t}</button>
          ))}
        </div>
        {type === '便便' && (
          <div className="space-y-3 mb-3">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">颜色</label>
              <div className="flex gap-2 flex-wrap">
                {['棕色', '黑色', '红色', '绿色', '黄色', '白色'].map(c => (
                  <button key={c} onClick={() => setPoopColor(c)}
                    className={`px-3 py-1 rounded-full text-xs ${poopColor === c ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-600'}`}>{c}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">形状</label>
              <div className="flex gap-2 flex-wrap">
                {['正常', '软便', '稀便', '硬便', '带血'].map(s => (
                  <button key={s} onClick={() => setPoopShape(s)}
                    className={`px-3 py-1 rounded-full text-xs ${poopShape === s ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-600'}`}>{s}</button>
                ))}
              </div>
            </div>
          </div>
        )}
        {type === '饮水' && (
          <div className="mb-3">
            <label className="text-xs text-gray-500 mb-1 block">饮水量 (ml)</label>
            <input type="number" value={value} onChange={e => setValue(e.target.value)}
              placeholder="如: 500" className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary" />
          </div>
        )}
        {type === '呕吐' && (
          <div className="mb-3">
            <label className="text-xs text-gray-500 mb-1 block">呕吐物</label>
            <div className="flex gap-2 flex-wrap">
              {['食物', '黄水', '白沫', '血丝', '异物'].map(v => (
                <button key={v} onClick={() => setVomitType(v)}
                  className={`px-3 py-1 rounded-full text-xs ${vomitType === v ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600'}`}>{v}</button>
              ))}
            </div>
          </div>
        )}
        {['呕吐', '便便', '精神', '食欲'].includes(type) && (
          <div className="mb-3">
            <label className="text-xs text-gray-500 mb-1 block">严重程度</label>
            <div className="flex gap-2">
              {[{ v: 'normal', l: '🟢 正常' }, { v: 'warning', l: '🟡 注意' }, { v: 'danger', l: '🔴 严重' }].map(s => (
                <button key={s.v} onClick={() => setSeverity(s.v)}
                  className={`px-3 py-1 rounded-full text-xs ${severity === s.v ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600'}`}>{s.l}</button>
              ))}
            </div>
          </div>
        )}
        <div className="mb-4">
          <textarea value={note} onChange={e => setNote(e.target.value)}
            placeholder="补充说明..." rows={2}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary resize-none" />
        </div>
        <button onClick={handleSubmit} disabled={saving || !petName}
          className="w-full bg-primary text-white py-3 rounded-xl font-medium text-sm disabled:opacity-50">
          {saving ? '保存中...' : `✅ 保存${petName ? `到 ${petName}` : '记录'}`}
        </button>
      </div>
    </div>,
    document.body
  )
}

// ===== 日程提醒 Tab =====
function ScheduleTab({ pets }) {
  const [schedules, setSchedules] = useState([])
  const [presets, setPresets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [actionId, setActionId] = useState(null)
  const [petFilter, setPetFilter] = useState('')
  const loggedIn = !!getToken()

  const loadData = () => {
    if (!loggedIn) { setLoading(false); return }
    Promise.all([api.getSchedules(), api.getSchedulePresets()])
      .then(([sData, pData]) => { setSchedules(sData.items || []); setPresets(pData || []) })
      .catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(() => { loadData() }, [])

  const handleMarkDone = async (id) => {
    setActionId(id)
    try { await api.markScheduleDone(id); loadData() } catch (e) { alert(e.message) }
    finally { setActionId(null) }
  }
  const handleDelete = async (id) => {
    if (!confirm('确定删除这个日程吗？')) return
    setActionId(id)
    try { await api.deleteSchedule(id); loadData() } catch (e) { alert(e.message) }
    finally { setActionId(null) }
  }
  const handleAdd = async (data) => {
    setShowAdd(false)
    try { await api.createSchedule(data); loadData() } catch (e) { alert(e.message) }
  }

  // 按宠物筛选
  const filteredSchedules = petFilter
    ? schedules.filter(s => s.pet_name === petFilter)
    : schedules

  if (loading) {
    return (
      <div className="space-y-3 mt-3">
        {[1,2,3].map(i => <div key={i} className="h-24 bg-white rounded-2xl animate-pulse" />)}
      </div>
    )
  }

  return (
    <div className="mt-3">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-400">驱虫·疫苗·体检提醒</p>
        <button onClick={() => {
          if (pets.length === 0) {
            alert('请先去个人中心 → 品种档案添加宠物')
            return
          }
          setShowAdd(true)
        }}
          className="px-4 py-1.5 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors">
          + 添加
        </button>
      </div>

      {/* 宠物筛选 */}
      {pets.length > 1 && (
        <div className="flex gap-2 overflow-x-auto scrollbar-hide mb-3">
          <button onClick={() => setPetFilter('')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
              !petFilter ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
            }`}>
            🐾 全部
          </button>
          {pets.map(p => (
            <button key={p.id} onClick={() => setPetFilter(p.pet_name)}
              className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                petFilter === p.pet_name ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
              }`}>
              {p.breed?.species === '猫' ? '🐱' : '🐶'} {p.pet_name}
            </button>
          ))}
        </div>
      )}

      {filteredSchedules.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-5xl mb-3">📋</p>
          <p className="text-gray-400 mb-2">{petFilter ? `${petFilter} 还没有日程提醒` : '还没有日程提醒'}</p>
          <p className="text-sm text-gray-300 mb-4">添加宠物后会自动生成智能提醒</p>
          
          {/* 年龄适配提醒建议 */}
          {pets.length > 0 && (
            <div className="mt-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-4 text-left">
              <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
                <span>🎯</span>
                <span>根据宠物年龄推荐的提醒</span>
              </h4>
              <div className="space-y-2">
                {pets.slice(0, 3).map(pet => {
                  const ageCategory = pet.age_category || '成年'
                  const species = pet.breed?.species === '猫' ? '🐱' : '🐶'
                  
                  // 根据年龄分类显示不同的提醒建议
                  const recommendations = {
                    '幼崽': [
                      { icon: '💉', text: '疫苗（每2-4周一次）', color: 'text-pink-600' },
                      { icon: '🦟', text: '体外驱虫（每月）', color: 'text-pink-600' },
                      { icon: '💊', text: '体内驱虫（每2周）', color: 'text-pink-600' },
                    ],
                    '幼年': [
                      { icon: '💉', text: '疫苗加强针', color: 'text-blue-600' },
                      { icon: '🦟', text: '体外驱虫（每月）', color: 'text-blue-600' },
                      { icon: '💊', text: '体内驱虫（每月→每3月）', color: 'text-blue-600' },
                    ],
                    '成年': [
                      { icon: '💉', text: '疫苗（每年）', color: 'text-green-600' },
                      { icon: '🦟', text: '体外驱虫（每月）', color: 'text-green-600' },
                      { icon: '💊', text: '体内驱虫（每3月）', color: 'text-green-600' },
                      { icon: '🩺', text: '体检（每半年）', color: 'text-green-600' },
                    ],
                    '老年': [
                      { icon: '💉', text: '疫苗（根据抗体水平）', color: 'text-purple-600' },
                      { icon: '🦟', text: '体外驱虫（每月）', color: 'text-purple-600' },
                      { icon: '💊', text: '体内驱虫（每3月）', color: 'text-purple-600' },
                      { icon: '🩺', text: '体检（每3月）', color: 'text-purple-600' },
                      { icon: '🦷', text: '牙齿检查（每半年）', color: 'text-purple-600' },
                    ],
                  }
                  
                  const recs = recommendations[ageCategory] || recommendations['成年']
                  
                  return (
                    <div key={pet.id} className="bg-white rounded-xl p-3 shadow-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <span>{species}</span>
                        <span className="font-medium text-sm">{pet.pet_name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          ageCategory === '幼崽' ? 'bg-pink-100 text-pink-600' :
                          ageCategory === '幼年' ? 'bg-blue-100 text-blue-600' :
                          ageCategory === '成年' ? 'bg-green-100 text-green-600' :
                          'bg-purple-100 text-purple-600'
                        }`}>
                          {ageCategory}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-1.5">
                        {recs.map((rec, idx) => (
                          <div key={idx} className={`text-xs flex items-center gap-1 ${rec.color}`}>
                            <span>{rec.icon}</span>
                            <span>{rec.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
              <p className="text-xs text-gray-500 mt-3">
                💡 添加宠物时设置生日，系统会自动生成适合的提醒
              </p>
            </div>
          )}
          
          <button onClick={() => setShowAdd(true)}
            className="px-6 py-2.5 bg-primary text-white rounded-xl text-sm font-medium mt-4">
            添加第一个日程
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSchedules.map(s => {
            const c = STATUS_COLORS[s.status] || STATUS_COLORS.normal
            const icon = SCHEDULE_ICONS[s.schedule_type] || '📅'
            const isActive = actionId === s.id
            const pet = pets.find(p => p.pet_name === s.pet_name)
            const ageCategory = pet?.age_category
            return (
              <div key={s.id}
                className={`bg-white rounded-2xl p-3 shadow-sm border transition-all ${
                  s.status === 'overdue' ? 'border-red-200 ring-2 ring-red-100' :
                  s.status === 'urgent' ? 'border-orange-200 ring-2 ring-orange-100' :
                  s.status === 'warning' ? 'border-yellow-200 ring-1 ring-yellow-100' :
                  'border-gray-100'
                }`}>
                <div className="flex items-center gap-3">
                  <CountdownCircle daysLeft={s.days_left} status={s.status} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-base">{icon}</span>
                      <span className="font-semibold text-sm">{s.title}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.bg} text-white`}>{c.label}</span>
                    </div>
                    <p className="text-xs text-gray-400">
                      <span className="inline-flex items-center gap-0.5">
                        {pet?.breed?.species === '猫' ? '🐱' : '🐶'} {s.pet_name}
                        {pet?.breed ? ` (${pet.breed.name})` : ''}
                        {ageCategory && (
                          <span className={`ml-1 px-1.5 py-0.5 rounded text-xs ${
                            ageCategory === '幼崽' ? 'bg-pink-100 text-pink-600' :
                            ageCategory === '幼年' ? 'bg-blue-100 text-blue-600' :
                            ageCategory === '成年' ? 'bg-green-100 text-green-600' :
                            'bg-purple-100 text-purple-600'
                          }`}>
                            {ageCategory}
                          </span>
                        )}
                      </span>
                      {' · '}每{s.interval_days}天 · 上次: {s.last_done_at ? new Date(s.last_done_at).toLocaleDateString('zh-CN') : '未记录'}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3 pt-3 border-t border-gray-50">
                  <button onClick={() => handleMarkDone(s.id)} disabled={isActive}
                    className="flex-1 py-2 text-sm bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
                    {isActive ? '处理中...' : '✅ 标记完成'}
                  </button>
                  <button onClick={() => handleDelete(s.id)} disabled={isActive}
                    className="py-2 px-3 text-sm border border-gray-200 rounded-xl text-gray-400 hover:text-red-500 hover:border-red-200 transition-colors disabled:opacity-50">
                    🗑
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {filteredSchedules.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 rounded-xl">
          <p className="text-xs text-blue-700 leading-relaxed">
            💡 点击「标记完成」后倒计时自动重置
          </p>
        </div>
      )}

      {showAdd && <AddScheduleModal pets={pets} presets={presets} onClose={() => setShowAdd(false)} onAdd={handleAdd} />}
    </div>
  )
}

// ===== 添加日程弹窗 =====
function AddScheduleModal({ pets, presets, onClose, onAdd }) {
  const [selected, setSelected] = useState(null)
  const [petName, setPetName] = useState(pets[0]?.pet_name || '')

  if (selected) {
    const p = presets.find(x => x.type === selected)
    return createPortal(
      <div className="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center p-4" onClick={onClose}>
        <div className="bg-white rounded-2xl w-full max-w-sm p-6 pb-20 animate-slideUp safe-bottom" onClick={e => e.stopPropagation()}>
          <h3 className="text-lg font-bold mb-4">确认添加</h3>
          <div className="space-y-3 mb-6">
            {/* 宠物选择 */}
            <PetPicker pets={pets} value={petName} onChange={setPetName} />
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
              <span className="text-2xl">{p.icon}</span>
              <div>
                <p className="font-medium text-sm">{p.title}</p>
                <p className="text-xs text-gray-400">每 {p.interval_days} 天 · {p.note}</p>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setSelected(null)}
              className="flex-1 py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl">返回</button>
            <button onClick={() => onAdd({ schedule_type: selected, pet_name: petName })}
              disabled={!petName}
              className="flex-1 py-2.5 text-sm bg-primary text-white rounded-xl font-medium disabled:opacity-50">确认添加</button>
          </div>
        </div>
      </div>,
      document.body
    )
  }

  return createPortal(
    <div className="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-sm p-6 pb-20 animate-slideUp safe-bottom" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">添加日程提醒</h3>
        <div className="space-y-2">
          {presets.map(p => (
            <button key={p.type} onClick={() => setSelected(p.type)}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors text-left">
              <span className="text-2xl">{p.icon}</span>
              <div className="flex-1">
                <p className="font-medium text-sm">{p.title}</p>
                <p className="text-xs text-gray-400">每 {p.interval_days} 天 · {p.note}</p>
              </div>
              <span className="text-gray-300">→</span>
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  )
}

// ===== 主页面 =====
export default function HealthTracker() {
  const { state } = useApp()
  const [tab, setTab] = useState('health') // health | schedule
  const [pets, setPets] = useState([])
  const [petsLoading, setPetsLoading] = useState(true)
  const loggedIn = !!state.user

  // 加载宠物档案
  useEffect(() => {
    if (state.user) {
      api.getPets()
        .then(data => setPets(data.items || []))
        .catch(() => {})
        .finally(() => setPetsLoading(false))
    } else {
      setPetsLoading(false)
    }
  }, [state.user])

  if (!loggedIn) {
    return (
      <div className="animate-fadeIn flex flex-col items-center justify-center py-20 px-4">
        <div className="text-6xl mb-4">🐾</div>
        <h2 className="text-lg font-semibold text-gray-700 mb-2">登录后记录宠物日常</h2>
        <p className="text-sm text-gray-400 text-center">记录便便、饮水、呕吐等，掌握宠物健康状况</p>
      </div>
    )
  }

  if (petsLoading) {
    return (
      <div className="animate-fadeIn px-4 py-8">
        <div className="max-w-2xl mx-auto space-y-4 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3" />
          <div className="h-12 bg-gray-200 rounded-xl" />
          <div className="h-40 bg-gray-200 rounded-2xl" />
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn pb-20">
      {/* 顶部 */}
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-8 pb-4 sticky top-0 z-30 shadow-sm">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">🏥 家庭管家</h1>
          <p className="text-sm text-gray-500 mt-1">健康记录 + 日程提醒</p>
          {/* Tab 切换 */}
          <div className="flex gap-1 mt-3 bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setTab('health')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                tab === 'health' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'
              }`}
            >
              📋 健康日记
            </button>
            <button
              onClick={() => setTab('schedule')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                tab === 'schedule' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'
              }`}
            >
              📅 日程提醒
            </button>
          </div>
        </div>
      </div>

      {/* 内容区 */}
      <div className="px-4 md:px-8 mt-4">
        <div className="max-w-2xl mx-auto">
          {tab === 'health'
            ? <HealthTab state={state} pets={pets} />
            : <ScheduleTab pets={pets} />
          }
        </div>
      </div>
    </div>
  )
}
