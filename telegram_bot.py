"""
Telegram Bot - 连接 Coze 智能体
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== 配置信息 ====================
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token_here")

# Coze 智能体配置
COZE_BOT_ID = os.getenv("COZE_BOT_ID", "your_coze_bot_id_here")
COZE_API_KEY = os.getenv("COZE_API_KEY", "your_coze_api_key_here")
COZE_API_BASE_URL = "https://api.coze.com/open_api/v2/chat"

# Coze 工作空间 API（如果需要）
COZE_WORKSPACE_ID = os.getenv("COZE_WORKSPACE_ID", "your_workspace_id_here")
COZE_PAT_TOKEN = os.getenv("COZE_PAT_TOKEN", "your_pat_token_here")


# ==================== Coze API 调用 ====================
def call_coze_bot(user_message: str, user_id: str) -> str:
    """
    调用 Coze 智能体 API
    
    Args:
        user_message: 用户发送的消息
        user_id: 用户唯一标识（用于保持对话上下文）
    
    Returns:
        智能体的回复内容
    """
    headers = {
        "Authorization": f"Bearer {COZE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 构建请求数据
    payload = {
        "bot_id": COZE_BOT_ID,
        "user": user_id,
        "query": user_message,
        "stream": False  # 非流式响应
    }
    
    try:
        # 发送请求到 Coze API
        response = requests.post(COZE_API_BASE_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取智能体的回复
        if "messages" in result:
            for msg in result["messages"]:
                if msg.get("type") == "answer":
                    return msg.get("content", "抱歉，我无法理解您的请求。")
        
        return "智能体返回了空回复，请稍后重试。"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"调用 Coze API 失败: {e}")
        return f"调用智能体时出错: {str(e)}"
    except Exception as e:
        logger.error(f"处理 Coze 响应失败: {e}")
        return f"处理响应时出错: {str(e)}"


# ==================== Telegram Bot 处理器 ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /start 命令
    """
    user = update.effective_user
    await update.message.reply_html(
        f"你好，{user.mention_html()}！🤖\n\n"
        f"我是连接到 Coze 智能体的助手。\n"
        f"请直接发送消息，我会智能回复你。\n\n"
        f"可用命令：\n"
        f"/start - 开始对话\n"
        f"/help - 帮助信息"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理 /help 命令
    """
    await update.message.reply_text(
        "📖 帮助信息\n\n"
        "这是一个连接到 Coze 智能体的 Telegram Bot。\n\n"
        "使用方法：\n"
        "1. 直接发送任何文字消息\n"
        "2. Bot 会将消息转发给 Coze 智能体\n"
        "3. 智能体的回复会通过 Bot 返回给你\n\n"
        "命令列表：\n"
        "/start - 开始对话\n"
        "/help - 显示此帮助信息"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理普通文本消息
    """
    # 获取用户消息
    user_message = update.message.text
    
    # 获取用户唯一标识（用于保持对话上下文）
    user_id = str(update.effective_user.id)
    
    # 发送"正在输入..."状态
    await update.message.chat.send_action(action="typing")
    
    logger.info(f"用户 {user_id} 发送消息: {user_message}")
    
    try:
        # 调用 Coze 智能体
        bot_response = call_coze_bot(user_message, user_id)
        
        # 发送智能体的回复
        await update.message.reply_text(bot_response)
        
        logger.info(f"智能体回复: {bot_response[:100]}...")
    
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")
        await update.message.reply_text(f"抱歉，处理您的消息时出错了: {str(e)}")


# ==================== 主函数 ====================
def main() -> None:
    """
    启动 Telegram Bot
    """
    # 检查配置
    if TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
    
    if COZE_BOT_ID == "your_coze_bot_id_here" or COZE_API_KEY == "your_coze_api_key_here":
        logger.error("请设置 COZE_BOT_ID 和 COZE_API_KEY 环境变量")
        return
    
    # 创建 Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 注册命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # 注册消息处理器（处理所有文本消息）
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 启动 Bot
    logger.info("🚀 Telegram Bot 启动中...")
    
    # 使用 run_polling 启动轮询
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# ==================== 入口点 ====================
if __name__ == "__main__":
    main()
