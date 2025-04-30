"""
图片存储服务，提供图片的存储、处理和访问功能
"""

import os
import io
import uuid
from pathlib import Path
from typing import Union, BinaryIO, Optional, Tuple, Dict, Any
import logging
from datetime import datetime
import base64

# 图片处理
try:
    from PIL import Image
except ImportError:
    Image = None

from .local_storage_service import LocalStorageService
from src.domain.model.value_objects import ImageMetadata

logger = logging.getLogger(__name__)

class ImageStorageService(LocalStorageService):
    """图片存储服务，专门用于图片存储和处理"""
    
    def __init__(
        self,
        base_dir: Union[str, Path] = "storage/images",
        processed_dir: Union[str, Path] = "storage/images/processed",
        base_url: str = "",
        allowed_formats: Tuple[str, ...] = ("jpg", "jpeg", "png", "gif", "webp"),
        max_size_mb: float = 10.0,
        auto_thumbnail: bool = True,
        thumbnail_size: Tuple[int, int] = (300, 300)
    ):
        """
        初始化图片存储服务
        
        Args:
            base_dir: 基础图片存储目录
            processed_dir: 处理后图片存储目录
            base_url: 基础URL路径
            allowed_formats: 允许的图片格式
            max_size_mb: 最大图片大小（MB）
            auto_thumbnail: 是否自动生成缩略图
            thumbnail_size: 缩略图尺寸
        """
        super().__init__(base_dir, base_url)
        self.processed_dir = Path(processed_dir)
        self.allowed_formats = allowed_formats
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)  # 转换为字节
        self.auto_thumbnail = auto_thumbnail
        self.thumbnail_size = thumbnail_size
        
        # 确保处理目录存在
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 检查PIL库是否可用
        if Image is None and self.auto_thumbnail:
            logger.warning("PIL库未安装，无法进行图片处理。请安装: pip install Pillow")
            self.auto_thumbnail = False
    
    async def save_image(
        self,
        image_data: Union[bytes, BinaryIO, str],
        filename: Optional[str] = None,
        category: str = "default",
        generate_thumbnail: bool = None
    ) -> Tuple[str, ImageMetadata]:
        """
        保存图片并生成元数据
        
        Args:
            image_data: 图片数据（二进制、文件对象或base64字符串）
            filename: 文件名（如果不提供则自动生成）
            category: 图片分类目录
            generate_thumbnail: 是否生成缩略图（覆盖默认设置）
            
        Returns:
            Tuple[str, ImageMetadata]: 图片路径和元数据
        """
        # 处理base64编码的图片
        if isinstance(image_data, str) and image_data.startswith("data:image"):
            try:
                # 分离MIME类型和base64数据
                format_info, base64_data = image_data.split(",", 1)
                # 提取格式
                mime_type = format_info.split(":")[1].split(";")[0]
                img_format = mime_type.split("/")[1].lower()
                # 解码base64数据
                image_data = base64.b64decode(base64_data)
                # 设置默认文件名（如果未提供）
                if not filename:
                    filename = f"{uuid.uuid4()}.{img_format}"
            except Exception as e:
                logger.error(f"处理base64图片数据失败: {e}")
                raise ValueError("无效的base64图片数据")
        
        # 如果未提供文件名，生成随机文件名
        if not filename:
            filename = f"{uuid.uuid4()}.jpg"
        
        # 确保文件名有扩展名
        if "." not in filename:
            filename = f"{filename}.jpg"
        
        # 验证文件格式
        file_ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if file_ext not in self.allowed_formats:
            raise ValueError(f"不支持的图片格式: {file_ext}，允许的格式: {self.allowed_formats}")
        
        # 构建存储路径
        timestamp = datetime.now().strftime("%Y%m%d")
        relative_dir = Path(category) / timestamp
        relative_path = relative_dir / filename
        
        # 图片处理
        metadata = None
        if Image is not None:
            # 打开图片以获取元数据和可能的处理
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            else:
                # 确保文件指针在开头
                if hasattr(image_data, "seek"):
                    image_data.seek(0)
                img = Image.open(image_data)
            
            # 获取图片信息
            width, height = img.size
            img_format = img.format or file_ext.upper()
            
            # 验证图片大小
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=img_format)
            size_bytes = img_buffer.tell()
            
            if size_bytes > self.max_size_bytes:
                raise ValueError(f"图片大小超过限制: {size_bytes/1024/1024:.2f}MB，最大允许: {self.max_size_bytes/1024/1024:.2f}MB")
            
            # 创建元数据
            metadata = ImageMetadata(
                width=width,
                height=height,
                format=img_format.lower(),
                size=size_bytes,
                created_at=datetime.now(),
                location=str(relative_path)
            )
            
            # 生成缩略图（如果需要）
            should_generate_thumbnail = self.auto_thumbnail if generate_thumbnail is None else generate_thumbnail
            if should_generate_thumbnail:
                await self._generate_thumbnail(img, relative_path)
            
            # 将图片转换回字节数据
            image_data = img_buffer.getvalue()
        
        # 保存原始图片
        saved_path = await self.save_file(relative_path, image_data)
        
        # 如果没有通过PIL获取元数据，则创建基本元数据
        if metadata is None:
            # 获取文件大小
            absolute_path = self._get_absolute_path(relative_path)
            size_bytes = os.path.getsize(absolute_path)
            
            metadata = ImageMetadata(
                width=0,  # 未知
                height=0,  # 未知
                format=file_ext,
                size=size_bytes,
                created_at=datetime.now(),
                location=str(relative_path)
            )
        
        logger.info(f"图片保存成功: {saved_path}")
        return saved_path, metadata
    
    async def get_image_with_metadata(self, image_path: Union[str, Path]) -> Tuple[Optional[bytes], Optional[ImageMetadata]]:
        """
        获取图片数据和元数据
        
        Args:
            image_path: 图片路径
            
        Returns:
            Tuple[Optional[bytes], Optional[ImageMetadata]]: 图片数据和元数据
        """
        # 获取图片数据
        image_data = await self.get_file(image_path)
        if image_data is None:
            return None, None
        
        # 提取元数据
        try:
            if Image is not None:
                img = Image.open(io.BytesIO(image_data))
                width, height = img.size
                img_format = img.format.lower() if img.format else ""
                size_bytes = len(image_data)
                
                metadata = ImageMetadata(
                    width=width,
                    height=height,
                    format=img_format,
                    size=size_bytes,
                    created_at=datetime.now(),  # 这里使用当前时间，因为无法从图片获取创建时间
                    location=str(image_path)
                )
                return image_data, metadata
            else:
                # 基本元数据（无法获取尺寸）
                size_bytes = len(image_data)
                file_ext = os.path.splitext(str(image_path))[1].lower().lstrip(".")
                
                metadata = ImageMetadata(
                    width=0,  # 未知
                    height=0,  # 未知
                    format=file_ext,
                    size=size_bytes,
                    created_at=datetime.now(),
                    location=str(image_path)
                )
                return image_data, metadata
        except Exception as e:
            logger.error(f"获取图片元数据失败: {e}")
            return image_data, None
    
    async def get_thumbnail_url(self, image_path: Union[str, Path]) -> Optional[str]:
        """
        获取缩略图URL
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            Optional[str]: 缩略图URL，如果不存在则返回None
        """
        thumbnail_path = self._get_thumbnail_path(image_path)
        
        # 检查缩略图是否存在
        if await self.file_exists(thumbnail_path):
            return await self.get_file_url(thumbnail_path)
        
        # 如果缩略图不存在但原图存在，尝试创建缩略图
        if Image is not None and await self.file_exists(image_path):
            image_data = await self.get_file(image_path)
            if image_data:
                try:
                    img = Image.open(io.BytesIO(image_data))
                    await self._generate_thumbnail(img, image_path)
                    return await self.get_file_url(thumbnail_path)
                except Exception as e:
                    logger.error(f"生成缩略图失败: {e}")
        
        return None
    
    async def get_image_as_base64(self, image_path: Union[str, Path]) -> Optional[str]:
        """
        获取图片的base64编码
        
        Args:
            image_path: 图片路径
            
        Returns:
            Optional[str]: base64编码的图片数据，如果图片不存在则返回None
        """
        image_data = await self.get_file(image_path)
        if image_data is None:
            return None
        
        # 获取MIME类型
        file_ext = os.path.splitext(str(image_path))[1].lower().lstrip(".")
        mime_type = f"image/{file_ext}"
        if file_ext == "jpg":
            mime_type = "image/jpeg"
        
        # 转换为base64
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{base64_data}"
    
    async def _generate_thumbnail(self, img: 'Image.Image', original_path: Union[str, Path]) -> str:
        """
        生成并保存缩略图
        
        Args:
            img: PIL图片对象
            original_path: 原始图片路径
            
        Returns:
            str: 缩略图路径
        """
        if Image is None:
            logger.warning("PIL库未安装，无法生成缩略图")
            return ""
        
        thumbnail_path = self._get_thumbnail_path(original_path)
        
        try:
            # 创建缩略图
            thumbnail = img.copy()
            thumbnail.thumbnail(self.thumbnail_size, Image.LANCZOS)
            
            # 保存缩略图
            img_buffer = io.BytesIO()
            thumbnail.save(img_buffer, format=img.format)
            await self.save_file(thumbnail_path, img_buffer.getvalue())
            
            logger.info(f"缩略图生成成功: {thumbnail_path}")
            return str(thumbnail_path)
        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            return ""
    
    def _get_thumbnail_path(self, original_path: Union[str, Path]) -> Path:
        """
        获取缩略图路径
        
        Args:
            original_path: 原始图片路径
            
        Returns:
            Path: 缩略图路径
        """
        # 从完整路径中提取文件名
        original_filename = os.path.basename(str(original_path))
        filename_without_ext, ext = os.path.splitext(original_filename)
        thumbnail_filename = f"{filename_without_ext}_thumb{ext}"
        
        # 为缩略图构建相对路径（保持与原图相同的目录结构）
        original_relative = Path(original_path)
        parent_dir = original_relative.parent
        thumbnail_path = parent_dir / thumbnail_filename
        
        # 将相对路径转换为处理目录中的路径
        if self.base_dir in Path(original_path).parents:
            # 如果原始路径已经是绝对路径，则提取相对部分
            relative_to_base = Path(original_path).relative_to(self.base_dir)
            parent_dir = relative_to_base.parent
            thumbnail_path = parent_dir / thumbnail_filename
        
        # 返回相对于处理目录的路径
        return Path("thumbnails") / thumbnail_path 