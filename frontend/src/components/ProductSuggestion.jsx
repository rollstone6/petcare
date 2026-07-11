import { useState } from 'react'
import { createPortal } from 'react-dom'
import { api, getToken } from '../api/client'

export default function ProductSuggestion({ searchQuery, onClose }) {
  const [step, setStep] = useState(1) // 1: 表单, 2: AI分析, 3: 提交成功
  const [productName, setProductName] = useState(searchQuery || '')
  const [brandName, setBrandName] = useState('')
  const [productType, setProductType] = useState('食品')
  const [ingredientsText, setIngredientsText] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => setImagePreview(reader.result)
      reader.readAsDataURL(file)
    }
  }

  const handleAnalyze = async () => {
    if (!ingredientsText.trim()) {
      setError('请输入配料表内容')
      return
    }

    setAnalyzing(true)
    setError('')

    try {
      const result = await api.analyzeIngredients({
        ingredients_text: ingredientsText,
        product_name: productName,
        product_type: productType,
      })
      setAnalysis(result.data)
      setStep(2)
    } catch (e) {
      setError(e.message || 'AI 分析失败，请稍后再试')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('search_query', searchQuery)
      formData.append('product_name', productName)
      formData.append('brand_name', brandName)
      formData.append('product_type', productType)
      formData.append('ingredients_text', ingredientsText)
      formData.append('ai_analysis', JSON.stringify(analysis))
      formData.append('ai_score', analysis?.score || 3.0)

      if (imageFile) {
        formData.append('image', imageFile)
      }

      await api.createSuggestion(formData)
      setStep(3)
    } catch (e) {
      setError(e.message || '提交失败，请稍后再试')
    } finally {
      setSubmitting(false)
    }
  }

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-6xl mb-3">🎁</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          发现宝藏产品！
        </h2>
        <p className="text-sm text-gray-600">
          这款产品我们还没收录，<br/>
          动动小手上传配料表，<br/>
          <span className="text-primary font-medium">AI 大脑将在 1 分钟内为你生成专属安全报告</span>
        </p>
      </div>

      {/* 基本信息 */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            产品名称 *
          </label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            placeholder="例：皇家猫粮 室内成猫"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            品牌（可选）
          </label>
          <input
            type="text"
            value={brandName}
            onChange={(e) => setBrandName(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            placeholder="例：皇家"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            产品类型
          </label>
          <div className="grid grid-cols-3 gap-2">
            {['药品', '食品', '保健品'].map(type => (
              <button
                key={type}
                onClick={() => setProductType(type)}
                className={`px-3 py-2 rounded-xl text-sm transition-all ${
                  productType === type
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 配料表输入 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          配料表内容 *
        </label>
        <textarea
          value={ingredientsText}
          onChange={(e) => setIngredientsText(e.target.value)}
          rows={6}
          className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
          placeholder="请从包装上复制配料表，每行一个成分&#10;例：&#10;鸡肉&#10;玉米&#10;糙米&#10;..."
        />
      </div>

      {/* 图片上传 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          拍照上传（可选）
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center hover:border-primary transition-colors">
          {imagePreview ? (
            <div className="relative">
              <img src={imagePreview} alt="预览" className="max-h-48 mx-auto rounded-lg aspect-video object-cover" />
              <button
                onClick={() => { setImageFile(null); setImagePreview('') }}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-red-600 touch-target"
              >
                ×
              </button>
            </div>
          ) : (
            <label className="cursor-pointer block">
              <div className="text-4xl mb-2">📷</div>
              <p className="text-sm text-gray-600">点击拍照或上传配料表照片</p>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleImageChange}
                className="hidden"
              />
            </label>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={analyzing || !ingredientsText.trim()}
        className="w-full bg-primary text-white py-3 rounded-xl font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-dark transition-colors"
      >
        {analyzing ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            AI 正在分析配料表...
          </span>
        ) : (
          '🤖 让 AI 分析安全性'
        )}
      </button>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-6xl mb-3">📊</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          AI 安全报告
        </h2>
      </div>

      {/* 安全评分 */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 text-center">
        <div className="text-5xl font-bold text-primary mb-2">
          {analysis?.score?.toFixed(1) || '3.0'}
        </div>
        <div className="flex justify-center gap-1 mb-2">
          {[1, 2, 3, 4, 5].map(i => (
            <div
              key={i}
              className={`w-8 h-8 rounded-full ${
                i <= (analysis?.score || 3) ? 'bg-primary' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        <p className="text-sm text-gray-600">
          {analysis?.score >= 4 ? '安全可靠' :
           analysis?.score >= 3 ? '基本安全' :
           analysis?.score >= 2 ? '谨慎使用' : '风险较高'}
        </p>
      </div>

      {/* 总体评价 */}
      <div className="bg-white rounded-xl p-4 border border-gray-200">
        <h3 className="font-medium text-gray-900 mb-2">💡 总体评价</h3>
        <p className="text-sm text-gray-700 leading-relaxed">
          {analysis?.summary || '暂无评价'}
        </p>
      </div>

      {/* 优质成分 */}
      {analysis?.good_ingredients?.length > 0 && (
        <div className="bg-green-50 rounded-xl p-4 border border-green-200">
          <h3 className="font-medium text-green-900 mb-2">✅ 优质成分</h3>
          <div className="flex flex-wrap gap-2">
            {analysis.good_ingredients.map((item, idx) => (
              <span key={idx} className="bg-white px-3 py-1 rounded-full text-sm text-green-700 border border-green-200">
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 风险成分 */}
      {analysis?.risk_ingredients?.length > 0 && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-200">
          <h3 className="font-medium text-red-900 mb-2">⚠️ 风险成分</h3>
          <div className="space-y-2">
            {analysis.risk_ingredients.map((item, idx) => (
              <div key={idx} className="bg-white rounded-lg p-3 border border-red-200">
                <div className="font-medium text-red-900 mb-1">{item.name}</div>
                <div className="text-sm text-red-700">{item.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={() => setStep(1)}
          className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl font-medium text-sm hover:bg-gray-200 transition-colors"
        >
          返回修改
        </button>
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="flex-1 bg-primary text-white py-3 rounded-xl font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-dark transition-colors"
        >
          {submitting ? '提交中...' : '✅ 提交到数据库'}
        </button>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="text-center space-y-6 py-8">
      <div className="text-6xl mb-3">🎉</div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        感谢你的贡献！
      </h2>
      <p className="text-gray-600 leading-relaxed">
        你提交的产品信息已成功入库<br/>
        审核通过后将正式收录到产品库中<br/>
        <span className="text-primary font-medium">帮助更多铲屎官做出安全选择</span>
      </p>
      <button
        onClick={onClose}
        className="mt-6 bg-primary text-white px-8 py-3 rounded-xl font-medium hover:bg-primary-dark transition-colors"
      >
        关闭
      </button>
    </div>
  )

  return createPortal(
    <div className="fixed inset-0 z-[60] flex items-end md:items-center justify-center modal-overlay" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="relative bg-white rounded-t-3xl md:rounded-3xl w-full max-w-md max-h-[90vh] overflow-y-auto safe-bottom"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* 关闭按钮 */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl z-10"
          >
            ×
          </button>

          {/* 步骤指示器 */}
          {step < 3 && (
            <div className="flex items-center justify-center gap-2 mb-6">
              {[1, 2].map(s => (
                <div key={s} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= s ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {s}
                  </div>
                  {s < 2 && <div className={`w-12 h-1 mx-2 rounded ${step > s ? 'bg-primary' : 'bg-gray-200'}`} />}
                </div>
              ))}
            </div>
          )}

          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>
      </div>
    </div>,
    document.body
  )
}
