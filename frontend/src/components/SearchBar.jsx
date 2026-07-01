import { useNavigate } from 'react-router-dom'

export default function SearchBar({ placeholder = '搜索宠物药品、食品...', className = '' }) {
  const navigate = useNavigate()

  return (
    <div className={`relative ${className}`} onClick={() => navigate('/search')}>
      <div className="flex items-center bg-gray-100 rounded-xl px-4 py-3">
        <span className="text-gray-400 mr-2">🔍</span>
        <span className="text-gray-400 text-sm">{placeholder}</span>
      </div>
    </div>
  )
}
