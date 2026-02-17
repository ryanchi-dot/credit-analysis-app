"""
Agent 调用封装
用于调用银行信贷分析助手 Agent
支持单次分析和多轮对话
"""

import os
import sys
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.agent import build_agent


class CreditAnalysisAgent:
    """银行信贷分析助手 Agent 封装"""

    def __init__(self):
        """初始化 Agent"""
        self.agents = {}  # 为每个 session_id 创建独立的 Agent 实例
        self.default_agent = None

    def get_agent(self, session_id: Optional[str] = None):
        """
        获取 Agent 实例（支持多会话）

        Args:
            session_id: 会话ID，如果为None则返回默认Agent

        Returns:
            Agent 实例
        """
        # 如果没有提供 session_id，使用默认 Agent
        if session_id is None:
            if self.default_agent is None:
                print("正在初始化默认 Agent...")
                self.default_agent = build_agent()
                print("默认 Agent 初始化完成！")
            return self.default_agent

        # 为每个 session_id 创建独立的 Agent 实例（以保持独立记忆）
        if session_id not in self.agents:
            print(f"正在初始化会话 {session_id} 的 Agent...")
            self.agents[session_id] = build_agent()
            print(f"会话 {session_id} 的 Agent 初始化完成！")

        return self.agents[session_id]

    async def analyze_company(self, company_name: str, template: str = "standard") -> str:
        """
        分析公司授信情况（单次分析）

        Args:
            company_name: 公司名称
            template: 分析模板（默认 standard）

        Returns:
            分析报告文本
        """
        try:
            # 使用默认 Agent（不需要记忆）
            agent = self.get_agent(None)

            # 构建用户消息
            user_message = f"请分析{company_name}的授信情况。使用标准模板，没有额外材料。"

            # 调用 Agent
            print(f"开始分析: {company_name}")
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_message)]}
            )

            # 提取回复内容
            report_text = response["messages"][-1].content
            print(f"分析完成！报告长度: {len(report_text)} 字符")

            return report_text

        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            print(error_msg)
            return error_msg

    async def chat(self, session_id: str, user_message: str) -> str:
        """
        对话交互（支持多轮对话，保持记忆）

        Args:
            session_id: 会话ID（用于保持对话上下文）
            user_message: 用户消息

        Returns:
            Agent 的回复
        """
        try:
            # 使用特定会话的 Agent（保持记忆）
            agent = self.get_agent(session_id)

            # 调用 Agent（使用 thread_id 区分不同会话）
            print(f"[会话 {session_id}] 用户消息: {user_message[:50]}...")
            config = {"configurable": {"thread_id": session_id}}

            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_message)]},
                config=config
            )

            # 提取回复内容
            reply = response["messages"][-1].content
            print(f"[会话 {session_id}] Agent 回复长度: {len(reply)} 字符")

            return reply

        except Exception as e:
            error_msg = f"对话失败: {str(e)}"
            print(error_msg)
            return error_msg


# 创建全局 Agent 实例
agent_instance = CreditAnalysisAgent()
