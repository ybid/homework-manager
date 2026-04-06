const { get, post } = require('../../utils/request');

Page({
  data: {
    currentTab: 0,
    userPoints: 0,
    rewards: [],
    records: [],
    loading: true,
    recordLoading: false,
    showModal: false,
    selectedReward: {},
    showSuccess: false,
    successMsg: '',
    rewardPage: 1,
    recordPage: 1,
    pageSize: 20,
    rewardNoMore: false,
    recordNoMore: false
  },

  onLoad() {
    this.loadPoints();
    this.loadRewards(true);
  },

  onShow() {
    this.loadPoints();
  },

  onPullDownRefresh() {
    const p = this.data.currentTab === 0
      ? this.loadRewards(true)
      : this.loadRecords(true);

    Promise.all([this.loadPoints(), p]).then(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (this.data.currentTab === 0 && !this.data.rewardNoMore) {
      this.loadRewards(false);
    } else if (this.data.currentTab === 1 && !this.data.recordNoMore) {
      this.loadRecords(false);
    }
  },

  switchTab(e) {
    const tab = parseInt(e.currentTarget.dataset.tab);
    this.setData({ currentTab: tab });
    if (tab === 1 && this.data.records.length === 0) {
      this.loadRecords(true);
    }
  },

  loadPoints() {
    return get('/points/stats', {}, { noLoading: true })
      .then(data => {
        this.setData({ userPoints: data.total_points || 0 });
      });
  },

  loadRewards(refresh) {
    if (refresh) {
      this.setData({ rewardPage: 1, rewardNoMore: false, loading: true });
    }
    const page = refresh ? 1 : this.data.rewardPage;

    return get('/rewards', { page, page_size: this.data.pageSize }, { noLoading: true })
      .then(data => {
        const list = data.list || [];
        const pagination = data.pagination || {};
        this.setData({
          rewards: refresh ? list : this.data.rewards.concat(list),
          rewardPage: page + 1,
          rewardNoMore: page >= (pagination.total_pages || 1),
          loading: false
        });
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },

  loadRecords(refresh) {
    if (refresh) {
      this.setData({ recordPage: 1, recordNoMore: false, recordLoading: true });
    }
    const page = refresh ? 1 : this.data.recordPage;

    return get('/exchanges', { page, page_size: this.data.pageSize }, { noLoading: true })
      .then(data => {
        const list = data.list || [];
        const pagination = data.pagination || {};
        this.setData({
          records: refresh ? list : this.data.records.concat(list),
          recordPage: page + 1,
          recordNoMore: page >= (pagination.total_pages || 1),
          recordLoading: false
        });
      })
      .catch(() => {
        this.setData({ recordLoading: false });
      });
  },

  onRewardTap(e) {
    const { item, disabled } = e.detail;
    if (disabled) {
      wx.showToast({ title: '积分不足', icon: 'none' });
      return;
    }
    this.setData({
      showModal: true,
      selectedReward: item
    });
  },

  closeModal() {
    this.setData({ showModal: false });
  },

  confirmExchange() {
    const reward = this.data.selectedReward;
    this.setData({ showModal: false });

    post('/rewards/' + reward.id + '/exchange')
      .then(data => {
        this.setData({
          showSuccess: true,
          successMsg: data.reward_name + ' 兑换成功！剩余 ' + data.remaining_points + ' 积分',
          userPoints: data.remaining_points
        });

        setTimeout(() => {
          this.setData({ showSuccess: false });
        }, 2000);

        this.loadRewards(true);
      });
  }
});
