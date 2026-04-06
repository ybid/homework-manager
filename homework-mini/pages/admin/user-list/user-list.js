const app = getApp()
const { get, post } = require('../../../utils/request')

Page({
  data: {
    users: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    loading: false,
    isEmpty: false,
    showAdjust: false,
    currentUser: null,
    adjustPoints: '',
    adjustReason: ''
  },

  onLoad() {
    this.loadUsers()
  },

  loadUsers(reset = false) {
    if (this.data.loading) return
    if (!reset && !this.data.hasMore) return

    const page = reset ? 1 : this.data.page
    this.setData({ loading: true })

    get('/admin/users', { page, page_size: this.data.pageSize }, { noLoading: true })
      .then(data => {
        const list = data.list || data.users || []
        const users = reset ? list : this.data.users.concat(list)
        this.setData({
          users,
          page: page + 1,
          hasMore: list.length >= this.data.pageSize,
          isEmpty: users.length === 0,
          loading: false
        })
      })
      .catch(() => {
        this.setData({ loading: false })
      })
  },

  onPullDownRefresh() {
    this.loadUsers(true)
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    this.loadUsers()
  },

  onUserTap(e) {
    const user = e.currentTarget.dataset.user
    this.setData({
      showAdjust: true,
      currentUser: user,
      adjustPoints: '',
      adjustReason: ''
    })
  },

  onAdjustPointsInput(e) {
    this.setData({ adjustPoints: e.detail.value })
  },

  onAdjustReasonInput(e) {
    this.setData({ adjustReason: e.detail.value })
  },

  onCancelAdjust() {
    this.setData({
      showAdjust: false,
      currentUser: null,
      adjustPoints: '',
      adjustReason: ''
    })
  },

  onConfirmAdjust() {
    const { currentUser, adjustPoints, adjustReason } = this.data
    const points = Number(adjustPoints)

    if (!adjustPoints || points === 0) {
      wx.showToast({ title: '请输入有效的积分数', icon: 'none' })
      return
    }
    if (!adjustReason.trim()) {
      wx.showToast({ title: '请输入调整原因', icon: 'none' })
      return
    }

    post('/admin/points/adjust', {
      user_id: currentUser.id,
      points: points,
      reason: adjustReason.trim()
    })
      .then(() => {
        wx.showToast({ title: '调整成功', icon: 'success' })
        this.setData({ showAdjust: false })
        this.loadUsers(true)
      })
      .catch(() => {})
  },

  onMaskTap() {
    this.setData({ showAdjust: false })
  },

  formatTime(time) {
    if (!time) return ''
    const d = new Date(time)
    const pad = n => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  },

  getRoleText(role) {
    const map = { admin: '管理员', teacher: '老师', parent: '家长', student: '学生' }
    return map[role] || role
  }
})
