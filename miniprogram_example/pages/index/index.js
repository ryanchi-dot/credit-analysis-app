// pages/index/index.js
const app = getApp()

Page({
  data: {
    companyName: '',
    templateIndex: 0,
    templates: ['标准模板'],
    loading: false
  },

  onCompanyNameInput(e) {
    this.setData({
      companyName: e.detail.value
    });
  },

  onTemplateChange(e) {
    this.setData({
      templateIndex: parseInt(e.detail.value)
    });
  },

  onSubmit() {
    // 验证输入
    if (!this.data.companyName.trim()) {
      wx.showToast({
        title: '请输入公司名称',
        icon: 'none'
      });
      return;
    }

    // 显示加载状态
    this.setData({ loading: true });

    // 提交分析请求
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/analyze`,
      method: 'POST',
      data: {
        company_name: this.data.companyName,
        template: 'standard'
      },
      success: (res) => {
        console.log('提交成功:', res.data);

        // 跳转到进度页面
        wx.navigateTo({
          url: `/pages/progress/progress?taskId=${res.data.task_id}&companyName=${this.data.companyName}`
        });
      },
      fail: (err) => {
        console.error('提交失败:', err);
        wx.showToast({
          title: '提交失败，请重试',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  }
});
