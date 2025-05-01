"""图像处理器测试模块"""
import os
import pytest
from PIL import Image
import numpy as np

from src.utils.image_processor import ImageProcessor, process_clothing_image

@pytest.fixture
def test_image_path(tmp_path):
    """创建测试用图片"""
    # 创建一个简单的测试图片
    image = Image.new('RGBA', (100, 100), 'white')
    # 在中间画一个红色方块
    for x in range(30, 70):
        for y in range(30, 70):
            image.putpixel((x, y), (255, 0, 0, 255))
    
    # 保存图片
    image_path = os.path.join(tmp_path, "test_image.png")
    image.save(image_path)
    return image_path

@pytest.mark.asyncio
async def test_remove_background(test_image_path):
    """测试背景移除功能"""
    processor = ImageProcessor()
    
    # 移除背景
    output_path = await processor.remove_background(test_image_path)
    
    # 验证输出文件存在
    assert os.path.exists(output_path)
    
    # 验证输出图片是否为RGBA格式
    output_image = Image.open(output_path)
    assert output_image.mode == 'RGBA'

@pytest.mark.asyncio
async def test_extract_main_colors(test_image_path):
    """测试主要颜色提取功能"""
    processor = ImageProcessor()
    
    # 提取颜色
    colors = await processor.extract_main_colors(test_image_path)
    
    # 验证返回结果
    assert len(colors) == 3  # 默认提取3种颜色
    assert all(isinstance(c, tuple) and len(c) == 3 for c in colors)  # 验证返回格式
    
    # 验证颜色占比之和接近100%
    total_percentage = sum(c[2] for c in colors)
    assert 99 <= total_percentage <= 101

@pytest.mark.asyncio
async def test_process_clothing_image(test_image_path):
    """测试完整的图片处理流程"""
    # 处理图片
    no_bg_path, colors = await process_clothing_image(test_image_path)
    
    # 验证输出文件存在
    assert os.path.exists(no_bg_path)
    
    # 验证颜色提取结果
    assert len(colors) == 3
    assert all(isinstance(c, tuple) and len(c) == 3 for c in colors)
    
    # 验证颜色名称和十六进制码格式
    for color_name, hex_code, percentage in colors:
        assert isinstance(color_name, str)
        assert hex_code.startswith('#')
        assert len(hex_code) == 7
        assert 0 <= percentage <= 100 