"""
智能体API调用模块 - 优化版
减少日志输出，提升响应速度
"""
import os
import json
import requests
from typing import Dict, Any, Optional, Generator, List
from dotenv import load_dotenv

load_dotenv()


class AgentClient:
    """智能体API客户端 - 流式对话"""
    
    def __init__(self):
        """初始化智能体客户端"""
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        self.timeout = 900  # 15分钟超时
    
    def chat_stream(
        self,
        user_message: str,
        messages: List[Dict] = None,
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
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        
        # 处理API URL
        if '/stream_run' in self.api_url:
            stream_url = self.api_url
        elif self.api_url.endswith('/run'):
            stream_url = self.api_url.replace('/run', '/stream_run')
        else:
            stream_url = self.api_url.rstrip('/') + '/stream_run'
        
        # 构造Coze Bot期望的payload格式
        payload = {
            "content": {
                "query": {
                    "prompt": [
                        {
                            "type": "text",
                            "content": {
                                "text": user_message
                            }
                        }
                    ]
                }
            },
            "type": "query"
        }
        
        # 添加会话ID（确保用户隔离）
        if session_id:
            payload["session_id"] = session_id
        
        # 添加项目ID
        project_id = os.getenv('AGENT_PROJECT_ID')
        if project_id:
            payload["project_id"] = project_id
        
        # 构造headers
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            # 发送流式请求
            response = requests.post(
                stream_url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_text = response.text[:500]
                yield f"❌ API请求失败: {response.status_code}\n\n{error_text}"
                return
            
            # 处理SSE流式响应
            full_content = ""
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_text = line.decode('utf-8')
                
                if not line_text.strip():
                    continue
                
                # 跳过event行
                if line_text.startswith('event:'):
                    continue
                
                if line_text.startswith('data:'):
                    data_text = line_text[5:].strip()
                    
                    if data_text == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_text)
                        msg_type = data.get('type')
                        
                        if msg_type == 'answer':
                            content_obj = data.get('content', {})
                            
                            if isinstance(content_obj, dict):
                                answer_text = content_obj.get('answer', '')
                            else:
                                answer_text = str(content_obj)
                            
                            if answer_text:
                                full_content += answer_text
                                yield answer_text
                        
                        elif msg_type == 'message_end':
                            break
                    
                    except json.JSONDecodeError:
                        continue
                    
                    except Exception:
                        continue
        
        except requests.Timeout:
            yield "❌ 请求超时（超过15分钟），请稍后重试"
        
        except requests.RequestException as e:
            yield f"❌ 请求失败: {str(e)}"
        
        except Exception as e:
            yield f"❌ 未知错误: {str(e)}"


# 全局智能体客户端实例
agent_client = AgentClient()
