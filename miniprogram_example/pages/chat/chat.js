// pages/chat/chat.js
const app = getApp()

Page({
  data: {
    sessionId: null,  // 会话ID
    messages: [],     // 对话历史
    inputText: '',    // 输入框文本
    loading: false,   // 加载状态
    scrollTop: 0,     // 滚动位置
    toView: ''        // 滚动到指定消息
  },

  onLoad() {
    // 创建新会话或恢复旧会话
    const sessionId = wx.getStorageSync('chat_session_id') || null;
    this.setData({
      sessionId: sessionId
    });

    // 如果有旧会话，加载历史记录
    if (sessionId) {
      this.loadChatHistory();
    }
  },

  onUnload() {
    // 保存会话ID
    if (this.data.sessionId) {
      wx.setStorageSync('chat_session_id', this.data.sessionId);
    }
  },

  // 加载对话历史
  loadChatHistory() {
    if (!this.data.sessionId) {
      return;
    }

    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/chat/${this.data.sessionId}`,
      method: 'GET',
      success: (res) => {
        const { messages } = res.data;
        if (messages && messages.length > 0) {
          this.setData({
            messages: messages
          });
          this.scrollToBottom();
        }
      },
      fail: (err) => {
        console.error('加载历史失败:', err);
      }
    });
  },

  // 输入框输入事件
  onInput(e) {
    this.setData({
      inputText: e.detail.value
    });
  },

  // 发送消息
  onSend() {
    const text = this.data.inputText.trim();

    if (!text) {
      return;
    }

    // 添加用户消息
    this.addMessage('user', text);

    // 清空输入框
    this.setData({
      inputText: '',
      loading: true
    });

    // 发送给 Agent
    this.sendToAgent(text);
  },

  // 添加消息到聊天记录
  addMessage(role, content) {
    const messages = this.data.messages;
    messages.push({
      role: role,
      content: content,
      timestamp: new Date().toISOString()
    });

    this.setData({
      messages: messages
    });

    this.scrollToBottom();
  },

  // 发送给 Agent
  sendToAgent(text) {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/chat`,
      method: 'POST',
      data: {
        session_id: this.data.sessionId,
        message: text
      },
      success: (res) => {
        const { session_id, reply } = res.data;

        // 保存会话ID
        if (!this.data.sessionId && session_id) {
          this.setData({
            sessionId: session_id
          });
          wx.setStorageSync('chat_session_id', session_id);
        }

        // 添加 Assistant 回复
        this.addMessage('assistant', reply);
      },
      fail: (err) => {
        console.error('发送失败:', err);
        wx.showToast({
          title: '发送失败，请重试',
          icon: 'none'
        });
        this.addMessage('assistant', '抱歉，我遇到了一些问题，请稍后再试。');
      },
      complete: () => {
        this.setData({
          loading: false
        });
      }
    });
  },

  // 滚动到底部
  scrollToBottom() {
    const messages = this.data.messages;
    if (messages.length > 0) {
      this.setData({
        toView: `msg-${messages.length - 1}`
      });
    }
  },

  // 清空对话历史
  onClear() {
    if (!this.data.sessionId) {
      this.setData({
        messages: []
      });
      return;
    }

    wx.showModal({
      title: '清空对话',
      content: '确定要清空所有对话记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `${app.globalData.apiBaseUrl}/api/chat/${this.data.sessionId}`,
            method: 'DELETE',
            success: () => {
              this.setData({
                messages: []
              });
              wx.showToast({
                title: '对话已清空',
                icon: 'success'
              });
            },
            fail: (err) => {
              console.error('清空失败:', err);
              wx.showToast({
                title: '清空失败',
                icon: 'none'
              });
            }
          });
        }
      }
    });
  }
});
