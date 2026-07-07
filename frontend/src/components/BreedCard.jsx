import { Link } from 'react-router-dom';

export default function BreedCard({ breed }) {
  return (
    <Link
      to={`/breed/${breed.id}`}
      className="group flex flex-col items-center bg-white rounded-xl md:rounded-2xl p-2 md:p-3 shadow-sm hover:shadow-md transition-all active:scale-95"
    >
      <div className="w-full aspect-square rounded-lg md:rounded-xl overflow-hidden bg-gray-100 mb-1.5 md:mb-2">
        {breed.image_url ? (
          <img
            src={breed.image_url}
            alt={breed.name}
            loading="lazy"
            className="w-full h-full object-cover group-hover:scale-105 group-hover:rotate-6 transition-transform duration-300"
            onError={(e) => { e.target.style.display = 'none' }}
          />
        ) : (
          <span className="flex items-center justify-center w-full h-full text-3xl">
            {breed.species === '猫' ? '🐱' : '🐶'}
          </span>
        )}
      </div>
      <span className="text-xs md:text-sm font-medium text-gray-800 text-center line-clamp-1 w-full">{breed.name}</span>
      <span className="text-[10px] md:text-xs text-gray-400">{breed.species}</span>
    </Link>
  );
}
