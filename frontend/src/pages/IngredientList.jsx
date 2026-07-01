import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getIngredients } from '../api';
import { getSafetyColor, getSafetyEmoji } from '../utils';

export default function IngredientList() {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getIngredients({ page_size: 100 }).then(res => {
      setIngredients(res.data.data.items);
    }).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 pb-20 md:pb-8">
      <h1 className="text-xl font-bold text-gray-900 mb-6">🧪 成分百科</h1>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => <div key={i} className="skeleton h-16 rounded-xl" />)}
        </div>
      ) : (
        <div className="space-y-2">
          {ingredients.map(ing => {
            const colorClass = getSafetyColor(ing.safety_level);
            return (
              <Link
                key={ing.id}
                to={`/ingredient/${ing.id}`}
                className="flex items-center justify-between p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{ing.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${colorClass}`}>
                      {getSafetyEmoji(ing.safety_level)} {ing.safety_level}级
                    </span>
                  </div>
                  {ing.function && <p className="text-xs text-gray-400 mt-1 truncate">{ing.function}</p>}
                </div>
                <span className="text-gray-300 ml-4">→</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
