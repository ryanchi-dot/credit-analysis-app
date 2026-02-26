# Telegram Bot - Coze 智能体对接

这是一个简单的 Telegram Bot，用于连接 Coze 智能体，实现通过 Telegram 与智能体对话。

## 功能特点

- ✅ 连接到 Coze 智能体
- ✅ 保持对话上下文
- ✅ 支持文本消息交互
- ✅ 简单易用，易于部署

## 快速开始

### 1. 安装依赖

```bash
pip install -r telegram_requirements.txt
```

或者手动安装：

```bash
pip install python-telegram-bot requests
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置信息：

```env
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Coze Bot ID (智能体 ID)
COZE_BOT_ID=your_coze_bot_id_here

# Coze API Key (API 密钥)
COZE_API_KEY=your_coze_api_key_here

# 可选配置
COZE_WORKSPACE_ID=your_workspace_id_here
COZE_PAT_TOKEN=your_pat_token_here
```

### 3. 获取 Telegram Bot Token

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按照提示设置机器人名称和用户名
4. BotFather 会返回一个 Token，格式如：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. 将 Token 复制到 `.env` 文件中的 `TELEGRAM_BOT_TOKEN`

### 4. 获取 Coze 智能体信息

#### 获取 Coze Bot ID
1. 访问 [Coze 官网](https://www.coze.cn/)
2. 创建或选择一个智能体
3. 在智能体设置中找到 Bot ID
4. 将 Bot ID 复制到 `.env` 文件中的 `COZE_BOT_ID`

#### 获取 Coze API Key
1. 访问 [Coze 官网](https://www.coze.cn/)
2. 进入个人中心 -> API 管理
3. 创建新的 API Key
4. 将 API Key 复制到 `.env` 文件中的 `COZE_API_KEY`

### 5. 启动 Bot

```bash
python telegram_bot.py
```

你会看到类似的输出：

```
2025-01-23 10:00:00 - __main__ - INFO - 🚀 Telegram Bot 启动中...
```

### 6. 在 Telegram 中测试

1. 在 Telegram 中搜索你的 Bot 用户名
2. 发送 `/start` 命令
3. 发送任意消息，Bot 会将消息转发给 Coze 智能体
4. 智能体的回复会通过 Bot 返回给你

## 可用命令

- `/start` - 开始对话
- `/help` - 显示帮助信息

## 项目结构

```
.
├── telegram_bot.py          # Bot 主程序
├── telegram_requirements.txt # Python 依赖
├── .env.example             # 环境变量模板
├── .env                     # 环境变量配置（需手动创建）
└── README.md                # 本文件
```

## 环境变量说明

| 变量名 | 说明 | 必需 | 获取方式 |
|--------|------|------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | ✅ | 从 @BotFather 获取 |
| `COZE_BOT_ID` | Coze 智能体 ID | ✅ | Coze 智能体设置中 |
| `COZE_API_KEY` | Coze API 密钥 | ✅ | Coze 个人中心 -> API 管理 |
| `COZE_WORKSPACE_ID` | Coze 工作空间 ID | ❌ | Coze 工作空间设置中 |
| `COZE_PAT_TOKEN` | Coze PAT Token | ❌ | Coze 个人中心 -> API 管理 |

## 故障排查

### Bot 无法启动

**问题**：`请设置 TELEGRAM_BOT_TOKEN 环境变量`

**解决方案**：
- 确保已创建 `.env` 文件
- 确保已填写 `TELEGRAM_BOT_TOKEN`
- 确保使用的是真实的 Token，不是模板值

**问题**：`请设置 COZE_BOT_ID 和 COZE_API_KEY 环境变量`

**解决方案**：
- 确保已填写 `COZE_BOT_ID`
- 确保已填写 `COZE_API_KEY`
- 确保使用的是真实值，不是模板值

### Bot 不回复消息

**问题**：发送消息后 Bot 没有回复

**解决方案**：
- 检查 Coze API Key 是否正确
- 检查 Coze Bot ID 是否正确
- 检查 Coze 智能体是否已发布
- 查看终端日志，查看错误信息

### Coze API 调用失败

**问题**：终端显示 `调用 Coze API 失败`

**解决方案**：
- 检查网络连接
- 检查 Coze API Key 是否有效
- 检查 Coze 服务是否正常运行

## 进阶配置

### 使用环境变量加载器

如果你希望使用 `python-dotenv` 来加载环境变量，可以安装：

```bash
pip install python-dotenv
```

然后在 `telegram_bot.py` 开头添加：

```python
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()
```

### 自定义端口

默认使用 Telegram Bot 的 Webhook 模式。如需使用轮询模式，代码已配置为 `run_polling`。

### 添加日志记录

当前日志会输出到终端。如需保存到文件，可以修改日志配置：

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='a'
)
```

## 注意事项

1. **不要泄露敏感信息**：不要将 `.env` 文件提交到代码仓库
2. **定期更新 Token**：定期更换 API Key 和 Token 以提高安全性
3. **监控 Bot 运行状态**：建议使用进程管理工具（如 `systemd`、`supervisor`）来管理 Bot 进程
4. **处理高并发**：如果用户量大，考虑使用 Webhook 模式和负载均衡

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
