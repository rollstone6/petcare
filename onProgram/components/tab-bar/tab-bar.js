Component({
  properties: {
    selected: {
      type: Number,
      value: 0
    }
  },

  data: {
    tabs: [
      { icon: '🏠', label: '首页', path: '/pages/index/index' },
      { icon: '🧪', label: '成分', path: '/pages/ingredient/index' },
      { icon: '🐾', label: '品种', path: '/pages/breed/index' },
      { icon: '👤', label: '我的', path: '/pages/user/index' }
    ]
  },

  methods: {
    onTabTap(e) {
      const index = e.currentTarget.dataset.index
      const tab = this.data.tabs[index]
      if (this.data.selected !== index) {
        wx.redirectTo({ url: tab.path })
      }
    }
  }
})