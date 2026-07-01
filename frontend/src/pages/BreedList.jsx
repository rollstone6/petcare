import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { SkeletonBreedCard } from '../components/Skeleton'
import { api } from '../api/client'

const speciesTabs = ['全部', '狗', '猫']

export default function BreedList() {
  const navigate = useNavigate()
  const [breeds, setBreeds] = useState([])
  const [species, setSpecies] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.getBreeds(species || undefined).then(data => {
      setBreeds(data.items || [])
      setLoading(false)
    })
  }, [species])

  return (
    <div className="animate-fadeIn pb-4">
      <div className="bg-white px-4 md:px-8 pt-6 md:pt-10 pb-4 sticky top-0 z-40 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">🐾 品种百科</h1>
          <p className="text-sm md:text-base text-gray-500 mt-1">{breeds.length} 个品种</p>
        </div>
      </div>

      <div className="px-4 md:px-8 py-3">
        <div className="max-w-4xl mx-auto flex gap-2">
          {speciesTabs.map(s => (
            <button
              key={s}
              onClick={() => setSpecies(s === '全部' ? '' : s)}
              className={`px-4 md:px-5 py-1.5 md:py-2 rounded-full text-sm transition-colors ${
                (s === '全部' && !species) || s === species
                  ? 'bg-primary text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          {loading ? (
            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 md:gap-4">
              {Array.from({length: 12}).map((_, i) => <SkeletonBreedCard key={i} />)}
            </div>
          ) : (
            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 md:gap-4">
              {breeds.map(b => (
                <button
                  key={b.id}
                  onClick={() => navigate(`/breed/${b.id}`)}
                  className="flex flex-col items-center bg-white rounded-xl md:rounded-2xl p-2 md:p-3 shadow-sm hover:shadow-md transition-all active:scale-95 touch-target"
                >
                  <div className="w-full aspect-square rounded-lg md:rounded-xl overflow-hidden bg-gray-100 mb-1.5 md:mb-2">
                    <img
                      src={b.image_url || '/placeholder-breed.svg'}
                      alt={b.name}
                      loading="lazy"
                      className="w-full h-full object-cover"
                      onError={(e) => { e.target.style.display = 'none' }}
                    />
                  </div>
                  <span className="text-xs md:text-sm font-medium text-gray-800 text-center line-clamp-1 w-full">{b.name}</span>
                  <span className="text-[10px] md:text-xs text-gray-400">{b.species}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
