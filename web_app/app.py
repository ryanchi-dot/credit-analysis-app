"""
银行信贷分析助手 - Streamlit主应用

功能：
- 无需注册，直接使用
- 真正的对话式界面（像ChatGPT）
- 文件上传
- 流式响应显示
- 历史记录
"""
import streamlit as st
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
from agent_client import agent_client
from utils import file_storage, format_file_size, is_allowed_file_type, get_file_type


# ============ 页面配置 ============
st.set_page_config(
    page_title="银行信贷分析助手",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e3a5f;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        
        .user-message {
            background-color: #e3f2fd;
            margin-left: 2rem;
        }
        
        .assistant-message {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            margin-right: 2rem;
        }
        
        .report-link {
            display: inline-block;
            margin: 0.5rem 0.5rem 0.5rem 0;
            padding: 0.5rem 1rem;
            background-color: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 5px;
            color: #2e7d32;
            text-decoration: none;
        }
        
        .report-link:hover {
            background-color: #c8e6c9;
        }
        
        .file-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background-color: #fff3e0;
            border-radius: 3px;
            font-size: 0.85rem;
            margin: 0.25rem;
        }
        
        .sidebar-section {
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)


# ============ 初始化Session State ============
def init_session_state():
    """初始化session state"""
    # 生成唯一用户ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"guest_{uuid.uuid4().hex[:16]}"
    
    # 当前会话ID
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    
    # 对话消息列表
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 历史会话
    if 'history' not in st.session_state:
        st.session_state.history = []


# ============ 侧边栏 ============
def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.markdown("### 🏦 银行信贷分析助手")
        st.markdown("---")
        
        # 使用说明
        with st.expander("📖 使用说明", expanded=False):
            st.markdown("""
            **这是一个AI助手，专门用于生成银行授信分析报告。**
            
            你可以这样问我：
            - "帮我分析腾讯的授信风险"
            - "生成京东的授信分析报告"
            - "分析一下字节跳动的财务情况"
            
            **功能特点**：
            - ✅ 自动搜集企业公开信息
            - ✅ 生成专业的授信分析报告
            - ✅ 支持上传参考资料
            - ✅ 实时对话交互
            
            **预计耗时**：5-8分钟
            """)
        
        st.markdown("---")
        
        # 文件上传区域
        st.markdown("### 📎 上传参考资料")
        uploaded_files = st.file_uploader(
            "支持PDF、Word、Excel、图片",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )
        
        # 显示已上传文件
        if uploaded_files:
            st.info(f"已上传 {len(uploaded_files)} 个文件")
            for file in uploaded_files:
                st.markdown(f"<span class='file-badge'>{file.name}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 历史记录
        st.markdown("### 📝 历史记录")
        if st.session_state.history:
            for i, session in enumerate(st.session_state.history[:10]):  # 只显示最近10条
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"{session['title'][:15]}...",
                        key=f"history_{i}",
                        help=session['created_at']
                    ):
                        load_history_session(i)
                with col2:
                    if st.button("🗑️", key=f"del_{i}", help="删除"):
                        st.session_state.history.pop(i)
                        st.rerun()
        else:
            st.info("暂无历史记录")
        
        st.markdown("---")
        
        # 新建会话
        if st.button("➕ 新建会话", use_container_width=True):
            create_new_session()
        
        # 清空当前会话
        if st.button("🗑️ 清空当前会话", use_container_width=True):
            clear_current_session()
        
        st.markdown("---")
        
        # 版本信息
        st.caption("版本: 2.0 | Powered by AI")


# ============ 主界面 ============
def show_main_page():
    """显示主界面"""
    # 侧边栏
    show_sidebar()
    
    # 主标题
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 显示对话消息
    display_chat_messages()
    
    # 聊天输入
    handle_chat_input()


# ============ 显示对话消息 ============
def display_chat_messages():
    """显示所有对话消息"""
    if not st.session_state.messages:
        # 欢迎消息
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h2>👋 欢迎使用银行信贷分析助手！</h2>
            <p>我是一个AI助手，专门帮助您生成专业的银行授信分析报告。</p>
            <p>您可以直接输入企业名称或描述您的需求，我会为您分析并生成报告。</p>
            <br>
            <p><strong>示例提问：</strong></p>
            <p>• 帮我分析腾讯控股有限公司的授信风险</p>
            <p>• 生成京东集团股份有限公司的授信分析报告</p>
            <p>• 分析一下字节跳动的财务状况和行业地位</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 显示所有消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🏦"):
            # 显示消息内容
            st.markdown(msg["content"])
            
            # 显示上传的文件（如果有）
            if msg.get("files"):
                st.markdown("**📎 已上传文件**:")
                for file_info in msg["files"]:
                    st.markdown(f"<span class='file-badge'>{file_info['name']}</span>", unsafe_allow_html=True)
            
            # 显示报告链接（如果有）
            if msg.get("report_links"):
                st.markdown("**📥 报告下载**:")
                links = msg["report_links"]
                
                cols = st.columns(min(4, len(links)))
                link_names = [
                    "申报方案分析",
                    "财务分析",
                    "行业分析",
                    "结论"
                ]
                
                for i, (col, name) in enumerate(zip(cols, link_names)):
                    key = f"report_part{i+1}_url"
                    if key in links and links[key]:
                        with col:
                            st.link_button(
                                f"📄 {name}",
                                links[key],
                                use_container_width=True
                            )


