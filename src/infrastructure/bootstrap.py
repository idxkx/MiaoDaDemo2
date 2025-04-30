"""
应用引导模块，负责初始化应用资源和配置
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from src.infrastructure.storage import StorageFactory

logger = logging.getLogger(__name__)

class AppBootstrap:
    """应用引导类，负责初始化应用环境"""
    
    @classmethod
    def init_storage(cls) -> None:
        """
        初始化存储目录
        """
        logger.info("初始化存储目录...")
        StorageFactory.ensure_storage_dirs()
        logger.info("存储目录初始化完成")
    
    @classmethod
    def init_logging(cls, log_level: str = "INFO") -> None:
        """
        初始化日志系统
        
        Args:
            log_level: 日志级别，默认为INFO
        """
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'无效的日志级别: {log_level}')
        
        # 确保logs目录存在
        os.makedirs("storage/logs", exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"storage/logs/app.log")
            ]
        )
        
        logger.info(f"日志系统初始化完成，级别: {log_level}")
    
    @classmethod
    def init_app(cls, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化整个应用
        
        Args:
            config: 应用配置
        """
        # 默认配置
        app_config = {
            "log_level": "INFO",
            "storage_base_dir": "storage",
            "image_storage_dir": "storage/images",
            "temp_dir": "storage/temp",
            "log_dir": "storage/logs"
        }
        
        # 合并用户配置
        if config:
            app_config.update(config)
        
        # 初始化日志
        cls.init_logging(app_config["log_level"])
        
        # 初始化存储
        cls.init_storage()
        
        logger.info("应用初始化完成")
        
    @classmethod
    def validate_env(cls) -> None:
        """
        验证运行环境
        检查必要的依赖和权限
        """
        # 检查PIL库
        try:
            from PIL import Image
            logger.info("PIL库可用，支持图片处理")
        except ImportError:
            logger.warning("PIL库未安装，图片处理功能将受限")
            logger.info("请安装Pillow: pip install Pillow")
        
        # 检查存储目录权限
        storage_dir = Path("storage")
        if storage_dir.exists():
            # 测试写入权限
            try:
                test_file = storage_dir / ".permission_test"
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                logger.info("存储目录权限正常")
            except (IOError, PermissionError) as e:
                logger.error(f"存储目录权限不足: {e}")
                logger.error("请确保应用有足够的存储目录读写权限")
                raise 