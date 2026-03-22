"""
银行信贷分析助手 - Streamlit主应用
优化版本：快速响应 + 类DeepSeek输入框
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
    initial_sidebar_state="collapsed"  # 默认收起侧边栏，加快加载
)

# 自定义CSS（优化样式）
st.markdown("""
    <style>
        /* 隐藏默认的Streamlit元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 主容器 */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem;
            max-width: 1000px;
        }
        
        /* 标题样式 */
        .main-title {
            font-size: 2rem;
            font-weight: bold;
            color: #1e3a5f;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        /* 聊天消息样式 */
        .stChatMessage {
            padding: 0.5rem 0;
        }
        
        /* 文件标签样式 */
        .file-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background-color: #e3f2fd;
            border-radius: 12px;
            font-size: 0.8rem;
            margin: 0.25rem;
            color: #1565c0;
        }
        
        /* 上传按钮样式 */
        .upload-btn {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.5rem;
            color: #666;
        }
        
        .upload-btn:hover {
            background-color: #e0e0e0;
        }
        
        /* 侧边栏样式 */
        section[data-testid="stSidebar"] {
            width: 300px !important;
        }
        
        /* 响应式布局 */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)


# ============ 初始化Session State ============
def init_session_state():
    """初始化session state - 确保每个用户独立"""
    # 用户ID（使用浏览器session，每个浏览器会话唯一）
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:16]}"
    
    # 当前会话ID（每次新建对话生成新的）
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    
    # 对话消息列表
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 已上传文件列表（临时存储）
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # 历史会话
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # 显示上传对话框
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False


# ============ 主界面 ============
def show_main_page():
    """显示主界面"""
    # 顶部工具栏
    show_top_bar()
    
    # 主标题
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    
    # 显示对话消息
    display_chat_messages()
    
    # 底部输入区域（类似DeepSeek）
    handle_chat_input_with_upload()


# ============ 顶部工具栏 ============
def show_top_bar():
    """显示顶部工具栏"""
    col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
    
    with col2:
        # 新建对话按钮
        if st.button("➕", help="新建对话", key="new_chat_btn"):
            create_new_session()
            st.rerun()
    
    with col3:
        # 历史记录按钮（打开侧边栏）
        if st.button("📝", help="历史记录", key="history_btn"):
            st.session_state.show_sidebar = not st.session_state.get('show_sidebar', False)
    
    with col4:
        # 使用说明按钮
        if st.button("❓", help="使用说明", key="help_btn"):
            st.session_state.show_help = not st.session_state.get('show_help', False)
    
    # 显示帮助信息
    if st.session_state.get('show_help', False):
        with st.expander("📖 使用说明", expanded=True):
            st.markdown("""
            **直接输入企业名称，我会立即为您生成授信分析报告！**
            
            **示例**：
            - 百度在线网络技术（北京）有限公司
            - 腾讯控股有限公司
            - 阿里巴巴集团
            
            **功能特点**：
            - ✅ 自动搜集企业公开信息
            - ✅ 生成专业的授信分析报告
            - ✅ 支持上传参考资料
            - ✅ 实时对话交互
            
            **预计耗时**：5-8分钟
            """)
    
    st.markdown("---")


# ============ 显示对话消息 ============
def display_chat_messages():
    """显示所有对话消息"""
    if not st.session_state.messages:
        # 欢迎消息
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; color: #666;">
            <h2>👋 欢迎使用银行信贷分析助手！</h2>
            <p style="font-size: 1.1rem; margin: 1rem 0;">直接输入企业名称，我会立即为您生成授信分析报告</p>
            <div style="margin-top: 2rem;">
                <p><strong>快速开始：</strong></p>
                <p style="color: #1565c0; cursor: pointer;" onclick="document.querySelector('textarea').value='百度在线网络技术（北京）有限公司';">
                    • 百度在线网络技术（北京）有限公司
                </p>
                <p style="color: #1565c0; cursor: pointer;" onclick="document.querySelector('textarea').value='腾讯控股有限公司';">
                    • 腾讯控股有限公司
                </p>
                <p style="color: #1565c0; cursor: pointer;" onclick="document.querySelector('textarea').value='阿里巴巴集团';">
                    • 阿里巴巴集团
                </p>
            </div>
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
                files_html = " ".join([f'<span class="file-badge">📎 {f["name"]}</span>' for f in msg["files"]])
                st.markdown(files_html, unsafe_allow_html=True)
            
            # 显示报告链接（如果有）
            if msg.get("report_links"):
                st.markdown("**📥 报告下载**:")
                links = msg["report_links"]
                cols = st.columns(min(4, len(links)))
                link_names = ["申报方案分析", "财务分析", "行业分析", "结论"]
                
                for i, (col, name) in enumerate(zip(cols, link_names)):
                    key = f"report_part{i+1}_url"
                    if key in links and links[key]:
                        with col:
                            st.link_button(f"📄 {name}", links[key], use_container_width=True)


