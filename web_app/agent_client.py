"""
智能体API调用模块 - 流式对话版本

负责调用银行信贷分析智能体API，支持流式响应。
"""
import os
import json
import requests
from typing import Dict, Any, Optional, Generator
from dotenv import load_dotenv

load_dotenv()


class AgentClient:
    """智能体API客户端 - 支持流式对话"""
    
    def __init__(self):
        """初始化智能体客户端"""
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        self.timeout = 900  # 15分钟超时
        
        # 自动推断流式接口地址
        if '/run' in self.api_url:
            # 如果是 /run 接口，改为流式接口
            self.stream_url = self.api_url.replace('/run', '/v1/chat/completions')
        else:
            self.stream_url = f"{self.api_url}/v1/chat/completions"
        
        print(f"[AgentClient] 初始化完成")
        print(f"[AgentClient] API URL: {self.api_url}")
        print(f"[AgentClient] Stream URL: {self.stream_url}")
        print(f"[AgentClient] API Key已设置: {bool(self.api_key)}")
    
    def chat_stream(
        self,
        user_message: str,
        messages: list = None,
        user_id: str = None,
        session_id: str = None
    ) -> Generator[str, None, None]:
        """
        流式对话
        
        Args:
            user_message: 用户消息
            messages: 历史消息列表
            user_id: 用户ID
            session_id: 会话ID
        
        Yields:
            流式响应的文本片段
        """
        # 重新读取环境变量
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        
        # 更新流式URL
        if '/run' in self.api_url:
            self.stream_url = self.api_url.replace('/run', '/v1/chat/completions')
        else:
            self.stream_url = f"{self.api_url}/v1/chat/completions"
        
        print(f"[AgentClient] 开始流式对话")
        print(f"[AgentClient] Stream URL: {self.stream_url}")
        print(f"[AgentClient] 用户消息: {user_message[:100]}...")
        
        # 构造OpenAI格式的消息
        openai_messages = []
        
        # 添加历史消息
        if messages:
            for msg in messages:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 添加当前用户消息
        openai_messages.append({
            "role": "user",
            "content": user_message
        })
        
        # 构造OpenAI兼容请求
        payload = {
            "model": "credit-analysis-agent",
            "messages": openai_messages,
            "stream": True,
            "temperature": 0.7
        }
        
        # 添加用户ID和会话ID（如果提供）
        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id
        
        print(f"[AgentClient] 请求payload: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        
        # 构造headers
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            # 发送流式请求
            response = requests.post(
                self.stream_url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
            
            print(f"[AgentClient] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                print(f"[AgentClient] 错误: {error_msg}")
                yield f"❌ {error_msg}"
                return
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    # 跳过空行
                    if not line_text.strip():
                        continue
                    
                    # 处理SSE格式
                    if line_text.startswith('data: '):
                        data_text = line_text[6:]  # 移除 'data: ' 前缀
                        
                        # 检查是否结束
                        if data_text.strip() == '[DONE]':
                            print("[AgentClient] 流式响应结束")
                            break
                        
                        # 解析JSON
                        try:
                            data = json.loads(data_text)
                            
                            # 提取内容
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    yield content
                            
                        except json.JSONDecodeError as e:
                            print(f"[AgentClient] JSON解析失败: {e}")
                            continue
            
            print("[AgentClient] 流式对话完成")
        
        except requests.Timeout:
            error_msg = "请求超时"
            print(f"[AgentClient] 错误: {error_msg}")
            yield f"❌ {error_msg}"
        
        except requests.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            print(f"[AgentClient] 错误: {error_msg}")
            yield f"❌ {error_msg}"
        
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"[AgentClient] 错误: {error_msg}")
            yield f"❌ {error_msg}"


# 全局智能体客户端实例
agent_client = AgentClient()
