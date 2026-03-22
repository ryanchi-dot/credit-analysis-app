"""
银行信贷分析助手 - Streamlit主应用
优化版本：停止按钮 + 输入框内上传 + 历史记录功能
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
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
    <style>
        /* 隐藏默认的Streamlit元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 主容器 */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 100px;
            max-width: 900px;
        }
        
        /* 标题样式 */
        .main-title {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1e3a5f;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        /* 文件标签样式 */
        .file-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            background-color: #e3f2fd;
            border-radius: 12px;
            font-size: 0.75rem;
            margin: 0.15rem;
            color: #1565c0;
        }
        
        /* 底部输入区域固定 */
        .bottom-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 1rem;
            border-top: 1px solid #e0e0e0;
            z-index: 100;
        }
        
        /* 输入框容器 */
        .input-box {
            display: flex;
            align-items: center;
            background: #f5f5f5;
            border-radius: 24px;
            padding: 0.5rem 1rem;
            border: 1px solid #e0e0e0;
        }
        
        /* 历史记录侧边栏 */
        .history-item {
            padding: 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 0.5rem;
            background: #f8f9fa;
        }
        
        .history-item:hover {
            background: #e9ecef;
        }
        
        /* 停止按钮 */
        .stop-button {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)


# ============ 初始化Session State ============
def init_session_state():
    """初始化session state"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:16]}"
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    
    if 'stop_generation' not in st.session_state:
        st.session_state.stop_generation = False
    
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False


# ============ 侧边栏（历史记录）============
def show_history_sidebar():
    """显示历史记录侧边栏"""
    if st.session_state.show_history:
        with st.sidebar:
            st.markdown("### 📝 历史记录")
            st.markdown("---")
            
            if not st.session_state.history:
                st.info("暂无历史记录")
            else:
                for i, session in enumerate(st.session_state.history[:20]):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if st.button(
                            f"💬 {session['title'][:20]}",
                            key=f"history_item_{i}",
                            use_container_width=True
                        ):
                            load_history_session(i)
                    with col2:
                        if st.button("🗑️", key=f"del_history_{i}", help="删除"):
                            st.session_state.history.pop(i)
                            st.rerun()
            
            st.markdown("---")
            if st.button("➕ 新建对话", use_container_width=True):
                create_new_session()
                st.session_state.show_history = False
                st.rerun()
            
            if st.button("✖️ 关闭", use_container_width=True):
                st.session_state.show_history = False
                st.rerun()


# ============ 主界面 ============
def show_main_page():
    """显示主界面"""
    # 显示历史记录侧边栏
    show_history_sidebar()
    
    # 顶部工具栏
    show_top_bar()
    
    # 主标题
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    
    # 显示对话消息
    display_chat_messages()
    
    # 底部输入区域
    show_bottom_input_area()


# ============ 顶部工具栏 ============
def show_top_bar():
    """显示顶部工具栏"""
    col1, col2, col3, col4 = st.columns([8, 1, 1, 1])
    
    with col2:
        if st.button("➕", help="新建对话", key="new_chat"):
            create_new_session()
            st.rerun()
    
    with col3:
        if st.button("📝", help="历史记录", key="history_btn"):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()
    
    with col4:
        if st.button("❓", help="使用说明", key="help_btn"):
            st.session_state.show_help = not st.session_state.get('show_help', False)
    
    if st.session_state.get('show_help', False):
        with st.expander("📖 使用说明", expanded=True):
            st.markdown("""
            **输入企业名称，我会帮您生成授信分析报告**
            
            **步骤**：
            1. 输入企业名称（如：百度在线网络技术（北京）有限公司）
            2. 确认分析范围和是否有参考资料
            3. 等待报告生成
            
            **功能**：
            - ✅ 自动搜集企业公开信息
            - ✅ 生成专业授信分析报告
            - ✅ 支持上传参考资料
            
            **耗时**：约5-8分钟
            """)
    
    st.markdown("---")


# ============ 显示对话消息 ============
def display_chat_messages():
    """显示所有对话消息"""
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; color: #666;">
            <h2>👋 欢迎使用银行信贷分析助手</h2>
            <p style="font-size: 1rem; margin: 1rem 0;">输入企业名称开始分析</p>
            <div style="margin-top: 1.5rem; color: #999;">
                <p>示例：百度在线网络技术（北京）有限公司</p>
                <p>腾讯控股有限公司</p>
                <p>阿里巴巴集团</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🏦"):
            st.markdown(msg["content"])
            
            if msg.get("files"):
                files_html = " ".join([f'<span class="file-badge">📎 {f["name"]}</span>' for f in msg["files"]])
                st.markdown(files_html, unsafe_allow_html=True)
            
            if msg.get("report_links"):
                st.markdown("**📥 报告下载**:")
                links = msg["report_links"]
                cols = st.columns(min(4, len(links)))
                link_names = ["申报方案", "财务分析", "行业分析", "结论"]
                
                for i, (col, name) in enumerate(zip(cols, link_names)):
                    key = f"report_part{i+1}_url"
                    if key in links and links[key]:
                        with col:
                            st.link_button(f"📄 {name}", links[key], use_container_width=True)


