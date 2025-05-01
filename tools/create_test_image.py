"""
创建简单的测试图片
"""
from PIL import Image, ImageDraw
import os

def create_test_image(output_path, size=(300, 300)):
    """
    创建一个简单的测试图片
    
    Args:
        output_path: 输出文件路径
        size: 图片尺寸，默认为300x300
    """
    # 创建空白图像，RGB模式
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # 绘制一些基本形状
    # 画一个红色的圆
    draw.ellipse(
        [(50, 50), (250, 250)],
        fill='red'
    )
    
    # 画一个蓝色的矩形
    draw.rectangle(
        [(180, 180), (280, 280)],
        fill='blue'
    )
    
    # 画一个绿色的三角形
    draw.polygon(
        [(150, 50), (250, 150), (50, 150)],
        fill='green'
    )
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存图像
    image.save(output_path)
    print(f"测试图片已保存至: {output_path}")

if __name__ == "__main__":
    output_path = "storage/images/test_image.jpg"
    create_test_image(output_path) 