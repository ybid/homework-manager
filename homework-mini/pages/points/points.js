const { get } = require('../../utils/request');

Page({
  data: {
    stats: {},
    logs: [],
    loading: true,
    loadingMore: false,
    noMore: false,
    page: 1,
    pageSize: 20
  },

  onLoad() {
    this.loadStats();
    this.loadLogs(true);
  },

  onShow() {
    this.loadStats();
  },

  onPullDownRefresh() {
    Promise.all([
      this.loadStats(),
      this.loadLogs(true)
    ]).then(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (!this.data.noMore && !this.data.loadingMore) {
      this.loadLogs(false);
    }
  },

  loadStats() {
    return get('/points/stats', {}, { noLoading: true })
      .then(data => {
        this.setData({ stats: data });
      });
  },

  loadLogs(refresh) {
    if (refresh) {
      this.setData({ page: 1, noMore: false, loading: true });
    } else {
      this.setData({ loadingMore: true });
    }

    const page = refresh ? 1 : this.data.page;

    return get('/points/logs', {
      page: page,
      page_size: this.data.pageSize
    }, { noLoading: true })
      .then(data => {
        const list = data.list || [];
        const pagination = data.pagination || {};
        const noMore = page >= (pagination.total_pages || 1);

        this.setData({
          logs: refresh ? list : this.data.logs.concat(list),
          page: page + 1,
          noMore: noMore,
          loading: false,
          loadingMore: false
        });
      })
      .catch(() => {
        this.setData({ loading: false, loadingMore: false });
      });
  }
});
