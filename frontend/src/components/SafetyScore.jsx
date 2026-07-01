export default function SafetyScore({ score, size = 'md' }) {
  const stars = Math.round(score)
  const color = score >= 4.5 ? 'text-green-500' : score >= 3.5 ? 'text-yellow-500' : score >= 2.5 ? 'text-orange-500' : 'text-red-500'
  const sizeClass = size === 'lg' ? 'text-2xl' : size === 'sm' ? 'text-sm' : 'text-lg'

  return (
    <div className={`flex items-center gap-1 ${sizeClass} ${color}`}>
      <span className="font-bold">{score}</span>
      <span className="text-yellow-400">
        {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
      </span>
    </div>
  )
}
