export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-14 h-14 bg-gray-200 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-100 rounded w-1/2" />
          <div className="flex gap-2 mt-2">
            <div className="h-5 bg-gray-200 rounded-full w-12" />
            <div className="h-5 bg-gray-100 rounded-full w-10" />
          </div>
        </div>
      </div>
    </div>
  )
}

export function SkeletonBreedCard() {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm animate-pulse">
      <div className="w-full aspect-square bg-gray-200 rounded-xl mb-3" />
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
      <div className="h-3 bg-gray-100 rounded w-1/2" />
    </div>
  )
}

export function SkeletonList({ count = 6, type = 'card' }) {
  const Comp = type === 'breed' ? SkeletonBreedCard : SkeletonCard
  const gridClass = type === 'breed' 
    ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4'
    : 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4'
  
  return (
    <div className={gridClass}>
      {Array.from({ length: count }, (_, i) => <Comp key={i} />)}
    </div>
  )
}
