const app = getApp()

Page({
  data: {
    menus: [
      {
        title: '奖品管理',
        desc: '添加、编辑和管理兑换奖品',
        icon: '🎁',
        path: '/pages/admin/reward-edit/reward-edit'
      },
      {
        title: '用户管理',
        desc: '查看用户列表、调整积分',
        icon: '👥',
        path: '/pages/admin/user-list/user-list'
      },
      {
        title: '数据统计',
        desc: '查看平台运营数据概览',
        icon: '📊',
        path: '/pages/admin/stats/stats'
      }
    ]
  },

  onLoad() {
    const userInfo = app.globalData.userInfo
    if (!userInfo || userInfo.role !== 'admin') {
      wx.showToast({ title: '无权限访问', icon: 'none' })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  onMenuTap(e) {
    const path = e.currentTarget.dataset.path
    wx.navigateTo({ url: path })
  }
})
