"""
银行信贷分析助手 - Streamlit主应用

功能：
- 用户注册/登录
- 多轮对话
- 文件上传
- 历史记录
- 用户数据隔离
"""
import streamlit as st
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 调试：打印环境变量（仅在开发环境）
if os.getenv('DEBUG'):
    st.write("🔍 环境变量调试:")
    st.write(f"AGENT_API_URL: {os.getenv('AGENT_API_URL', '未设置')}")
    st.write(f"AGENT_API_KEY: {os.getenv('AGENT_API_KEY', '未设置')[:20]}..." if os.getenv('AGENT_API_KEY') else "AGENT_API_KEY: 未设置")

# 导入自定义模块
from database import db
from agent_client import agent_client
from utils import file_storage, format_file_size, is_allowed_file_type, get_file_type, generate_session_id


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
        
        .user-message {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: right;
        }
        
        .assistant-message {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: left;
            border-left: 4px solid #1e3a5f;
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
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []


# ============ 用户认证 ============
def show_login_page():
    """显示登录页面"""
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["登录", "注册"])
    
    with tab1:
        st.subheader("登录")
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        
        if st.button("登录", key="login_button"):
            if username and password:
                user = db.verify_user(username, password)
                if user:
                    st.session_state.current_user = user
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误！")
            else:
                st.warning("请输入用户名和密码")
    
    with tab2:
        st.subheader("注册")
        new_username = st.text_input("用户名", key="register_username")
        new_password = st.text_input("密码", type="password", key="register_password")
        confirm_password = st.text_input("确认密码", type="password", key="confirm_password")
        
        if st.button("注册", key="register_button"):
            if new_username and new_password:
                if new_password != confirm_password:
                    st.error("两次密码输入不一致！")
                elif len(new_password) < 6:
                    st.error("密码长度不能少于6位！")
                else:
                    user_id = db.create_user(new_username, new_password)
                    if user_id:
                        st.success("注册成功！请登录")
                    else:
                        st.error("用户名已存在！")
            else:
                st.warning("请填写完整信息")


# ============ 侧边栏 ============
def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        # 用户信息
        st.markdown("### 👤 用户信息")
        user = st.session_state.current_user
        st.write(f"**用户名**: {user['username']}")
        st.write(f"**用户ID**: {user['user_id'][:20]}...")
        
        st.markdown("---")
        
        # 历史记录
        st.markdown("### 📝 历史记录")
        sessions = db.get_user_sessions(user['user_id'])
        
        if sessions:
            for session in sessions:
                session_title = session['title']
                session_time = datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M')
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(session_title, key=f"session_{session['session_id']}", help=session_time):
                        load_session(session['session_id'])
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session['session_id']}", help="删除会话"):
                        if delete_session(session['session_id']):
                            st.success("会话已删除")
                            st.rerun()
        else:
            st.info("暂无历史记录")
        
        st.markdown("---")
        
        # 新建会话
        if st.button("➕ 新建会话"):
            create_new_session()
        
        st.markdown("---")
        
        # 退出登录
        if st.button("🚪 退出登录"):
            logout()


