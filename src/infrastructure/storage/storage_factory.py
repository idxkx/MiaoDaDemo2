"""
存储服务工厂，用于创建和管理存储服务实例
"""

import os
from pathlib import Path
from typing import Dict, Optional, Type, Union

from .storage_service import StorageService
from .local_storage_service import LocalStorageService
from .image_storage_service import ImageStorageService


class StorageServiceFactory:
    """存储服务工厂类"""
    
    _instances: Dict[str, StorageService] = {}
    
    @classmethod
    def get_local_storage(
        cls,
        name: str = "default",
        base_dir: Union[str, Path] = "storage",
        base_url: str = ""
    ) -> LocalStorageService:
        """
        获取本地存储服务实例
        
        Args:
            name: 存储服务名称
            base_dir: 基础存储目录
            base_url: 基础URL路径
            
        Returns:
            LocalStorageService: 本地存储服务实例
        """
        key = f"local:{name}"
        if key not in cls._instances:
            cls._instances[key] = LocalStorageService(base_dir, base_url)
        return cls._instances[key]
    
    @classmethod
    def get_image_storage(
        cls,
        name: str = "default",
        base_dir: Union[str, Path] = "storage/images",
        processed_dir: Union[str, Path] = "storage/images/processed",
        base_url: str = "",
        **kwargs
    ) -> ImageStorageService:
        """
        获取图片存储服务实例
        
        Args:
            name: 存储服务名称
            base_dir: 基础图片存储目录
            processed_dir: 处理后图片存储目录
            base_url: 基础URL路径
            **kwargs: 其他参数，如allowed_formats, max_size_mb等
            
        Returns:
            ImageStorageService: 图片存储服务实例
        """
        key = f"image:{name}"
        if key not in cls._instances:
            cls._instances[key] = ImageStorageService(
                base_dir=base_dir,
                processed_dir=processed_dir,
                base_url=base_url,
                **kwargs
            )
        return cls._instances[key]
    
    @classmethod
    def ensure_storage_dirs(cls) -> None:
        """
        确保所有存储目录存在
        """
        dirs = [
            'storage',
            'storage/images',
            'storage/images/processed',
            'storage/images/thumbnails',
            'storage/temp'
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    @classmethod
    def register_storage_service(cls, name: str, service: StorageService) -> None:
        """
        注册自定义存储服务
        
        Args:
            name: 存储服务名称
            service: 存储服务实例
        """
        cls._instances[name] = service
    
    @classmethod
    def get_storage_service(cls, name: str) -> Optional[StorageService]:
        """
        获取已注册的存储服务
        
        Args:
            name: 存储服务名称
            
        Returns:
            Optional[StorageService]: 存储服务实例，如果不存在则返回None
        """
        return cls._instances.get(name) 