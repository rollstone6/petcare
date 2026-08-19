// 共享常量 - PC端和小程序端公用

// 物种图标映射
const SPECIES_ICONS = {
  '全部': '🐾',
  '狗': '🐕',
  '猫': '🐈',
  '兔子': '🐇',
  '仓鼠': '🐹',
  '鸟类': '🐦',
  '鱼类': '🐟',
  '爬行类': '🦎',
  '刺猬': '🦔',
  '雪貂': '🦦',
  '豚鼠': '🐹',
  '龙猫': '🐭',
  '蜜袋鼯': '🐿️'
}

// 排序选项
const SORT_OPTIONS = [
  { key: 'name', label: '按名字', icon: '🔤' },
  { key: 'species', label: '按种类', icon: '🏷️' }
]

// 分页大小
const PAGE_SIZE = 24

module.exports = {
  SPECIES_ICONS,
  SORT_OPTIONS,
  PAGE_SIZE
}
