const auth = require('./utils/auth');

App({
  globalData: {
    token: '',
    userInfo: null,
    isLoggedIn: false,
    isNew: false
  },

  onLaunch() {
    const token = wx.getStorageSync('auth_token');
    const userInfo = wx.getStorageSync('user_info');

    if (token) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      this.globalData.isLoggedIn = true;
    }

    this.autoLogin();
  },

  autoLogin() {
    auth.login()
      .then(data => {
        console.log('Auto login success:', data.user.nick_name);
        if (this._loginCallbacks) {
          this._loginCallbacks.forEach(cb => cb(data));
          this._loginCallbacks = [];
        }
      })
      .catch(err => {
        console.error('Auto login failed:', err);
        if (this._loginCallbacks) {
          this._loginCallbacks.forEach(cb => cb(null));
          this._loginCallbacks = [];
        }
      });
  },

  onLoginReady(callback) {
    if (this.globalData.isLoggedIn) {
      callback({
        token: this.globalData.token,
        user: this.globalData.userInfo
      });
    } else {
      if (!this._loginCallbacks) this._loginCallbacks = [];
      this._loginCallbacks.push(callback);
    }
  }
});
