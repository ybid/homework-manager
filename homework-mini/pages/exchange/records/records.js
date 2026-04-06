const app = getApp()
const { get } = require('../../../utils/request')

Page({
  data: {
    records: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    loading: false,
    isEmpty: false
  },

  onLoad() {
    this.loadRecords()
  },

  loadRecords(reset = false) {
    if (this.data.loading) return
    if (!reset && !this.data.hasMore) return

    const page = reset ? 1 : this.data.page

    this.setData({ loading: true })

    get('/exchanges', { page, page_size: this.data.pageSize }, { noLoading: true })
      .then(data => {
        const list = data.list || data.records || []
        const records = reset ? list : this.data.records.concat(list)
        this.setData({
          records,
          page: page + 1,
          hasMore: list.length >= this.data.pageSize,
          isEmpty: records.length === 0,
          loading: false
        })
      })
      .catch(() => {
        this.setData({ loading: false })
      })
  },

  onPullDownRefresh() {
    this.loadRecords(true)
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    this.loadRecords()
  },

  getStatusText(status) {
    const map = {
      pending: '处理中',
      completed: '已完成',
      rejected: '已拒绝',
      cancelled: '已取消'
    }
    return map[status] || status
  },

  getStatusClass(status) {
    const map = {
      pending: 'status-pending',
      completed: 'status-completed',
      rejected: 'status-rejected',
      cancelled: 'status-cancelled'
    }
    return map[status] || ''
  },

  formatTime(time) {
    if (!time) return ''
    const d = new Date(time)
    const pad = n => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
})
