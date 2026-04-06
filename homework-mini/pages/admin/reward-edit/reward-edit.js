const app = getApp()
const { get, post, put } = require('../../../utils/request')

Page({
  data: {
    id: '',
    isEdit: false,
    form: {
      name: '',
      description: '',
      image_url: '',
      points_cost: '',
      stock: '',
      status: 'active'
    },
    statusOptions: ['上架', '下架'],
    statusIndex: 0,
    submitting: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({
        id: options.id,
        isEdit: true
      })
      wx.setNavigationBarTitle({ title: '编辑奖品' })
      this.loadReward(options.id)
    } else {
      wx.setNavigationBarTitle({ title: '添加奖品' })
    }
  },

  loadReward(id) {
    get('/rewards')
      .then(data => {
        const list = data.list || data.rewards || data || []
        const reward = list.find(r => String(r.id) === String(id))
        if (reward) {
          const statusIndex = reward.status === 'inactive' ? 1 : 0
          this.setData({
            form: {
              name: reward.name || '',
              description: reward.description || '',
              image_url: reward.image_url || '',
              points_cost: String(reward.points_cost || ''),
              stock: String(reward.stock || ''),
              status: reward.status || 'active'
            },
            statusIndex
          })
        } else {
          wx.showToast({ title: '奖品不存在', icon: 'none' })
        }
      })
      .catch(() => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  onInputChange(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`form.${field}`]: e.detail.value
    })
  },

  onStatusChange(e) {
    const index = Number(e.detail.value)
    this.setData({
      statusIndex: index,
      'form.status': index === 0 ? 'active' : 'inactive'
    })
  },

  validateForm() {
    const { name, points_cost, stock } = this.data.form
    if (!name.trim()) {
      wx.showToast({ title: '请输入奖品名称', icon: 'none' })
      return false
    }
    if (!points_cost || Number(points_cost) <= 0) {
      wx.showToast({ title: '请输入有效的所需积分', icon: 'none' })
      return false
    }
    if (!stock || Number(stock) < 0) {
      wx.showToast({ title: '请输入有效的库存数量', icon: 'none' })
      return false
    }
    return true
  },

  onSubmit() {
    if (!this.validateForm()) return
    if (this.data.submitting) return

    this.setData({ submitting: true })

    const { form, isEdit, id } = this.data
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      image_url: form.image_url.trim(),
      points_cost: Number(form.points_cost),
      stock: Number(form.stock),
      status: form.status
    }

    const req = isEdit
      ? put(`/admin/rewards/${id}`, payload)
      : post('/admin/rewards', payload)

    req
      .then(() => {
        wx.showToast({ title: isEdit ? '修改成功' : '添加成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      })
      .catch(() => {
        this.setData({ submitting: false })
      })
  }
})
