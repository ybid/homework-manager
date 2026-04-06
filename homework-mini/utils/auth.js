const config = require('./config');
const { post } = require('./request');

function login() {
  return new Promise((resolve, reject) => {
    wx.login({
      success(res) {
        if (res.code) {
          post('/auth/login', { code: res.code }, { noAuth: true, noLoading: true })
            .then(data => {
              wx.setStorageSync(config.storageKeys.token, data.token);
              wx.setStorageSync(config.storageKeys.userInfo, data.user);
              const app = getApp();
              app.globalData.token = data.token;
              app.globalData.userInfo = data.user;
              app.globalData.isNew = data.is_new;
              app.globalData.isLoggedIn = true;
              resolve(data);
            })
            .catch(err => {
              reject(err);
            });
        } else {
          reject(new Error('wx.login failed: ' + res.errMsg));
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
}

function getToken() {
  return wx.getStorageSync(config.storageKeys.token) || '';
}

function getUserInfo() {
  return wx.getStorageSync(config.storageKeys.userInfo) || null;
}

function isLoggedIn() {
  return !!getToken();
}

function isAdmin() {
  const user = getUserInfo();
  return user && user.role === 'admin';
}

function logout() {
  wx.removeStorageSync(config.storageKeys.token);
  wx.removeStorageSync(config.storageKeys.userInfo);
  const app = getApp();
  app.globalData.token = '';
  app.globalData.userInfo = null;
  app.globalData.isLoggedIn = false;
}

module.exports = {
  login,
  getToken,
  getUserInfo,
  isLoggedIn,
  isAdmin,
  logout
};
