"""
工具函数模块

提供文件处理、路径管理等工具函数。
确保用户文件完全隔离。
"""
import os
import secrets
from pathlib import Path
from typing import Tuple


class FileStorage:
    """文件存储管理类"""
    
    def __init__(self, base_path: str = "data/uploads"):
        """
        初始化文件存储
        
        Args:
            base_path: 基础存储路径
        """
        self.base_path = base_path
        self._ensure_base_path()
    
    def _ensure_base_path(self):
        """确保基础路径存在"""
        os.makedirs(self.base_path, exist_ok=True)
    
    def get_user_dir(self, user_id: str) -> str:
        """
        获取用户的文件存储目录
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户文件目录路径
        """
        user_dir = os.path.join(self.base_path, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def save_file(self, user_id: str, file_name: str, file_content: bytes) -> str:
        """
        保存用户文件
        
        Args:
            user_id: 用户ID
            file_name: 文件名
            file_content: 文件内容（字节）
        
        Returns:
            文件存储路径
        """
        user_dir = self.get_user_dir(user_id)
        
        # 生成安全的文件名（避免路径遍历攻击）
        safe_filename = self._sanitize_filename(file_name)
        file_path = os.path.join(user_dir, safe_filename)
        
        # 确保文件名唯一
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    def get_file_path(self, user_id: str, file_name: str) -> str:
        """
        获取文件路径
        
        Args:
            user_id: 用户ID
            file_name: 文件名
        
        Returns:
            文件完整路径
        """
        user_dir = self.get_user_dir(user_id)
        return os.path.join(user_dir, file_name)
    
    def file_exists(self, user_id: str, file_name: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            user_id: 用户ID
            file_name: 文件名
        
        Returns:
            文件是否存在
        """
        file_path = self.get_file_path(user_id, file_name)
        return os.path.exists(file_path)
    
    def delete_file(self, user_id: str, file_name: str) -> bool:
        """
        删除用户文件
        
        Args:
            user_id: 用户ID
            file_name: 文件名
        
        Returns:
            是否删除成功
        """
        file_path = self.get_file_path(user_id, file_name)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，防止路径遍历攻击
        
        Args:
            filename: 原始文件名
        
        Returns:
            安全的文件名
        """
        # 移除路径分隔符
        filename = filename.replace('/', '').replace('\\', '')
        
        # 移除特殊字符
        filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
        
        # 如果文件名为空，使用默认名称
        if not filename:
            filename = f"file_{secrets.token_hex(8)}"
        
        return filename
    
    def get_file_size(self, user_id: str, file_name: str) -> int:
        """
        获取文件大小
        
        Args:
            user_id: 用户ID
            file_name: 文件名
        
        Returns:
            文件大小（字节）
        """
        file_path = self.get_file_path(user_id, file_name)
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名
        
        Args:
            filename: 文件名
        
        Returns:
            文件扩展名（小写，包含点）
        """
        return os.path.splitext(filename)[1].lower()


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_allowed_file_type(filename: str) -> bool:
    """
    检查文件类型是否允许
    
    Args:
        filename: 文件名
    
    Returns:
        是否允许
    """
    allowed_extensions = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.jpg', '.jpeg', '.png', '.gif'
    }
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def get_file_type(filename: str) -> str:
    """
    获取文件类型描述
    
    Args:
        filename: 文件名
    
    Returns:
        文件类型描述
    """
    ext = os.path.splitext(filename)[1].lower()
    
    type_map = {
        '.pdf': 'PDF文档',
        '.doc': 'Word文档',
        '.docx': 'Word文档',
        '.xls': 'Excel表格',
        '.xlsx': 'Excel表格',
        '.jpg': '图片',
        '.jpeg': '图片',
        '.png': '图片',
        '.gif': '图片'
    }
    
    return type_map.get(ext, '未知文件')


def generate_session_id() -> str:
    """生成唯一的会话ID"""
    return f"session_{secrets.token_hex(16)}"


# 全局文件存储实例
file_storage = FileStorage()
