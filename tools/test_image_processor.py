"""
测试image_processor模块
"""
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.image_processor import ImageProcessor, process_clothing_image
from PIL import Image

async def test_image_processor():
    """测试image_processor模块的功能"""
    input_path = "storage/images/test_image.jpg"
    output_dir = "storage/images/processed"
    
    print("=" * 50)
    print("测试 ImageProcessor.remove_background 方法")
    print("=" * 50)
    
    try:
        output_path = await ImageProcessor.remove_background(input_path)
        print(f"背景移除成功: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
    except Exception as e:
        print(f"背景移除失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("测试 ImageProcessor.extract_main_colors 方法")
    print("=" * 50)
    
    try:
        colors = await ImageProcessor.extract_main_colors(input_path, num_colors=5)
        print(f"颜色提取成功. 找到 {len(colors)} 种颜色:")
        for i, (name, hex_code, percentage) in enumerate(colors, 1):
            print(f"  {i}. {name} ({hex_code}) - {percentage:.1f}%")
    except Exception as e:
        print(f"颜色提取失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("测试 process_clothing_image 函数")
    print("=" * 50)
    
    def progress_callback(message, value):
        print(f"进度: {value}% - {message}")
    
    try:
        output_path, colors = await process_clothing_image(
            input_path, 
            progress_callback=progress_callback,
            output_dir=output_dir,
            config={
                'num_colors': 5
            }
        )
        
        print(f"\n处理成功!")
        print(f"输出路径: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
        print(f"识别到 {len(colors)} 种颜色:")
        for i, (name, hex_code, percentage) in enumerate(colors, 1):
            print(f"  {i}. {name} ({hex_code}) - {percentage:.1f}%")
    except Exception as e:
        print(f"处理失败: {str(e)}")
    
if __name__ == "__main__":
    asyncio.run(test_image_processor()) 