# ============ 主界面 ============
def show_main_page():
    """显示主界面"""
    # 侧边栏
    show_sidebar()
    
    # 主标题
    st.markdown('<div class="main-title">🏦 银行信贷分析助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 显示当前会话信息
    if st.session_state.current_session_id:
        session = db.get_session(st.session_state.current_session_id)
        if session:
            st.info(f"当前会话: {session['title']}")
    
    # 聊天区域
    st.markdown("### 💬 对话区域")
    
    # 显示消息
    display_messages()
    
    # 消息输入区域
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # 文件上传
        uploaded_files = st.file_uploader(
            "上传参考资料（可选）",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        # 企业名称输入
        company_name = st.text_input(
            "企业名称（必填）",
            placeholder="请输入企业全称，如：腾讯控股有限公司",
            key="company_name"
        )
        
        # 分析重点选择
        analysis_focus = st.selectbox(
            "分析重点",
            ["全面分析（推荐）", "财务分析", "行业研究", "风险评估"],
            key="analysis_focus"
        )
        
        # 是否有参考材料
        has_materials = "是" if uploaded_files else "否"
        
        # 发送按钮
        if st.button("📤 开始分析", key="send_button", use_container_width=True):
            if not company_name:
                st.error("请输入企业名称！")
            else:
                # 处理上传的文件
                uploaded_file_info = []
                for uploaded_file in uploaded_files:
                    if is_allowed_file_type(uploaded_file.name):
                        # 保存文件
                        file_path = file_storage.save_file(
                            st.session_state.current_user['user_id'],
                            uploaded_file.name,
                            uploaded_file.read()
                        )
                        
                        # 保存文件记录到数据库
                        db.save_file(
                            st.session_state.current_user['user_id'],
                            st.session_state.current_session_id,
                            uploaded_file.name,
                            file_path,
                            uploaded_file.size,
                            get_file_type(uploaded_file.name)
                        )
                        
                        uploaded_file_info.append({
                            'name': uploaded_file.name,
                            'size': format_file_size(uploaded_file.size),
                            'type': get_file_type(uploaded_file.name)
                        })
                    
                    # 清空文件上传器
                    st.session_state.uploaded_files = []
                
                # 发送用户消息
                user_message = {
                    'role': 'user',
                    'content': f"请为【{company_name}】生成授信分析报告。",
                    'company_name': company_name,
                    'analysis_focus': analysis_focus,
                    'has_materials': has_materials,
                    'files': uploaded_file_info,
                    'timestamp': datetime.now().isoformat()
                }
                
                add_message(user_message)
                
                # 调用智能体
                with st.spinner("智能体正在分析中，请稍候...（预计需要5-8分钟）"):
                    result = agent_client.analyze_company(
                        company_name=company_name,
                        analysis_focus=analysis_focus,
                        has_reference_materials=has_materials,
                        user_id=st.session_state.current_user['user_id'],
                        session_id=st.session_state.current_session_id
                    )
                
                # 显示智能体回复
                if result.get('success'):
                    report_links = result.get('report_links', {})
                    
                    assistant_message = {
                        'role': 'assistant',
                        'content': f"✅ 分析完成！已为【{company_name}】生成授信分析报告。",
                        'report_links': report_links,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    add_message(assistant_message)
                else:
                    assistant_message = {
                        'role': 'assistant',
                        'content': f"❌ 分析失败：{result.get('message', '未知错误')}",
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    add_message(assistant_message)
    
    with col2:
        # 清空会话按钮
        if st.button("🗑️ 清空会话", key="clear_button", use_container_width=True):
            clear_current_session_messages()
            st.success("会话已清空")
            st.rerun()


# ============ 消息显示 ============
def display_messages():
    """显示聊天消息"""
    messages = st.session_state.messages
    
    if not messages:
        st.info("还没有对话，请输入企业名称开始分析")
        return
    
    for msg in messages:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(f"**企业名称**: {msg.get('company_name', 'N/A')}")
                st.markdown(f"**分析重点**: {msg.get('analysis_focus', 'N/A')}")
                st.markdown(f"**参考材料**: {msg.get('has_materials', '否')}")
                
                # 显示上传的文件
                if msg.get('files'):
                    st.markdown("**上传文件**:")
                    for file_info in msg['files']:
                        st.markdown(f"- {file_info['name']} ({file_info['size']})")
        
        elif msg['role'] == 'assistant':
            with st.chat_message("assistant"):
                st.markdown(msg['content'])
                
                # 显示报告链接
                if msg.get('report_links'):
                    st.markdown("**报告下载链接**:")
                    
                    part1_url = msg['report_links'].get('report_part1_url')
                    part2_url = msg['report_links'].get('report_part2_url')
                    part3_url = msg['report_links'].get('report_part3_url')
                    part4_url = msg['report_links'].get('report_part4_url')
                    
                    if part1_url:
                        st.markdown(f"1. [申报方案分析与客户分析]({part1_url})")
                    if part2_url:
                        st.markdown(f"2. [财务分析]({part2_url})")
                    if part3_url:
                        st.markdown(f"3. [行业分析及同业比较]({part3_url})")
                    if part4_url:
                        st.markdown(f"4. [结论]({part4_url})")


# ============ 会话管理 ============
def create_new_session():
    """创建新会话"""
    session_id = db.create_session(
        st.session_state.current_user['user_id'],
        title=f"新对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    st.session_state.current_session_id = session_id
    st.session_state.messages = []
    
    st.rerun()


def load_session(session_id: str):
    """加载会话"""
    session = db.get_session(session_id)
    if session and session['user_id'] == st.session_state.current_user['user_id']:
        st.session_state.current_session_id = session_id
        st.session_state.messages = db.get_session_messages(session_id)
        st.rerun()
    else:
        st.error("无法加载该会话")


def delete_session(session_id: str) -> bool:
    """删除会话"""
    return db.delete_session(st.session_state.current_user['user_id'], session_id)


def clear_current_session_messages():
    """清空当前会话的消息"""
    st.session_state.messages = []


def add_message(message: Dict[str, Any]):
    """添加消息到当前会话"""
    st.session_state.messages.append(message)
    
    # 保存到数据库
    if st.session_state.current_session_id:
        db.add_message(
            st.session_state.current_session_id,
            message['role'],
            message.get('content', '')
        )


def logout():
    """退出登录"""
    st.session_state.current_user = None
    st.session_state.current_session_id = None
    st.session_state.messages = []
    st.rerun()


# ============ 主程序 ============
def main():
    """主函数"""
    # 初始化session state
    init_session_state()
    
    # 检查用户是否登录
    if not st.session_state.current_user:
        show_login_page()
    else:
        # 如果还没有当前会话，创建一个
        if not st.session_state.current_session_id:
            create_new_session()
        
        show_main_page()


if __name__ == "__main__":
    main()
