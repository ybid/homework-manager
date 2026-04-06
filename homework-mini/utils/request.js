const config = require('./config');

let isRefreshing = false;
let pendingRequests = [];

function getToken() {
  return wx.getStorageSync(config.storageKeys.token) || '';
}

function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    noAuth = false,
    noLoading = false,
    showError = true
  } = options;

  const fullUrl = url.startsWith('http') ? url : config.baseUrl + url;

  if (!noLoading) {
    wx.showLoading({ title: '加载中...', mask: true });
  }

  return new Promise((resolve, reject) => {
    const header = {
      'Content-Type': 'application/json'
    };

    if (!noAuth) {
      const token = getToken();
      if (token) {
        header['Authorization'] = 'Bearer ' + token;
      }
    }

    wx.request({
      url: fullUrl,
      method,
      data,
      header,
      success(res) {
        if (!noLoading) wx.hideLoading();

        if (res.statusCode === 401) {
          handleUnauthorized(url, options, resolve, reject);
          return;
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          const body = res.data;
          if (body.code === 0) {
            resolve(body.data);
          } else {
            const errMsg = body.message || '请求失败';
            if (showError) {
              wx.showToast({ title: errMsg, icon: 'none', duration: 2000 });
            }
            reject(new Error(errMsg));
          }
        } else {
          const errMsg = '服务器错误 (' + res.statusCode + ')';
          if (showError) {
            wx.showToast({ title: errMsg, icon: 'none', duration: 2000 });
          }
          reject(new Error(errMsg));
        }
      },
      fail(err) {
        if (!noLoading) wx.hideLoading();
        const errMsg = '网络连接失败';
        if (showError) {
          wx.showToast({ title: errMsg, icon: 'none', duration: 2000 });
        }
        reject(new Error(errMsg));
      }
    });
  });
}

function handleUnauthorized(url, options, resolve, reject) {
  if (isRefreshing) {
    pendingRequests.push({ url, options, resolve, reject });
    return;
  }

  isRefreshing = true;

  wx.login({
    success(loginRes) {
      if (loginRes.code) {
        wx.request({
          url: config.baseUrl + '/auth/login',
          method: 'POST',
          data: { code: loginRes.code },
          header: { 'Content-Type': 'application/json' },
          success(res) {
            isRefreshing = false;
            if (res.statusCode === 200 && res.data.code === 0) {
              const data = res.data.data;
              wx.setStorageSync(config.storageKeys.token, data.token);
              wx.setStorageSync(config.storageKeys.userInfo, data.user);
              const app = getApp();
              app.globalData.token = data.token;
              app.globalData.userInfo = data.user;

              request(url, options).then(resolve).catch(reject);

              pendingRequests.forEach(p => {
                request(p.url, p.options).then(p.resolve).catch(p.reject);
              });
              pendingRequests = [];
            } else {
              rejectAll(reject, new Error('登录失败，请重试'));
            }
          },
          fail() {
            isRefreshing = false;
            rejectAll(reject, new Error('登录失败，请重试'));
          }
        });
      } else {
        isRefreshing = false;
        rejectAll(reject, new Error('获取登录凭证失败'));
      }
    },
    fail() {
      isRefreshing = false;
      rejectAll(reject, new Error('微信登录失败'));
    }
  });
}

function rejectAll(reject, err) {
  reject(err);
  pendingRequests.forEach(p => p.reject(err));
  pendingRequests = [];
  wx.showToast({ title: err.message, icon: 'none' });
}

function get(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'GET', data });
}

function post(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'POST', data });
}

function put(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'PUT', data });
}

function del(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'DELETE', data });
}

module.exports = { request, get, post, put, del };
