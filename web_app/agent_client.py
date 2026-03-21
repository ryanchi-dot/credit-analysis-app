"""
智能体API调用模块

负责调用银行信贷分析智能体API。
"""
import os
import json
import requests
from typing import Dict, Any, Optional


class AgentClient:
    """智能体API客户端"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        初始化智能体客户端
        
        Args:
            api_url: 智能体API URL
            api_key: API密钥（可选）
        """
        self.api_url = api_url or os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = api_key or os.getenv('AGENT_API_KEY', '')
        self.timeout = 900  # 15分钟超时
        
        # 调试信息
        print(f"[AgentClient] 初始化完成")
        print(f"[AgentClient] API URL: {self.api_url}")
        print(f"[AgentClient] API Key已设置: {bool(self.api_key)}")
    
    def analyze_company(
        self, 
        company_name: str, 
        analysis_focus: str = "全面分析（推荐）",
        has_reference_materials: str = "否",
        user_id: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        调用智能体分析企业
        
        Args:
            company_name: 企业名称
            analysis_focus: 分析重点
            has_reference_materials: 是否有参考材料
            user_id: 用户ID（用于会话隔离）
            session_id: 会话ID（用于会话隔离）
        
        Returns:
            智能体返回的结果
        """
        # 重新读取环境变量（确保在Docker环境中能正确获取）
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        
        print(f"[AgentClient] 开始分析企业: {company_name}")
        print(f"[AgentClient] 当前API URL: {self.api_url}")
        print(f"[AgentClient] API Key已设置: {bool(self.api_key)}")
        
        # 构造用户消息
        user_message = f"请为【{company_name}】生成授信分析报告。"
        
        if analysis_focus and analysis_focus != "全面分析（推荐）":
            user_message += f"分析重点是：{analysis_focus}。"
        
        if has_reference_materials == "是":
            user_message += "我将提供参考材料。"
        else:
            user_message += "无参考材料，请基于公开信息分析。"
        
        # 构造请求参数
        payload = {
            "messages": [
                {
                    "type": "user",
                    "content": user_message
                }
            ]
        }
        
        # 如果提供了user_id和session_id，添加到请求中
        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id
        
        # 调用API
        try:
            print(f"[AgentClient] 发送请求到: {self.api_url}")
            print(f"[AgentClient] 请求payload: {json.dumps(payload, ensure_ascii=False)}")
            print(f"[AgentClient] 使用API Key: {self.api_key[:50]}..." if self.api_key else "[AgentClient] 未使用API Key")
            
            headers = {
                'Content-Type': 'application/json',
            }
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            print(f"[AgentClient] 请求headers: {headers}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            print(f"[AgentClient] 响应状态码: {response.status_code}")
            print(f"[AgentClient] 响应内容: {response.text[:500]}..." if len(response.text) > 500 else f"[AgentClient] 响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            print(f"[AgentClient] 解析后的JSON: {json.dumps(result, ensure_ascii=False)[:500]}")
            
            # 提取报告链接
            report_links = self._extract_report_links(result)
            
            print(f"[AgentClient] 提取到的报告链接: {report_links}")
            
            if report_links:
                return {
                    "success": True,
                    "report_links": report_links,
                    "raw_response": result
                }
            else:
                # 如果没有提取到报告链接，返回原始响应
                print(f"[AgentClient] 未提取到报告链接，返回原始响应")
                return {
                    "success": False,
                    "message": "未提取到报告链接",
                    "raw_response": result
                }
        
        except requests.Timeout:
            return {
                "success": False,
                "message": f"请求超时（超过{self.timeout}秒）"
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"请求失败: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "响应格式错误"
            }
    
    def _extract_report_links(self, response: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        从智能体响应中提取报告链接
        
        Args:
            response: 智能体响应
        
        Returns:
            报告链接字典
        """
        import re
        
        # 检查响应中是否包含报告链接
        if "report_part1_url" in response:
            return {
                "report_part1_url": response.get("report_part1_url", ""),
                "report_part2_url": response.get("report_part2_url", ""),
                "report_part3_url": response.get("report_part3_url", ""),
                "report_part4_url": response.get("report_part4_url", ""),
                "report_summary": response.get("report_summary", "")
            }
        
        # 如果messages中包含链接，尝试提取
        if "messages" in response:
            all_content = ""
            for msg in response["messages"]:
                content = msg.get("content", "")
                if isinstance(content, str):
                    all_content += content + "\n"
            
            # 使用正则表达式提取URL
            url_pattern = r'https?://[^\s<>"]+\.docx?[^\s<>"]*'
            url_matches = re.findall(url_pattern, all_content)
            
            if url_matches:
                return {
                    "report_part1_url": url_matches[0] if len(url_matches) > 0 else "",
                    "report_part2_url": url_matches[1] if len(url_matches) > 1 else "",
                    "report_part3_url": url_matches[2] if len(url_matches) > 2 else "",
                    "report_part4_url": url_matches[3] if len(url_matches) > 3 else "",
                    "report_summary": all_content[:200] + "..." if len(all_content) > 200 else all_content
                }
        
        return None


# 全局智能体客户端实例
agent_client = AgentClient()
