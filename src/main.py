#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能穿搭助手主程序入口
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale, QTranslator
from dotenv import load_dotenv

# 确保能够正确导入其他模块
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.views.main_window import MainWindow

# 加载环境变量
load_dotenv(Path('.') / '.env')

def main():
    """应用程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("智能穿搭助手")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 