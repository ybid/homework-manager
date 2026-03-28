// pages/exchange/exchange.js
const app = getApp();
const http = require('../../utils/request');

Page({
  data: {
    rewards: [],
    exchanges: [],
    tab: 'rewards', // rewards | records
    loading: false,
  },

  onLoad() {
    this.loadRewards();
    this.loadExchanges();
  },

  onShow() {
    this.loadRewards();
  },

  // 切换 tab
  switchTab(e) {
    const { tab } = e.currentTarget.dataset;
    this.setData({ tab });
  },

  async loadRewards() {
    this.setData({ loading: true });
    try {
      const rewards = await http.get('/rewards');
      this.setData({ rewards });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'error' });
    } finally {
      this.setData({ loading: false });
    }
  },

  async loadExchanges() {
    try {
      const result = await http.get('/rewards/exchanges');
      this.setData({ exchanges: result.list || [] });
    } catch (error) {
      console.error('加载兑换记录失败:', error);
    }
  },

  // 兑换奖品
  onExchange(e) {
    const { id, name, stock, points } = e.currentTarget.dataset;

    if (stock <= 0) {
      wx.showToast({ title: '库存不足', icon: 'error' });
      return;
    }

    const userInfo = app.globalData.userInfo;
    if (userInfo && userInfo.total_points < points) {
      wx.showToast({ title: '积分不足', icon: 'error' });
      return;
    }

    wx.showModal({
      title: '确认兑换',
      content: `确定要用 ${points} 积分兑换 ${name} 吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            const result = await http.post(`/rewards/${id}/exchange`, {});
            wx.showToast({
              title: '兑换成功',
              icon: 'success',
            });
            // 更新用户积分
            if (app.globalData.userInfo) {
              app.globalData.userInfo.total_points = result.remaining_points;
              wx.setStorageSync('userInfo', app.globalData.userInfo);
            }
            this.loadRewards();
            this.loadExchanges();
          } catch (error) {
            wx.showToast({ title: error.message, icon: 'error' });
          }
        }
      },
    });
  },

  onPullDownRefresh() {
    Promise.all([
      this.loadRewards(),
      this.loadExchanges(),
    ]).then(() => {
      wx.stopPullDownRefresh();
    });
  },
});
