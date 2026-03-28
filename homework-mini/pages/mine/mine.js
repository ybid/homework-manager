// pages/mine/mine.js
const app = getApp();
const http = require('../../utils/request');

Page({
  data: {
    userInfo: null,
    stats: {},
  },

  onLoad() {
    this.setData({ userInfo: app.globalData.userInfo });
  },

  onShow() {
    if (app.globalData.token) {
      this.loadUserInfo();
      this.loadStats();
    }
  },

  async loadUserInfo() {
    try {
      const userInfo = await http.get('/user/info');
      this.setData({ userInfo });
      app.globalData.userInfo = userInfo;
      wx.setStorageSync('userInfo', userInfo);
    } catch (error) {
      console.error('加载用户信息失败:', error);
    }
  },

  async loadStats() {
    try {
      const stats = await http.get('/points/stats');
      this.setData({ stats });
    } catch (error) {
      console.error('加载积分统计失败:', error);
    }
  },

  // 重新登录
  async onLogin() {
    try {
      const result = await app.login();
      this.setData({ userInfo: result.user });
      this.loadStats();
      wx.showToast({ title: '登录成功', icon: 'success' });
    } catch (error) {
      wx.showToast({ title: '登录失败', icon: 'error' });
    }
  },

  // 查看我的作业
  onMyHomeworks() {
    // TODO: 跳转到我的作业页面
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  // 查看设置
  onSettings() {
    // TODO: 跳转到设置页面
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },
});
