"""
测试背景移除和颜色识别的简单应用程序
"""
import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from src.utils.image_processor import remove, process_clothing_image

# 创建棋盘格背景图案
TRANSPARENT_BG_PATH = os.path.join(ROOT_DIR, "resources", "images", "transparent_bg.png")
if not os.path.exists(TRANSPARENT_BG_PATH):
    from tools.create_transparent_bg import create_transparent_background
    create_transparent_background(TRANSPARENT_BG_PATH, size=20, grid_size=20)
    print(f"已创建透明背景图案: {TRANSPARENT_BG_PATH}")

class ImageProcessThread(QThread):
    """图片处理线程"""
    finished = pyqtSignal(str, list)  # 发送处理后的图片路径和颜色列表
    error = pyqtSignal(str)  # 发送错误信息
    progress = pyqtSignal(str, int)  # 发送进度信息和百分比
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self._loop = None
        print(f"创建图片处理线程，处理图片：{image_path}")
    
    def run(self):
        """运行图片处理任务"""
        try:
            # 创建事件循环
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # 设置输出目录
            output_dir = os.path.join(ROOT_DIR, "storage", "images", "processed")
            os.makedirs(output_dir, exist_ok=True)
            
            # 处理配置
            config = {
                'num_colors': 5,  # 提取5种主要颜色
                'min_size': (100, 100),
                'max_size': (4000, 4000),
                'quality': 90
            }
            
            # 进度回调
            def progress_callback(message, value):
                self.progress.emit(message, value)
            
            # 处理图片
            print("开始处理图片...")
            output_path, colors = self._loop.run_until_complete(
                process_clothing_image(
                    self.image_path,
                    progress_callback=progress_callback,
                    output_dir=output_dir,
                    config=config
                )
            )
            
            # 发送结果
            self.finished.emit(output_path, colors)
            
        except Exception as e:
            print(f"图片处理失败: {str(e)}")
            self.error.emit(str(e))
        finally:
            # 清理事件循环
            if self._loop:
                self._loop.close()

class TestApp(QMainWindow):
    """测试应用程序"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("背景移除和颜色识别测试")
        self.resize(800, 600)
        
        # 初始化变量
        self.original_image_path = None
        self.processed_image_path = None
        self.process_thread = None
        
        # 设置中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 图像显示区域
        image_layout = QHBoxLayout()
        
        # 原图
        original_layout = QVBoxLayout()
        original_layout.addWidget(QLabel("原图:"))
        self.original_label = QLabel()
        self.original_label.setFixedSize(350, 350)
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setStyleSheet("border: 1px solid #ccc;")
        self.original_label.setText("选择图片以显示")
        original_layout.addWidget(self.original_label)
        image_layout.addLayout(original_layout)
        
        # 处理后图像
        processed_layout = QVBoxLayout()
        processed_layout.addWidget(QLabel("去背景后:"))
        self.processed_label = QLabel()
        self.processed_label.setFixedSize(350, 350)
        self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processed_label.setStyleSheet("border: 1px solid #ccc;")
        self.processed_label.setText("点击处理按钮")
        processed_layout.addWidget(self.processed_label)
        image_layout.addLayout(processed_layout)
        
        main_layout.addLayout(image_layout)
        
        # 颜色显示区域
        self.color_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("识别的颜色:"))
        main_layout.addLayout(self.color_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # 状态信息
        self.status_label = QLabel("准备就绪")
        main_layout.addWidget(self.status_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 选择图片按钮
        select_btn = QPushButton("选择图片")
        select_btn.clicked.connect(self.select_image)
        button_layout.addWidget(select_btn)
        
        # 处理图片按钮
        self.process_btn = QPushButton("处理图片")
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        # 生成测试图片按钮
        test_btn = QPushButton("生成测试图片")
        test_btn.clicked.connect(self.generate_test_image)
        button_layout.addWidget(test_btn)
        
        main_layout.addLayout(button_layout)
    
    def select_image(self):
        """选择图片"""
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if image_path:
            self.original_image_path = image_path
            self.show_image(self.original_label, image_path)
            self.process_btn.setEnabled(True)
            self.status_label.setText(f"已选择图片: {os.path.basename(image_path)}")
    
    def generate_test_image(self):
        """生成测试图片"""
        try:
            from tools.create_test_image import create_test_image
            
            # 创建输出目录
            output_dir = os.path.join(ROOT_DIR, "storage", "images")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成测试图片
            output_path = os.path.join(output_dir, "test_image.jpg")
            create_test_image(output_path)
            
            # 显示测试图片
            self.original_image_path = output_path
            self.show_image(self.original_label, output_path)
            self.process_btn.setEnabled(True)
            self.status_label.setText(f"已生成测试图片: {os.path.basename(output_path)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成测试图片失败: {str(e)}")
    
    def process_image(self):
        """处理图片"""
        if not self.original_image_path:
            return
        
        # 禁用处理按钮
        self.process_btn.setEnabled(False)
        
        # 清空颜色显示
        self.clear_colors()
        
        # 开始处理
        self.status_label.setText("正在处理图片...")
        self.process_thread = ImageProcessThread(self.original_image_path)
        self.process_thread.finished.connect(self.process_finished)
        self.process_thread.error.connect(self.process_error)
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.start()
    
    def update_progress(self, message, value):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def process_finished(self, output_path, colors):
        """处理完成"""
        self.processed_image_path = output_path
        self.show_image(self.processed_label, output_path, is_transparent=True)
        self.show_colors(colors)
        self.status_label.setText("图片处理完成")
        self.process_btn.setEnabled(True)
    
    def process_error(self, error_message):
        """处理错误"""
        QMessageBox.warning(self, "处理错误", error_message)
        self.status_label.setText(f"处理失败: {error_message}")
        self.process_btn.setEnabled(True)
    
    def show_image(self, label, image_path, is_transparent=False):
        """在标签上显示图片"""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                raise ValueError(f"无法加载图片: {image_path}")
            
            # 缩放图片
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 设置样式
            if is_transparent and image_path.lower().endswith('.png'):
                label.setStyleSheet(f"""
                    QLabel {{
                        border: 1px solid #ccc;
                        background-image: url({TRANSPARENT_BG_PATH.replace('\\', '/')});
                        background-repeat: repeat;
                        background-position: top left;
                        background-attachment: fixed;
                    }}
                """)
            else:
                label.setStyleSheet("border: 1px solid #ccc;")
            
            # 显示图片
            label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示图片失败: {str(e)}")
    
    def clear_colors(self):
        """清空颜色显示"""
        # 清除颜色布局中的所有小部件
        while self.color_layout.count():
            item = self.color_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_colors(self, colors):
        """显示识别的颜色"""
        # 清空现有颜色
        self.clear_colors()
        
        # 添加新颜色
        for color_name, hex_code, percentage in colors:
            # 创建颜色块
            color_widget = QWidget()
            color_widget.setFixedSize(80, 80)
            color_widget.setStyleSheet(f"background-color: {hex_code}; border: 1px solid #ccc;")
            
            # 创建颜色信息标签
            color_label = QLabel(f"{color_name}\n{hex_code}\n{percentage:.1f}%")
            color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 创建布局
            color_box = QVBoxLayout()
            color_box.addWidget(color_widget)
            color_box.addWidget(color_label)
            
            # 添加到主布局
            self.color_layout.addLayout(color_box)

def main():
    """应用程序入口"""
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 