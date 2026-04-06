const { get, del } = require('../../../utils/request');
const util = require('../../../utils/util');

Page({
  data: {
    homework: null,
    typeLabel: '',
    typeColor: ''
  },

  onLoad(options) {
    if (options.id) {
      this.loadDetail(options.id);
    }
  },

  loadDetail(id) {
    get('/homeworks/' + id)
      .then(data => {
        this.setData({
          homework: data,
          typeLabel: util.getTypeLabel(data.type),
          typeColor: util.getTypeColor(data.type)
        });
      });
  },

  onEdit() {
    wx.navigateTo({
      url: '/pages/homework/add/add?id=' + this.data.homework.id
    });
  },

  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除吗？',
      confirmColor: '#FF6B6B',
      success: (res) => {
        if (res.confirm) {
          del('/homeworks/' + this.data.homework.id)
            .then(() => {
              wx.showToast({ title: '删除成功', icon: 'success' });
              setTimeout(() => {
                wx.navigateBack();
              }, 1500);
            });
        }
      }
    });
  }
});
