"""
本地存储服务，基于本地文件系统实现文件存储
"""

import os
import shutil
import aiofiles
from pathlib import Path
from typing import Union, BinaryIO, Optional
import logging

from .storage_service import StorageService

logger = logging.getLogger(__name__)

class LocalStorageService(StorageService):
    """本地文件系统存储服务实现"""
    
    def __init__(self, base_dir: Union[str, Path], base_url: str = ""):
        """
        初始化本地存储服务
        
        Args:
            base_dir: 基础存储目录
            base_url: 基础URL路径，用于构建文件访问URL
        """
        self.base_dir = Path(base_dir)
        self.base_url = base_url
        self._ensure_base_dir()
    
    def _ensure_base_dir(self) -> None:
        """确保基础目录存在"""
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"已确保存储目录存在: {self.base_dir}")
    
    async def save_file(self, file_path: Union[str, Path], file_data: Union[bytes, BinaryIO]) -> str:
        """
        保存文件到本地存储
        
        Args:
            file_path: 相对于base_dir的文件路径
            file_data: 文件数据（二进制数据或文件对象）
            
        Returns:
            str: 文件的存储路径
        """
        absolute_path = self._get_absolute_path(file_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        
        try:
            if isinstance(file_data, bytes):
                async with aiofiles.open(absolute_path, "wb") as f:
                    await f.write(file_data)
            else:
                # 文件对象
                if hasattr(file_data, "read"):
                    if hasattr(file_data, "seek"):
                        file_data.seek(0)
                    
                    # 使用缓冲复制
                    with open(absolute_path, "wb") as f:
                        shutil.copyfileobj(file_data, f)
                else:
                    raise ValueError("file_data必须是字节数据或可读文件对象")
            
            logger.info(f"文件保存成功: {absolute_path}")
            return str(Path(file_path))
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise
    
    async def get_file(self, file_path: Union[str, Path]) -> Optional[bytes]:
        """
        从本地存储获取文件
        
        Args:
            file_path: 相对于base_dir的文件路径
            
        Returns:
            Optional[bytes]: 文件数据，如果文件不存在则返回None
        """
        absolute_path = self._get_absolute_path(file_path)
        
        if not os.path.exists(absolute_path):
            logger.warning(f"文件不存在: {absolute_path}")
            return None
        
        try:
            async with aiofiles.open(absolute_path, "rb") as f:
                data = await f.read()
            return data
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return None
    
    async def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        从本地存储删除文件
        
        Args:
            file_path: 相对于base_dir的文件路径
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        absolute_path = self._get_absolute_path(file_path)
        
        if not os.path.exists(absolute_path):
            logger.warning(f"要删除的文件不存在: {absolute_path}")
            return False
        
        try:
            os.remove(absolute_path)
            logger.info(f"文件删除成功: {absolute_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    async def file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否存在于本地存储
        
        Args:
            file_path: 相对于base_dir的文件路径
            
        Returns:
            bool: 文件存在返回True，否则返回False
        """
        absolute_path = self._get_absolute_path(file_path)
        return os.path.exists(absolute_path)
    
    async def get_file_url(self, file_path: Union[str, Path]) -> str:
        """
        获取文件的访问URL
        
        Args:
            file_path: 相对于base_dir的文件路径
            
        Returns:
            str: 文件的访问URL
        """
        # 组合基础URL和文件路径，确保URL格式正确
        if not self.base_url:
            # 本地文件系统模式，返回文件路径
            return str(self._get_absolute_path(file_path))
        
        # 网络模式，构建URL
        file_path_str = str(file_path).replace("\\", "/")
        if self.base_url.endswith("/"):
            return f"{self.base_url}{file_path_str}"
        else:
            return f"{self.base_url}/{file_path_str}"
    
    def _get_absolute_path(self, file_path: Union[str, Path]) -> Path:
        """
        获取文件的绝对路径
        
        Args:
            file_path: 相对于base_dir的文件路径
            
        Returns:
            Path: 文件的绝对路径
        """
        return self.base_dir / Path(file_path) 