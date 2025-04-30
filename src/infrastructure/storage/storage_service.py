"""
存储服务基类，定义存储服务的通用接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, BinaryIO, Optional


class StorageService(ABC):
    """存储服务抽象基类"""

    @abstractmethod
    async def save_file(self, file_path: Union[str, Path], file_data: Union[bytes, BinaryIO]) -> str:
        """
        保存文件到存储系统
        
        Args:
            file_path: 文件路径或文件名
            file_data: 文件数据（二进制数据或文件对象）
            
        Returns:
            str: 文件的访问路径
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: Union[str, Path]) -> Optional[bytes]:
        """
        从存储系统获取文件
        
        Args:
            file_path: 文件路径或文件名
            
        Returns:
            Optional[bytes]: 文件数据，如果文件不存在则返回None
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        从存储系统删除文件
        
        Args:
            file_path: 文件路径或文件名
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径或文件名
            
        Returns:
            bool: 文件存在返回True，否则返回False
        """
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: Union[str, Path]) -> str:
        """
        获取文件的访问URL
        
        Args:
            file_path: 文件路径或文件名
            
        Returns:
            str: 文件的访问URL
        """
        pass 