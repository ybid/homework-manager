const util = require('../../utils/util');

Component({
  properties: {
    item: {
      type: Object,
      value: {}
    },
    showAction: {
      type: Boolean,
      value: true
    }
  },

  data: {
    showPointsAnim: false,
    typeLabel: '',
    typeColor: ''
  },

  observers: {
    'item.type': function (type) {
      this.setData({
        typeLabel: util.getTypeLabel(type),
        typeColor: util.getTypeColor(type)
      });
    }
  },

  methods: {
    onCardTap() {
      this.triggerEvent('cardtap', { item: this.data.item });
    },

    onComplete() {
      const item = this.data.item;
      if (item.completed) return;

      this.triggerEvent('complete', {
        item: item,
        callback: (success) => {
          if (success) {
            this.setData({ showPointsAnim: true });
            setTimeout(() => {
              this.setData({ showPointsAnim: false });
            }, 1300);
          }
        }
      });
    }
  }
});
