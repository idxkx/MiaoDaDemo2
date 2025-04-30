"""
存储服务包，提供文件存储和管理功能
"""

# 导出模块接口
from .storage_service import StorageService
from .local_storage_service import LocalStorageService
from .image_storage_service import ImageStorageService
from .storage_factory import StorageServiceFactory

# 为便于导入，提供别名
LocalStorage = LocalStorageService
ImageStorage = ImageStorageService
StorageFactory = StorageServiceFactory 