"""
银行信贷分析助手 - Streamlit主应用

功能：
- 无需注册，直接使用
- 对话式界面
- 文件上传
- 实时进度显示
- 历史记录
"""
import streamlit as st
import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import uuid

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
        
        .chat-container {
            max-height: 600px;
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        
        .progress-box {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #2196f3;
        }
        
        .report-link {
            display: block;
            margin: 0.5rem 0;
            padding: 0.5rem;
            background-color: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 5px;
            color: #2e7d32;
            text-decoration: none;
        }
        
        .report-link:hover {
            background-color: #c8e6c9;
        }
        
        .file-info {
            background-color: #fff3e0;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .sidebar-section {
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)


# ============ 初始化Session State ============
def init_session_state():
    """初始化session state"""
    # 生成唯一用户ID（基于浏览器session）
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"guest_{uuid.uuid4().hex[:16]}"
    
    # 当前会话ID
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:16]}"
    
    # 消息列表
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 历史会话
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # 是否正在分析
    if 'is_analyzing' not in st.session_state:
        st.session_state.is_analyzing = False


# ============ 侧边栏 ============
def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.markdown("### 🏦 银行信贷分析助手")
        st.markdown("---")
        
        # 使用说明
        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. **输入企业名称**或直接描述需求
        2. **上传参考资料**（可选）
        3. 点击发送，等待分析完成
        4. 下载生成的报告
        
        **预计耗时**：5-8分钟
        """)
        
        st.markdown("---")
        
        # 历史记录
        st.markdown("### 📝 历史记录")
        if st.session_state.history:
            for i, session in enumerate(st.session_state.history):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"{session['title'][:20]}...",
                        key=f"history_{i}",
                        help=session['created_at']
                    ):
                        load_history_session(i)
                with col2:
                    if st.button("🗑️", key=f"delete_{i}", help="删除"):
                        st.session_state.history.pop(i)
                        st.rerun()
        else:
            st.info("暂无历史记录")
        
        st.markdown("---")
        
        # 新建会话
        if st.button("➕ 新建会话", use_container_width=True):
            create_new_session()
        
        st.markdown("---")
        
        # 清空当前会话
        if st.button("🗑️ 清空当前会话", use_container_width=True):
            clear_current_session()


# ============ 主界面 ============
def show_main_page():
    """显示主界面"""
    # 侧边栏
    show_sidebar()
    
    # 主标题
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 显示消息
    display_messages()
    
    # 输入区域
    st.markdown("---")
    show_input_area()


# ============ 消息显示 ============
def display_messages():
    """显示聊天消息"""
    messages = st.session_state.messages
    
    if not messages:
        st.info("👋 欢迎使用银行信贷分析助手！\n\n请在下方输入企业名称或描述你的需求，我会为你生成专业的授信分析报告。")
        return
    
    for msg in messages:
        if msg['role'] == 'user':
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg['content'])
                
                # 显示上传的文件
                if msg.get('files'):
                    st.markdown("**📎 上传文件**:")
                    for file_info in msg['files']:
                        st.markdown(f"- {file_info['name']} ({file_info['size']})")
        
        elif msg['role'] == 'assistant':
            with st.chat_message("assistant", avatar="🏦"):
                st.markdown(msg['content'])
                
                # 显示报告链接
                if msg.get('report_links'):
                    st.markdown("---")
                    st.markdown("**📥 报告下载链接**:")
                    
                    part1_url = msg['report_links'].get('report_part1_url')
                    part2_url = msg['report_links'].get('report_part2_url')
                    part3_url = msg['report_links'].get('report_part3_url')
                    part4_url = msg['report_links'].get('report_part4_url')
                    
                    if part1_url:
                        st.markdown(f"1. [📄 申报方案分析与客户分析]({part1_url})")
                    if part2_url:
                        st.markdown(f"2. [📄 财务分析]({part2_url})")
                    if part3_url:
                        st.markdown(f"3. [📄 行业分析及同业比较]({part3_url})")
                    if part4_url:
                        st.markdown(f"4. [📄 结论]({part4_url})")


# ============ 输入区域 ============
def show_input_area():
    """显示输入区域"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 文本输入
        user_input = st.chat_input(
            "输入企业名称或描述你的需求...",
            key="chat_input"
        )
    
    with col2:
        # 文件上传
        st.markdown("### 📎 上传文件")
        uploaded_files = st.file_uploader(
            "参考资料（可选）",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.info(f"已上传 {len(uploaded_files)} 个文件")
    
    # 处理用户输入
    if user_input and not st.session_state.is_analyzing:
        process_user_input(user_input, uploaded_files)


# ============ 处理用户输入 ============
def process_user_input(user_input: str, uploaded_files: List = None):
    """处理用户输入"""
    # 标记为正在分析
    st.session_state.is_analyzing = True
    
    # 处理上传的文件
    uploaded_file_info = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if is_allowed_file_type(uploaded_file.name):
                # 保存文件
                file_path = file_storage.save_file(
                    st.session_state.user_id,
                    uploaded_file.name,
                    uploaded_file.read()
                )
                
                uploaded_file_info.append({
                    'name': uploaded_file.name,
                    'size': format_file_size(uploaded_file.size),
                    'type': get_file_type(uploaded_file.name),
                    'path': file_path
                })
    
    # 添加用户消息
    user_message = {
        'role': 'user',
        'content': user_input,
        'files': uploaded_file_info,
        'timestamp': datetime.now().isoformat()
    }
    
    st.session_state.messages.append(user_message)
    
    # 提取企业名称（简单提取，实际可以更智能）
    company_name = extract_company_name(user_input)
    
    # 显示进度
    with st.status("正在分析中...", expanded=True) as status:
        st.markdown(f"**📋 分析企业**: {company_name}")
        st.markdown(f"**⏱️ 预计耗时**: 5-8分钟")
        st.markdown("---")
        
        # 进度步骤
        progress_steps = [
            ("🔍 正在搜集企业公开信息...", "企业基本信息、工商数据"),
            ("📊 正在分析财务数据...", "财务报表、经营指标"),
            ("🏢 正在进行行业分析...", "行业趋势、竞争格局"),
            ("📝 正在生成分析报告...", "整合信息、生成文档"),
        ]
        
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        # 模拟进度更新（实际应该从智能体获取）
        for i, (step, detail) in enumerate(progress_steps):
            progress_text.markdown(f"{step}")
            st.markdown(f"<small style='color:gray'>{detail}</small>", unsafe_allow_html=True)
            progress_bar.progress((i + 1) / len(progress_steps))
            time.sleep(0.5)  # 短暂显示，让用户看到进度
        
        # 调用智能体API
        result = agent_client.analyze_company(
            company_name=company_name,
            analysis_focus="全面分析（推荐）",
            has_reference_materials="是" if uploaded_file_info else "否",
            user_id=st.session_state.user_id,
            session_id=st.session_state.current_session_id
        )
        
        # 完成进度
        progress_bar.progress(1.0)
        progress_text.markdown("✅ 分析完成！")
        status.update(label="分析完成", state="complete")
    
    # 显示智能体回复
    if result.get('success'):
        report_links = result.get('report_links', {})
        
        assistant_message = {
            'role': 'assistant',
            'content': f"✅ 已为【{company_name}】生成授信分析报告！\n\n报告包含以下部分：\n1. 申报方案分析与客户分析\n2. 财务分析\n3. 行业分析及同业比较\n4. 结论\n\n请点击下方链接下载报告。",
            'report_links': report_links,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.messages.append(assistant_message)
        
        # 保存到历史记录
        save_to_history(company_name)
    else:
        assistant_message = {
            'role': 'assistant',
            'content': f"❌ 分析失败：{result.get('message', '未知错误')}\n\n请检查企业名称是否正确，或稍后重试。",
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.messages.append(assistant_message)
    
    # 标记分析完成
    st.session_state.is_analyzing = False
    
    # 清空文件上传器
    st.session_state.uploaded_files = []
    
    # 刷新页面
    st.rerun()


# ============ 工具函数 ============
def extract_company_name(text: str) -> str:
    """从用户输入中提取企业名称"""
    # 简单的提取逻辑：查找【】中的内容
    import re
    match = re.search(r'【(.+?)】', text)
    if match:
        return match.group(1)
    
    # 如果没有【】，尝试查找常见格式
    # 例如："分析腾讯"、"腾讯公司"等
    common_suffixes = ['公司', '集团', '有限公司', '股份有限公司', '控股']
    for suffix in common_suffixes:
        if suffix in text:
            # 提取包含后缀的词
            words = text.split()
            for word in words:
                if suffix in word:
                    return word
    
    # 如果都没匹配到，返回整个文本（去掉"分析"等动词）
    verbs = ['分析', '生成', '请', '帮我', '为']
    result = text
    for verb in verbs:
        result = result.replace(verb, '')
    
    return result.strip() or text.strip()


def save_to_history(company_name: str):
    """保存到历史记录"""
    session = {
        'session_id': st.session_state.current_session_id,
        'title': f"{company_name} 授信分析",
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'messages': st.session_state.messages.copy()
    }
    
    # 添加到历史记录（保留最近20条）
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