# ============ 处理聊天输入（带上传功能） ============
def handle_chat_input_with_upload():
    """处理用户输入 - 类似DeepSeek的输入框"""
    
    # 显示已上传的文件标签
    if st.session_state.uploaded_files:
        files_html = " ".join([f'<span class="file-badge">📎 {f["name"]}</span>' for f in st.session_state.uploaded_files])
        st.markdown(files_html, unsafe_allow_html=True)
    
    # 使用容器创建底部输入区域
    with st.container():
        # 创建两列：主输入框 + 上传按钮
        col1, col2 = st.columns([12, 1])
        
        with col1:
            # 聊天输入框
            prompt = st.chat_input("输入企业名称开始分析...", key="main_chat_input")
        
        with col2:
            # 上传按钮（+号）
            st.markdown("""
                <style>
                .upload-container {
                    position: relative;
                    margin-top: 25px;
                }
                </style>
                <div class="upload-container">
            """, unsafe_allow_html=True)
            
            # 使用expander来模拟弹出上传窗口
            with st.expander("", expanded=st.session_state.get('show_upload', False)):
                uploaded_files = st.file_uploader(
                    "上传参考资料",
                    type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
                    accept_multiple_files=True,
                    key="file_uploader_popup",
                    label_visibility="collapsed"
                )
                
                if uploaded_files:
                    # 保存上传的文件
                    for uploaded_file in uploaded_files:
                        if is_allowed_file_type(uploaded_file.name):
                            file_path = file_storage.save_file(
                                st.session_state.user_id,
                                uploaded_file.name,
                                uploaded_file.read()
                            )
                            
                            # 检查是否已存在
                            exists = any(f['name'] == uploaded_file.name for f in st.session_state.uploaded_files)
                            if not exists:
                                st.session_state.uploaded_files.append({
                                    'name': uploaded_file.name,
                                    'size': format_file_size(uploaded_file.size),
                                    'type': get_file_type(uploaded_file.name),
                                    'path': file_path
                                })
                    
                    st.success(f"已上传 {len(uploaded_files)} 个文件")
    
    # 处理用户输入
    if prompt:
        process_user_message(prompt)


# ============ 处理用户消息 ============
def process_user_message(prompt: str):
    """处理用户消息并发送请求"""
    # 添加用户消息
    user_msg = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加上传的文件（如果有）
    if st.session_state.uploaded_files:
        user_msg["files"] = st.session_state.uploaded_files.copy()
    
    # 添加到消息列表
    st.session_state.messages.append(user_msg)
    
    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        if user_msg.get("files"):
            files_html = " ".join([f'<span class="file-badge">📎 {f["name"]}</span>' for f in user_msg["files"]])
            st.markdown(files_html, unsafe_allow_html=True)
    
    # 显示助手回复（流式）
    with st.chat_message("assistant", avatar="🏦"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 调用智能体流式API（不显示spinner，加快响应感知）
        response_stream = agent_client.chat_stream(
            user_message=prompt,
            user_id=st.session_state.user_id,
            session_id=st.session_state.current_session_id
        )
        
        # 流式显示响应
        for chunk in response_stream:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        # 最终显示
        message_placeholder.markdown(full_response)
        
        # 提取报告链接
        report_links = extract_report_links(full_response)
        
        if report_links:
            st.markdown("**📥 报告下载**:")
            cols = st.columns(min(4, len(report_links)))
            link_names = ["申报方案分析", "财务分析", "行业分析", "结论"]
            
            for i, (col, name) in enumerate(zip(cols, link_names)):
                key = f"report_part{i+1}_url"
                if key in report_links and report_links[key]:
                    with col:
                        st.link_button(f"📄 {name}", report_links[key], use_container_width=True)
    
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
    
    # 清空上传的文件
    st.session_state.uploaded_files = []
    
    # 刷新页面
    st.rerun()


# ============ 工具函数 ============
def extract_report_links(text: str) -> Dict[str, str]:
    """从文本中提取报告链接"""
    import re
    
    links = {}
    
    # 匹配Markdown链接格式
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
    url_pattern = r'(https?://[^\s<>"]+\.docx?)'
    all_urls = re.findall(url_pattern, text)
    
    for i, url in enumerate(all_urls[:4]):
        key = f"report_part{i+1}_url"
        if key not in links:
            links[key] = url
    
    return links if links else None


def save_to_history(user_message: str):
    """保存到历史记录"""
    title = user_message[:30] + "..." if len(user_message) > 30 else user_message
    
    session = {
        'session_id': st.session_state.current_session_id,
        'title': title,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'messages': st.session_state.messages.copy()
    }
    
    # 检查是否已存在
    existing_index = None
    for i, s in enumerate(st.session_state.history):
        if s['session_id'] == session['session_id']:
            existing_index = i
            break
    
    if existing_index is not None:
        st.session_state.history[existing_index] = session
    else:
        st.session_state.history.insert(0, session)
        if len(st.session_state.history) > 20:
            st.session_state.history.pop()


def create_new_session():
    """创建新会话"""
    st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    st.session_state.messages = []
    st.session_state.uploaded_files = []


# ============ 主程序 ============
def main():
    """主函数"""
    # 初始化session state
    init_session_state()
    
    # 显示主界面
    show_main_page()


if __name__ == "__main__":
    main()