# ============ 处理聊天输入 ============
def handle_chat_input():
    """处理用户输入"""
    # 获取上传的文件
    uploaded_files = st.session_state.get('file_uploader', [])
    
    # 聊天输入框
    if prompt := st.chat_input("输入企业名称或描述你的需求..."):
        # 添加用户消息
        user_msg = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        # 处理上传的文件
        if uploaded_files:
            user_msg["files"] = []
            for uploaded_file in uploaded_files:
                if is_allowed_file_type(uploaded_file.name):
                    # 保存文件
                    file_path = file_storage.save_file(
                        st.session_state.user_id,
                        uploaded_file.name,
                        uploaded_file.read()
                    )
                    
                    user_msg["files"].append({
                        'name': uploaded_file.name,
                        'size': format_file_size(uploaded_file.size),
                        'type': get_file_type(uploaded_file.name),
                        'path': file_path
                    })
        
        # 添加到消息列表
        st.session_state.messages.append(user_msg)
        
        # 准备历史消息（用于上下文）
        history_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages[:-1]  # 不包括当前消息
        ]
        
        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if user_msg.get("files"):
                st.markdown("**📎 已上传文件**:")
                for file_info in user_msg["files"]:
                    st.markdown(f"<span class='file-badge'>{file_info['name']}</span>", unsafe_allow_html=True)
        
        # 显示助手回复（流式）
        with st.chat_message("assistant", avatar="🏦"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 显示进度提示
            with st.spinner("思考中..."):
                # 调用智能体流式API
                response_stream = agent_client.chat_stream(
                    user_message=prompt,
                    messages=history_messages,
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.current_session_id
                )
            
            # 流式显示响应
            for chunk in response_stream:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            # 最终显示（移除光标）
            message_placeholder.markdown(full_response)
            
            # 提取报告链接（如果有）
            report_links = extract_report_links(full_response)
            
            if report_links:
                st.markdown("**📥 报告下载**:")
                cols = st.columns(min(4, len(report_links)))
                link_names = ["申报方案分析", "财务分析", "行业分析", "结论"]
                
                for i, (col, name) in enumerate(zip(cols, link_names)):
                    key = f"report_part{i+1}_url"
                    if key in report_links and report_links[key]:
                        with col:
                            st.link_button(
                                f"📄 {name}",
                                report_links[key],
                                use_container_width=True
                            )
        
        # 添加助手消息到历史
        assistant_msg = {
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().isoformat()
        }
        
        if report_links:
            assistant_msg["report_links"] = report_links
        
        st.session_state.messages.append(assistant_msg)
        
        # 保存到历史记录
        save_to_history(prompt)
        
        # 清空文件上传器
        if uploaded_files:
            st.session_state.file_uploader = []
        
        # 刷新页面
        st.rerun()


# ============ 工具函数 ============
def extract_report_links(text: str) -> Dict[str, str]:
    """从文本中提取报告链接"""
    import re
    
    links = {}
    
    # 匹配Markdown链接格式
    # [申报方案分析与客户分析](https://...)
    patterns = {
        "report_part1_url": r'\[.*?申报方案.*?\]\((https?://[^\)]+\.docx?)\)',
        "report_part2_url": r'\[.*?财务分析.*?\]\((https?://[^\)]+\.docx?)\)',
        "report_part3_url": r'\[.*?行业分析.*?\]\((https?://[^\)]+\.docx?)\)',
        "report_part4_url": r'\[.*?结论.*?\]\((https?://[^\)]+\.docx?)\)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            links[key] = match.group(1)
    
    # 也尝试匹配普通URL格式
    # https://.../report_part1.docx
    url_pattern = r'(https?://[^\s<>"]+\.docx?)'
    all_urls = re.findall(url_pattern, text)
    
    for i, url in enumerate(all_urls[:4]):  # 最多4个
        key = f"report_part{i+1}_url"
        if key not in links:
            links[key] = url
    
    return links if links else None


def save_to_history(user_message: str):
    """保存到历史记录"""
    # 提取标题（取前20个字符）
    title = user_message[:30] + "..." if len(user_message) > 30 else user_message
    
    session = {
        'session_id': st.session_state.current_session_id,
        'title': title,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'messages': st.session_state.messages.copy()
    }
    
    # 检查是否已存在相同session_id
    existing_index = None
    for i, s in enumerate(st.session_state.history):
        if s['session_id'] == session['session_id']:
            existing_index = i
            break
    
    if existing_index is not None:
        # 更新现有会话
        st.session_state.history[existing_index] = session
    else:
        # 添加新会话（保留最近20条）
        st.session_state.history.insert(0, session)
        if len(st.session_state.history) > 20:
            st.session_state.history.pop()


def create_new_session():
    """创建新会话"""
    st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    st.session_state.messages = []
    st.rerun()


def load_history_session(index: int):
    """加载历史会话"""
    if 0 <= index < len(st.session_state.history):
        session = st.session_state.history[index]
        st.session_state.current_session_id = session['session_id']
        st.session_state.messages = session['messages'].copy()
        st.rerun()


def clear_current_session():
    """清空当前会话"""
    st.session_state.messages = []
    st.rerun()


# ============ 主程序 ============
def main():
    """主函数"""
    # 初始化session state
    init_session_state()
    
    # 显示主界面
    show_main_page()


if __name__ == "__main__":
    main()
