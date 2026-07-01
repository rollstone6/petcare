import { useState, useRef, useEffect } from 'react'

export default function AIChat({ productName, ingredients }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const answerRef = useRef(null)

  useEffect(() => {
    if (answer && answerRef.current) {
      answerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [answer])

  const askAI = async () => {
    if (!question.trim()) return
    setLoading(true)
    setError('')
    setAnswer('')
    try {
      const res = await fetch('/api/ai/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          product_name: productName,
          ingredients: ingredients,
        }),
      })
      const data = await res.json()
      if (data.code === 0) {
        setAnswer(data.data.answer)
      } else {
        setError(data.message || 'AI 暂时不可用')
      }
    } catch (e) {
      setError('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* 快捷问题 */}
      <div className="flex flex-wrap gap-1.5 md:gap-2 mb-3">
        {['这个产品安全吗？', '主要成分有什么作用？', '适合什么体型的宠物？', '有什么副作用吗？'].map(q => (
          <button
            key={q}
            onClick={() => setQuestion(q)}
            className={`text-xs md:text-sm px-2.5 py-1 md:px-3 md:py-1.5 rounded-full transition-colors ${
              question === q
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {q}
          </button>
        ))}
      </div>

      {/* 输入区 */}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && askAI()}
          placeholder="输入你想了解的问题..."
          className="flex-1 px-3 py-2 md:px-4 md:py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-primary"
        />
        <button
          onClick={askAI}
          disabled={loading || !question.trim()}
          className="px-4 py-2 md:px-5 md:py-2.5 bg-primary text-white rounded-xl text-sm font-medium disabled:opacity-50 hover:bg-primary/90 transition-colors flex-shrink-0"
        >
          {loading ? '思考中...' : '提问'}
        </button>
      </div>

      {/* 结果 */}
      {error && (
        <p className="mt-3 text-sm text-red-500">{error}</p>
      )}
      {answer && (
        <div ref={answerRef} className="mt-3 md:mt-4 p-3 md:p-4 bg-blue-50 rounded-xl">
          <p className="text-xs md:text-sm text-blue-900 leading-relaxed whitespace-pre-line">{answer}</p>
        </div>
      )}
    </div>
  )
}
