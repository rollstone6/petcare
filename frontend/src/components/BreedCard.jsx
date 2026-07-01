import { Link } from 'react-router-dom';

export default function BreedCard({ breed }) {
  return (
    <Link
      to={`/breed/${breed.id}`}
      className="block bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow p-4"
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-3xl">{breed.species === '猫' ? '🐱' : '🐶'}</span>
        <div>
          <h3 className="font-semibold text-gray-900">{breed.name}</h3>
          <p className="text-xs text-gray-400">{breed.size}型 | {breed.species}</p>
        </div>
      </div>
      {breed.common_issues && (
        <div className="mt-2 space-y-1">
          {breed.common_issues.split('、').slice(0, 2).map((issue, i) => (
            <p key={i} className="text-xs text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full inline-block mr-1">
              ⚠️ {issue}
            </p>
          ))}
        </div>
      )}
    </Link>
  );
}
