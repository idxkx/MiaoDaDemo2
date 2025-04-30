from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from ..dialogs.base_dialog import BaseDialog

class AddClothingDialog(BaseDialog):
    """添加衣物对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "添加衣物")
        self.setup_ui()
        
    def setup_ui(self):
        """初始化界面"""
        # 基本信息
        basic_group = QWidget()
        basic_layout = QVBoxLayout(basic_group)
        
        # 名称
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)
        
        # 分类
        category_layout = QHBoxLayout()
        category_label = QLabel("分类:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["上装", "下装", "外套"])
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        basic_layout.addLayout(category_layout)
        
        # 子分类
        subcategory_layout = QHBoxLayout()
        subcategory_label = QLabel("子分类:")
        self.subcategory_combo = QComboBox()
        subcategory_layout.addWidget(subcategory_label)
        subcategory_layout.addWidget(self.subcategory_combo)
        basic_layout.addLayout(subcategory_layout)
        
        # 更新子分类选项
        self.category_combo.currentTextChanged.connect(self.update_subcategories)
        self.update_subcategories(self.category_combo.currentText())
        
        self.add_widget(basic_group)
        self.add_spacing(10)
        
        # 图片上传
        image_group = QWidget()
        image_layout = QVBoxLayout(image_group)
        
        # 预览区
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 200)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                background: #f9f9f9;
            }
        """)
        image_layout.addWidget(self.preview_label)
        
        # 上传按钮
        upload_btn = QPushButton("选择图片")
        upload_btn.clicked.connect(self.on_upload_image)
        image_layout.addWidget(upload_btn)
        
        self.add_widget(image_group)
        self.add_spacing(10)
        
        # 详细信息
        detail_group = QWidget()
        detail_layout = QVBoxLayout(detail_group)
        
        # 颜色
        color_layout = QHBoxLayout()
        color_label = QLabel("颜色:")
        self.color_combo = QComboBox()
        self.color_combo.addItems(["黑色", "白色", "红色", "蓝色", "灰色"])
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_combo)
        detail_layout.addLayout(color_layout)
        
        # 尺码
        size_layout = QHBoxLayout()
        size_label = QLabel("尺码:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["XS", "S", "M", "L", "XL", "XXL"])
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        detail_layout.addLayout(size_layout)
        
        # 季节
        season_layout = QHBoxLayout()
        season_label = QLabel("适用季节:")
        self.season_combo = QComboBox()
        self.season_combo.addItems(["春秋", "夏季", "冬季", "四季"])
        season_layout.addWidget(season_label)
        season_layout.addWidget(self.season_combo)
        detail_layout.addLayout(season_layout)
        
        # 描述
        desc_label = QLabel("描述:")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        detail_layout.addWidget(desc_label)
        detail_layout.addWidget(self.desc_input)
        
        self.add_widget(detail_group)
    
    def update_subcategories(self, category):
        """更新子分类选项"""
        self.subcategory_combo.clear()
        if category == "上装":
            self.subcategory_combo.addItems(["T恤", "衬衫", "毛衣"])
        elif category == "下装":
            self.subcategory_combo.addItems(["牛仔裤", "休闲裤", "短裤"])
        elif category == "外套":
            self.subcategory_combo.addItems(["夹克", "大衣", "风衣"])
    
    def on_upload_image(self):
        """处理图片上传"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if file_name:
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(
                200,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
    
    def get_clothing_data(self):
        """获取衣物数据"""
        return {
            "name": self.name_input.text(),
            "category": self.category_combo.currentText(),
            "subcategory": self.subcategory_combo.currentText(),
            "color": self.color_combo.currentText(),
            "size": self.size_combo.currentText(),
            "season": self.season_combo.currentText(),
            "description": self.desc_input.toPlainText()
        } 