const { get, post, put } = require('../../../utils/request');

Page({
  data: {
    isEdit: false,
    homeworkId: '',
    submitting: false,
    form: {
      name: '',
      description: '',
      type: 'daily',
      config: {},
      points: '',
      penalty: '',
      expire_days: ''
    },
    typeOptions: [
      { label: '每日', value: 'daily' },
      { label: '每周', value: 'weekly' },
      { label: '每月', value: 'monthly' },
      { label: '自定义', value: 'custom' }
    ],
    weekdays: ['日', '一', '二', '三', '四', '五', '六']
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ isEdit: true, homeworkId: options.id });
      wx.setNavigationBarTitle({ title: '编辑作业' });
      this.loadHomework(options.id);
    }
  },

  loadHomework(id) {
    get('/homeworks/' + id)
      .then(data => {
        this.setData({
          form: {
            name: data.name || '',
            description: data.description || '',
            type: data.type || 'daily',
            config: data.config || {},
            points: data.points ? String(data.points) : '',
            penalty: data.penalty ? String(data.penalty) : '',
            expire_days: data.expire_days ? String(data.expire_days) : ''
          }
        });
      });
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      ['form.' + field]: e.detail.value
    });
  },

  selectType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      'form.type': type,
      'form.config': {}
    });
  },

  toggleWeekday(e) {
    const day = e.currentTarget.dataset.day;
    let weekdays = this.data.form.config.weekdays || [];
    weekdays = weekdays.slice();
    const idx = weekdays.indexOf(day);
    if (idx > -1) {
      weekdays.splice(idx, 1);
    } else {
      weekdays.push(day);
    }
    weekdays.sort((a, b) => a - b);
    this.setData({ 'form.config.weekdays': weekdays });
  },

  toggleMonthDay(e) {
    const day = e.currentTarget.dataset.day;
    let days = this.data.form.config.days || [];
    days = days.slice();
    const idx = days.indexOf(day);
    if (idx > -1) {
      days.splice(idx, 1);
    } else {
      days.push(day);
    }
    days.sort((a, b) => a - b);
    this.setData({ 'form.config.days': days });
  },

  onDateChange(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      ['form.config.' + field]: e.detail.value
    });
  },

  validate() {
    const form = this.data.form;

    if (!form.name.trim()) {
      wx.showToast({ title: '请输入作业名称', icon: 'none' });
      return false;
    }

    if (!form.type) {
      wx.showToast({ title: '请选择作业类型', icon: 'none' });
      return false;
    }

    if (form.type === 'weekly') {
      if (!form.config.weekdays || form.config.weekdays.length === 0) {
        wx.showToast({ title: '请选择周几', icon: 'none' });
        return false;
      }
    }

    if (form.type === 'monthly') {
      if (!form.config.days || form.config.days.length === 0) {
        wx.showToast({ title: '请选择日期', icon: 'none' });
        return false;
      }
    }

    if (form.type === 'custom') {
      if (!form.config.start_date) {
        wx.showToast({ title: '请选择开始日期', icon: 'none' });
        return false;
      }
      if (!form.config.end_date) {
        wx.showToast({ title: '请选择结束日期', icon: 'none' });
        return false;
      }
    }

    if (!form.points || parseInt(form.points) <= 0) {
      wx.showToast({ title: '请输入有效积分', icon: 'none' });
      return false;
    }

    return true;
  },

  onSubmit() {
    if (!this.validate()) return;
    if (this.data.submitting) return;

    this.setData({ submitting: true });

    const form = this.data.form;
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      type: form.type,
      config: form.config,
      points: parseInt(form.points),
      penalty: form.penalty ? parseInt(form.penalty) : 0,
      expire_days: form.expire_days ? parseInt(form.expire_days) : 0
    };

    const req = this.data.isEdit
      ? put('/homeworks/' + this.data.homeworkId, payload)
      : post('/homeworks', payload);

    req.then(() => {
      wx.showToast({
        title: this.data.isEdit ? '修改成功' : '创建成功',
        icon: 'success'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }).catch(() => {
      this.setData({ submitting: false });
    });
  }
});
