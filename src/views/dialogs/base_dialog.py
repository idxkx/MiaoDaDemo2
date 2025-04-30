from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt

class BaseDialog(QDialog):
    """基础对话框模板"""
    
    def __init__(self, parent=None, title="对话框"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # 创建内容区
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # 创建按钮区
        self.create_button_box()
        
        # 设置样式
        self.setup_style()
    
    def create_button_box(self):
        """创建按钮区"""
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(button_box)
    
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QPushButton {
                min-width: 80px;
                padding: 8px;
            }
        """)
    
    def add_widget(self, widget):
        """添加部件到内容区"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到内容区"""
        self.content_layout.addLayout(layout)
    
    def add_spacing(self, spacing):
        """添加间距"""
        self.content_layout.addSpacing(spacing) 