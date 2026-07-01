import { useState } from 'react'

export default function HealthCalculator() {
  const [form, setForm] = useState({
    breed: '', species: '狗', size: '中型', age_months: 12, weight_kg: 10,
    food_brand: '', food_protein: 0, food_calcium: 0,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const speciesOptions = [
    { value: '狗', breeds: ['金毛寻回犬', '拉布拉多寻回犬', '德国牧羊犬', '哈士奇', '柯基犬', '柴犬', '边境牧羊犬', '法国斗牛犬', '贵宾犬(泰迪)', '比熊犬', '博美犬', '吉娃娃', '约克夏梗', '阿拉斯加雪橇犬'] },
    { value: '猫', breeds: ['英国短毛猫', '美国短毛猫', '布偶猫', '波斯猫', '缅因猫', '暹罗猫', '中华田园猫(橘猫)', '斯芬克斯猫(无毛)', '挪威森林猫', '异国短毛猫(加菲)'] },
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch('/api/health/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (data.code === 0) setResult(data.data)
      else alert(data.message || '计算失败')
    } catch (e) {
      alert('网络错误')
    } finally {
      setLoading(false)
    }
  }

  const selectedSpecies = speciesOptions.find(s => s.value === form.species)

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-primary px-4 md:px-8 pt-8 md:pt-10 pb-8 md:pb-10 md:rounded-b-3xl">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-white text-xl md:text-2xl font-bold">🏥 宠物健康计算器</h1>
          <p className="text-green-100 text-sm md:text-base mt-2">输入宠物信息，获取钙质/关节营养推荐 + 成长曲线</p>
        </div>
      </div>

      <div className="px-4 md:px-8 -mt-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-sm p-4 md:p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 物种选择 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">物种</label>
                <div className="flex gap-2">
                  {speciesOptions.map(s => (
                    <button key={s.value} type="button"
                      onClick={() => setForm({ ...form, species: s.value, breed: '' })}
                      className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
                        form.species === s.value ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {s.value === '狗' ? '🐶 狗' : '🐱 猫'}
                    </button>
                  ))}
                </div>
              </div>

              {/* 品种 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">品种</label>
                <select value={form.breed} onChange={e => setForm({ ...form, breed: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary bg-white"
                >
                  <option value="">请选择品种</option>
                  {selectedSpecies?.breeds.map(b => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>

              {/* 体型 + 月龄 + 体重 一行 */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">体型</label>
                  <select value={form.size} onChange={e => setForm({ ...form, size: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary bg-white"
                  >
                    <option value="小型">小型</option>
                    <option value="中型">中型</option>
                    <option value="大型">大型</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">月龄</label>
                  <input type="number" value={form.age_months} onChange={e => setForm({ ...form, age_months: parseInt(e.target.value) || 0 })}
                    min={1} max={240}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">体重(kg)</label>
                  <input type="number" step="0.1" value={form.weight_kg} onChange={e => setForm({ ...form, weight_kg: parseFloat(e.target.value) || 0 })}
                    min={0.5} max={100}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                  />
                </div>
              </div>

              {/* 主粮信息（可选） */}
              <details className="group">
                <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">📦 主粮信息（可选）</summary>
                <div className="mt-3 grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="text-xs text-gray-500 mb-1 block">主粮品牌</label>
                    <input type="text" value={form.food_brand} onChange={e => setForm({ ...form, food_brand: e.target.value })}
                      placeholder="如：冠能、皇家"
                      className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">蛋白质%</label>
                    <input type="number" step="0.1" value={form.food_protein} onChange={e => setForm({ ...form, food_protein: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
                    />
                  </div>
                </div>
              </details>

              <button type="submit" disabled={loading || !form.breed}
                className="w-full bg-primary text-white py-3 rounded-xl font-medium text-sm md:text-base hover:bg-primary-dark transition-colors disabled:opacity-50"
              >
                {loading ? '⏳ 计算中...' : '🔬 开始分析'}
              </button>
            </form>
          </div>

          {/* 结果展示 */}
          {result && (
            <div className="mt-6 space-y-4">
              {/* 核心数值卡片 */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <ResultCard label="每日钙推荐" value={`${result.calcium_mg_per_day}mg`} icon="🦴" />
                <ResultCard label="葡萄糖胺" value={`${result.joint.glucosamine_mg}mg`} icon="💊" />
                <ResultCard label="软骨素" value={`${result.joint.chondroitin_mg}mg`} icon="✨" />
                <ResultCard label="关节优先级" value={priorityLabel(result.joint.priority)} icon="⚠️" highlight={result.joint.priority} />
                <ResultCard label="预估成年体重" value={`${result.growth_curve.estimated_adult_weight}kg`} icon="⚖️" />
                <ResultCard label="当前体重" value={`${form.weight_kg}kg`} icon="📊" />
              </div>

              {/* 成长曲线 */}
              <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
                <h2 className="font-semibold text-gray-900 mb-4">📈 成长曲线</h2>
                <GrowthChart points={result.growth_curve.points} currentWeight={form.weight_kg} />
              </div>

              {/* AI 建议 */}
              {result.ai_advice && (
                <div className="bg-white rounded-2xl p-4 md:p-6 shadow-sm">
                  <h2 className="font-semibold text-gray-900 mb-3">🤖 AI 营养建议</h2>
                  <p className="text-sm md:text-base text-gray-700 leading-relaxed whitespace-pre-wrap">{result.ai_advice}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ResultCard({ label, value, icon, highlight }) {
  const colors = {
    critical: 'border-red-300 bg-red-50',
    high: 'border-orange-300 bg-orange-50',
    medium: 'border-yellow-300 bg-yellow-50',
    low: 'border-green-300 bg-green-50',
    none: 'border-gray-200',
  }
  const cls = highlight ? colors[highlight] || '' : ''
  return (
    <div className={`rounded-xl p-3 md:p-4 border ${cls}`}>
      <div className="text-lg mb-1">{icon}</div>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-sm md:text-base font-bold text-gray-900 mt-0.5">{value}</div>
    </div>
  )
}

function priorityLabel(p) {
  const map = { critical: '🔴 极高', high: '🟠 高', medium: '🟡 中等', low: '🟢 低', none: '⚪ 无需' }
  return map[p] || p
}

function GrowthChart({ points, currentWeight }) {
  if (!points || points.length === 0) return null

  const maxW = Math.max(...points.map(p => p.weight), currentWeight) * 1.2
  const width = 100
  const height = 200
  const padX = 30
  const padY = 20
  const chartW = width - padX * 2
  const chartH = height - padY * 2

  const scaleX = (month) => padX + (month / Math.max(...points.map(p => p.month))) * chartW
  const scaleY = (w) => height - padY - (w / maxW) * chartH

  const pathD = points.map((p, i) => {
    const cmd = i === 0 ? 'M' : 'L'
    return `${cmd}${scaleX(p.month)},${scaleY(p.weight)}`
  }).join(' ')

  const currentPoint = points.find(p => p.is_current)
  const adultPoint = points[points.length - 1]

  return (
    <div className="relative" style={{ height }}>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
        {/* 网格线 */}
        {[0, 0.25, 0.5, 0.75, 1].map(frac => (
          <line key={frac} x1={padX} y1={scaleY(maxW * frac)} x2={width - padX} y2={scaleY(maxW * frac)}
            stroke="#f0f0f0" strokeWidth="0.5" />
        ))}
        {/* 曲线 */}
        <path d={pathD} fill="none" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
        {/* 未来虚线 */}
        {points.filter(p => p.is_future).length > 0 && (
          <path d={points.filter(p => !p.is_future).map((p, i) => {
            const cmd = i === 0 ? 'M' : 'L'
            return `${cmd}${scaleX(p.month)},${scaleY(p.weight)}`
          }).join(' ') + points.filter(p => p.is_future).map(p => `L${scaleX(p.month)},${scaleY(p.weight)}`).join('')}
            fill="none" stroke="#10B981" strokeWidth="2" strokeDasharray="4,4" strokeLinecap="round" opacity="0.5" />
        )}
        {/* 当前体重标记 */}
        {currentPoint && (
          <circle cx={scaleX(currentPoint.month)} cy={scaleY(currentPoint.weight)} r="4" fill="#10B981" stroke="white" strokeWidth="2" />
        )}
        {/* 成年体重线 */}
        {adultPoint && (
          <line x1={padX} y1={scaleY(adultPoint.weight)} x2={width - padX} y2={scaleY(adultPoint.weight)}
            stroke="#F59E0B" strokeWidth="1" strokeDasharray="3,3" opacity="0.6" />
        )}
      </svg>
      {/* 图例 */}
      <div className="absolute top-2 right-2 flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-green-500 inline-block" /> 实际</span>
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-green-500/50 inline-block" style={{borderTop:'2px dashed'}} /> 预测</span>
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-yellow-500 inline-block" style={{borderTop:'1px dashed'}} /> 成年</span>
      </div>
    </div>
  )
}
