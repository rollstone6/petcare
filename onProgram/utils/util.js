/**
 * 将相对路径图片URL转为完整URL
 * @param {string} url - 图片URL（可能是相对路径如 /avatars/xxx.webp）
 * @param {string} fallback - 备用图片URL
 * @returns {string} 完整的图片URL
 */
const formatImageUrl = (url, fallback = '') => {
  if (!url) return fallback
  // 已经是完整URL
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  // 相对路径，拼接网站域名
  return 'https://petcare.yjyblog.xyz' + url
}

module.exports = {
  formatImageUrl
}
