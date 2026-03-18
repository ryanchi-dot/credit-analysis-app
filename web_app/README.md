# 银行信贷分析助手 - 网页版

基于Streamlit的银行信贷分析助手网页应用，支持多用户、历史记录、文件上传等功能。

## 功能特性

### ✅ 核心功能
- **用户系统**：支持用户注册、登录，每个用户完全隔离
- **智能对话**：与银行信贷分析智能体进行多轮对话
- **文件上传**：支持PDF、Word、Excel、图片格式的文件上传
- **报告生成**：自动生成专业的银行授信分析报告（Word格式）
- **历史记录**：保存用户的对话历史，支持查看和恢复
- **数据安全**：每个用户的数据完全隔离，确保信息安全

### 🔐 安全特性
- **用户隔离**：每个用户的数据（消息、文件、历史记录）完全独立
- **权限控制**：用户只能访问自己的数据
- **密码加密**：用户密码使用SHA-256加密存储
- **会话管理**：使用user_id和session_id实现会话隔离
- **文件隔离**：用户上传的文件按用户ID分别存储

## 项目结构

```
web_app/
├── app.py                 # 主应用文件
├── database.py            # 数据库操作（用户、会话、消息、文件）
├── agent_client.py        # 智能体API调用
├── utils.py               # 工具函数（加密、文件处理等）
├── data/                  # 数据目录
│   ├── users.db           # SQLite数据库（用户数据）
│   └── uploads/           # 用户上传文件（按用户ID隔离）
│       ├── user_1/        # 用户1的文件
│       ├── user_2/        # 用户2的文件
│       └── ...
├── requirements.txt       # Python依赖
└── README.md             # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd web_app
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（可选）：

```bash
# 智能体API配置
AGENT_API_URL=https://your-agent-url/run
AGENT_API_KEY=your-api-key

# 安全配置
SECRET_KEY=your-secret-key-for-session
```

### 3. 运行应用

```bash
streamlit run app.py
```

访问：http://localhost:8501

## 部署到云端

### 部署到Render（免费）

1. 将代码推送到GitHub
2. 在Render创建新项目
3. 连接GitHub仓库
4. 自动部署

详细部署步骤请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 数据安全说明

### 用户数据隔离

系统使用以下机制确保用户数据隔离：

1. **用户ID隔离**
   - 每个用户有唯一的user_id
   - 所有数据都关联到user_id
   - 数据库查询时强制过滤user_id

2. **文件存储隔离**
   - 用户上传的文件存储在 `data/uploads/user_{user_id}/` 目录
   - 文件路径包含user_id，防止跨用户访问

3. **会话隔离**
   - 每个用户会话有唯一的session_id
   - 智能体API调用时传递user_id和session_id
   - 智能体使用user_id作为thread_id，实现用户会话隔离

### 数据库结构

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,  -- SHA-256加密
    user_id TEXT UNIQUE,  -- 唯一标识
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

-- 会话表
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id TEXT,  -- 关联用户ID
    session_id TEXT UNIQUE,
    title TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 消息表
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    role TEXT,  -- user/assistant
    content TEXT,
    file_name TEXT,  -- 如果有文件上传
    file_path TEXT,  -- 文件路径
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### 权限控制

所有数据库操作都强制包含user_id过滤：

```python
# 只查询当前用户的数据
SELECT * FROM sessions WHERE user_id = ?
SELECT * FROM messages WHERE session_id IN (
    SELECT session_id FROM sessions WHERE user_id = ?
)
```

## 使用说明

### 1. 注册/登录

- 首次使用需要注册账号（输入用户名和密码）
- 之后使用用户名和密码登录
- 系统会自动创建唯一的user_id

### 2. 开始对话

- 在输入框中输入企业名称或问题
- 点击发送按钮
- 等待智能体分析并返回结果

### 3. 上传文件

- 点击上传按钮
- 选择文件（PDF、Word、Excel、图片）
- 文件会自动上传并传递给智能体

### 4. 查看历史记录

- 点击侧边栏的"历史记录"
- 查看所有历史会话
- 点击会话可以恢复对话

## 智能体API调用

智能体API调用流程：

1. 用户发送消息
2. 网页调用智能体API (`/run` 端点)
3. 传递参数：
   ```json
   {
     "messages": [
       {
         "type": "user",
         "content": "请为【中国石油】生成授信分析报告..."
       }
     ],
     "user_id": "user_xxx",
     "session_id": "session_xxx"
   }
   ```
4. 智能体返回报告链接
5. 网页显示下载链接

## 常见问题

### Q: 我的文件上传到哪里了？

A: 文件存储在 `data/uploads/user_{user_id}/` 目录，只有你自己可以访问。

### Q: 如何查看历史对话？

A: 点击侧边栏的"历史记录"按钮，可以查看所有历史会话。

### Q: 删除对话会删除文件吗？

A: 不会，文件会永久保留，除非你手动删除。

### Q: 我的密码安全吗？

A: 密码使用SHA-256加密存储，管理员也无法查看明文密码。

## 技术栈

- **前端**：Streamlit
- **后端**：Python
- **数据库**：SQLite
- **智能体**：银行信贷分析助手

## 许可证

MIT License
