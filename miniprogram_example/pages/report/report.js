// pages/report/report.js
const app = getApp()

Page({
  data: {
    taskId: '',
    companyName: '',
    report: ''
  },

  onLoad(options) {
    const { taskId, companyName } = options;
    this.setData({
      taskId,
      companyName
    });

    // 获取报告内容
    this.getReport();
  },

  getReport() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/task/${this.data.taskId}`,
      method: 'GET',
      success: (res) => {
        const { report } = res.data;
        if (report) {
          this.setData({ report });
        } else {
          wx.showToast({
            title: '报告获取失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('获取报告失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  onCopy() {
    wx.setClipboardData({
      data: this.data.report,
      success: () => {
        wx.showToast({
          title: '已复制到剪贴板',
          icon: 'success'
        });
      }
    });
  },

  onShare() {
    // TODO: 实现分享功能
    wx.showToast({
      title: '分享功能开发中',
      icon: 'none'
    });
  }
});
