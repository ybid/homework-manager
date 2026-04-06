const { get, post } = require('../../utils/request');
const util = require('../../utils/util');

Page({
  data: {
    today: '',
    weekday: '',
    homeworks: [],
    stats: {
      total: 0,
      completed: 0,
      pending: 0,
      today_points: 0
    },
    loading: true
  },

  onLoad() {
    const now = new Date();
    this.setData({
      today: util.formatDate(now, 'YYYY年MM月DD日'),
      weekday: util.getWeekday(now)
    });
  },

  onShow() {
    this.loadTodayData();
  },

  onPullDownRefresh() {
    this.loadTodayData().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  loadTodayData() {
    this.setData({ loading: true });
    return get('/homeworks/today', {}, { noLoading: true })
      .then(data => {
        this.setData({
          homeworks: data.list || [],
          stats: data.stats || { total: 0, completed: 0, pending: 0, today_points: 0 },
          loading: false
        });
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },

  onComplete(e) {
    const { item, callback } = e.detail;
    post('/homeworks/' + item.id + '/complete')
      .then(data => {
        wx.showToast({
          title: '+' + data.points + '积分',
          icon: 'none',
          duration: 1500
        });
        if (callback) callback(true);
        setTimeout(() => {
          this.loadTodayData();
        }, 1000);
      })
      .catch(() => {
        if (callback) callback(false);
      });
  },

  onCardTap(e) {
    const { item } = e.detail;
    wx.navigateTo({
      url: '/pages/homework/detail/detail?id=' + item.id
    });
  },

  goAddHomework() {
    wx.navigateTo({
      url: '/pages/homework/add/add'
    });
  }
});
