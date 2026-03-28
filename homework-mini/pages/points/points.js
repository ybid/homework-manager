// pages/points/points.js
const http = require('../../utils/request');

Page({
  data: {
    stats: {},
    logs: [],
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true,
  },

  onLoad() {
    this.loadStats();
    this.loadLogs();
  },

  onShow() {
    this.loadStats();
  },

  async loadStats() {
    try {
      const stats = await http.get('/points/stats');
      this.setData({ stats });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'error' });
    }
  },

  async loadLogs(refresh = false) {
    if (this.data.loading) return;

    const page = refresh ? 1 : this.data.page;
    this.setData({ loading: true });

    try {
      const result = await http.get('/points/logs', {
        page,
        page_size: this.data.pageSize,
      });

      const logs = refresh ? result.list : [...this.data.logs, ...result.list];

      this.setData({
        logs,
        page: page + 1,
        hasMore: logs.length < result.total,
      });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'error' });
    } finally {
      this.setData({ loading: false });
    }
  },

  onReachBottom() {
    if (this.data.hasMore) {
      this.loadLogs();
    }
  },

  onPullDownRefresh() {
    Promise.all([
      this.loadStats(),
      this.loadLogs(true),
    ]).then(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取类型标签样式
  getTypeClass(type) {
    return type === 'earn' ? 'earn' : type === 'spend' ? 'spend' : 'expire';
  },
});
