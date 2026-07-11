import { useState, useEffect, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { Swiper, SwiperSlide } from 'swiper/react'
import { FreeMode, Mousewheel } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/free-mode'
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
function CountdownCircle({ daysLeft, status, size = 'md' }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS.normal
  const isOverdue = status === 'overdue'
  const dim = size === 'sm' ? 'w-12 h-12' : 'w-20 h-20'
  const fontSize = size === 'sm' ? 'text-base' : 'text-lg'
  const labelSize = size === 'sm' ? 'text-[8px]' : 'text-[10px]'
  const strokeW = size === 'sm' ? '6' : '5'
  return (
    <div className={`relative ${dim} flex-shrink-0`}>
      <svg className={`${dim} -rotate-90`} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" strokeWidth={strokeW} />
        <circle cx="50" cy="50" r="42" fill="none"
          stroke={isOverdue ? '#ef4444' : daysLeft <= 3 ? '#f97316' : daysLeft <= 7 ? '#eab308' : '#22c55e'}
          strokeWidth={strokeW} strokeLinecap="round"
          strokeDasharray={`${2 * Math.PI * 42}`}
          strokeDashoffset={`${2 * Math.PI * 42 * (1 - Math.min((daysLeft || 0) / 30, 1))}`}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`${fontSize} font-bold ${c.text} leading-none`}>
          {isOverdue ? `+${Math.abs(daysLeft)}` : daysLeft ?? '--'}
        </span>
        <span className={`${labelSize} text-gray-400 mt-0.5`}>{isOverdue ? '天超' : '天后'}</span>
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
          <Swiper
            modules={[FreeMode, Mousewheel]}
            spaceBetween={8}
            slidesPerView="auto"
            freeMode={true}
            mousewheel={true}
          >
            <SwiperSlide className="!w-auto">
              <button onClick={() => setPetFilter('')}
                className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                  !petFilter ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
                }`}>
                🐾 全部
              </button>
            </SwiperSlide>
            {pets.map(p => (
              <SwiperSlide key={p.id} className="!w-auto">
                <button onClick={() => setPetFilter(p.pet_name)}
                  className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                    petFilter === p.pet_name ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
                  }`}>
                  {p.breed?.species === '猫' ? '🐱' : '🐶'} {p.pet_name}
                </button>
              </SwiperSlide>
            ))}
          </Swiper>
        )}
        <Swiper
          modules={[FreeMode, Mousewheel]}
          spaceBetween={8}
          slidesPerView="auto"
          freeMode={true}
          mousewheel={true}
        >
          {['', '便便', '饮水', '呕吐', '体重', '食欲', '用药'].map(t => (
            <SwiperSlide key={t || '全部'} className="!w-auto">
              <button onClick={() => setFilter(t)}
                className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                  filter === t ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'
                }`}>
                {t ? `${TYPE_ICONS[t]} ${t}` : '📋 全部'}
              </button>
            </SwiperSlide>
          ))}
        </Swiper>
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
    <div className="fixed inset-0 z-[60] flex items-end justify-center modal-overlay" onClick={onClose}>
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
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [toast, setToast] = useState(null)
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
    try {
      await api.markScheduleDone(id)
      loadData()
      // 计算下次提醒日期
      const schedule = schedules.find(s => s.id === id)
      if (schedule) {
        const nextDate = new Date()
        nextDate.setDate(nextDate.getDate() + schedule.interval_days)
        const month = nextDate.getMonth() + 1
        const day = nextDate.getDate()
        setToast(`✅ 已标记完成！下次提醒: ${month}月${day}日`)
        setTimeout(() => setToast(null), 3000)
      }
    } catch (e) { alert(e.message) }
    finally { setActionId(null) }
  }

  const handleUpdate = async (id, data) => {
    setEditingSchedule(null)
    try { await api.updateSchedule(id, data); loadData() } catch (e) { alert(e.message) }
  }

  const handleDelete = async (id) => {
    setActionId(id)
    try { await api.deleteSchedule(id); loadData() } catch (e) { alert(e.message) }
    finally { setActionId(null); setDeleteConfirm(null) }
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
        <Swiper
          modules={[FreeMode, Mousewheel]}
          spaceBetween={8}
          slidesPerView="auto"
          freeMode={true}
          mousewheel={true}
          className="mb-3"
        >
          <SwiperSlide className="!w-auto">
            <button onClick={() => setPetFilter('')}
              className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                !petFilter ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
              }`}>
              🐾 全部
            </button>
          </SwiperSlide>
          {pets.map(p => (
            <SwiperSlide key={p.id} className="!w-auto">
              <button onClick={() => setPetFilter(p.pet_name)}
                className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                  petFilter === p.pet_name ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200'
                }`}>
                {p.breed?.species === '猫' ? '🐱' : '🐶'} {p.pet_name}
              </button>
            </SwiperSlide>
          ))}
        </Swiper>
      )}

      {filteredSchedules.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-5xl mb-3">📋</p>
          <p className="text-gray-400 mb-2">{petFilter ? `${petFilter} 还没有日程提醒` : '还没有日程提醒'}</p>
          <p className="text-sm text-gray-300 mb-4">添加宠物后会自动生成智能提醒</p>
          
          {/* 快速添加入口 */}
          {pets.length > 0 && (
            <div className="mt-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-4">
              <h4 className="font-semibold text-sm mb-3 flex items-center justify-center gap-2">
                <span>⚡</span>
                <span>快速添加提醒</span>
              </h4>
              <div className="grid grid-cols-2 gap-3">
                {presets.slice(0, 4).map(p => (
                  <button key={p.type} onClick={() => handleAdd({ schedule_type: p.type, pet_name: pets[0]?.pet_name })}
                    className="bg-white rounded-xl p-3 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center gap-2">
                    <span className="text-2xl">{p.icon}</span>
                    <span className="text-xs font-medium">{p.title}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <button onClick={() => setShowAdd(true)}
            className="px-6 py-2.5 bg-primary text-white rounded-xl text-sm font-medium mt-4">
            查看更多选项
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {(() => {
            // 按宠物分组
            const grouped = {}
            filteredSchedules.forEach(s => {
              if (!grouped[s.pet_name]) grouped[s.pet_name] = []
              grouped[s.pet_name].push(s)
            })
            return Object.entries(grouped).map(([petName, items]) => {
              const pet = pets.find(p => p.pet_name === petName)
              const speciesIcon = pet?.breed?.species === '猫' ? '🐱' : '🐶'
              return (
                <div key={petName}>
                  {/* 宠物标题行 */}
                  <div className="flex items-center gap-2 mb-2 px-1">
                    <span className="text-base">{speciesIcon}</span>
                    <span className="font-semibold text-sm">{petName}</span>
                    {pet?.breed && <span className="text-xs text-gray-400">({pet.breed.name})</span>}
                    <span className="text-xs text-gray-400 ml-auto">{items.length} 个提醒</span>
                  </div>
                  {/* 该宠物的日程横向滑动 */}
                  <Swiper
                    modules={[FreeMode, Mousewheel]}
                    spaceBetween={10}
                    slidesPerView={2.3}
                    breakpoints={{
                      640: { slidesPerView: 3.2 },
                      1024: { slidesPerView: 4.2 },
                    }}
                    freeMode={true}
                    mousewheel={{ forceToAxis: true }}
                    className="schedule-swiper select-none"
                  >
                    {items.map(s => {
                      const c = STATUS_COLORS[s.status] || STATUS_COLORS.normal
                      const icon = SCHEDULE_ICONS[s.schedule_type] || '📅'
                      const isActive = actionId === s.id

                      let nextDueText = '未开始'
                      if (s.last_done_at) {
                        const nextDate = new Date(s.next_due_at || (new Date(s.last_done_at).getTime() + s.interval_days * 86400000))
                        nextDueText = `${nextDate.getMonth() + 1}月${nextDate.getDate()}日`
                      }

                      const statusIcon = s.status === 'overdue' ? '❗' : s.status === 'urgent' ? '⚡' : ''

                      return (
                        <SwiperSlide key={s.id} className="!h-auto pb-2">
                          <div className={`bg-white rounded-2xl p-3 shadow-sm border transition-all h-full flex flex-col ${
                            s.status === 'overdue' ? 'border-red-200 ring-2 ring-red-100' :
                            s.status === 'urgent' ? 'border-orange-200 ring-2 ring-orange-100' :
                            s.status === 'warning' ? 'border-yellow-200 ring-1 ring-yellow-100' :
                            'border-gray-100'
                          }`}>
                            {/* 倒计时圈 + 状态 */}
                            <div className="flex items-center justify-between mb-2">
                              <div className="w-10 h-10 flex-shrink-0">
                                <CountdownCircle daysLeft={s.days_left} status={s.status} size="sm" />
                              </div>
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.bg} text-white flex items-center gap-0.5`}>
                                {statusIcon && <span>{statusIcon}</span>}
                                <span>{c.label}</span>
                              </span>
                            </div>
                            {/* 标题 */}
                            <div className="flex items-center gap-1 mb-1">
                              <span className="text-sm">{icon}</span>
                              <span className="font-semibold text-xs">{s.title}</span>
                            </div>
                            <p className="text-xs text-gray-500 mb-0.5">
                              每{s.interval_days}天
                            </p>
                            <p className="text-xs text-gray-600 mb-2">
                              下次: <span className="font-semibold text-primary">{nextDueText}</span>
                            </p>
                            {/* 操作按钮 */}
                            <div className="flex gap-1 mt-auto pt-2 border-t border-gray-100">
                              <button onClick={() => handleMarkDone(s.id)} disabled={isActive}
                                className="flex-1 py-1 text-xs bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
                                {isActive ? '...' : '✅ 完成'}
                              </button>
                              <button onClick={() => setEditingSchedule(s)} disabled={isActive}
                                className="py-1 px-2 text-xs border border-gray-200 rounded-lg text-gray-500 hover:text-primary hover:border-primary transition-colors disabled:opacity-50">
                                ✏️
                              </button>
                              <button onClick={() => setDeleteConfirm(s)} disabled={isActive}
                                className="py-1 px-2 text-xs border border-gray-200 rounded-lg text-gray-400 hover:text-red-500 hover:border-red-200 transition-colors disabled:opacity-50">
                                🗑
                              </button>
                            </div>
                          </div>
                        </SwiperSlide>
                      )
                    })}
                  </Swiper>
                </div>
              )
            })
          })()}
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
      {editingSchedule && <EditScheduleModal schedule={editingSchedule} pets={pets} onClose={() => setEditingSchedule(null)} onUpdate={handleUpdate} />}
      {deleteConfirm && <DeleteConfirmModal schedule={deleteConfirm} onClose={() => setDeleteConfirm(null)} onConfirm={() => handleDelete(deleteConfirm.id)} />}
      {toast && <Toast message={toast} />}
    </div>
  )
}

