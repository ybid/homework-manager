Component({
  properties: {
    item: {
      type: Object,
      value: {}
    },
    userPoints: {
      type: Number,
      value: 0
    }
  },

  data: {
    disabled: false
  },

  observers: {
    'item.points, userPoints': function (needPoints, userPoints) {
      this.setData({
        disabled: userPoints < needPoints
      });
    }
  },

  methods: {
    onTap() {
      this.triggerEvent('tap', { item: this.data.item, disabled: this.data.disabled });
    }
  }
});
