const app = getApp()
const { get } = require('../../../utils/request')

Page({
  data: {
    stats: null,
    loading: true,
    cards: []
  },

  onLoad() {
    this.loadStats()
  },

  onPullDownRefresh() {
    this.loadStats()
    wx.stopPullDownRefresh()
  },

  loadStats() {
    this.setData({ loading: true })

    get('/admin/stats', {}, { noLoading: true })
      .then(data => {
        const cards = [
          { label: '总用户数', value: data.total_users || 0, icon: '👥', color: '#4A90D9' },
          { label: '今日活跃', value: data.today_active || 0, icon: '🔥', color: '#FF6B6B' },
          { label: '总作业数', value: data.total_homework || data.total_tasks || 0, icon: '📝', color: '#52C41A' },
          { label: '今日打卡', value: data.today_checkins || 0, icon: '✅', color: '#FFA940' },
          { label: '总积分发放', value: data.total_points_issued || 0, icon: '⬆️', color: '#52C41A' },
          { label: '总积分消耗', value: data.total_points_consumed || 0, icon: '⬇️', color: '#FF6B6B' }
        ]
        this.setData({ stats: data, cards, loading: false })
      })
      .catch(() => {
        this.setData({ loading: false })
      })
  }
})
