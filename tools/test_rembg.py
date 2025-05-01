"""
测试rembg是否能正常移除背景
"""
import os
from rembg import remove
from PIL import Image
import time

def test_remove_bg(input_path, output_path):
    """
    测试rembg移除背景功能
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
    """
    start_time = time.time()
    
    print(f"开始处理图片: {input_path}")
    print(f"输出路径: {output_path}")
    
    try:
        # 读取图片
        input_image = Image.open(input_path)
        
        # 移除背景
        print("正在移除背景...")
        output_image = remove(input_image, alpha_matting=True)
        
        # 强制输出为PNG格式
        output_path = os.path.splitext(output_path)[0] + ".png"
        print(f"修正输出路径为: {output_path}（PNG格式）")
        
        # 保存结果
        print("保存结果...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_image.save(output_path, format="PNG")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"处理成功! 耗时: {duration:.2f}秒")
        print(f"输出图片保存至: {output_path}")
        
        # 检查输出文件
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"输出文件大小: {size} 字节")
        else:
            print("警告: 输出文件不存在!")
            
    except Exception as e:
        print(f"处理失败: {str(e)}")
        
if __name__ == "__main__":
    input_folder = "storage/images"
    output_folder = "storage/images/processed"
    
    # 如果指定文件夹不存在，创建并提示用户
    if not os.path.exists(input_folder):
        os.makedirs(input_folder, exist_ok=True)
        print(f"已创建输入文件夹: {input_folder}")
        print(f"请将图片放入该文件夹后再运行此脚本。")
        exit(0)
    
    # 获取文件夹中的图片
    image_files = [f for f in os.listdir(input_folder) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(input_folder, f))]
    
    if not image_files:
        print(f"文件夹 {input_folder} 中没有图片文件。")
        print(f"请将图片放入该文件夹后再运行此脚本。")
        exit(0)
    
    # 处理第一张图片
    input_path = os.path.join(input_folder, image_files[0])
    output_path = os.path.join(output_folder, f"test_nobg_{os.path.basename(input_path)}")
    
    print(f"已找到图片: {image_files[0]}")
    test_remove_bg(input_path, output_path) 