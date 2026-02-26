# Telegram Bot 部署完整指南

## 📖 目录
1. [准备工作](#准备工作)
2. [创建 Telegram Bot](#创建-telegram-bot)
3. [部署后端服务](#部署后端服务)
4. [配置 Webhook](#配置-webhook)
5. [测试 Bot](#测试-bot)
6. [常见问题](#常见问题)

---

## 准备工作

### 需要准备的资源

- ✅ 腾讯云服务器（已购买）
- ✅ 服务器已安装 Python 3.9+
- ✅ 域名（可选，用于 HTTPS）
- ✅ SSL 证书（如果使用 HTTPS）

### 检查服务器环境

```bash
# 检查 Python 版本
python --version
# 应该显示：Python 3.9.x 或更高版本

# 如果没有安装 Python，请先安装
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# CentOS:
sudo yum install python3 python3-pip
```

---

## 创建 Telegram Bot

### 步骤1：与 BotFather 对话

1. **打开 Telegram**（手机或电脑都可以）
2. **搜索 `@BotFather`**
3. **点击"开始"（Start）**

### 步骤2：创建新 Bot

1. **输入命令**：`/newbot`
2. **设置 Bot 名称**：
   - BotFather 问："How are we going to call it?"
   - 输入显示名称，例如：`信贷分析助手`
3. **设置 Bot 用户名**：
   - BotFather 问："Choose a username for your bot. It must end in `bot`."
   - 输入用户名，例如：`credit_analysis_bot`
   - **必须以 `bot` 结尾**

### 步骤3：获取 Token

创建成功后，BotFather 会返回类似这样的信息：

```
Done! Congratulations on your new bot. You will find it at t.me/credit_analysis_bot

You can now add a description, about section and profile picture for your bot, see /help for a command list.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**保存这个 Token**！格式是：`数字:字母数字混合`

示例：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 步骤4：测试 Bot

在浏览器中访问（替换 `YOUR_BOT_TOKEN`）：

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

如果返回 ` "ok": true`，说明 Bot 创建成功 ✅

---

## 部署后端服务

### 步骤1：上传代码到服务器

将以下文件上传到服务器（例如 `/opt/telegram-bot/`）：

```
backend_telegram/
├── main.py
├── telegram_config.json
└── requirements.txt
```

**上传方法**：

**方法1：使用 SCP（命令行）**
```bash
# 在本地电脑执行
scp -r backend_telegram root@your-server-ip:/opt/telegram-bot/
```

**方法2：使用 FTP/SFTP 工具**
- 使用 FileZilla、WinSCP 等工具
- 上传整个 `backend_telegram` 文件夹

### 步骤2：登录服务器

```bash
ssh root@your-server-ip
```

### 步骤3：进入项目目录

```bash
cd /opt/telegram-bot
```

### 步骤4：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤5：配置 Bot Token

**方法1：编辑配置文件**

```bash
nano telegram_config.json
```

将 `YOUR_BOT_TOKEN_HERE` 替换为您的真实 Token：

```json
{
  "telegram_bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "webhook_url": "https://your-domain.com/webhook"
}
```

保存并退出（按 `Ctrl+O`，按回车，按 `Ctrl+X`）

**方法2：使用环境变量（推荐）**

```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

为了永久生效，添加到 `.bashrc`：

```bash
echo 'export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"' >> ~/.bashrc
source ~/.bashrc
```

### 步骤6：测试服务

启动服务：

```bash
python main.py
```

预期输出：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**保持这个窗口打开**，不要关闭！

### 步骤7：验证服务

**在新窗口**（SSH 新连接）执行：

```bash
curl http://localhost:8000
```

预期返回：

```json
{
  "status": "running",
  "service": "Telegram Bot API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00"
}
```

如果看到这个返回，说明服务正常 ✅

---

## 配置 Webhook

Webhook 是 Telegram 主动推送消息到您的服务器的方式。

### 方案1：使用 Polling（轮询，测试用）

如果只是测试，不需要配置 Webhook，服务会自动轮询 Telegram API。

**修改 main.py**，在 `main()` 函数前添加轮询逻辑：

```python
# 在 main.py 末尾添加
async def polling():
    """轮询 Telegram API 获取更新"""
    import time
    last_update_id = 0
    
    while True:
        try:
            url = f"{TELEGRAM_API_URL}/getUpdates?timeout=30&offset={last_update_id + 1}"
            response = requests.get(url, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        # 处理每个更新
                        await webhook_process(update)
                        last_update_id = update["update_id"]
            
            await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Polling error: {e}")
            await asyncio.sleep(5)

async def webhook_process(update):
    """处理更新（类似 webhook 逻辑）"""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/"):
            await handle_command(chat_id, text)
        else:
            await handle_message(chat_id, text)

if __name__ == "__main__":
    logger.info("Starting Telegram Bot API server...")
    
    # 启动轮询
    import asyncio
    asyncio.run(polling())
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 方案2：使用 Webhook（生产环境推荐）

如果域名已配置 HTTPS，使用 Webhook 更高效。

#### 前提条件

1. **已购买域名**（例如：`bot.example.com`）
2. **域名已解析到服务器 IP**
3. **已配置 SSL 证书**

#### 设置 Webhook

**在浏览器中访问**（替换参数）：

```
https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://your-domain.com/webhook
```

**示例**：

```
https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/setWebhook?url=https://bot.example.com/webhook
```

预期返回：

```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

#### 验证 Webhook

在浏览器中访问：

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo
```

检查 `url` 字段是否为您设置的 URL。

---

## 测试 Bot

### 测试步骤

1. **打开 Telegram**
2. **搜索您的 Bot**（例如：`@credit_analysis_bot`）
3. **点击"开始"（Start）**
4. **发送命令**：`/start`

预期 Bot 回复：

```
👋 欢迎使用银行信贷分析助手！

我可以帮您：
• 分析企业的授信情况
• 生成完整的授信分析报告
• 回答关于企业财务、风险的问题

💡 使用方法：
直接发送公司名称，例如：'腾讯' 或 '中国移动通信集团有限公司'

📊 其他命令：
/help - 查看帮助
/clear - 清空对话历史
/about - 关于
```

### 测试对话功能

1. **发送**：`分析腾讯`
2. **等待回复**（2-5分钟）
3. **继续提问**：`利润怎么样？`

预期 Bot 能记住上下文，正常回复。

---

## 配置服务自动启动（推荐）

使用 systemd 让服务自动启动，即使服务器重启也能正常运行。

### 创建 systemd 服务文件

```bash
nano /etc/systemd/system/telegram-bot.service
```

**内容**：

```ini
[Unit]
Description=Telegram Bot API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/telegram-bot
Environment="TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
ExecStart=/usr/bin/python3 /opt/telegram-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存并退出。

### 启用并启动服务

```bash
# 重新加载 systemd 配置
systemctl daemon-reload

# 启用服务（开机自启）
systemctl enable telegram-bot

# 启动服务
systemctl start telegram-bot

# 查看服务状态
systemctl status telegram-bot
```

预期输出：

```
● telegram-bot.service - Telegram Bot API Server
   Loaded: loaded (/etc/systemd/system/telegram-bot.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2024-01-01 12:00:00 UTC; 1s ago
 Main PID: 12345 (python3)
    Tasks: 2 (limit: 4915)
   Memory: 45.2M
   CGroup: /system.slice/telegram-bot.service
           └─12345 /usr/bin/python3 /opt/telegram-bot/main.py
```

### 管理服务命令

```bash
# 查看服务状态
systemctl status telegram-bot

# 停止服务
systemctl stop telegram-bot

# 重启服务
systemctl restart telegram-bot

# 查看日志
journalctl -u telegram-bot -f
```

---

## 配置 HTTPS（生产环境必需）

Telegram 要求 Webhook 必须使用 HTTPS。

### 方法1：使用 Let's Encrypt（免费）

```bash
# 安装 certbot
sudo apt install certbot

# 获取证书（需要域名已解析）
sudo certbot certonly --standalone -d bot.example.com

# 证书位置：
# /etc/letsencrypt/live/bot.example.com/fullchain.pem
# /etc/letsencrypt/live/bot.example.com/privkey.pem
```

### 方法2：使用 Nginx 反向代理

安装 Nginx：

```bash
sudo apt install nginx
```

配置 Nginx：

```bash
nano /etc/nginx/sites-available/telegram-bot
```

**内容**：

```nginx
server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

配置 SSL：

```bash
sudo certbot --nginx -d bot.example.com
```

现在可以访问 `https://bot.example.com`

---

## 常见问题

### Q1: Bot 不回复消息

**可能原因**：
1. 后端服务未运行
2. Webhook 配置错误
3. 防火墙阻止

**解决方法**：

检查服务状态：
```bash
systemctl status telegram-bot
```

查看日志：
```bash
journalctl -u telegram-bot -n 50
```

检查防火墙：
```bash
sudo ufw status
# 如果需要，开放端口
sudo ufw allow 8000
```

### Q2: 提示 Token 无效

**解决方法**：
1. 检查 Token 是否正确复制（不要有多余空格）
2. 在浏览器中测试：`https://api.telegram.org/botYOUR_BOT_TOKEN/getMe`
3. 如果 Token 泄露，重新生成：在 Telegram 中向 `@BotFather` 发送 `/revoke`

### Q3: 消息发送失败

**可能原因**：
1. 消息过长（超过 4096 字符）
2. Markdown 格式错误
3. 网络问题

**解决方法**：
- 代码已自动处理长消息分割
- 代码已自动移除导致解析错误的特殊字符
- 检查网络连接

### Q4: Agent 响应很慢

**原因**：正常现象，Agent 需要搜索和分析

**解决方法**：
- 告知用户需要耐心等待
- 可以优化搜索关键词
- 考虑增加服务器性能

### Q5: 如何更新 Bot

```bash
# 1. 停止服务
systemctl stop telegram-bot

# 2. 更新代码
cd /opt/telegram-bot
# 上传新代码（覆盖 main.py）

# 3. 更新依赖（如果有变化）
pip install -r requirements.txt

# 4. 重启服务
systemctl start telegram-bot
```

---

## 📊 总结

部署 Telegram Bot 的关键步骤：

1. ✅ 通过 `@BotFather` 创建 Bot 并获取 Token
2. ✅ 上传代码到服务器
3. ✅ 配置 Bot Token
4. ✅ 启动后端服务
5. ✅ 配置 Webhook 或使用轮询
6. ✅ 测试 Bot 功能
7. ✅ 配置服务自动启动
8. ✅ 配置 HTTPS（生产环境）

---

## 🎉 完成！

恭喜您的银行信贷分析助手已成功部署到 Telegram！

用户可以通过：
- 在 Telegram 中搜索您的 Bot 用户名
- 发送 `/start` 开始使用
- 发送公司名称进行分析
- 使用命令 `/help`、`/clear`、`/about`

需要帮助？查看日志：
```bash
journalctl -u telegram-bot -f
```
