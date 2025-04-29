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

# 加载环境变量
load_dotenv(ROOT_DIR / '.env')

def main():
    """主程序入口"""
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 设置中文环境
    translator = QTranslator()
    translator.load('zh_CN', str(ROOT_DIR / 'resources' / 'translations'))
    app.installTranslator(translator)
    QLocale.setDefault(QLocale(QLocale.Language.Chinese, QLocale.Country.China))
    
    # TODO: 初始化主窗口
    # from views.main_window import MainWindow
    # main_window = MainWindow()
    # main_window.show()
    
    # 启动应用
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 