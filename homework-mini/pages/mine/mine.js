const { get } = require('../../utils/request');
const auth = require('../../utils/auth');

Page({
  data: {
    userInfo: {},
    points: 0,
    isAdmin: false
  },

  onShow() {
    this.loadUserInfo();
    this.loadPoints();
  },

  loadUserInfo() {
    const cached = auth.getUserInfo();
    if (cached) {
      this.setData({
        userInfo: cached,
        isAdmin: cached.role === 'admin'
      });
    }

    get('/user/info', {}, { noLoading: true, showError: false })
      .then(data => {
        this.setData({
          userInfo: data,
          isAdmin: data.role === 'admin'
        });
        wx.setStorageSync('user_info', data);
      });
  },

  loadPoints() {
    get('/points/stats', {}, { noLoading: true, showError: false })
      .then(data => {
        this.setData({ points: data.total_points || 0 });
      });
  },

  goPage(e) {
    const url = e.currentTarget.dataset.url;
    wx.navigateTo({ url });
  }
});
