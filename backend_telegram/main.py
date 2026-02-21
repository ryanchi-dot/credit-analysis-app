"""
Telegram Bot 后端服务
用于与 Telegram Bot API 交互，调用 Agent 生成回复
"""

import os
import sys
import json
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import requests
import asyncio
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入 Agent
from agents.agent import build_agent
from langchain_core.messages import HumanMessage, AIMessage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI
app = FastAPI(title="Telegram Bot API", version="1.0.0")

# Telegram Bot Token (从环境变量获取)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 如果没有设置环境变量，从配置文件读取
if not TELEGRAM_BOT_TOKEN:
    try:
        with open("telegram_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            TELEGRAM_BOT_TOKEN = config.get("telegram_bot_token")
    except FileNotFoundError:
        logger.warning("telegram_config.json not found, please set TELEGRAM_BOT_TOKEN env var")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set! Please set environment variable or create telegram_config.json")

# Telegram API Base URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# 存储 Agent 实例（每个 chat_id 一个独立实例）
agents_cache = {}

# 锁，防止并发问题
import threading
agent_lock = threading.Lock()

# 请求模型
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None

class SendMessageRequest(BaseModel):
    chat_id: int
    text: str
    parse_mode: Optional[str] = "Markdown"


def get_or_create_agent(chat_id: int):
    """获取或创建 Agent 实例"""
    with agent_lock:
        if chat_id not in agents_cache:
            logger.info(f"Creating new agent for chat_id: {chat_id}")
            agent = build_agent()
            agents_cache[chat_id] = agent
        return agents_cache[chat_id]


def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """发送消息到 Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    # 处理消息，限制长度（Telegram 单条消息最大 4096 字符）
    max_length = 4000
    messages = []
    
    if len(text) > max_length:
        # 分割长消息
        for i in range(0, len(text), max_length):
            messages.append(text[i:i + max_length])
    else:
        messages.append(text)
    
    # 发送所有消息段
    for msg_text in messages:
        # 移除可能导致 Markdown 解析错误的特殊字符
        safe_text = msg_text.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
        
        payload = {
            "chat_id": chat_id,
            "text": safe_text,
            "parse_mode": parse_mode if parse_mode else None
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Message sent to chat_id {chat_id}, length: {len(msg_text)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Telegram: {e}")
            # 尝试不带 parse_mode 发送
            try:
                payload["parse_mode"] = None
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
            except:
                logger.error("Failed to send message even without parse_mode")


def send_typing_action(chat_id: int):
    """发送"正在输入"状态"""
    url = f"{TELEGRAM_API_URL}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "running",
        "service": "Telegram Bot API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook")
async def webhook(request: Request):
    """接收 Telegram Webhook"""
    try:
        # 解析请求体
        data = await request.json()
        logger.info(f"Received update: {json.dumps(data, ensure_ascii=False)}")
        
        # 检查是否是消息
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            logger.info(f"Chat ID: {chat_id}, Message: {text}")
            
            # 处理命令
            if text.startswith("/"):
                await handle_command(chat_id, text)
            else:
                # 处理普通消息
                await handle_message(chat_id, text)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def handle_command(chat_id: int, command: str):
    """处理 Bot 命令"""
    if command == "/start":
        send_telegram_message(
            chat_id,
            "👋 欢迎使用银行信贷分析助手！\n\n"
            "我可以帮您：\n"
            "• 分析企业的授信情况\n"
            "• 生成完整的授信分析报告\n"
            "• 回答关于企业财务、风险的问题\n\n"
            "💡 使用方法：\n"
            "直接发送公司名称，例如：'腾讯' 或 '中国移动通信集团有限公司'\n\n"
            "📊 其他命令：\n"
            "/help - 查看帮助\n"
            "/clear - 清空对话历史\n"
            "/about - 关于"
        )
    elif command == "/help":
        send_telegram_message(
            chat_id,
            "📖 帮助信息\n\n"
            "🎯 主要功能：\n"
            "1. 企业授信分析 - 发送公司名称，获取完整报告\n"
            "2. 对话交互 - 连续提问，深入了解\n\n"
            "💬 使用示例：\n"
            "• '分析腾讯'\n"
            "• '中国移动财务怎么样？'\n"
            "• '腾讯有什么风险？'\n\n"
            "📋 支持的命令：\n"
            "/start - 开始使用\n"
            "/help - 查看帮助\n"
            "/clear - 清空对话历史\n"
            "/about - 关于"
        )
    elif command == "/clear":
        # 清空该用户的 Agent 实例
        with agent_lock:
            if chat_id in agents_cache:
                del agents_cache[chat_id]
        send_telegram_message(chat_id, "✅ 对话历史已清空")
    elif command == "/about":
        send_telegram_message(
            chat_id,
            "🤖 关于银行信贷分析助手\n\n"
            "这是一个基于 AI 的企业信贷分析工具，可以：\n"
            "• 搜集企业公开信息\n"
            "• 分析财务状况\n"
            "• 评估风险等级\n"
            "• 生成专业报告\n\n"
            "版本：1.0.0\n"
            "技术：LangChain + LangGraph + doubao-seed"
        )
    else:
        send_telegram_message(
            chat_id,
            "❓ 未知命令。使用 /help 查看可用命令。"
        )


async def handle_message(chat_id: int, text: str):
    """处理普通消息"""
    if not text.strip():
        return
    
    try:
        # 发送"正在输入"状态
        send_typing_action(chat_id)
        
        # 获取或创建 Agent
        agent = get_or_create_agent(chat_id)
        
        # 创建配置
        config = {"configurable": {"thread_id": str(chat_id)}}
        
        # 调用 Agent
        logger.info(f"Processing message for chat_id {chat_id}: {text}")
        
        # 异步调用 Agent
        response = await asyncio.to_thread(
            agent.invoke,
            {"messages": [HumanMessage(content=text)]},
            config
        )
        
        # 提取回复
        reply = response["messages"][-1].content
        
        logger.info(f"Agent response for chat_id {chat_id}: {reply[:100]}...")
        
        # 发送回复
        send_telegram_message(chat_id, reply)
    
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        send_telegram_message(
            chat_id,
            f"❌ 处理请求时出错：{str(e)}\n\n请稍后重试。"
        )


@app.post("/api/send")
async def send_message(req: SendMessageRequest):
    """手动发送消息到 Telegram（用于测试）"""
    try:
        send_telegram_message(req.chat_id, req.text, req.parse_mode)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhook/info")
async def get_webhook_info():
    """获取当前 Webhook 信息"""
    url = f"{TELEGRAM_API_URL}/getWebhookInfo"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/set")
async def set_webhook(webhook_url: str):
    """设置 Webhook"""
    url = f"{TELEGRAM_API_URL}/setWebhook"
    try:
        response = requests.post(url, json={"url": webhook_url})
        response.raise_for_status()
        logger.info(f"Webhook set to: {webhook_url}")
        return response.json()
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/delete")
async def delete_webhook():
    """删除 Webhook"""
    url = f"{TELEGRAM_API_URL}/deleteWebhook"
    try:
        response = requests.post(url)
        response.raise_for_status()
        logger.info("Webhook deleted")
        return response.json()
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 启动服务
    logger.info("Starting Telegram Bot API server...")
    logger.info(f"Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
