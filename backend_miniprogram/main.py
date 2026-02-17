"""
后端服务主程序
提供 API 接口供小程序调用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from typing import Optional
from datetime import datetime

from agent_wrapper import agent_instance

# 创建 FastAPI 应用
app = FastAPI(title="银行信贷分析助手 API", version="1.0.0")

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


# ============ 内存存储（生产环境建议使用数据库）===========

tasks = {}  # 存储任务信息


# ============ API 接口 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "银行信贷分析助手 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_company(request: AnalyzeRequest):
    """
    提交分析请求

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
    print("银行信贷分析助手 API 服务")
    print("=" * 60)
    print("服务地址: http://127.0.0.1:8000")
    print("API 文档: http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
