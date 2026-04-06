function formatDate(date, fmt = 'YYYY-MM-DD') {
  if (typeof date === 'string') date = new Date(date);
  if (!(date instanceof Date)) date = new Date();

  const o = {
    'YYYY': date.getFullYear(),
    'MM': padZero(date.getMonth() + 1),
    'DD': padZero(date.getDate()),
    'HH': padZero(date.getHours()),
    'mm': padZero(date.getMinutes()),
    'ss': padZero(date.getSeconds())
  };

  let result = fmt;
  Object.keys(o).forEach(key => {
    result = result.replace(key, o[key]);
  });
  return result;
}

function padZero(n) {
  return n < 10 ? '0' + n : '' + n;
}

function getWeekday(date) {
  if (typeof date === 'string') date = new Date(date);
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return days[date.getDay()];
}

function getRelativeTime(dateStr) {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return minutes + '分钟前';
  if (hours < 24) return hours + '小时前';
  if (days < 7) return days + '天前';
  return formatDate(date, 'MM-DD HH:mm');
}

function getDaysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
  return new Date(year, month - 1, 1).getDay();
}

function throttle(fn, delay = 300) {
  let last = 0;
  return function () {
    const now = Date.now();
    if (now - last >= delay) {
      last = now;
      return fn.apply(this, arguments);
    }
  };
}

function debounce(fn, delay = 300) {
  let timer = null;
  return function () {
    if (timer) clearTimeout(timer);
    const args = arguments;
    const ctx = this;
    timer = setTimeout(() => {
      fn.apply(ctx, args);
    }, delay);
  };
}

function rpxToPx(rpx) {
  const systemInfo = wx.getSystemInfoSync();
  return rpx * systemInfo.windowWidth / 750;
}

function getTypeLabel(type) {
  const map = {
    daily: '每日',
    weekly: '每周',
    monthly: '每月',
    custom: '自定义'
  };
  return map[type] || type;
}

function getTypeColor(type) {
  const map = {
    daily: '#4A90D9',
    weekly: '#52C41A',
    monthly: '#FFA940',
    custom: '#FF6B6B'
  };
  return map[type] || '#999';
}

module.exports = {
  formatDate,
  padZero,
  getWeekday,
  getRelativeTime,
  getDaysInMonth,
  getFirstDayOfMonth,
  throttle,
  debounce,
  rpxToPx,
  getTypeLabel,
  getTypeColor
};
