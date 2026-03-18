"""
数据库操作模块

负责用户、会话、消息、文件的存储和查询。
确保每个用户的数据完全隔离。
"""
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: str = "data/users.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """初始化数据库表结构"""
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # 会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # 消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')
            
            # 文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')
            
            conn.commit()
    
    # ============ 用户操作 ============
    
    def create_user(self, username: str, password: str) -> Optional[str]:
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码（明文，会自动加密）
        
        Returns:
            user_id: 成功返回user_id，失败返回None
        """
        try:
            # 加密密码
            password_hash = self._hash_password(password)
            
            # 生成唯一的user_id
            user_id = f"user_{secrets.token_hex(16)}"
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash, user_id) VALUES (?, ?, ?)',
                    (username, password_hash, user_id)
                )
                conn.commit()
                return user_id
        except sqlite3.IntegrityError:
            # 用户名已存在
            return None
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码（明文）
        
        Returns:
            用户信息字典，验证失败返回None
        """
        password_hash = self._hash_password(password)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_id, username, password_hash FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
            
            if row and row['password_hash'] == password_hash:
                # 更新最后登录时间
                cursor.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?',
                    (row['user_id'],)
                )
                conn.commit()
                
                return {
                    'user_id': row['user_id'],
                    'username': row['username']
                }
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_id, username, created_at, last_login FROM users WHERE user_id = ?',
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def _hash_password(self, password: str) -> str:
        """加密密码（SHA-256）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ============ 会话操作 ============
    
    def create_session(self, user_id: str, title: str = None) -> str:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            title: 会话标题
        
        Returns:
            session_id: 会话ID
        """
        session_id = f"session_{secrets.token_hex(16)}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sessions (user_id, session_id, title) VALUES (?, ?, ?)',
                (user_id, session_id, title or "新对话")
            )
            conn.commit()
            return session_id
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户ID
        
        Returns:
            会话列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, session_id, title, created_at FROM sessions WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM sessions WHERE session_id = ?',
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def delete_session(self, user_id: str, session_id: str) -> bool:
        """
        删除会话（包括关联的消息）
        
        Args:
            user_id: 用户ID（安全检查）
            session_id: 会话ID
        
        Returns:
            是否删除成功
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 安全检查：只能删除自己的会话
            cursor.execute(
                'SELECT user_id FROM sessions WHERE session_id = ?',
                (session_id,)
            )
            row = cursor.fetchone()
            
            if not row or row['user_id'] != user_id:
                return False
            
            # 删除会话的消息
            cursor.execute(
                'DELETE FROM messages WHERE session_id = ?',
                (session_id,)
            )
            
            # 删除会话
            cursor.execute(
                'DELETE FROM sessions WHERE session_id = ?',
                (session_id,)
            )
            
            conn.commit()
            return True
    
    # ============ 消息操作 ============
    
    def add_message(self, session_id: str, role: str, content: str, 
                   file_name: str = None, file_path: str = None, file_size: int = None) -> int:
        """
        添加消息
        
        Args:
            session_id: 会话ID
            role: 消息角色（user/assistant）
            content: 消息内容
            file_name: 文件名（可选）
            file_path: 文件路径（可选）
            file_size: 文件大小（可选）
        
        Returns:
            消息ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO messages 
                   (session_id, role, content, file_name, file_path, file_size) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session_id, role, content, file_name, file_path, file_size)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话的所有消息
        
        Args:
            session_id: 会话ID
        
        Returns:
            消息列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC',
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ============ 文件操作 ============
    
    def save_file(self, user_id: str, session_id: str, file_name: str, 
                 file_path: str, file_size: int, file_type: str) -> int:
        """
        保存文件记录
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            file_name: 文件名
            file_path: 文件路径
            file_size: 文件大小
            file_type: 文件类型
        
        Returns:
            文件ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO files 
                   (user_id, session_id, file_name, file_path, file_size, file_type) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, session_id, file_name, file_path, file_size, file_type)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有文件
        
        Args:
            user_id: 用户ID
        
        Returns:
            文件列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM files WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]


# 全局数据库实例
db = Database()