// ===== 添加日程弹窗 =====
function AddScheduleModal({ pets, presets, onClose, onAdd }) {
  const [selected, setSelected] = useState(null)
  const [petName, setPetName] = useState(pets[0]?.pet_name || '')
  const isDraggingRef = useRef(false)
  const startXRef = useRef(0)
  const scrollLeftRef = useRef(0)
  const currentScrollRef = useRef(null)

  const handleMouseDown = (e, scrollContainer) => {
    isDraggingRef.current = true
    startXRef.current = e.pageX - scrollContainer.offsetLeft
    scrollLeftRef.current = scrollContainer.scrollLeft
    currentScrollRef.current = scrollContainer
    scrollContainer.style.cursor = 'grabbing'
  }

  const handleMouseUp = (scrollContainer) => {
    isDraggingRef.current = false
    if (scrollContainer) scrollContainer.style.cursor = 'grab'
    currentScrollRef.current = null
  }

  const handleMouseMove = (e) => {
    if (!isDraggingRef.current || !currentScrollRef.current) return
    e.preventDefault()
    const x = e.pageX - currentScrollRef.current.offsetLeft
    const walk = (x - startXRef.current) * 2
    currentScrollRef.current.scrollLeft = scrollLeftRef.current - walk
  }

  if (selected) {
    const p = presets.find(x => x.type === selected)
    return createPortal(
      <div className="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center p-4 modal-overlay" onClick={onClose}>
        <div className="bg-white rounded-2xl w-full max-w-sm max-h-[85vh] overflow-y-auto p-6 pb-20 animate-slideUp safe-bottom" onClick={e => e.stopPropagation()}>
          <h3 className="text-lg font-bold mb-4">确认添加</h3>
          <div className="space-y-4 mb-6">
            {/* 宠物选择 */}
            <PetPicker pets={pets} value={petName} onChange={setPetName} />
            
            {/* 日程基本信息 */}
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
              <span className="text-2xl">{p.icon}</span>
              <div className="flex-1">
                <p className="font-medium text-sm">{p.title}</p>
                <p className="text-xs text-gray-500">默认周期：每 {p.interval_days} 天</p>
                <p className="text-xs text-gray-400 mt-1">{p.note}</p>
              </div>
            </div>

            {/* 周期规则说明 - 滑动卡片 */}
            {p.rules && p.rules.length > 0 && (
              <div className="bg-blue-50 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                  <span>📋</span>
                  <span>周期规则建议</span>
                  <span className="text-[10px] text-blue-400 ml-auto font-normal">← 左右滑动 →</span>
                </h4>
                <div
                  className="flex gap-2.5 overflow-x-auto scroll-smooth select-none"
                  style={{
                    scrollSnapType: 'x mandatory',
                    WebkitOverflowScrolling: 'touch',
                    scrollbarWidth: 'none',
                    cursor: 'grab',
                    userSelect: 'none',
                  }}
                  onMouseDown={(e) => { e.preventDefault(); handleMouseDown(e, e.currentTarget) }}
                  onMouseUp={(e) => handleMouseUp(e.currentTarget)}
                  onMouseLeave={(e) => handleMouseUp(e.currentTarget)}
                  onMouseMove={handleMouseMove}
                  onDragStart={(e) => e.preventDefault()}
                >
                  {p.rules.map((rule, idx) => (
                    <div key={idx} className="flex-shrink-0 w-[200px] pointer-events-none" style={{ scrollSnapAlign: 'start' }}>
                      <div className="bg-white rounded-lg p-3 border border-blue-100 h-[110px] flex flex-col">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[11px] font-medium text-blue-800 leading-tight flex-1 mr-2">{rule.stage}</span>
                          <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full whitespace-nowrap flex-shrink-0">
                            每{rule.interval}天
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-600 leading-relaxed flex-1">{rule.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 注意事项 - 滑动卡片 */}
            {p.tips && p.tips.length > 0 && (
              <div className="bg-amber-50 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-amber-900 mb-3 flex items-center gap-2">
                  <span>💡</span>
                  <span>注意事项</span>
                  <span className="text-[10px] text-amber-400 ml-auto font-normal">← 左右滑动 →</span>
                </h4>
                <div
                  className="flex gap-2.5 overflow-x-auto scroll-smooth select-none"
                  style={{
                    scrollSnapType: 'x mandatory',
                    WebkitOverflowScrolling: 'touch',
                    scrollbarWidth: 'none',
                    cursor: 'grab',
                    userSelect: 'none',
                  }}
                  onMouseDown={(e) => { e.preventDefault(); handleMouseDown(e, e.currentTarget) }}
                  onMouseUp={(e) => handleMouseUp(e.currentTarget)}
                  onMouseLeave={(e) => handleMouseUp(e.currentTarget)}
                  onMouseMove={handleMouseMove}
                  onDragStart={(e) => e.preventDefault()}
                >
                  {p.tips.map((tip, idx) => (
                    <div key={idx} className="flex-shrink-0 w-[180px] pointer-events-none" style={{ scrollSnapAlign: 'start' }}>
                      <div className="bg-white rounded-lg p-3 border border-amber-100 h-[80px] flex items-center">
                        <p className="text-[11px] text-amber-800 leading-relaxed">{tip}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="flex gap-3 sticky bottom-0 bg-white pt-2">
            <button onClick={() => setSelected(null)}
              className="flex-1 py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50">返回</button>
            <button onClick={() => onAdd({ schedule_type: selected, pet_name: petName })}
              disabled={!petName}
              className="flex-1 py-2.5 text-sm bg-primary text-white rounded-xl font-medium disabled:opacity-50 hover:bg-primary/90">确认添加</button>
          </div>
        </div>
      </div>,
      document.body
    )
  }

  return createPortal(
    <div className="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center p-4 modal-overlay" onClick={onClose}>
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

// ===== 编辑日程弹窗 =====
function EditScheduleModal({ schedule, pets, onClose, onUpdate }) {
  const [intervalDays, setIntervalDays] = useState(schedule.interval_days)
  const [petName, setPetName] = useState(schedule.pet_name)
  const [note, setNote] = useState(schedule.note || '')
  const [saving, setSaving] = useState(false)

  // 不同类型日程的合理范围
  const INTERVAL_RANGE = {
    '体外驱虫': { min: 7, max: 90, label: '建议 7~90 天' },
    '体内驱虫': { min: 7, max: 365, label: '建议 7~365 天' },
    '疫苗': { min: 21, max: 730, label: '建议 21~730 天（3周~2年）' },
    '体检': { min: 30, max: 365, label: '建议 30~365 天' },
  }
  const range = INTERVAL_RANGE[schedule.schedule_type] || { min: 1, max: 365, label: '1~365 天' }

  const handleSubmit = async () => {
    const clamped = Math.min(Math.max(Number(intervalDays) || 1, range.min), range.max)
    setSaving(true)
    try {
      await onUpdate(schedule.id, { interval_days: clamped, pet_name: petName, note })
    } catch (e) {
      alert(e.message)
      setSaving(false)
    }
  }

  const displayDays = Number(intervalDays) || 0
  const isOutOfRange = displayDays < range.min || displayDays > range.max

  return createPortal(
    <div className="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center p-4 modal-overlay" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-sm max-h-[85vh] overflow-y-auto p-6 pb-20 animate-slideUp safe-bottom" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">编辑日程</h3>
        <div className="space-y-4 mb-6">
          {/* 宠物选择 - 按钮组 */}
          <PetPicker pets={pets} value={petName} onChange={setPetName} />

          {/* 间隔天数 */}
          <div>
            <label className="text-xs text-gray-500 mb-1 flex justify-between">
              <span>间隔天数</span>
              <span className="text-gray-400">{range.label}</span>
            </label>
            <input type="number" value={intervalDays} onChange={e => setIntervalDays(e.target.value)}
              min={range.min} max={range.max} step="1"
              className={`w-full px-4 py-2.5 border rounded-xl text-sm outline-none transition-colors ${
                isOutOfRange ? 'border-red-300 focus:border-red-500 bg-red-50' : 'border-gray-200 focus:border-primary'
              }`} />
            {isOutOfRange && displayDays > 0 && (
              <p className="text-xs text-red-500 mt-1">
                ⚠️ 超出范围，保存时会自动调整为 {range.min}~{range.max} 天
              </p>
            )}
            {/* 常用天数快捷按钮 */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {[
                { label: '每2周', days: 14 },
                { label: '每月', days: 30 },
                { label: '每3月', days: 90 },
                { label: '每半年', days: 180 },
                { label: '每年', days: 365 },
              ].filter(o => o.days >= range.min && o.days <= range.max)
                .map(o => (
                  <button key={o.days} onClick={() => setIntervalDays(o.days)}
                    className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
                      intervalDays === o.days
                        ? 'bg-primary text-white border-primary'
                        : 'bg-white text-gray-600 border-gray-200 hover:border-primary'
                    }`}>
                    {o.label}
                  </button>
                ))}
            </div>
          </div>

          {/* 备注 */}
          <div>
            <label className="text-xs text-gray-500 mb-1 block">备注</label>
            <textarea value={note} onChange={e => setNote(e.target.value)}
              placeholder="添加备注..." rows={3} maxLength={200}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary resize-none" />
            <p className="text-xs text-gray-400 text-right mt-0.5">{note.length}/200</p>
          </div>

          {/* 日程信息 */}
          <div className="p-3 bg-gray-50 rounded-xl">
            <p className="text-xs text-gray-500 mb-1">日程类型</p>
            <p className="font-medium text-sm flex items-center gap-2">
              <span className="text-xl">{SCHEDULE_ICONS[schedule.schedule_type] || '📅'}</span>
              <span>{schedule.title}</span>
            </p>
          </div>
        </div>
        <div className="flex gap-3 sticky bottom-0 bg-white pt-2">
          <button onClick={onClose}
            className="flex-1 py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50">取消</button>
          <button onClick={handleSubmit} disabled={saving || !petName}
            className="flex-1 py-2.5 text-sm bg-primary text-white rounded-xl font-medium disabled:opacity-50 hover:bg-primary/90">
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}

// ===== 删除确认弹窗 =====
function DeleteConfirmModal({ schedule, onClose, onConfirm }) {
  return createPortal(
    <div className="fixed inset-0 bg-black/50 z-[60] flex items-end justify-center p-4 modal-overlay" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-sm p-6 pb-20 animate-slideUp safe-bottom" onClick={e => e.stopPropagation()}>
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">🗑️</div>
          <h3 className="text-lg font-bold mb-2">确定删除吗？</h3>
          <p className="text-sm text-gray-500">
            确定删除 <span className="font-medium">{schedule.title}</span> 吗？
          </p>
          <p className="text-xs text-gray-400 mt-1">此操作无法撤销</p>
        </div>
        <div className="flex gap-3">
          <button onClick={onClose}
            className="flex-1 py-2.5 text-sm text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50">取消</button>
          <button onClick={onConfirm}
            className="flex-1 py-2.5 text-sm bg-red-500 text-white rounded-xl font-medium hover:bg-red-600">删除</button>
        </div>
      </div>
    </div>,
    document.body
  )
}

// ===== Toast 提示 =====
function Toast({ message }) {
  return createPortal(
    <div className="fixed top-20 left-1/2 -translate-x-1/2 z-[70] animate-slideDown">
      <div className="bg-gray-800 text-white px-6 py-3 rounded-xl shadow-lg text-sm">
        {message}
      </div>
    </div>,
    document.body
  )
}

// ===== 喂养日记 Tab =====
function FeedingTab({ state, pets }) {
  const [feedingLogs, setFeedingLogs] = useState([])
  const [selectedLog, setSelectedLog] = useState(null)
  const [diaries, setDiaries] = useState([])
  const [showDiaryForm, setShowDiaryForm] = useState(false)
  const [loading, setLoading] = useState(true)

  const fetchFeedingLogs = useCallback(async () => {
    if (!state.user) { setLoading(false); return }
    try {
      const data = await api.getFeedingLogs({ active_only: 'true' })
      setFeedingLogs(data.items || [])
    } catch (e) { console.error(e) }
    setLoading(false)
  }, [state.user])

  const fetchDiaries = useCallback(async () => {
    if (!selectedLog) return
    try {
      const data = await api.getFeedingDiaries({ feeding_log_id: String(selectedLog.id) })
      setDiaries(data.items || [])
    } catch (e) { console.error(e) }
  }, [selectedLog])

  useEffect(() => { fetchFeedingLogs() }, [fetchFeedingLogs])
  useEffect(() => { fetchDiaries() }, [fetchDiaries])

  // 计算换粮天数和阶段
  const getFeedingDay = (startDate) => {
    const start = new Date(startDate)
    const today = new Date()
    const diff = Math.floor((today - start) / (1000 * 60 * 60 * 24)) + 1
    return diff
  }

  const getFeedingPhase = (day) => {
    if (day <= 2) return { phase: '适应期', desc: '新旧粮 1:3', color: 'bg-blue-500' }
    if (day <= 4) return { phase: '过渡期', desc: '新旧粮 1:1', color: 'bg-yellow-500' }
    if (day <= 7) return { phase: '切换期', desc: '新粮为主', color: 'bg-orange-500' }
    return { phase: '已完成', desc: '纯新粮', color: 'bg-green-500' }
  }

  const getStatusIcon = (status) => {
    const icons = {
      'good': '🟢', 'normal': '🟢', 'soft': '🟡', 'hard': '🟡',
      'diarrhea': '🔴', 'bloody': '🔴', 'poor': '🔴'
    }
    return icons[status] || '⚪'
  }

  if (loading) {
    return <div className="text-center py-10 text-gray-400">加载中...</div>
  }

  if (feedingLogs.length === 0) {
    return (
      <div className="text-center py-10">
        <div className="text-5xl mb-3">🍽</div>
        <p className="text-gray-400">还没有喂养记录</p>
        <p className="text-sm text-gray-300 mt-1">在产品详情页点击「我家正在吃」开始记录</p>
      </div>
    )
  }

  if (selectedLog) {
    const day = getFeedingDay(selectedLog.start_date)
    const phase = getFeedingPhase(day)
    
    return (
      <div>
        {/* 返回按钮 */}
        <button onClick={() => setSelectedLog(null)} className="text-primary text-sm mb-3 flex items-center gap-1">
          ← 返回喂养列表
        </button>

        {/* 换粮进度卡片 */}
        <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-4 mb-4 border border-orange-200">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center text-2xl shadow-sm">
              🍽
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{selectedLog.product_name}</h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {selectedLog.pet_name} · 第 {day} 天
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${phase.color}`}>
              {phase.phase}
            </span>
          </div>
          
          {/* 七天进度条 */}
          <div className="space-y-2">
            <div className="flex gap-1">
              {[1,2,3,4,5,6,7].map(d => (
                <div key={d} className="flex-1 h-2 rounded-full bg-white/50 relative overflow-hidden">
                  {day >= d && (
                    <div className={`absolute inset-0 ${phase.color} transition-all`} />
                  )}
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-600 text-center">
              💡 {phase.desc}
            </p>
          </div>
        </div>

        {/* 记录按钮 */}
        <button
          onClick={() => setShowDiaryForm(true)}
          className="w-full py-3 bg-primary text-white rounded-xl font-medium mb-4 hover:bg-primary/90 transition-colors"
        >
          + 记录今日观察
        </button>

        {/* 日记列表 */}
        {diaries.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-4xl mb-2">📝</p>
            <p className="text-gray-400">还没有观察记录</p>
            <p className="text-xs text-gray-300 mt-1">每天记录宠物状态，追踪换粮效果</p>
          </div>
        ) : (
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">观察记录</h3>
            {diaries.map(diary => {
              const d = getFeedingDay(diary.record_date)
              const ph = getFeedingPhase(d)
              return (
                <div key={diary.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`w-6 h-6 rounded-full ${ph.color} flex items-center justify-center text-white text-xs font-bold`}>
                        {d}
                      </span>
                      <span className="text-sm font-medium text-gray-900">第 {d} 天</span>
                      <span className="text-xs text-gray-400">
                        {new Date(diary.record_date).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                    <button
                      onClick={async () => {
                        if (confirm('确定删除这条记录吗？')) {
                          try {
                            await api.deleteFeedingDiary(diary.id)
                            fetchDiaries()
                          } catch (e) { alert(e.message) }
                        }
                      }}
                      className="text-gray-300 hover:text-red-500 text-sm"
                    >
                      🗑
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">便便：</span>
                      <span>{getStatusIcon(diary.poop_status)} {diary.poop_status || '未记录'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">次数：</span>
                      <span>{diary.poop_count || 0} 次</span>
                    </div>
                    <div>
                      <span className="text-gray-500">食欲：</span>
                      <span>{getStatusIcon(diary.appetite)} {diary.appetite || '未记录'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">精神：</span>
                      <span>{getStatusIcon(diary.energy)} {diary.energy || '未记录'}</span>
                    </div>
                  </div>
                  
                  {diary.note && (
                    <p className="text-xs text-gray-600 mt-2 bg-gray-50 p-2 rounded">
                      📝 {diary.note}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {showDiaryForm && (
          <DiaryForm
            feedingLog={selectedLog}
            day={day}
            onClose={() => setShowDiaryForm(false)}
            onSaved={() => { fetchDiaries(); setShowDiaryForm(false) }}
          />
        )}
      </div>
    )
  }

  return (
    <div>
      <p className="text-sm text-gray-500 mb-3">记录宠物喂养情况，追踪换粮效果</p>
      <div className="space-y-3">
        {feedingLogs.map(log => {
          const day = getFeedingDay(log.start_date)
          const phase = getFeedingPhase(day)
          return (
            <div
              key={log.id}
              onClick={() => setSelectedLog(log)}
              className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:border-primary/30 cursor-pointer transition-colors"
            >
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center text-2xl">
                  🍽
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{log.product_name}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{log.pet_name}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs text-white ${phase.color}`}>
                      {phase.phase}
                    </span>
                    <span className="text-xs text-gray-400">第 {day} 天</span>
                  </div>
                </div>
                <span className="text-gray-300">→</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ===== 日记表单 =====
function DiaryForm({ feedingLog, day, onClose, onSaved }) {
  const [poopStatus, setPoopStatus] = useState('')
  const [poopCount, setPoopCount] = useState(0)
  const [appetite, setAppetite] = useState('')
  const [energy, setEnergy] = useState('')
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    setSaving(true)
    try {
      await api.createFeedingDiary({
        pet_name: feedingLog.pet_name,
        feeding_log_id: feedingLog.id,
        day_number: day,
        record_date: new Date().toISOString().split('T')[0],
        poop_status: poopStatus,
        poop_count: poopCount,
        appetite,
        energy,
        note,
      })
      onSaved()
    } catch (e) {
      alert(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 modal-overlay" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">记录第 {day} 天观察</h3>
          <button onClick={onClose} className="text-gray-400 text-xl">✕</button>
        </div>

        <div className="space-y-4">
          {/* 便便状态 */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">便便状态</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'normal', label: '正常 🟢' },
                { value: 'soft', label: '软便 🟡' },
                { value: 'hard', label: '硬便 🟡' },
                { value: 'diarrhea', label: '拉稀 🔴' },
                { value: 'bloody', label: '带血 🔴' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setPoopStatus(opt.value)}
                  className={`py-2 px-3 rounded-lg text-sm ${
                    poopStatus === opt.value
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* 便便次数 */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">便便次数</label>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setPoopCount(Math.max(0, poopCount - 1))}
                className="w-10 h-10 rounded-lg bg-gray-100 text-xl font-bold"
              >
                -
              </button>
              <span className="text-2xl font-bold w-12 text-center">{poopCount}</span>
              <button
                onClick={() => setPoopCount(poopCount + 1)}
                className="w-10 h-10 rounded-lg bg-gray-100 text-xl font-bold"
              >
                +
              </button>
            </div>
          </div>

          {/* 食欲 */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">食欲</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'good', label: '很好 🟢' },
                { value: 'normal', label: '一般 🟡' },
                { value: 'poor', label: '很差 🔴' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setAppetite(opt.value)}
                  className={`py-2 px-3 rounded-lg text-sm ${
                    appetite === opt.value
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* 精神状态 */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">精神状态</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'good', label: '活泼 🟢' },
                { value: 'normal', label: '一般 🟡' },
                { value: 'poor', label: '萎靡 🔴' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setEnergy(opt.value)}
                  className={`py-2 px-3 rounded-lg text-sm ${
                    energy === opt.value
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* 备注 */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">备注（可选）</label>
            <textarea
              value={note}
              onChange={e => setNote(e.target.value)}
              placeholder="记录其他观察，如呕吐、饮水量等..."
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none"
              rows={3}
            />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full mt-4 py-3 bg-primary text-white rounded-xl font-medium disabled:opacity-50"
        >
          {saving ? '保存中...' : '保存记录'}
        </button>
      </div>
    </div>
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
          <p className="text-sm text-gray-500 mt-1">健康记录 + 日程提醒 + 喂养日记</p>
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
            <button
              onClick={() => setTab('feeding')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                tab === 'feeding' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'
              }`}
            >
              🍽 喂养日记
            </button>
          </div>
        </div>
      </div>

      {/* 内容区 */}
      <div className="px-4 md:px-8 mt-4">
        <div className="max-w-2xl mx-auto">
          {tab === 'health' && <HealthTab state={state} pets={pets} />}
          {tab === 'schedule' && <ScheduleTab state={state} pets={pets} />}
          {tab === 'feeding' && <FeedingTab state={state} pets={pets} />}
        </div>
      </div>
    </div>
  )
}