# ============ 底部输入区域 ============
def show_bottom_input_area():
    """显示底部输入区域 - 类似DeepSeek"""
    
    # 显示已上传的文件
    if st.session_state.uploaded_files:
        col_files, col_clear = st.columns([10, 1])
        with col_files:
            files_html = " ".join([f'<span class="file-badge">📎 {f["name"]} ✕</span>' for f in st.session_state.uploaded_files])
            st.markdown(files_html, unsafe_allow_html=True)
        with col_clear:
            if st.button("🗑️", key="clear_files", help="清空文件"):
                st.session_state.uploaded_files = []
                st.rerun()
    
    # 创建输入框和按钮的布局
    col_input, col_upload, col_send = st.columns([10, 1, 1])
    
    with col_input:
        prompt = st.chat_input("输入企业名称...", key="main_input")
    
    with col_upload:
        # 上传按钮（模拟在输入框内）
        st.markdown("<div style='height: 60px; display: flex; align-items: center;'>", unsafe_allow_html=True)
        if st.button("📎", key="upload_btn", help="上传附件"):
            st.session_state.show_upload = True
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_send:
        st.markdown("<div style='height: 60px; display: flex; align-items: center;'>", unsafe_allow_html=True)
        if st.button("➡️", key="send_btn", help="发送"):
            pass
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 上传文件弹窗
    if st.session_state.show_upload:
        with st.popover("📎 上传附件", help="点击上传文件"):
            uploaded_files = st.file_uploader(
                "选择文件",
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                key="file_uploader_main"
            )
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    if is_allowed_file_type(uploaded_file.name):
                        file_path = file_storage.save_file(
                            st.session_state.user_id,
                            uploaded_file.name,
                            uploaded_file.read()
                        )
                        exists = any(f['name'] == uploaded_file.name for f in st.session_state.uploaded_files)
                        if not exists:
                            st.session_state.uploaded_files.append({
                                'name': uploaded_file.name,
                                'size': format_file_size(uploaded_file.size),
                                'type': get_file_type(uploaded_file.name),
                                'path': file_path
                            })
                st.success(f"已添加 {len(uploaded_files)} 个文件")
            
            if st.button("完成", key="close_upload"):
                st.session_state.show_upload = False
                st.rerun()
    
    # 处理用户输入
    if prompt:
        process_user_message(prompt)


# ============ 处理用户消息 ============
def process_user_message(prompt: str):
    """处理用户消息"""
    # 添加用户消息
    user_msg = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    }
    
    if st.session_state.uploaded_files:
        user_msg["files"] = st.session_state.uploaded_files.copy()
    
    st.session_state.messages.append(user_msg)
    
    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        if user_msg.get("files"):
            files_html = " ".join([f'<span class="file-badge">📎 {f["name"]}</span>' for f in user_msg["files"]])
            st.markdown(files_html, unsafe_allow_html=True)
    
    # 显示助手回复
    with st.chat_message("assistant", avatar="🏦"):
        # 停止按钮
        stop_col, _ = st.columns([1, 10])
        with stop_col:
            if st.button("⏹️ 停止", key="stop_btn", type="primary"):
                st.session_state.stop_generation = True
                st.warning("正在停止...")
        
        message_placeholder = st.empty()
        full_response = ""
        
        # 调用智能体流式API
        response_stream = agent_client.chat_stream(
            user_message=prompt,
            user_id=st.session_state.user_id,
            session_id=st.session_state.current_session_id
        )
        
        # 流式显示响应
        for chunk in response_stream:
            # 检查是否停止
            if st.session_state.stop_generation:
                full_response += "\n\n*[已停止生成]*"
                break
            
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        # 提取报告链接
        report_links = extract_report_links(full_response)
        
        if report_links:
            st.markdown("**📥 报告下载**:")
            cols = st.columns(min(4, len(report_links)))
            link_names = ["申报方案", "财务分析", "行业分析", "结论"]
            
            for i, (col, name) in enumerate(zip(cols, link_names)):
                key = f"report_part{i+1}_url"
                if key in report_links and report_links[key]:
                    with col:
                        st.link_button(f"📄 {name}", report_links[key], use_container_width=True)
    
    # 重置停止标志
    st.session_state.stop_generation = False
    
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
    st.session_state.stop_generation = False


def load_history_session(index: int):
    """加载历史会话"""
    if 0 <= index < len(st.session_state.history):
        session = st.session_state.history[index]
        st.session_state.current_session_id = session['session_id']
        st.session_state.messages = session['messages'].copy()
        st.session_state.show_history = False
        st.rerun()


# ============ 主程序 ============
def main():
    """主函数"""
    init_session_state()
    show_main_page()


if __name__ == "__main__":
    main()
