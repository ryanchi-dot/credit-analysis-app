#!/bin/bash

# Telegram Bot 快速启动脚本
# 用于快速部署和测试 Telegram Bot

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Telegram Bot 快速启动脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo -e "${YELLOW}检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 未安装，请先安装 Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# 检查 pip
echo -e "${YELLOW}检查 pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip 未安装，请先安装 pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip 已安装${NC}"

# 提示输入 Bot Token
echo ""
echo -e "${YELLOW}请输入您的 Telegram Bot Token:${NC}"
echo "提示：通过 @BotFather 获取，格式类似：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
read -p "Bot Token: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}Bot Token 不能为空！${NC}"
    exit 1
fi

# 验证 Token 格式
if [[ ! $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
    echo -e "${RED}Bot Token 格式不正确！${NC}"
    echo "正确格式：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    exit 1
fi

echo -e "${GREEN}✓ Token 格式正确${NC}"

# 询问是否配置 Webhook
echo ""
read -p "是否配置 Webhook？(y/n): " SETUP_WEBHOOK

if [ "$SETUP_WEBHOOK" = "y" ]; then
    echo -e "${YELLOW}请输入 Webhook URL（例如：https://your-domain.com/webhook）：${NC}"
    read -p "Webhook URL: " WEBHOOK_URL
else
    WEBHOOK_URL=""
fi

# 创建配置文件
echo ""
echo -e "${YELLOW}创建配置文件...${NC}"
cat > telegram_config.json <<EOF
{
  "telegram_bot_token": "$BOT_TOKEN",
  "webhook_url": "$WEBHOOK_URL",
  "description": "Telegram Bot 配置文件"
}
EOF
echo -e "${GREEN}✓ 配置文件已创建：telegram_config.json${NC}"

# 安装依赖
echo ""
echo -e "${YELLOW}安装依赖包...${NC}"
pip3 install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 测试 Token
echo ""
echo -e "${YELLOW}测试 Bot Token 是否有效...${NC}"
TOKEN_TEST=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
if echo "$TOKEN_TEST" | grep -q '"ok":true'; then
    BOT_INFO=$(echo "$TOKEN_TEST" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Bot名称：{data['result']['first_name']}\\n用户名：@{data['result']['username']}\")" 2>/dev/null || echo "✓ Token 有效")
    echo -e "${GREEN}✓ Bot Token 有效！${NC}"
    echo "$BOT_INFO"
else
    echo -e "${RED}✗ Bot Token 无效！${NC}"
    echo "请检查 Token 是否正确"
    exit 1
fi

# 启动服务
echo ""
echo -e "${YELLOW}启动后端服务...${NC}"
echo -e "${GREEN}服务启动中，按 Ctrl+C 停止${NC}"
echo ""

python3 main.py

# 如果用户配置了 Webhook
if [ "$SETUP_WEBHOOK" = "y" ] && [ -n "$WEBHOOK_URL" ]; then
    echo ""
    echo -e "${YELLOW}设置 Webhook...${NC}"
    WEBHOOK_RESULT=$(curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$WEBHOOK_URL")
    if echo "$WEBHOOK_RESULT" | grep -q '"ok":true'; then
        echo -e "${GREEN}✓ Webhook 设置成功：$WEBHOOK_URL${NC}"
    else
        echo -e "${RED}✗ Webhook 设置失败${NC}"
        echo "$WEBHOOK_RESULT"
    fi
fi

echo ""
echo "=========================================="
echo "  启动完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 在 Telegram 中搜索您的 Bot"
echo "2. 发送 /start 开始使用"
echo "3. 发送公司名称进行分析"
echo ""
echo "常用命令："
echo "/start - 开始使用"
echo "/help - 查看帮助"
echo "/clear - 清空对话历史"
echo "/about - 关于"
echo ""
