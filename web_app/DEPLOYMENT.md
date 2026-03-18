# 部署指南

本文档介绍如何将银行信贷分析助手网页版部署到云端。

## 部署选项

### 1. Render（推荐，免费）

Render是一个云平台，提供免费的Web应用托管服务。

#### 步骤1：准备代码

1. 将 `web_app` 目录推送到GitHub
2. 确保 `requirements.txt` 和 `app.py` 在根目录

#### 步骤2：在Render创建项目

1. 访问 https://render.com
2. 注册/登录账号
3. 点击 "New +" → "Web Service"
4. 连接GitHub仓库
5. 选择你的仓库

#### 步骤3：配置项目

**基本信息**：
- Name: `credit-analysis-app`（或任意名称）
- Region: Singapore（或离你最近的区域）
- Branch: `main`

**构建配置**：
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

**环境变量**：
```
PYTHON_VERSION=3.9
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
AGENT_API_URL=https://your-agent-url/run
AGENT_API_KEY=your-api-key
SECRET_KEY=your-secret-key
```

#### 步骤4：部署

点击 "Create Web Service"，Render会自动部署。

**预计时间**：3-5分钟

#### 步骤5：访问应用

部署完成后，Render会提供一个URL，例如：
```
https://credit-analysis-app.onrender.com
```

访问该URL即可使用应用。

---

### 2. Vercel（免费）

Vercel也是一个流行的云平台，专注于前端应用，但也支持Python。

#### 步骤1：安装Vercel CLI

```bash
npm install -g vercel
```

#### 步骤2：部署

```bash
cd web_app
vercel
```

按照提示操作。

---

### 3. Railway（免费）

Railway是另一个云平台，提供免费套餐。

#### 步骤1：安装Railway CLI

```bash
npm install -g @railway/cli
```

#### 步骤2：登录

```bash
railway login
```

#### 步骤3：部署

```bash
railway init
railway up
```

---

## 本地部署

如果你想在本地运行：

### 1. 安装依赖

```bash
cd web_app
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
AGENT_API_URL=http://localhost:8000/run
AGENT_API_KEY=your-api-key
SECRET_KEY=your-secret-key
```

### 3. 运行应用

```bash
streamlit run app.py
```

访问：http://localhost:8501

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 必需 | 示例 |
|--------|------|------|------|
| `AGENT_API_URL` | 智能体API URL | 是 | `https://your-agent-url/run` |
| `AGENT_API_KEY` | API密钥 | 否 | `your-api-key` |
| `SECRET_KEY` | 会话密钥 | 否 | `your-secret-key` |

### 端口配置

Streamlit默认使用端口8501，但部署到云端时，平台会动态分配端口。

使用以下命令启动：
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 数据持久化

### Render免费版

**限制**：
- 免费版的应用在15分钟无活动后会休眠
- 下次访问时需要30秒-2分钟唤醒
- 文件系统是临时的，重启后文件会丢失

**解决方案**：
- 使用外部数据库（如PostgreSQL）
- 使用对象存储（如AWS S3）
- 使用Render的持久化存储（付费）

### 本地部署

**优势**：
- 数据永久保存
- 性能更好
- 完全控制

---

## 故障排查

### 问题1：应用无法启动

**原因**：依赖未安装

**解决**：
```bash
pip install -r requirements.txt
```

### 问题2：数据库错误

**原因**：data目录不存在

**解决**：
```bash
mkdir -p data/uploads
```

### 问题3：智能体API调用失败

**原因**：
1. API URL错误
2. API Key错误
3. 网络问题

**解决**：
1. 检查 `AGENT_API_URL` 环境变量
2. 检查 `AGENT_API_KEY` 环境变量
3. 检查网络连接

### 问题4：文件上传失败

**原因**：
1. 文件类型不支持
2. 文件大小超限
3. 磁盘空间不足

**解决**：
1. 检查文件类型（支持PDF、Word、Excel、图片）
2. 检查文件大小（建议小于50MB）
3. 检查磁盘空间

---

## 性能优化

### 1. 使用缓存

对于频繁访问的数据，可以使用缓存：

```python
@st.cache_data
def get_user_sessions(user_id: str):
    return db.get_user_sessions(user_id)
```

### 2. 使用异步

对于耗时的操作，使用异步处理：

```python
import asyncio

async def analyze_company_async(company_name: str):
    # 异步调用智能体
    pass
```

### 3. 使用CDN

对于静态资源，使用CDN加速。

---

## 安全建议

### 1. 使用HTTPS

部署到云端时，确保使用HTTPS。

### 2. 加密密码

用户密码使用SHA-256加密存储（已实现）。

### 3. 限制访问

可以添加访问控制，只允许特定IP访问。

### 4. 定期备份

定期备份数据库和文件。

---

## 监控和日志

### Render监控

Render提供：
- CPU使用率
- 内存使用率
- 请求日志
- 错误日志

访问Render Dashboard查看。

### 本地日志

Streamlit的日志会输出到终端。

---

## 更新应用

### 更新代码

1. 修改代码
2. 推送到GitHub
3. Render自动部署

### 更新依赖

```bash
pip install -r requirements.txt --upgrade
```

---

## 成本估算

### Render免费版

- ✅ 免费
- ⚠️ 15分钟无活动后休眠
- ⚠️ 文件系统临时

### Render付费版

- 💰 $5-25/月
- ✅ 不会休眠
- ✅ 持久化存储
- ✅ 更好的性能

### 本地部署

- 💰 服务器成本（约$5-50/月）
- ✅ 完全控制
- ✅ 数据永久保存

---

## 支持

如有问题，请：
1. 查看本文档的故障排查部分
2. 查看日志
3. 联系技术支持
