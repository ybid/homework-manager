const { get } = require('../../../utils/request');

Page({
  data: {
    homeworks: [],
    loading: true,
    noMore: false,
    page: 1,
    pageSize: 20,
    currentStatus: '',
    statusOptions: [
      { label: '全部', value: '' },
      { label: '进行中', value: 'active' },
      { label: '已完成', value: 'completed' },
      { label: '已过期', value: 'expired' }
    ]
  },

  onLoad() {
    this.loadList(true);
  },

  onPullDownRefresh() {
    this.loadList(true).then(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (!this.data.noMore) {
      this.loadList(false);
    }
  },

  onFilter(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({ currentStatus: status });
    this.loadList(true);
  },

  loadList(refresh) {
    if (refresh) {
      this.setData({ page: 1, noMore: false, loading: true });
    }

    const page = refresh ? 1 : this.data.page;
    const params = {
      page,
      page_size: this.data.pageSize
    };
    if (this.data.currentStatus) {
      params.status = this.data.currentStatus;
    }

    return get('/homeworks', params, { noLoading: true })
      .then(data => {
        const list = data.list || [];
        const pagination = data.pagination || {};
        this.setData({
          homeworks: refresh ? list : this.data.homeworks.concat(list),
          page: page + 1,
          noMore: page >= (pagination.total_pages || 1),
          loading: false
        });
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },

  onCardTap(e) {
    const { item } = e.detail;
    wx.navigateTo({
      url: '/pages/homework/detail/detail?id=' + item.id
    });
  },

  goAdd() {
    wx.navigateTo({
      url: '/pages/homework/add/add'
    });
  }
});
