"""
后端服务主程序
提供 API 接口供小程序调用
支持单次分析和对话交互两种模式
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from typing import Optional, List
from datetime import datetime

from agent_wrapper import agent_instance

# 创建 FastAPI 应用
app = FastAPI(title="银行信贷分析助手 API", version="2.0.0")

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


class ChatRequest(BaseModel):
    """对话请求模型"""
    session_id: Optional[str] = None  # 会话ID，用于保持对话上下文
    message: str  # 用户消息


class ChatResponse(BaseModel):
    """对话响应模型"""
    session_id: str  # 会话ID
    reply: str  # Agent 的回复
    timestamp: str  # 时间戳


class Message(BaseModel):
    """消息模型"""
    role: str  # user 或 assistant
    content: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    """对话历史响应模型"""
    session_id: str
    messages: List[Message]


# ============ 内存存储（生产环境建议使用数据库）===========

tasks = {}  # 存储任务信息
sessions = {}  # 存储会话信息和对话历史


# ============ API 接口 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "银行信贷分析助手 API v2.0",
        "version": "2.0.0",
        "status": "running",
        "features": ["single_analysis", "chat_dialog"]
    }


# ============ 单次分析接口 ============

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_company(request: AnalyzeRequest):
    """
    提交分析请求（单次分析模式）

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


# ============ 对话接口 ============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口（支持多轮对话）

    Args:
        request: 对话请求

    Returns:
        Agent 的回复
    """
    # 获取或创建会话ID
    session_id = request.session_id or str(uuid.uuid4())

    # 初始化会话（如果不存在）
    if session_id not in sessions:
        sessions[session_id] = {
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.now()
        }

    # 添加用户消息到历史
    sessions[session_id]["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })

    try:
        # 调用 Agent（传入会话ID以保持记忆）
        reply = await agent_instance.chat(session_id, request.message)

        # 添加 Assistant 回复到历史
        sessions[session_id]["messages"].append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now().isoformat()
        })

        return ChatResponse(
            session_id=session_id,
            reply=reply,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        error_msg = f"对话失败: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/chat/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """
    获取对话历史

    Args:
        session_id: 会话ID

    Returns:
        对话历史
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    session = sessions[session_id]

    return ChatHistoryResponse(
        session_id=session_id,
        messages=session["messages"]
    )


@app.delete("/api/chat/{session_id}")
async def clear_chat_history(session_id: str):
    """
    清空对话历史

    Args:
        session_id: 会话ID

    Returns:
        操作结果
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 清空消息历史
    sessions[session_id]["messages"] = []

    return {
        "session_id": session_id,
        "message": "对话历史已清空"
    }


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
    print("银行信贷分析助手 API 服务 v2.0")
    print("=" * 60)
    print("服务地址: http://127.0.0.1:8000")
    print("API 文档: http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
