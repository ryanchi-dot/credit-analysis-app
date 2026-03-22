"""
智能体API调用模块 - 流式对话版本

负责调用银行信贷分析智能体API，支持流式响应。
"""
import os
import json
import requests
from typing import Dict, Any, Optional, Generator, List
from dotenv import load_dotenv

load_dotenv()


class AgentClient:
    """智能体API客户端 - 支持流式对话"""
    
    def __init__(self):
        """初始化智能体客户端"""
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        self.timeout = 900  # 15分钟超时
        
        print(f"[AgentClient] 初始化完成")
        print(f"[AgentClient] API URL: {self.api_url}")
        print(f"[AgentClient] API Key已设置: {bool(self.api_key)}")
    
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
            messages: 历史消息列表（暂不使用，因为智能体会自动管理历史）
            user_id: 用户ID
            session_id: 会话ID
        
        Yields:
            流式响应的文本片段
        """
        # 重新读取环境变量
        self.api_url = os.getenv('AGENT_API_URL', 'http://localhost:8000/run')
        self.api_key = os.getenv('AGENT_API_KEY', '')
        
        print(f"\n{'='*60}")
        print(f"[AgentClient] 开始流式对话")
        print(f"[AgentClient] 环境变量 AGENT_API_URL: {os.getenv('AGENT_API_URL', '未设置')}")
        print(f"[AgentClient] 环境变量 AGENT_API_KEY: {'已设置' if self.api_key else '未设置'}")
        print(f"[AgentClient] 实际使用 API URL: {self.api_url}")
        
        # 处理API URL
        if '/stream_run' in self.api_url:
            stream_url = self.api_url
            print(f"[AgentClient] 检测到 /stream_run 接口，直接使用: {stream_url}")
        elif self.api_url.endswith('/run'):
            stream_url = self.api_url.replace('/run', '/stream_run')
            print(f"[AgentClient] 检测到 /run 接口，改为使用流式接口: {stream_url}")
        else:
            stream_url = self.api_url.rstrip('/') + '/stream_run'
            print(f"[AgentClient] 未检测到接口路径，添加 /stream_run: {stream_url}")
        
        print(f"[AgentClient] 用户消息: {user_message[:100]}...")
        print(f"{'='*60}\n")
        
        # 构造Coze Bot期望的payload格式
        # 参考: curl命令中的格式
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
        
        # 添加会话ID（用于会话隔离）
        if session_id:
            payload["session_id"] = session_id
        
        # 添加项目ID（如果环境变量中有设置）
        project_id = os.getenv('AGENT_PROJECT_ID')
        if project_id:
            payload["project_id"] = project_id
        
        print(f"[AgentClient] 请求payload: {json.dumps(payload, ensure_ascii=False)}")
        
        # 构造headers
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            # 发送流式请求
            print(f"[AgentClient] 正在发送请求到: {stream_url}")
            response = requests.post(
                stream_url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
            
            print(f"[AgentClient] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text[:500]
                print(f"[AgentClient] 错误响应: {error_text}")
                yield f"❌ API请求失败: {response.status_code}\n\n{error_text}"
                return
            
            # 处理SSE流式响应
            full_content = ""
            
            # 使用iter_lines处理SSE格式
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_text = line.decode('utf-8')
                
                # 跳过空行
                if not line_text.strip():
                    continue
                
                print(f"[AgentClient] 收到行: {line_text[:150]}...")
                
                # 处理SSE格式的两种行：
                # 1. event: message（事件类型，可以忽略）
                # 2. data: {...}（数据内容，需要解析）
                
                if line_text.startswith('event:'):
                    # 事件类型行，忽略
                    print(f"[AgentClient] 跳过event行")
                    continue
                
                if line_text.startswith('data:'):
                    # 数据行，提取data:后面的JSON
                    data_text = line_text[5:].strip()  # 移除 'data:' 前缀
                    
                    # 检查是否结束
                    if data_text == '[DONE]':
                        print("[AgentClient] 收到[DONE]，流式响应结束")
                        break
                    
                    # 解析JSON
                    try:
                        data = json.loads(data_text)
                        
                        # 打印完整数据结构
                        print(f"[AgentClient] 完整数据: {json.dumps(data, ensure_ascii=False)[:300]}")
                        
                        # 提取文本内容（根据type字段判断）
                        msg_type = data.get('type')
                        
                        if msg_type == 'answer':
                            # answer类型的消息
                            # content是一个字典: {"answer": "文本", "thinking": null, ...}
                            content_obj = data.get('content', {})
                            
                            # 确保content_obj是字典
                            if isinstance(content_obj, dict):
                                answer_text = content_obj.get('answer', '')
                            else:
                                # 如果不是字典，尝试直接当作字符串
                                answer_text = str(content_obj)
                            
                            if answer_text:
                                print(f"[AgentClient] 提取到answer: {answer_text[:50]}..." if len(answer_text) > 50 else f"[AgentClient] 提取到answer: {answer_text}")
                                full_content += answer_text
                                yield answer_text
                        
                        elif msg_type == 'message_end':
                            # 消息结束
                            print("[AgentClient] 收到message_end，流式响应结束")
                            break
                        
                        # 其他类型（如message_start）可以忽略
                        else:
                            print(f"[AgentClient] 忽略type={msg_type}的消息")
                    
                    except json.JSONDecodeError as e:
                        print(f"[AgentClient] JSON解析失败: {e}, 数据: {data_text[:100]}")
                        continue
                    
                    except Exception as e:
                        print(f"[AgentClient] 处理数据时出错: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
            
            print(f"[AgentClient] 流式对话完成，总长度: {len(full_content)}")
        
        except requests.Timeout:
            error_msg = "请求超时（超过15分钟）"
            print(f"[AgentClient] 错误: {error_msg}")
            yield f"❌ {error_msg}"
        
        except requests.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            print(f"[AgentClient] 错误: {error_msg}")
            yield f"❌ {error_msg}"
        
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"[AgentClient] 错误: {error_msg}")
            import traceback
            traceback.print_exc()
            yield f"❌ {error_msg}"


# 全局智能体客户端实例
agent_client = AgentClient()
