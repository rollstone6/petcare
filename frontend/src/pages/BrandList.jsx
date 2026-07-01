import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBrands } from '../api';

export default function BrandList() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBrands({ page_size: 100 }).then(res => {
      setBrands(res.data.data.items);
    }).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 pb-20 md:pb-8">
      <h1 className="text-xl font-bold text-gray-900 mb-6">🏢 品牌大全</h1>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4,5,6,7,8].map(i => <div key={i} className="skeleton h-24 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {brands.map(b => (
            <Link
              key={b.id}
              to={`/search?brand_id=${b.id}`}
              className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow p-4 text-center"
            >
              <div className="w-12 h-12 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-xl mx-auto mb-2">
                🏢
              </div>
              <h3 className="font-medium text-gray-900 text-sm">{b.name}</h3>
              <p className="text-xs text-gray-400 mt-1">{b.country}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
