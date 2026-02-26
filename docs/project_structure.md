# 项目结构说明

## 📁 完整项目结构

```
credit_analysis_miniprogram/
│
├── backend_miniprogram/              # 后端代码目录
│   ├── main.py                      # 后端服务主程序
│   ├── agent_wrapper.py             # Agent 调用封装
│   └── requirements.txt             # 依赖包列表
│
├── miniprogram_example/             # 小程序代码目录
│   ├── app.js                       # 小程序主逻辑
│   ├── app.json                     # 小程序配置文件
│   ├── sitemap.json                 # 站点地图配置
│   │
│   └── pages/                       # 页面目录
│       ├── index/                   # 首页（输入公司名称）
│       │   ├── index.js             # 首页逻辑
│       │   ├── index.json           # 首页配置
│       │   ├── index.wxml           # 首页页面结构
│       │   └── index.wxss           # 首页样式
│       │
│       ├── progress/                # 进度页（显示分析进度）
│       │   ├── progress.js          # 进度页逻辑
│       │   ├── progress.json        # 进度页配置
│       │   ├── progress.wxml        # 进度页页面结构
│       │   └── progress.wxss        # 进度页样式
│       │
│       └── report/                  # 报告页（显示分析结果）
│           ├── report.js            # 报告页逻辑
│           ├── report.json          # 报告页配置
│           ├── report.wxml          # 报告页页面结构
│           └── report.wxss          # 报告页样式
│
└── docs/                           # 文档目录
    ├── wechat_miniprogram_deployment_guide.md   # 完整部署文档
    └── quick_start_guide.md                     # 快速启动指南
```

---

## 🔧 核心文件说明

### 后端文件

#### backend_miniprogram/main.py
- **作用**：后端服务主程序，提供 API 接口
- **核心功能**：
  - POST /api/analyze - 提交分析请求
  - GET /api/task/{task_id} - 查询任务状态
  - GET / - 根路径（服务状态）
- **技术栈**：FastAPI + uvicorn

#### backend_miniprogram/agent_wrapper.py
- **作用**：封装 Agent 调用逻辑
- **核心功能**：
  - 初始化 Agent
  - 调用 analyze_company 方法
  - 返回分析报告

#### backend_miniprogram/requirements.txt
- **作用**：列出所有依赖包
- **内容**：fastapi, uvicorn, pydantic 等

---

### 小程序文件

#### miniprogram_example/app.js
- **作用**：小程序全局配置和全局数据
- **核心功能**：
  - 定义全局变量 `apiBaseUrl`
  - 初始化小程序

#### miniprogram_example/app.json
- **作用**：小程序配置文件
- **核心功能**：
  - 定义页面路径
  - 配置窗口样式
  - 配置导航栏样式

#### miniprogram_example/pages/index/
- **作用**：首页（输入公司名称）
- **核心功能**：
  - 输入公司名称
  - 选择分析模板
  - 提交分析请求

#### miniprogram_example/pages/progress/
- **作用**：进度页（显示分析进度）
- **核心功能**：
  - 显示进度条
  - 轮询任务状态
  - 自动跳转到报告页

#### miniprogram_example/pages/report/
- **作用**：报告页（显示分析结果）
- **核心功能**：
  - 显示完整报告
  - 复制报告内容
  - 分享报告（待实现）

---

## 📖 文档说明

### docs/wechat_miniprogram_deployment_guide.md
- **作用**：完整的部署文档
- **内容**：
  - 总体方案说明
  - 准备工作
  - 后端开发步骤
  - 小程序开发步骤
  - 部署上线步骤
  - 测试验证
  - 常见问题

### docs/quick_start_guide.md
- **作用**：快速启动指南
- **内容**：
  - 3 步快速启动
  - 环境准备
  - 本地测试
  - 真机测试
  - 部署到云服务器
  - 常见问题

---

## 🔄 数据流转

```
1. 用户在小程序输入公司名称
   ↓
2. 小程序调用 POST /api/analyze
   ↓
3. 后端创建任务，返回 task_id
   ↓
4. 小程序轮询 GET /api/task/{task_id}
   ↓
5. 后端调用 Agent 分析
   ↓
6. Agent 返回分析报告
   ↓
7. 后端更新任务状态
   ↓
8. 小程序显示报告页面
```

---

## ⚙️ 配置说明

### 需要修改的配置

#### 1. backend_miniprogram/agent_wrapper.py
```python
# 修改第 10 行的路径
project_root = os.path.abspath(os.path.dirname(__file__))
```

#### 2. miniprogram_example/app.js
```javascript
// 修改第 6 行的 API 地址
apiBaseUrl: 'http://localhost:8000'  // 本地测试
// apiBaseUrl: 'https://your-domain.com'  // 生产环境
```

#### 3. 微信公众平台
- 添加服务器域名白名单
- 配置 HTTPS 域名

---

## 🚀 启动顺序

1. 启动后端服务
   ```bash
   cd backend_miniprogram
   python main.py
   ```

2. 启动小程序
   - 打开微信开发者工具
   - 选择 miniprogram_example 目录
   - 点击"编译"

3. 测试功能
   - 在模拟器中输入公司名称
   - 点击"开始分析"
   - 查看进度和报告

---

## 📝 开发建议

### 后端开发
- 使用 IDE（如 VS Code 或 PyCharm）
- 安装 Python 插件
- 使用虚拟环境（推荐）
- 查看 API 文档：http://localhost:8000/docs

### 小程序开发
- 使用微信开发者工具
- 查看调试日志（控制台）
- 使用真机预览测试
- 参考官方文档：https://developers.weixin.qq.com/miniprogram/dev/framework/

---

## 🔍 调试技巧

### 后端调试
- 查看命令行输出
- 访问 http://localhost:8000/docs 测试 API
- 使用 print 打印日志

### 小程序调试
- 查看控制台输出
- 使用 console.log 打印日志
- 使用断点调试
- 使用真机预览

---

## ✅ 检查清单

部署前请确认：
- [ ] Python 3.9+ 已安装
- [ ] 微信开发者工具已安装
- [ ] 小程序账号已注册
- [ ] 后端依赖已安装
- [ ] 后端服务能正常启动
- [ ] 小程序能正常编译
- [ ] API 地址配置正确
- [ ] Agent 路径配置正确
