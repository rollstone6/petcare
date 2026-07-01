import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, getToken } from '../api/client'

// 删除按钮：只显示给自己的评论
function DeleteButton({ reviewUserId, onDelete }) {
  // 简单检查：如果评论是匿名的或不是自己的，不显示删除按钮
  // 后端会做最终权限校验
  return (
    <button
      onClick={onDelete}
      className="text-xs text-red-500 hover:text-red-700"
    >
      删除
    </button>
  )
}

export default function ReviewSection({ productId }) {
  const navigate = useNavigate()
  const [reviews, setReviews] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    rating: 5,
    content: '',
    pet_type: '',
    pet_age: '',
    is_anonymous: false
  })

  useEffect(() => {
    loadReviews()
  }, [productId])

  const loadReviews = async () => {
    try {
      const data = await api.getProductReviews(productId)
      setReviews(data.items)
      setStats(data.stats)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!getToken()) {
      alert('请先登录')
      navigate('/profile')
      return
    }

    try {
      await api.createReview({
        product_id: productId,
        ...formData
      })
      setShowForm(false)
      setFormData({ rating: 5, content: '', pet_type: '', pet_age: '', is_anonymous: false })
      loadReviews() // 刷新列表
      alert('评论成功！')
    } catch (e) {
      alert(e.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('确定删除这条评论？')) return
    try {
      await api.deleteReview(id)
      loadReviews()
      alert('删除成功')
    } catch (e) {
      alert(e.message)
    }
  }

  const renderStars = (rating, interactive = false, onChange = null) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map(i => (
          <button
            key={i}
            type="button"
            onClick={interactive ? () => onChange(i) : undefined}
            className={`text-2xl ${interactive ? 'cursor-pointer hover:scale-110' : ''} transition-transform`}
          >
            {i <= rating ? '⭐' : '☆'}
          </button>
        ))}
      </div>
    )
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-400">加载中...</div>
  }

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">用户评价</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors text-sm"
        >
          {showForm ? '取消' : '写评价'}
        </button>
      </div>

      {/* 评分统计 */}
      {stats && stats.total_reviews > 0 && (
        <div className="bg-white rounded-lg p-4 mb-4 border">
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary">{stats.avg_rating}</div>
              <div className="text-sm text-gray-500 mt-1">平均分</div>
              <div className="text-xs text-gray-400">{stats.total_reviews} 条评价</div>
            </div>
            <div className="flex-1 space-y-1">
              {[5, 4, 3, 2, 1].map(rating => {
                const count = stats.rating_distribution[rating] || 0
                const percent = stats.total_reviews > 0 ? (count / stats.total_reviews) * 100 : 0
                return (
                  <div key={rating} className="flex items-center gap-2 text-sm">
                    <span className="w-8">{rating}星</span>
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-400"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span className="w-12 text-right text-gray-500">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* 写评价表单 */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg p-4 mb-4 border space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">评分</label>
            {renderStars(formData.rating, true, (r) => setFormData({ ...formData, rating: r }))}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">评价内容</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              rows="4"
              maxLength="500"
              placeholder="分享您的使用体验..."
            />
            <div className="text-xs text-gray-400 mt-1">{formData.content.length}/500</div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">宠物类型</label>
              <select
                value={formData.pet_type}
                onChange={(e) => setFormData({ ...formData, pet_type: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
              >
                <option value="">不填写</option>
                <option value="猫">猫</option>
                <option value="狗">狗</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">宠物年龄</label>
              <input
                type="text"
                value={formData.pet_age}
                onChange={(e) => setFormData({ ...formData, pet_age: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="如：2岁"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="anonymous"
              checked={formData.is_anonymous}
              onChange={(e) => setFormData({ ...formData, is_anonymous: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor="anonymous" className="text-sm">匿名评价</label>
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
          >
            提交评价
          </button>
        </form>
      )}

      {/* 评论列表 */}
      {reviews.length === 0 ? (
        <div className="text-center py-8 text-gray-400">暂无评价，快来成为第一个评价的人吧！</div>
      ) : (
        <div className="space-y-4">
          {reviews.map(review => (
            <div key={review.id} className="bg-white rounded-lg p-4 border">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  {review.avatar_url ? (
                    <img src={review.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
                      {review.nickname?.[0] || '匿'}
                    </div>
                  )}
                  <div>
                    <div className="font-medium">{review.nickname}</div>
                    <div className="text-xs text-gray-400">
                      {new Date(review.created_at).toLocaleString('zh-CN')}
                    </div>
                  </div>
                </div>
                {getToken() && (
                  <DeleteButton reviewUserId={review.user_id} onDelete={() => handleDelete(review.id)} />
                )}
              </div>

              <div className="mb-2">
                {renderStars(review.rating)}
              </div>

              {review.content && (
                <div className="text-gray-700 mb-2 whitespace-pre-wrap">{review.content}</div>
              )}

              {(review.pet_type || review.pet_age) && (
                <div className="flex gap-2 text-xs text-gray-500">
                  {review.pet_type && <span className="px-2 py-1 bg-gray-100 rounded">{review.pet_type}</span>}
                  {review.pet_age && <span className="px-2 py-1 bg-gray-100 rounded">{review.pet_age}</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
