export function getSafetyColor(score) {
  if (score >= 4.5) return 'safety-green';
  if (score >= 3.5) return 'safety-yellow';
  if (score >= 2.5) return 'safety-orange';
  return 'safety-red';
}

export function getSafetyLabel(score) {
  if (score >= 4.5) return '非常安全';
  if (score >= 3.5) return '安全';
  if (score >= 2.5) return '需注意';
  return '有风险';
}

export function getSafetyEmoji(score) {
  if (score >= 4.5) return '🟢';
  if (score >= 3.5) return '🟡';
  if (score >= 2.5) return '🟠';
  return '🔴';
}
