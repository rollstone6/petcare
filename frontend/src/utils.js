export function getSafetyColor(score) {
  if (score >= 90) return 'safety-green';
  if (score >= 70) return 'safety-green';
  if (score >= 50) return 'safety-yellow';
  if (score >= 30) return 'safety-orange';
  return 'safety-red';
}

// 成分级别颜色（1-5分制，5=最安全）
export function getIngredientSafetyColor(level) {
  if (level >= 4.5) return 'bg-emerald-100 text-emerald-700';
  if (level >= 3.5) return 'bg-green-100 text-green-700';
  if (level >= 2.5) return 'bg-yellow-100 text-yellow-700';
  if (level >= 1.5) return 'bg-orange-100 text-orange-700';
  return 'bg-red-100 text-red-700';
}

export function getSafetyLabel(score) {
  if (score >= 90) return '优秀';
  if (score >= 70) return '良好';
  if (score >= 50) return '中等';
  if (score >= 30) return '较差';
  return '危险';
}

export function getSafetyEmoji(score) {
  if (score >= 90) return '🟢';
  if (score >= 70) return '🟢';
  if (score >= 50) return '🟡';
  if (score >= 30) return '🟠';
  return '🔴';
}
