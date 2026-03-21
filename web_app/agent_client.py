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
        # 如果URL已经包含 /stream_run，直接使用
        # 如果URL是 /run 结尾，替换为 /stream_run
        # 如果URL没有路径，添加 /stream_run
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
        
        # 构造智能体期望的payload格式
        payload = {
            "messages": [
                {
                    "type": "user",
                    "content": user_message
                }
            ]
        }
        
        # 添加用户ID和会话ID（用于会话隔离）
        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id
        
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
            print(f"[AgentClient] 响应headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                error_text = response.text[:500]
                print(f"[AgentClient] 错误响应: {error_text}")
                yield f"❌ API请求失败: {response.status_code}\n\n{error_text}"
                return
            
            # 处理流式响应
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    # 跳过空行
                    if not line_text.strip():
                        continue
                    
                    print(f"[AgentClient] 收到行: {line_text[:100]}...")
                    
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
                            
                            # 提取内容（适配多种格式）
                            content = None
                            
                            # 打印完整数据，用于调试
                            print(f"[AgentClient] 完整响应数据: {json.dumps(data, ensure_ascii=False)[:300]}")
                            
                            # 格式1: OpenAI格式 {"choices": [{"delta": {"content": "..."}}]}
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                print(f"[AgentClient] OpenAI格式，content类型: {type(content)}")
                            
                            # 格式2: 直接内容 {"content": "..."}
                            elif 'content' in data:
                                content = data['content']
                                print(f"[AgentClient] 直接内容格式，content类型: {type(content)}")
                            
                            # 格式3: 消息格式 {"message": {"content": "..."}}
                            elif 'message' in data:
                                content = data['message'].get('content', '')
                                print(f"[AgentClient] 消息格式，content类型: {type(content)}")
                            
                            # 格式4: 文本格式 {"text": "..."}
                            elif 'text' in data:
                                content = data['text']
                                print(f"[AgentClient] 文本格式，content类型: {type(content)}")
                            
                            # 确保content是字符串
                            if content:
                                # 多重保护：确保content一定是字符串
                                if isinstance(content, dict):
                                    # 如果content是字典，尝试提取text或content字段
                                    print(f"[AgentClient] content是字典: {content}")
                                    if 'text' in content:
                                        content = content['text']
                                    elif 'content' in content:
                                        content = content['content']
                                    else:
                                        # 如果没有这些字段，转为JSON字符串
                                        content = json.dumps(content, ensure_ascii=False)
                                
                                if not isinstance(content, str):
                                    print(f"[AgentClient] content不是字符串，尝试转换: {type(content)}")
                                    content = str(content)
                                
                                # 最终检查
                                if isinstance(content, str):
                                    full_content += content
                                    yield content
                                else:
                                    print(f"[AgentClient] 转换失败，跳过此内容")
                            else:
                                print(f"[AgentClient] 未找到有效content字段，跳过")
                        
                        except json.JSONDecodeError as e:
                            print(f"[AgentClient] JSON解析失败: {e}, 数据: {data_text[:100]}")
                            continue
                        
                        except Exception as e:
                            print(f"[AgentClient] 处理数据时出错: {e}, 数据: {data_text[:100]}")
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
