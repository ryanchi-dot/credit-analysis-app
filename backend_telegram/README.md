# Telegram Bot - 银行信贷分析助手

## 📖 简介

这是一个基于 LangChain 和 LangGraph 构建的 Telegram Bot，可以分析企业授信情况，生成专业的银行信贷分析报告。

### 功能特点

- ✅ **智能分析**：基于公开信息分析企业财务状况
- ✅ **对话交互**：支持多轮对话，深入探讨
- ✅ **专业报告**：生成符合银行标准的授信分析报告
- ✅ **记忆功能**：记住对话上下文（20轮滑动窗口）
- ✅ **命令支持**：`/start`、`/help`、`/clear`、`/about`

### 技术栈

- **后端框架**：FastAPI
- **AI 框架**：LangChain + LangGraph
- **大模型**：doubao-seed-2-0-pro-260215
- **消息平台**：Telegram Bot API

---

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Telegram 账号
- 服务器（腾讯云/阿里云等）

### 步骤1：创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新 Bot
3. 设置 Bot 名称和用户名
4. 保存返回的 Token

### 步骤2：配置并启动

**方法1：使用快速启动脚本（推荐）**

```bash
cd backend_telegram
./start.sh
```

按照提示输入 Bot Token 和 Webhook URL。

**方法2：手动启动**

```bash
cd backend_telegram

# 安装依赖
pip install -r requirements.txt

# 配置 Bot Token
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"

# 启动服务
python main.py
```

### 步骤3：测试 Bot

1. 在 Telegram 中搜索您的 Bot（用户名）
2. 发送 `/start`
3. 发送公司名称（如"腾讯"）进行分析

---

## 📁 项目结构

```
backend_telegram/
├── main.py                 # 主程序（FastAPI 服务）
├── telegram_config.json    # 配置文件
├── requirements.txt        # Python 依赖
├── start.sh               # 快速启动脚本
└── README.md              # 本文件
```

---

## ⚙️ 配置说明

### telegram_config.json

```json
{
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "webhook_url": "https://your-domain.com/webhook"
}
```

**配置项说明**：

- `telegram_bot_token`：Bot Token（必填）
  - 从 `@BotFather` 获取
  - 格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

- `webhook_url`：Webhook URL（可选）
  - 如果不配置，使用轮询模式（Polling）
  - 如果配置，使用 Webhook 模式（推荐）

### 环境变量

也可以使用环境变量配置：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

---

## 🤖 Bot 命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用，显示欢迎信息 |
| `/help` | 查看帮助信息 |
| `/clear` | 清空对话历史 |
| `/about` | 关于信息 |

---

## 🌐 API 接口

服务启动后，提供以下接口：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/webhook` | POST | 接收 Telegram Webhook |
| `/webhook/info` | GET | 获取 Webhook 信息 |
| `/webhook/set` | POST | 设置 Webhook |
| `/webhook/delete` | POST | 删除 Webhook |
| `/api/send` | POST | 手动发送消息（测试用） |

---

## 🚀 部署到生产环境

### 使用 systemd 管理服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

内容：

```ini
[Unit]
Description=Telegram Bot API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/telegram-bot
Environment="TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN"
ExecStart=/usr/bin/python3 /opt/telegram-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### 配置 HTTPS（Webhook 必需）

Telegram 要求 Webhook 必须使用 HTTPS。

**使用 Let's Encrypt**：

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d bot.example.com
```

**使用 Nginx 反向代理**：

```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/telegram-bot
```

配置：

```nginx
server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用：

```bash
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d bot.example.com
```

---

## 📊 使用示例

### 示例1：单次分析

```
用户：分析腾讯
Bot：正在为您分析腾讯公司的授信情况...
     [生成完整报告]
```

### 示例2：对话交互

```
用户：分析腾讯
Bot：[生成简要分析]

用户：利润怎么样？
Bot：腾讯2024年净利润为1941亿元...

用户：有什么风险？
Bot：主要风险包括：1. 游戏监管趋严...
```

---

## 🔧 故障排查

### 问题1：Bot 不回复

**检查服务状态**：

```bash
systemctl status telegram-bot
```

**查看日志**：

```bash
journalctl -u telegram-bot -f
```

### 问题2：Token 无效

**测试 Token**：

```bash
curl https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

如果返回 `"ok": false`，检查 Token 是否正确。

### 问题3：消息发送失败

**检查网络**：

```bash
curl https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

**检查日志**：查看是否有错误信息。

---

## 📚 文档

- [完整部署指南](../docs/telegram_bot_deployment_guide.md)

---

## 💡 提示

1. **Token 安全**：不要泄露 Bot Token
2. **服务器资源**：确保服务器有足够的 CPU 和内存
3. **响应时间**：Agent 分析需要 2-5 分钟，请耐心等待
4. **对话记忆**：默认记住最近 20 轮对话

---

## 📄 许可证

MIT License

---

## 🤝 支持

如有问题，请查看：
- 完整部署指南：`docs/telegram_bot_deployment_guide.md`
- 日志文件：`journalctl -u telegram-bot -f`

---

## 🎉 开始使用

1. 创建 Telegram Bot
2. 配置并启动服务
3. 在 Telegram 中搜索您的 Bot
4. 发送 `/start` 开始使用

祝您使用愉快！🚀
