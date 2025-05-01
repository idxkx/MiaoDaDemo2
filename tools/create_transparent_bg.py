"""
创建透明背景棋盘格图案
用于显示透明背景图片
"""
from PIL import Image, ImageDraw
import os

def create_transparent_background(output_path, size=20, grid_size=10):
    """
    创建透明背景棋盘格图案
    
    Args:
        output_path: 输出文件路径
        size: 棋盘格尺寸，默认为20像素
        grid_size: 图像网格大小，默认为10（产生10x10的棋盘）
    """
    # 创建空白图像，RGBA模式
    width = size * grid_size
    height = size * grid_size
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制棋盘格
    for i in range(grid_size):
        for j in range(grid_size):
            if (i + j) % 2 == 0:
                color = (240, 240, 240, 255)  # 浅灰色
            else:
                color = (220, 220, 220, 255)  # 深灰色
            
            # 绘制矩形
            draw.rectangle(
                [(i * size, j * size), ((i + 1) * size, (j + 1) * size)],
                fill=color
            )
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存图像
    image.save(output_path)
    print(f"透明背景图案已保存至: {output_path}")

if __name__ == "__main__":
    output_path = "resources/images/transparent_bg.png"
    create_transparent_background(output_path) 