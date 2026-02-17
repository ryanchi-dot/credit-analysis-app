"""
Agent 调用封装
用于调用银行信贷分析助手 Agent
"""

import os
import sys

# 添加项目根目录到 Python 路径
# 注意：这里的路径需要根据实际部署情况调整
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.agent import build_agent
from langchain_core.messages import HumanMessage


class CreditAnalysisAgent:
    """银行信贷分析助手 Agent 封装"""

    def __init__(self):
        """初始化 Agent"""
        self.agent = None

    def get_agent(self):
        """获取 Agent 实例（单例模式）"""
        if self.agent is None:
            print("正在初始化 Agent...")
            self.agent = build_agent()
            print("Agent 初始化完成！")
        return self.agent

    async def analyze_company(self, company_name: str, template: str = "standard") -> str:
        """
        分析公司授信情况

        Args:
            company_name: 公司名称
            template: 分析模板（默认 standard）

        Returns:
            分析报告文本
        """
        try:
            agent = self.get_agent()

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


# 创建全局 Agent 实例
agent_instance = CreditAnalysisAgent()
