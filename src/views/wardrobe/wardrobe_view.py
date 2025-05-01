from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QListView,
    QSplitter,
    QPushButton,
    QToolBar,
    QLabel,
    QComboBox,
    QLineEdit,
    QScrollArea,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap
import os
import logging
import sys
from pathlib import Path

from src.domain.model.entities import ClothingItem
from .add_clothing_dialog import AddClothingDialog

logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
TRANSPARENT_BG_PATH = os.path.join(ROOT_DIR, "resources", "images", "transparent_bg.png")
logger.info(f"透明背景图案路径: {TRANSPARENT_BG_PATH}")

class WardrobeView(QWidget):
    """衣橱管理视图 - 显示列表和详情"""
    
    # 信号定义
    # category_selected = pyqtSignal(str)  # 分类选中信号 (暂时保留，但功能需调整)
    item_selected = pyqtSignal(ClothingItem)  # 衣物选中信号
    add_clothing_requested = pyqtSignal() 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items_map: dict[UUID, ClothingItem] = {} # 存储加载的衣物，ID -> Item
        self.setup_ui()
        
    def setup_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_toolbar(layout)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter, 1) # 让分割器占据主要空间
        
        # --- 左侧：分类树 (暂时保留，数据和功能待完善) ---
        # self.create_category_tree(main_splitter)
        left_panel = QWidget() # 使用 QWidget 作为容器
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5,5,5,5)
        left_layout.addWidget(QLabel("分类 (待实现)"))
        # TODO: 添加真实的分类树逻辑
        main_splitter.addWidget(left_panel)
        # ---
        
        # --- 右侧：衣橱内容区 (列表 + 详情) ---
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_splitter = QSplitter(Qt.Orientation.Horizontal)
        right_layout.addWidget(right_panel_splitter)
        main_splitter.addWidget(right_panel)
        
        # --- 右侧 -> 左：衣物列表 ---
        self.items_list_widget = QListWidget()
        self.items_list_widget.setFixedWidth(250) # 给列表一个固定宽度
        self.items_list_widget.currentItemChanged.connect(self.on_item_selection_changed)
        right_panel_splitter.addWidget(self.items_list_widget)
        # ---

        # --- 右侧 -> 右：衣物详情区 (带滚动) ---
        detail_scroll_area = QScrollArea()
        detail_scroll_area.setWidgetResizable(True)
        detail_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        right_panel_splitter.addWidget(detail_scroll_area)

        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        detail_scroll_area.setWidget(self.detail_widget)

        # 详情区控件 (先创建占位符)
        self.detail_image_label = QLabel("图片预览")
        self.detail_image_label.setMinimumSize(200, 200)
        self.detail_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_image_label.setStyleSheet("border: 1px dashed #ccc; color: #aaa;")
        detail_layout.addWidget(self.detail_image_label)

        self.detail_name_label = QLabel("名称: -")
        self.detail_category_label = QLabel("分类: -") # 需要转换 ID
        self.detail_color_label = QLabel("颜色: -")
        self.detail_size_label = QLabel("尺码: -")
        self.detail_brand_label = QLabel("品牌: -")
        self.detail_material_label = QLabel("材质: -")
        self.detail_purchase_date_label = QLabel("购买日期: -")
        self.detail_price_label = QLabel("价格: -")
        self.detail_description_label = QLabel("描述: -")
        self.detail_tags_label = QLabel("标签: -") # 用于显示标签
        self.detail_tags_label.setWordWrap(True) # 允许标签换行
        self.detail_favorite_label = QLabel("收藏: 否")

        detail_layout.addWidget(self.detail_name_label)
        detail_layout.addWidget(self.detail_category_label)
        detail_layout.addWidget(self.detail_color_label)
        detail_layout.addWidget(self.detail_size_label)
        detail_layout.addWidget(self.detail_brand_label)
        detail_layout.addWidget(self.detail_material_label)
        detail_layout.addWidget(self.detail_purchase_date_label)
        detail_layout.addWidget(self.detail_price_label)
        detail_layout.addWidget(self.detail_description_label)
        detail_layout.addWidget(self.detail_tags_label)
        detail_layout.addWidget(self.detail_favorite_label)

        detail_layout.addStretch() # 将内容推到顶部
        # ---
        
        # 设置分割器比例
        main_splitter.setSizes([200, 800]) # 左侧分类窄，右侧宽
        right_panel_splitter.setSizes([250, 550]) # 右侧中列表窄，详情宽
    
    def create_toolbar(self, layout):
        """创建工具栏"""
        toolbar = QToolBar()
        layout.addWidget(toolbar)
        
        # 添加分类按钮
        self.add_category_btn = QPushButton("添加分类")
        toolbar.addWidget(self.add_category_btn)
        
        # 添加衣物按钮
        self.add_clothing_btn = QPushButton("添加衣物")
        self.add_clothing_btn.clicked.connect(self.add_clothing_requested.emit)
        toolbar.addWidget(self.add_clothing_btn)
        
        toolbar.addSeparator()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索衣物...")
        self.search_input.setMaximumWidth(200)
        toolbar.addWidget(self.search_input)
        
        # 排序下拉框
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["按名称", "按添加时间", "按最后使用"])
        toolbar.addWidget(self.sort_combo)
        
        # 视图切换按钮
        self.view_mode_btn = QPushButton("切换视图")
        toolbar.addWidget(self.view_mode_btn)
    
    def display_items(self, items: List[ClothingItem]):
        """用 ClothingItem 对象列表填充衣物列表"""
        self.items_list_widget.clear()
        self.items_map.clear()
        print(f"WardrobeView: Displaying {len(items)} items.")
        if not items:
             self.clear_details() # 如果没有物品，清空详情区
             list_item = QListWidgetItem("衣橱为空")
             list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # 不可选
             self.items_list_widget.addItem(list_item)
             return

        for item in items:
            self.items_map[item.id] = item # 存储对象引用
            list_item = QListWidgetItem(item.name) 
            list_item.setData(Qt.ItemDataRole.UserRole, item.id) # 存储 ID 以便查找
            self.items_list_widget.addItem(list_item)
            
        # 默认选中第一个
        if self.items_list_widget.count() > 0:
            self.items_list_widget.setCurrentRow(0)
            # self.on_item_selection_changed(self.items_list_widget.currentItem()) # 手动触发一次更新

    def on_item_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """列表选中项改变时，更新右侧详情区"""
        if current:
            item_id = current.data(Qt.ItemDataRole.UserRole)
            if item_id and item_id in self.items_map:
                selected_item = self.items_map[item_id]
                print(f"WardrobeView: Item selected - ID: {selected_item.id}, Name: {selected_item.name}")
                self.show_item_details(selected_item)
            else:
                 print(f"WardrobeView: Error finding selected item data for ID {item_id}")
                 self.clear_details()
        else:
             self.clear_details()

    def show_item_details(self, item: ClothingItem):
        """在右侧详情区显示衣物信息"""
        self.detail_name_label.setText(f"名称: {item.name or '-'}")
        # TODO: 需要根据 category_id 获取分类名称
        self.detail_category_label.setText(f"分类ID: {item.category_id}") 
        
        # 显示颜色信息
        if item.color:
            color_text = f"{item.color.name}"
            if hasattr(item.color, 'hex_code'):
                self.detail_color_label.setStyleSheet(f"""
                    QLabel {{
                        background: {item.color.hex_code};
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        padding: 2px 5px;
                    }}
                """)
            else:
                self.detail_color_label.setStyleSheet("")
            self.detail_color_label.setText(f"颜色: {color_text}")
        else:
            self.detail_color_label.setText("颜色: -")
            self.detail_color_label.setStyleSheet("")
        
        self.detail_size_label.setText(f"尺码: {item.size.value if item.size else '-'}")
        self.detail_brand_label.setText(f"品牌: {item.brand.name if item.brand else '-'}")
        self.detail_material_label.setText(f"材质: {item.material.name if item.material else '-'}")
        date_str = item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '-'
        self.detail_purchase_date_label.setText(f"购买日期: {date_str}")
        self.detail_price_label.setText(f"价格: {item.price:.2f}" if item.price is not None else "价格: -")
        self.detail_description_label.setText(f"描述: {item.description or '无'}")
        self.detail_favorite_label.setText(f"收藏: {'是' if item.is_favorite else '否'}")

        # --- 显示标签 --- 
        if item.tags:
            tag_names = [f"{tag.category}:{tag.name}" for tag in item.tags] # 显示类别和名称
            self.detail_tags_label.setText(f"标签: {', '.join(tag_names)}")
        else:
            self.detail_tags_label.setText("标签: 无")
        # ---

        # --- 显示图片预览 --- 
        if item.image_url and os.path.exists(item.image_url):
            try:
                logger.info(f"加载图片: {item.image_url}")
                # 对于PNG格式（可能有透明背景），设置透明背景
                if item.image_url.lower().endswith('.png'):
                    pixmap = QPixmap(item.image_url)
                    if not pixmap.isNull():
                        # 为透明图片设置棋盘格背景
                        self.detail_image_label.setStyleSheet(f"""
                            QLabel {{
                                background-color: white;
                                border: 1px solid black;
                                background-image: url({TRANSPARENT_BG_PATH.replace('\\', '/')});
                                background-repeat: repeat;
                            }}
                        """)
                        # 缩放图片
                        scaled_pixmap = pixmap.scaled(
                            self.detail_image_label.size() * 0.95,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.detail_image_label.setPixmap(scaled_pixmap)
                        return
                
                # 处理普通图片
                pixmap = QPixmap(item.image_url)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.detail_image_label.size() * 0.95,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.detail_image_label.setPixmap(scaled_pixmap)
                    self.detail_image_label.setStyleSheet("border: 1px solid black;")
                    return # 成功加载图片后返回
                else:
                    logger.warning(f"无法加载图片: {item.image_url}")
            except Exception as e:
                logger.error(f"显示图片时发生错误: {str(e)}", exc_info=True)
                 
        # 如果没有图片或加载失败，显示默认状态
        self.detail_image_label.setText("无图片或加载失败")
        self.detail_image_label.setStyleSheet("border: 1px dashed #ccc; color: #aaa;")
        # ---

    def clear_details(self):
         """清空右侧详情区"""
         self.detail_image_label.setText("图片预览")
         self.detail_image_label.setStyleSheet("border: 1px dashed #ccc; color: #aaa;")
         self.detail_image_label.setPixmap(QPixmap()) # 清除图片
         self.detail_name_label.setText("名称: -")
         self.detail_category_label.setText("分类: -") 
         self.detail_color_label.setText("颜色: -")
         self.detail_size_label.setText("尺码: -")
         self.detail_brand_label.setText("品牌: -")
         self.detail_material_label.setText("材质: -")
         self.detail_purchase_date_label.setText("购买日期: -")
         self.detail_price_label.setText("价格: -")
         self.detail_description_label.setText("描述: -")
         self.detail_tags_label.setText("标签: -")
         self.detail_favorite_label.setText("收藏: 否") 

    def on_add_clothing(self):
        """添加衣物"""
        dialog = AddClothingDialog(self)
        if dialog.exec():
            # 获取衣物数据
            data = dialog.get_clothing_data()
            print("添加衣物:", data) 