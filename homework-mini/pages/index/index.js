// pages/index/index.js
const app = getApp();
const http = require('../../utils/request');

Page({
  data: {
    today: {},
    loading: false,
    showAddModal: false,
    addForm: {
      name: '',
      description: '',
      type: 'daily',
      points: 10,
      penalty: 0,
    },
    types: [
      { label: '每日', value: 'daily' },
      { label: '每周', value: 'weekly' },
      { label: '每月', value: 'monthly' },
      { label: '自定义', value: 'custom' },
    ],
  },

  onLoad() {
    this.checkLogin();
  },

  onShow() {
    if (app.globalData.token) {
      this.loadTodayHomework();
    }
  },

  async checkLogin() {
    if (!app.globalData.token) {
      try {
        await app.login();
        this.loadTodayHomework();
      } catch (error) {
        wx.showToast({ title: '登录失败', icon: 'error' });
      }
    }
  },

  async loadTodayHomework() {
    this.setData({ loading: true });
    try {
      const today = await http.get('/homeworks/today');
      this.setData({ today });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'error' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 完成打卡
  async onComplete(e) {
    const { id } = e.currentTarget.dataset;

    wx.showModal({
      title: '确认打卡',
      content: '确定要完成这个作业吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            const result = await http.post(`/points/complete/${id}`, {});
            wx.showToast({
              title: `+${result.points}积分`,
              icon: 'success',
            });
            this.loadTodayHomework();
          } catch (error) {
            wx.showToast({ title: error.message, icon: 'error' });
          }
        }
      },
    });
  },

  // 显示添加弹窗
  showAdd() {
    this.setData({ showAddModal: true });
  },

  // 隐藏添加弹窗
  hideAdd() {
    this.setData({ showAddModal: false });
  },

  // 表单输入
  onInput(e) {
    const { field } = e.currentTarget.dataset;
    const { value } = e.detail;
    this.setData({
      [`addForm.${field}`]: value,
    });
  },

  // 选择类型
  onTypeChange(e) {
    this.setData({
      'addForm.type': e.detail.value,
    });
  },

  // 提交添加
  async onAdd() {
    const { addForm } = this.data;

    if (!addForm.name) {
      wx.showToast({ title: '请输入作业名称', icon: 'error' });
      return;
    }

    try {
      await http.post('/homeworks', addForm);
      wx.showToast({ title: '添加成功', icon: 'success' });
      this.hideAdd();
      this.loadTodayHomework();
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'error' });
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadTodayHomework().then(() => {
      wx.stopPullDownRefresh();
    });
  },
});
