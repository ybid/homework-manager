const { get } = require('../../utils/request');
const util = require('../../utils/util');

Page({
  data: {
    year: 0,
    month: 0,
    calendarDays: [],
    emptyDays: [],
    selectedDate: '',
    selectedDayData: null,
    calendarMap: {}
  },

  onLoad() {
    const now = new Date();
    this.setData({
      year: now.getFullYear(),
      month: now.getMonth() + 1
    });
    this.loadCalendar();
  },

  prevMonth() {
    let { year, month } = this.data;
    month--;
    if (month < 1) {
      month = 12;
      year--;
    }
    this.setData({ year, month, selectedDate: '', selectedDayData: null });
    this.loadCalendar();
  },

  nextMonth() {
    let { year, month } = this.data;
    month++;
    if (month > 12) {
      month = 1;
      year++;
    }
    this.setData({ year, month, selectedDate: '', selectedDayData: null });
    this.loadCalendar();
  },

  loadCalendar() {
    const { year, month } = this.data;

    get('/homeworks/calendar', { year, month }, { noLoading: true })
      .then(data => {
        this.buildCalendar(data.days || []);
      })
      .catch(() => {
        this.buildCalendar([]);
      });
  },

  buildCalendar(days) {
    const { year, month } = this.data;
    const daysInMonth = util.getDaysInMonth(year, month);
    const firstDay = util.getFirstDayOfMonth(year, month);
    const today = util.formatDate(new Date());

    const calendarMap = {};
    days.forEach(d => {
      calendarMap[d.date] = d;
    });

    const calendarDays = [];
    for (let i = 1; i <= daysInMonth; i++) {
      const dateStr = year + '-' + util.padZero(month) + '-' + util.padZero(i);
      const dayData = calendarMap[dateStr] || {};
      calendarDays.push({
        day: i,
        date: dateStr,
        total: dayData.total || 0,
        completed: dayData.completed || 0,
        list: dayData.list || [],
        isToday: dateStr === today
      });
    }

    const emptyDays = new Array(firstDay).fill(0);

    this.setData({
      calendarDays,
      emptyDays,
      calendarMap
    });
  },

  selectDay(e) {
    const date = e.currentTarget.dataset.date;
    const dayItem = this.data.calendarDays.find(d => d.date === date);

    this.setData({
      selectedDate: date,
      selectedDayData: dayItem || { total: 0, completed: 0, list: [] }
    });
  }
});
