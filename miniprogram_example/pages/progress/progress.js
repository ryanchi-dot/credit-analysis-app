// pages/progress/progress.js
const app = getApp()

Page({
  data: {
    taskId: '',
    companyName: '',
    progress: 0,
    status: 'processing',
    statusMessage: '正在初始化...',
    timer: null
  },

  onLoad(options) {
    const { taskId, companyName } = options;
    this.setData({
      taskId,
      companyName
    });

    // 开始轮询任务状态
    this.startPolling();
  },

  onUnload() {
    // 清除定时器
    if (this.data.timer) {
      clearInterval(this.data.timer);
    }
  },

  startPolling() {
    // 每2秒查询一次任务状态
    const timer = setInterval(() => {
      this.checkTaskStatus();
    }, 2000);

    this.setData({ timer });

    // 立即查询一次
    this.checkTaskStatus();
  },

  checkTaskStatus() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/task/${this.data.taskId}`,
      method: 'GET',
      success: (res) => {
        const { status, progress, message, report } = res.data;

        // 更新进度
        this.setData({
          progress,
          status,
          statusMessage: message || '正在处理...'
        });

        // 如果任务完成，跳转到报告页
        if (status === 'completed' && report) {
          clearInterval(this.data.timer);
          setTimeout(() => {
            wx.redirectTo({
              url: `/pages/report/report?taskId=${this.data.taskId}&companyName=${this.data.companyName}`
            });
          }, 1000);
        }

        // 如果任务失败，显示错误提示
        if (status === 'failed') {
          clearInterval(this.data.timer);
          wx.showModal({
            title: '分析失败',
            content: message || '未知错误',
            showCancel: false,
            success: () => {
              wx.navigateBack();
            }
          });
        }
      },
      fail: (err) => {
        console.error('查询失败:', err);
      }
    });
  }
});
