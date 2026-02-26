# 银行信贷分析助手 - 微信小程序完整部署指南

> 📅 更新时间：2026年2月
> 👤 适用人群：零基础开发者
> ⏱️ 预计完成时间：2-3小时

---

## 📋 目录

1. [总体方案说明](#1-总体方案说明)
2. [准备工作](#2-准备工作)
3. [后端服务开发](#3-后端服务开发)
4. [小程序前端开发](#4-小程序前端开发)
5. [部署上线](#5-部署上线)
6. [测试验证](#6-测试验证)
7. [常见问题](#7-常见问题)

---

## 1. 总体方案说明

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户（微信用户）                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  小程序前端（用户界面）                       │
│  - 输入公司名称                                              │
│  - 查看分析进度                                              │
│  - 展示分析报告                                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS 请求
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                后端服务（API服务器）                          │
│  - 接收小程序请求                                            │
│  - 调用 Agent                                                │
│  - 返回分析结果                                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ 内部调用
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           银行信贷分析助手 Agent（已开发）                    │
│  - 搜索公司信息                                              │
│  - 生成分析报告                                              │
│  - 生成图表                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 需要开发的模块

| 模块 | 技术栈 | 复杂度 | 说明 |
|------|--------|--------|------|
| 后端服务 | Python + FastAPI | ⭐⭐ | 提供 API 接口，调用 Agent |
| 小程序前端 | 微信小程序原生 | ⭐⭐⭐ | 用户界面，展示报告 |
| 部署 | 腾讯云 | ⭐ | 部署后端服务 |

### 1.3 使用的工具和平台

| 用途 | 工具/平台 | 说明 |
|------|-----------|------|
| 后端开发 | Python 3.9+ | 编程语言 |
| 后端框架 | FastAPI | Web 框架 |
| 后端部署 | 腾讯云服务器/云函数 | 云计算平台 |
| 小程序开发 | 微信开发者工具 | 官方开发工具 |
| 小程序账号 | 微信公众平台 | 申请小程序账号 |
| 代码托管 | Gitee/GitHub | 代码管理（可选） |

---

## 2. 准备工作

### 2.1 需要的账号和资源

#### ✅ 必须准备的：

1. **微信小程序账号**
   - 访问：https://mp.weixin.qq.com/
   - 点击"立即注册"
   - 选择"小程序"
   - 填写邮箱、密码等信息
   - 完成邮箱验证
   - 💰 注意：需要认证费 300 元（企业认证）或个人认证（免费但功能受限）

2. **云服务器（后端部署）**
   - 推荐：腾讯云服务器（CVM）
   - 配置建议：
     - CPU：2核
     - 内存：4GB
     - 带宽：1Mbps
     - 操作系统：Ubuntu 20.04 LTS
   - 💰 费用：约 50-100 元/月
   - 或者使用：腾讯云函数（Serverless，按使用付费，更便宜）

3. **域名（可选，推荐）**
   - 用于 HTTPS 访问
   - 域名费用：约 50 元/年
   - 需要 SSL 证书（免费）

#### 📱 需要安装的软件：

1. **Python 3.9 或更高版本**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **微信开发者工具**
   - 下载：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
   - 选择对应系统版本下载安装

3. **代码编辑器（推荐 VS Code）**
   - 下载：https://code.visualstudio.com/

### 2.2 检查准备情况

请确认以下事项：

- [ ] 已注册微信小程序账号
- [ ] 已购买云服务器（或准备使用云函数）
- [ ] 已安装 Python 3.9+
- [ ] 已安装微信开发者工具
- [ ] 已安装代码编辑器

---

## 3. 后端服务开发

### 3.1 创建项目目录

在你的电脑上创建一个工作目录：

```bash
# Windows 示例
mkdir C:\credit_analysis_miniprogram
cd C:\credit_analysis_miniprogram

# macOS/Linux 示例
mkdir ~/credit_analysis_miniprogram
cd ~/credit_analysis_miniprogram
```

在项目目录中创建以下结构：

```
credit_analysis_miniprogram/
├── backend/              # 后端代码
│   ├── main.py          # 主程序
│   ├── requirements.txt # 依赖包
│   └── agent_wrapper.py # Agent 调用封装
├── miniprogram/         # 小程序代码
│   ├── pages/           # 页面
│   ├── app.js
│   ├── app.json
│   └── app.wxss
└── docs/               # 文档
```

### 3.2 编写后端代码

#### 步骤1：创建 requirements.txt

在 `backend/` 目录下创建 `requirements.txt` 文件，内容如下：

```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
requests==2.31.0
```

#### 步骤2：创建 agent_wrapper.py

在 `backend/` 目录下创建 `agent_wrapper.py` 文件，内容如下：

```python
"""
Agent 调用封装
用于调用银行信贷分析助手 Agent
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.agent import build_agent
from langchain_core.messages import HumanMessage


class CreditAnalysisAgent:
    """银行信贷分析助手 Agent 封装"""

    def __init__(self):
        """初始化 Agent"""
        self.agent = None

    def get_agent(self):
        """获取 Agent 实例（单例模式）"""
        if self.agent is None:
            print("正在初始化 Agent...")
            self.agent = build_agent()
            print("Agent 初始化完成！")
        return self.agent

    async def analyze_company(self, company_name: str, template: str = "standard") -> str:
        """
        分析公司授信情况

        Args:
            company_name: 公司名称
            template: 分析模板（默认 standard）

        Returns:
            分析报告文本
        """
        try:
            agent = self.get_agent()

            # 构建用户消息
            user_message = f"请分析{company_name}的授信情况。使用标准模板，没有额外材料。"

            # 调用 Agent
            print(f"开始分析: {company_name}")
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_message)]}
            )

            # 提取回复内容
            report_text = response["messages"][-1].content
            print(f"分析完成！报告长度: {len(report_text)} 字符")

            return report_text

        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            print(error_msg)
            return error_msg


# 创建全局 Agent 实例
agent_instance = CreditAnalysisAgent()
```

#### 步骤3：创建 main.py

在 `backend/` 目录下创建 `main.py` 文件，内容如下：

```python
"""
后端服务主程序
提供 API 接口供小程序调用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from typing import Optional
from datetime import datetime

from agent_wrapper import agent_instance

# 创建 FastAPI 应用
app = FastAPI(title="银行信贷分析助手 API", version="1.0.0")

# 配置 CORS（允许小程序跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    company_name: str
    template: str = "standard"


class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    task_id: str
    status: str  # processing, completed, failed
    message: Optional[str] = None
    report: Optional[str] = None


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str
    progress: int  # 0-100
    message: Optional[str] = None
    report: Optional[str] = None


# ============ 内存存储（生产环境建议使用数据库）===========

tasks = {}  # 存储任务信息


# ============ API 接口 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "银行信贷分析助手 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_company(request: AnalyzeRequest):
    """
    提交分析请求

    Args:
        request: 分析请求

    Returns:
        任务ID和状态
    """
    # 创建任务ID
    task_id = str(uuid.uuid4())

    # 初始化任务
    tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0,
        "message": "分析任务已提交，正在处理...",
        "report": None,
        "created_at": datetime.now()
    }

    # 异步执行分析任务
    asyncio.create_task(run_analysis_task(task_id, request.company_name, request.template))

    return AnalyzeResponse(
        task_id=task_id,
        status="processing",
        message="分析任务已提交，正在处理..."
    )


@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    查询任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        report=task["report"]
    )


# ============ 异步任务 ============

async def run_analysis_task(task_id: str, company_name: str, template: str):
    """
    执行分析任务

    Args:
        task_id: 任务ID
        company_name: 公司名称
        template: 模板类型
    """
    try:
        # 更新进度：10%
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = f"正在搜索 {company_name} 的公开信息..."

        await asyncio.sleep(1)  # 模拟延迟

        # 调用 Agent 分析
        report = await agent_instance.analyze_company(company_name, template)

        # 更新进度：100%
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "分析完成！"
        tasks[task_id]["report"] = report

    except Exception as e:
        # 任务失败
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"分析失败: {str(e)}"
        print(f"任务 {task_id} 失败: {str(e)}")


# ============ 启动命令 ============

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("银行信贷分析助手 API 服务")
    print("=" * 60)
    print("服务地址: http://127.0.0.1:8000")
    print("API 文档: http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.3 本地测试后端服务

#### 步骤1：安装依赖

打开命令行工具（CMD 或 PowerShell），进入 backend 目录：

```bash
cd C:\credit_analysis_miniprogram\backend
```

安装依赖包：

```bash
pip install -r requirements.txt
```

#### 步骤2：启动服务

```bash
python main.py
```

看到以下输出表示启动成功：

```
============================================================
银行信贷分析助手 API 服务
============================================================
服务地址: http://127.0.0.1:8000
API 文档: http://127.0.0.1:8000/docs
============================================================
```

#### 步骤3：测试 API

打开浏览器，访问：
- API 文档：http://127.0.0.1:8000/docs
- 根路径：http://127.0.0.1:8000/

在 API 文档页面中：
1. 找到 `POST /api/analyze` 接口
2. 点击 "Try it out"
3. 输入：
   ```json
   {
     "company_name": "腾讯控股有限公司",
     "template": "standard"
   }
   ```
4. 点击 "Execute"
5. 查看返回结果，应该包含 `task_id`

然后测试查询任务状态：
1. 找到 `GET /api/task/{task_id}` 接口
2. 输入刚才返回的 `task_id`
3. 点击 "Execute"
4. 查看任务状态

---

## 4. 小程序前端开发

### 4.1 创建小程序项目

#### 步骤1：打开微信开发者工具

1. 启动微信开发者工具
2. 使用微信扫码登录
3. 点击 "+" 新建项目

#### 步骤2：填写项目信息

```
项目名称：银行信贷分析助手
目录：选择你的 miniprogram 目录
AppID：选择你的小程序 AppID（从微信公众平台获取）
开发模式：小程序
后端服务：不使用云服务
```

点击"新建"。

### 4.2 编写小程序代码

#### 步骤1：修改 app.json

在 `miniprogram/` 目录下修改 `app.json` 文件：

```json
{
  "pages": [
    "pages/index/index",
    "pages/progress/progress",
    "pages/report/report"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#1890ff",
    "navigationBarTitleText": "银行信贷分析助手",
    "navigationBarTextStyle": "white"
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

#### 步骤2：修改 app.js

修改 `app.js` 文件：

```javascript
// app.js
App({
  globalData: {
    // 后端 API 地址（部署后需要修改为实际地址）
    apiBaseUrl: 'http://localhost:8000'
  }
})
```

#### 步骤3：创建首页（index）

**创建目录结构**：
```
miniprogram/
└── pages/
    └── index/
        ├── index.js
        ├── index.json
        ├── index.wxml
        └── index.wxss
```

**index.wxml**（首页页面）：

```xml
<!--index.wxml-->
<view class="container">
  <view class="header">
    <text class="title">银行信贷分析助手</text>
    <text class="subtitle">专业的企业授信分析工具</text>
  </view>

  <view class="form">
    <view class="form-item">
      <text class="label">公司名称</text>
      <input
        class="input"
        placeholder="请输入公司完整名称"
        value="{{companyName}}"
        bindinput="onCompanyNameInput"
      />
    </view>

    <view class="form-item">
      <text class="label">分析模板</text>
      <picker bindchange="onTemplateChange" value="{{templateIndex}}" range="{{templates}}">
        <view class="picker">
          {{templates[templateIndex]}}
        </view>
      </picker>
    </view>

    <button
      class="btn-submit"
      type="primary"
      bindtap="onSubmit"
      loading="{{loading}}"
      disabled="{{loading}}"
    >
      开始分析
    </button>
  </view>

  <view class="tips">
    <text class="tips-title">使用提示：</text>
    <text class="tips-item">• 请输入公司的完整名称</text>
    <text class="tips-item">• 分析过程可能需要 2-5 分钟</text>
    <text class="tips-item">• 分析结果将以报告形式展示</text>
  </view>
</view>
```

**index.js**（首页逻辑）：

```javascript
// pages/index/index.js
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
```

**index.wxss**（首页样式）：

```css
/* pages/index/index.wxss */
.container {
  padding: 40rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: #999;
}

.form {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.form-item {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
}

.input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 8rpx;
  font-size: 28rpx;
}

.picker {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 24rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
}

.btn-submit {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  font-size: 32rpx;
  margin-top: 20rpx;
}

.tips {
  margin-top: 60rpx;
  padding: 30rpx;
  background-color: #fff;
  border-radius: 16rpx;
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.tips-item {
  display: block;
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}
```

**index.json**（首页配置）：

```json
{
  "navigationBarTitleText": "银行信贷分析"
}
```

#### 步骤4：创建进度页（progress）

**创建目录**：
```
miniprogram/
└── pages/
    └── progress/
        ├── progress.js
        ├── progress.json
        ├── progress.wxml
        └── progress.wxss
```

**progress.wxml**：

```xml
<!--pages/progress/progress.wxml-->
<view class="container">
  <view class="header">
    <text class="title">分析进行中</text>
    <text class="company-name">{{companyName}}</text>
  </view>

  <view class="progress-container">
    <view class="progress-bar">
      <view class="progress-fill" style="width: {{progress}}%"></view>
    </view>
    <text class="progress-text">{{progress}}%</text>
  </view>

  <view class="status">
    <text class="status-text">{{statusMessage}}</text>
  </view>

  <view class="tips" wx:if="{{status === 'processing'}}">
    <text class="tips-item">• 分析过程可能需要 2-5 分钟</text>
    <text class="tips-item">• 请勿关闭此页面</text>
    <text class="tips-item">• 分析完成后将自动跳转</text>
  </view>
</view>
```

**progress.js**：

```javascript
// pages/progress/progress.js
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
```

**progress.wxss**：

```css
/* pages/progress/progress.wxss */
.container {
  padding: 40rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  text-align: center;
  margin-bottom: 80rpx;
}

.title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}

.company-name {
  display: block;
  font-size: 28rpx;
  color: #666;
}

.progress-container {
  width: 100%;
  margin-bottom: 40rpx;
}

.progress-bar {
  width: 100%;
  height: 16rpx;
  background-color: #e0e0e0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #1890ff;
  transition: width 0.3s;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 36rpx;
  font-weight: bold;
  color: #1890ff;
  margin-top: 20rpx;
}

.status {
  text-align: center;
  margin-bottom: 60rpx;
}

.status-text {
  font-size: 28rpx;
  color: #666;
}

.tips {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  width: 100%;
}

.tips-item {
  display: block;
  font-size: 26rpx;
  color: #999;
  line-height: 1.8;
}
```

**progress.json**：

```json
{
  "navigationBarTitleText": "分析进度"
}
```

#### 步骤5：创建报告页（report）

**创建目录**：
```
miniprogram/
└── pages/
    └── report/
        ├── report.js
        ├── report.json
        ├── report.wxml
        └── report.wxss
```

**report.wxml**：

```xml
<!--pages/report/report.wxml-->
<view class="container">
  <view class="header">
    <text class="title">{{companyName}}</text>
    <text class="subtitle">授信分析报告</text>
  </view>

  <view class="report-content">
    <text class="report-text">{{report}}</text>
  </view>

  <view class="actions">
    <button class="btn-action" bindtap="onCopy">复制报告</button>
    <button class="btn-action" bindtap="onShare">分享</button>
  </view>
</view>
```

**report.js**：

```javascript
// pages/report/report.js
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
```

**report.wxss**：

```css
/* pages/report/report.wxss */
.container {
  padding: 40rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
  padding-bottom: 30rpx;
  border-bottom: 2rpx solid #e0e0e0;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #999;
}

.report-content {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 40rpx;
  min-height: 400rpx;
}

.report-text {
  font-size: 26rpx;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

.actions {
  display: flex;
  justify-content: space-between;
}

.btn-action {
  width: 48%;
  height: 80rpx;
  line-height: 80rpx;
  font-size: 28rpx;
}
```

**report.json**：

```json
{
  "navigationBarTitleText": "分析报告"
}
```

---

## 5. 部署上线

### 5.1 后端服务部署

由于部署后端服务涉及云服务器配置，这里提供两种方案：

#### 方案A：使用腾讯云函数（推荐，更简单）

#### 方案B：使用腾讯云服务器（CVM）

由于篇幅限制，详细部署步骤请参考：
- 腾讯云函数部署文档：https://cloud.tencent.com/document/product/583
- 腾讯云服务器部署文档：https://cloud.tencent.com/document/product/213

### 5.2 小程序发布

#### 步骤1：配置服务器域名

1. 登录微信公众平台：https://mp.weixin.qq.com/
2. 进入"开发" → "开发管理" → "开发设置"
3. 在"服务器域名"中，找到"request 合法域名"
4. 添加你的后端服务域名（必须 HTTPS）

#### 步骤2：上传代码

1. 在微信开发者工具中，点击"上传"
2. 填写版本号和备注
3. 点击"确定"

#### 步骤3：提交审核

1. 登录微信公众平台
2. 进入"管理" → "版本管理"
3. 在"开发版本"中找到刚上传的版本
4. 点击"提交审核"
5. 填写审核信息
6. 等待审核通过（通常1-3天）

#### 步骤4：发布上线

审核通过后：
1. 在"审核版本"中点击"发布"
2. 选择"全量发布"
3. 点击"确定"

---

## 6. 测试验证

### 6.1 本地测试

1. 启动后端服务
2. 打开微信开发者工具
3. 点击"编译"
4. 在模拟器中测试：
   - 输入公司名称
   - 点击"开始分析"
   - 查看进度页面
   - 查看报告页面

### 6.2 真机测试

1. 点击"预览"
2. 使用微信扫码
3. 在手机上测试所有功能

---

## 7. 常见问题

### Q1: 后端服务启动失败
**A**: 检查以下几点：
- Python 版本是否为 3.9+
- 是否安装了所有依赖包：`pip install -r requirements.txt`
- 端口 8000 是否被占用

### Q2: 小程序无法连接后端
**A**: 检查以下几点：
- 后端服务是否正常运行
- `app.globalData.apiBaseUrl` 是否正确
- 是否配置了服务器域名白名单（发布时必须配置）

### Q3: 分析报告为空
**A**: 检查以下几点：
- Agent 是否正常初始化
- 公司名称是否正确
- 查看后端服务日志

### Q4: 分析速度太慢
**A**: 这是正常的，因为：
- 需要搜索大量公开信息
- Agent 需要生成完整的报告
- 网络速度也会影响

---

## 📞 需要帮助？

如果在部署过程中遇到问题，请：
1. 仔细检查每个步骤
2. 查看错误信息
3. 参考常见问题部分

---

## 🎉 恭喜！

完成以上步骤后，你就成功部署了银行信贷分析助手小程序！

现在用户可以通过小程序：
✅ 输入公司名称
✅ 查看分析进度
✅ 获取完整的授信分析报告
✅ 复制和分享报告
