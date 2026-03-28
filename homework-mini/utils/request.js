// utils/request.js
const app = getApp();

// 封装请求方法
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    const token = app.globalData.token;
    const header = {
      'Content-Type': 'application/json',
      ...options.header,
    };

    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header,
      success: (res) => {
        if (res.statusCode === 401) {
          // token 过期，重新登录
          app.login().then(() => {
            request(url, options).then(resolve).catch(reject);
          }).catch(reject);
          return;
        }

        if (res.data.code === 0) {
          resolve(res.data.data);
        } else {
          reject(new Error(res.data.message || '请求失败'));
        }
      },
      fail: reject,
    });
  });
}

// 快捷方法
const http = {
  get: (url, data) => request(url, { method: 'GET', data }),
  post: (url, data) => request(url, { method: 'POST', data }),
  put: (url, data) => request(url, { method: 'PUT', data }),
  delete: (url, data) => request(url, { method: 'DELETE', data }),
};

module.exports = http;
