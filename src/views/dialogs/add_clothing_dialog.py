# src/views/dialogs/add_clothing_dialog.py

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox, QSizePolicy,
    QWidget
)
from PyQt6.QtGui import QPixmap, QImageReader
from PyQt6.QtCore import Qt, pyqtSignal, QSize # 导入 QSize
from datetime import datetime # 需要导入 datetime

# 对话框使用的宽泛类别
BROAD_CATEGORIES = ["上衣", "裤子", "连体服", "包", "配饰", "鞋子"]
# 注意：目前 AI 模型输出的 50 个类别不包含 "配饰" 和 "鞋子"，所以映射中没有它们

# 假设我们有一些预定义的选项
COLORS = ["红色", "蓝色", "绿色", "黄色", "黑色", "白色", "灰色", "其他"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL", "均码"]
MATERIALS = ["棉", "麻", "丝", "涤纶", "羊毛", "皮革", "其他"]
BRANDS = ["无品牌", "优衣库", "ZARA", "H&M", "耐克", "阿迪达斯", "其他"]

# --- 新增：从 50 个具体 AI 类别到对话框宽泛类别的映射 --- 
# 基于 list_category_cloth.txt 的 type 和用户更新的 BROAD_CATEGORIES 建立
FINE_TO_BROAD_CATEGORY_MAP = {
    # Type 1 -> 上衣
    "冲锋衣": "上衣", "西装外套": "上衣", "女式衬衫": "上衣", "飞行员夹克": "上衣", "纽扣衬衫": "上衣", "开襟衫": "上衣", "法兰绒衬衫": "上衣",
    "挂脖上衣": "上衣", "亨利衫": "上衣", "连帽衫": "上衣", "夹克": "上衣", "运动上衣": "上衣", "派克大衣": "上衣", "海军呢大衣": "上衣", "斗篷(上装)": "上衣",
    "毛衣": "上衣", "背心": "上衣", "T恤": "上衣", "上衣": "上衣", "高领衫": "上衣",
    # Type 2 -> 裤子
    "中裤": "裤子", "卡其裤": "裤子", "阔腿裤": "裤子",
    "剪短裤": "裤子", "高乔裤": "裤子", "牛仔裤": "裤子", "紧身牛仔裤": "裤子", "马裤": "裤子", "慢跑裤": "裤子", "打底裤": "裤子",
    "纱笼": "裤子", "短裤": "裤子", "半身裙": "裤子", "运动裤": "裤子", "运动短裤": "裤子", "泳裤": "裤子",
    # Type 3 -> 连体服 (合并了原外套和连衣裙)
    "长衫": "上衣", # 保持映射到上衣
    "披肩": "连体服", # 原外套 -> 连体服
    "大衣": "连体服", # 原外套 -> 连体服
    "罩衫": "上衣", # 保持映射到上衣
    "连衣裙": "连体服", # 原连衣裙 -> 连体服
    "连体裤": None, # 保持无法映射
    "卡夫坦长袍": "连体服", # 原连衣裙 -> 连体服
    "和服": "连体服", # 原连衣裙 -> 连体服
    "睡裙": "连体服", # 原连衣裙 -> 连体服
    "连身衣": None, # 保持无法映射
    "浴袍": "连体服", # 原连衣裙 -> 连体服
    "连身短裤": "连体服", # 原连衣裙 -> 连体服
    "衬衫裙": "连体服", # 原连衣裙 -> 连体服
    "太阳裙": "连体服"  # 原连衣裙 -> 连体服
    # 注意：'包', '配饰', '鞋子' 暂时没有具体类别映射过来
}
# ---

class AddClothingDialog(QDialog):
    """添加新衣物的对话框 (含图片上传和AI预填)"""

    # 信号：当用户选择图片用于识别时发出，参数为图片路径(str)
    image_selected_for_recognition = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新衣物")
        self.setMinimumWidth(450)
        self.selected_image_path: str | None = None # 保存选择的图片路径

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 使用左右布局：左边表单，右边图片
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- 左侧：表单 ---
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.name_input = QLineEdit()
        form_layout.addRow("名称*:", self.name_input)

        self.category_combo = QComboBox()
        # --- 修改：使用 BROAD_CATEGORIES 填充下拉菜单 --- 
        self.category_combo.addItems(BROAD_CATEGORIES)
        # ---
        form_layout.addRow("分类:", self.category_combo)

        self.color_input = QLineEdit() # 或者用 QComboBox(COLORS)
        form_layout.addRow("颜色:", self.color_input)

        self.size_combo = QComboBox()
        self.size_combo.addItems(SIZES)
        form_layout.addRow("尺码:", self.size_combo)

        self.brand_input = QLineEdit() # 或者用 QComboBox(BRANDS)
        form_layout.addRow("品牌:", self.brand_input)

        self.material_input = QLineEdit() # 或者用 QComboBox(MATERIALS)
        form_layout.addRow("材质:", self.material_input)

        # 购买日期 (可以使用 QDateEdit)
        self.purchase_date_input = QLineEdit()
        self.purchase_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("购买日期:", self.purchase_date_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("例如: 199.00")
        form_layout.addRow("价格:", self.price_input)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("可选描述...")
        self.description_edit.setFixedHeight(60) # 限制高度
        form_layout.addRow("描述:", self.description_edit)

        content_layout.addWidget(form_widget)
        # --- 左侧表单结束 ---

        # --- 右侧：图片上传和预览 ---
        image_area_layout = QVBoxLayout()
        image_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addLayout(image_area_layout)

        self.upload_button = QPushButton("上传图片并识别")
        self.upload_button.clicked.connect(self.select_image)
        image_area_layout.addWidget(self.upload_button)

        self.image_preview_label = QLabel("图片预览")
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setMinimumSize(200, 200) # 最小尺寸
        self.image_preview_label.setStyleSheet("border: 1px dashed #ccc; color: #aaa;")
        # 设置大小策略，允许它在布局中缩放
        size_policy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_preview_label.setSizePolicy(size_policy)
        image_area_layout.addWidget(self.image_preview_label, stretch=1) # 占据剩余空间
        # --- 右侧图片区域结束 ---

        # OK 和 Cancel 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def select_image(self):
        """打开文件对话框选择图片"""
        # 支持的图片格式
        supported_formats = QImageReader.supportedImageFormats()
        format_filter = "Images (" + " ".join([f"*.{fmt.data().decode()}" for fmt in supported_formats]) + ")"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择衣物图片",
            "", # 起始目录
            format_filter
        )
        if file_path:
            self.selected_image_path = file_path
            print(f"Selected image: {file_path}")
            # 显示预览
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                 # 缩放图片以适应 QLabel，保持宽高比
                 scaled_pixmap = pixmap.scaled(
                     self.image_preview_label.size() * 0.95, # 留一点边距
                     Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation
                 )
                 self.image_preview_label.setPixmap(scaled_pixmap)
                 self.image_preview_label.setStyleSheet("border: 1px solid black;") # 清除提示样式
                 # 发出信号，请求进行 AI 识别
                 self.image_selected_for_recognition.emit(file_path)
            else:
                 QMessageBox.warning(self, "图片错误", "无法加载所选图片。")
                 self.selected_image_path = None
                 self.image_preview_label.setText("图片预览")
                 self.image_preview_label.setStyleSheet("border: 1px dashed #ccc; color: #aaa;")


    def update_fields_from_recognition(self, recognition_data: dict):
        """使用AI识别结果更新对话框字段，并尝试映射到宽泛类别"""
        print(f"Updating fields with recognition data: {recognition_data}")
        
        recognized_category = recognition_data.get("category")
        color = recognition_data.get("color")
        material = recognition_data.get("material")
        brand = recognition_data.get("brand")
        
        # --- 修改：类别处理逻辑 (添加更多 DEBUG 打印) --- 
        broad_category = None
        if recognized_category:
            print(f"DEBUG: Recognized category = '{recognized_category}'") # DEBUG
            broad_category = FINE_TO_BROAD_CATEGORY_MAP.get(recognized_category)
            print(f"DEBUG: Looked up in map, result (broad_category) = '{broad_category}'") # DEBUG
            
            # 检查映射结果和目标列表
            is_mapped = broad_category is not None
            is_in_dropdown_list = broad_category in BROAD_CATEGORIES if is_mapped else False
            print(f"DEBUG: Is mapped? {is_mapped}. Is mapped category in dropdown list? {is_in_dropdown_list}") # DEBUG
            
            if is_mapped and is_in_dropdown_list:
                print(f"DEBUG: Condition 'is_mapped and is_in_dropdown_list' is TRUE.") # DEBUG
                self.category_combo.setCurrentText(broad_category)
                print(f"已将识别类别 '{recognized_category}' 映射到下拉框类别 '{broad_category}'.")
                if not self.name_input.text().strip():
                     self.name_input.setText(recognized_category)
                     print(f"已将识别类别 '{recognized_category}' 填充到名称字段。")
            else:
                print(f"DEBUG: Condition 'is_mapped and is_in_dropdown_list' is FALSE.") # DEBUG
                print(f"识别的类别 '{recognized_category}' 无法映射到预设下拉框类别或不在映射表中。")
                if not self.name_input.text().strip():
                     self.name_input.setText(recognized_category)
        # ---

        # --- 颜色、材质、品牌处理保持不变 (因为 AI 目前不输出这些) ---
        if color:
            self.color_input.setText(color) 
        if material:
            self.material_input.setText(material)
        if brand:
            self.brand_input.setText(brand)
        # ---

        QMessageBox.information(self, "识别完成", "已根据图片识别结果预填部分信息，请检查并修改。")


    def accept(self):
        """处理点击 OK，进行验证"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "输入错误", "名称不能为空。")
            return
        # 可以在这里添加更多验证，比如价格格式、日期格式等
        try:
             price_str = self.price_input.text().strip()
             if price_str: # 允许价格为空
                 float(price_str)
        except ValueError:
             QMessageBox.warning(self, "输入错误", "价格必须是有效的数字。")
             return

        try:
             date_str = self.purchase_date_input.text().strip()
             if date_str: # 允许日期为空
                 datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
             QMessageBox.warning(self, "输入错误", "购买日期格式应为 YYYY-MM-DD。")
             return

        super().accept()


    def get_clothing_data(self) -> dict:
        """获取对话框中输入的衣物数据"""
        price_value = 0.0
        try:
             price_str = self.price_input.text().strip()
             if price_str:
                 price_value = float(price_str)
        except ValueError:
             pass # 验证时已处理，这里忽略

        return {
            "name": self.name_input.text().strip(),
            "category": self.category_combo.currentText(),
            "color": self.color_input.text().strip(),
            "size": self.size_combo.currentText(),
            "brand": self.brand_input.text().strip(),
            "material": self.material_input.text().strip(),
            "purchase_date": self.purchase_date_input.text().strip(), # 返回字符串，让调用者处理
            "price": price_value,
            "description": self.description_edit.toPlainText().strip(),
            "image_path": self.selected_image_path # 返回选择的图片路径
        } 