// app.js
App({
  globalData: {
    baseUrl: 'https://your-domain.com/api/v1', // 修改为你的服务器地址
    token: null,
    userInfo: null,
  },

  onLaunch() {
    // 检查登录状态
    this.checkLogin();
  },

  checkLogin() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
      this.globalData.userInfo = wx.getStorageSync('userInfo');
    }
  },

  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            wx.request({
              url: `${this.globalData.baseUrl}/auth/login`,
              method: 'POST',
              data: { code: res.code },
              success: (result) => {
                if (result.data.code === 0) {
                  const { token, user, is_new } = result.data.data;
                  this.globalData.token = token;
                  this.globalData.userInfo = user;
                  wx.setStorageSync('token', token);
                  wx.setStorageSync('userInfo', user);
                  resolve({ token, user, is_new });
                } else {
                  reject(new Error(result.data.message));
                }
              },
              fail: reject,
            });
          } else {
            reject(new Error('wx.login 失败'));
          }
        },
        fail: reject,
      });
    });
  },
});
