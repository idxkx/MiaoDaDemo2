"""
图像处理工具模块
提供图像背景移除和颜色分析功能
"""
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image
from sklearn.cluster import KMeans
from typing import List, Tuple, Callable, Optional, Dict, Any
import logging
import asyncio
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger(__name__)

class ImageProcessingError(Exception):
    """图像处理错误基类"""
    pass

class ImageLoadError(ImageProcessingError):
    """图像加载错误"""
    pass

class ImageSaveError(ImageProcessingError):
    """图像保存错误"""
    pass

class BackgroundRemovalError(ImageProcessingError):
    """背景移除错误"""
    pass

class ColorExtractionError(ImageProcessingError):
    """颜色提取错误"""
    pass

class ImageProcessor:
    """图像处理器类"""
    
    @staticmethod
    async def remove_background(image_path: str, output_path: str = None) -> str:
        """
        移除图片背景
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选）
            
        Returns:
            str: 处理后的图片路径
        """
        try:
            # 如果未指定输出路径，在原文件名后添加 _no_bg
            if output_path is None:
                filename, ext = os.path.splitext(image_path)
                output_path = f"{filename}_no_bg{ext}"
            
            # 读取图片
            input_image = Image.open(image_path)
            
            # 移除背景
            output_image = remove(input_image)
            
            # 保存结果
            output_image.save(output_path)
            
            logger.info(f"背景移除成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"背景移除失败: {str(e)}")
            raise
    
    @staticmethod
    async def extract_main_colors(image_path: str, num_colors: int = 3) -> List[Tuple[str, str, float]]:
        """
        提取图片中的主要颜色
        
        Args:
            image_path: 图片路径
            num_colors: 要提取的颜色数量（默认为3）
            
        Returns:
            List[Tuple[str, str, float]]: 主要颜色列表，每个元素为 (颜色名称, 十六进制颜色码, 占比)
        """
        try:
            # 读取图片
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            # 如果图片包含alpha通道（RGBA），只保留RGB通道
            if image.shape[-1] == 4:
                # 使用alpha通道作为mask
                mask = image[:, :, 3] > 0
                # 只处理非透明区域
                pixels = image[mask][:, :3]
            else:
                pixels = image.reshape(-1, 3)
            
            # 转换为RGB格式
            pixels = cv2.cvtColor(pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2RGB).reshape(-1, 3)
            
            # 使用K-means聚类
            kmeans = KMeans(n_clusters=num_colors, random_state=42)
            kmeans.fit(pixels)
            
            # 获取聚类中心（主要颜色）
            colors = kmeans.cluster_centers_
            
            # 计算每个颜色的像素占比
            labels = kmeans.labels_
            counts = np.bincount(labels)
            percentages = counts / len(pixels) * 100
            
            # 将RGB值转换为十六进制颜色码和颜色名称
            result = []
            for color, percentage in zip(colors, percentages):
                rgb = tuple(map(int, color))
                hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
                color_name = ImageProcessor._get_color_name(rgb)
                result.append((color_name, hex_code, float(percentage)))
            
            # 按占比降序排序
            result.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"成功提取 {num_colors} 种主要颜色")
            return result
            
        except Exception as e:
            logger.error(f"颜色提取失败: {str(e)}")
            raise
    
    @staticmethod
    def _get_color_name(rgb: Tuple[int, int, int]) -> str:
        """
        根据RGB值获取颜色名称
        使用扩展的颜色映射表提高识别准确性
        """
        # 扩展的颜色映射表
        color_map = {
            # 基础颜色
            (0, 0, 0): "黑色",
            (255, 255, 255): "白色",
            (128, 128, 128): "灰色",
            (192, 192, 192): "浅灰色",
            (64, 64, 64): "深灰色",
            
            # 红色系
            (255, 0, 0): "红色",
            (255, 192, 192): "浅粉色",
            (255, 128, 128): "粉色",
            (255, 64, 64): "深粉色",
            (128, 0, 0): "暗红色",
            (255, 69, 0): "橙红色",
            
            # 蓝色系
            (0, 0, 255): "蓝色",
            (0, 0, 128): "深蓝色",
            (0, 128, 255): "天蓝色",
            (135, 206, 235): "浅蓝色",
            (0, 255, 255): "青色",
            (0, 128, 128): "青绿色",
            
            # 绿色系
            (0, 255, 0): "绿色",
            (0, 128, 0): "深绿色",
            (128, 255, 128): "浅绿色",
            (34, 139, 34): "森林绿",
            (154, 205, 50): "黄绿色",
            
            # 黄色系
            (255, 255, 0): "黄色",
            (255, 215, 0): "金色",
            (218, 165, 32): "金黄色",
            (255, 192, 0): "橙黄色",
            
            # 紫色系
            (255, 0, 255): "紫色",
            (128, 0, 128): "深紫色",
            (238, 130, 238): "浅紫色",
            (148, 0, 211): "紫罗兰",
            
            # 棕色系
            (165, 42, 42): "棕色",
            (139, 69, 19): "深棕色",
            (210, 180, 140): "浅棕色",
            (160, 82, 45): "赭色",
            
            # 其他颜色
            (255, 165, 0): "橙色",
            (255, 192, 128): "杏色",
            (250, 128, 114): "珊瑚色",
            (255, 228, 196): "米色",
            (245, 245, 220): "米黄色",
            (240, 248, 255): "爱丽丝蓝",
            (230, 230, 250): "薰衣草色"
        }
        
        def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
            """计算两个颜色之间的欧氏距离"""
            return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5
        
        # 找到最接近的颜色
        min_distance = float('inf')
        closest_color = "未知"
        
        for base_rgb, name in color_map.items():
            distance = color_distance(rgb, base_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        return closest_color

async def process_clothing_image(
    image_path: str,
    progress_callback: Optional[Callable[[str, int], None]] = None,
    cancellation_token: Optional[asyncio.Event] = None,
    output_dir: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[Tuple[str, str, float]]]:
    """
    处理服装图片：移除背景并提取主要颜色
    
    Args:
        image_path: 输入图片路径
        progress_callback: 进度回调函数，接收消息和进度值(0-100)
        cancellation_token: 取消令牌，用于取消处理
        output_dir: 输出目录，默认使用临时目录
        config: 配置参数，包含：
            - num_colors: 要提取的颜色数量（默认3）
            - min_size: 最小图片尺寸（默认100x100）
            - max_size: 最大图片尺寸（默认4000x4000）
            - allowed_formats: 允许的图片格式（默认['jpg', 'jpeg', 'png']）
            - quality: 输出图片质量（默认85）
    
    Returns:
        Tuple[str, List[Tuple[str, str, float]]]: (处理后的图片路径, 主要颜色列表)
        
    Raises:
        ImageLoadError: 图片加载失败
        ImageSaveError: 图片保存失败
        BackgroundRemovalError: 背景移除失败
        ColorExtractionError: 颜色提取失败
        ValueError: 参数错误
    """
    try:
        # 默认配置
        default_config = {
            'num_colors': 3,
            'min_size': (100, 100),
            'max_size': (4000, 4000),
            'allowed_formats': ['jpg', 'jpeg', 'png'],
            'quality': 85
        }
        config = {**default_config, **(config or {})}
        
        # 验证输入
        if not os.path.exists(image_path):
            raise ImageLoadError(f"图片文件不存在: {image_path}")
            
        # 检查文件格式
        ext = os.path.splitext(image_path)[1].lower().lstrip('.')
        if ext not in config['allowed_formats']:
            raise ValueError(f"不支持的图片格式: {ext}")
            
        if progress_callback:
            progress_callback("正在验证图片...", 5)
            
        # 检查取消状态
        if cancellation_token and cancellation_token.is_set():
            logger.info("处理被取消")
            return "", []
            
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="clothing_process_")
        try:
            # 加载并验证图片
            try:
                image = Image.open(image_path)
                width, height = image.size
                
                # 检查图片尺寸
                if width < config['min_size'][0] or height < config['min_size'][1]:
                    raise ImageLoadError(f"图片尺寸太小: {width}x{height}")
                if width > config['max_size'][0] or height > config['max_size'][1]:
                    raise ImageLoadError(f"图片尺寸太大: {width}x{height}")
                    
            except Exception as e:
                raise ImageLoadError(f"无法加载图片: {str(e)}")
                
            if progress_callback:
                progress_callback("正在移除背景...", 20)
                
            # 检查取消状态
            if cancellation_token and cancellation_token.is_set():
                return "", []
                
            # 移除背景
            try:
                # 生成输出文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"no_bg_{timestamp}.png"
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, output_filename)
                else:
                    output_path = os.path.join(temp_dir, output_filename)
                
                # 移除背景
                output_image = remove(image)
                output_image.save(output_path, quality=config['quality'])
                
            except Exception as e:
                raise BackgroundRemovalError(f"背景移除失败: {str(e)}")
                
            if progress_callback:
                progress_callback("正在分析颜色...", 60)
                
            # 检查取消状态
            if cancellation_token and cancellation_token.is_set():
                return "", []
                
            # 提取颜色
            try:
                colors = await ImageProcessor.extract_main_colors(
                    output_path,
                    num_colors=config['num_colors']
                )
            except Exception as e:
                raise ColorExtractionError(f"颜色提取失败: {str(e)}")
                
            if progress_callback:
                progress_callback("处理完成", 100)
                
            # 如果使用临时目录且指定了输出目录，移动文件
            if output_dir and temp_dir in output_path:
                final_path = os.path.join(output_dir, output_filename)
                shutil.move(output_path, final_path)
                output_path = final_path
                
            return output_path, colors
            
        finally:
            # 清理临时目录
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"清理临时目录失败: {str(e)}")
                
    except Exception as e:
        logger.error(f"图片处理失败: {str(e)}", exc_info=True)
        raise 