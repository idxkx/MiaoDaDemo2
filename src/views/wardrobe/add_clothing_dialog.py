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
    QTextEdit,
    QProgressDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QDateEdit,
    QDialogButtonBox,
    QCheckBox,
    QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSettings
from PyQt6.QtGui import QPixmap, QIcon
import asyncio
import os
import logging
import json

from ..dialogs.base_dialog import BaseDialog
from src.utils.image_processor import (
    process_clothing_image,
    ImageProcessingError,
    ImageLoadError,
    BackgroundRemovalError,
    ColorExtractionError
)

logger = logging.getLogger(__name__)

class ImageProcessThread(QThread):
    """图片处理线程"""
    finished = pyqtSignal(str, list)  # 发送处理后的图片路径和颜色列表
    error = pyqtSignal(str)  # 发送错误信息
    progress = pyqtSignal(str, int)  # 发送进度信息和百分比
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self._is_cancelled = False
        self._loop = None
        self._cancel_event = asyncio.Event()
        logger.info(f"创建图片处理线程，处理图片：{image_path}")
    
    def run(self):
        """运行图片处理任务"""
        try:
            # 创建事件循环
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # 处理图片
            logger.info("开始处理图片...")
            
            # 设置输出目录
            output_dir = os.path.join("storage", "images", "processed")
            os.makedirs(output_dir, exist_ok=True)
            
            # 处理配置
            config = {
                'num_colors': 5,  # 提取5种主要颜色
                'min_size': (100, 100),
                'max_size': (4000, 4000),
                'quality': 90
            }
            
            # 处理图片
            no_bg_path, colors = self._loop.run_until_complete(
                process_clothing_image(
                    self.image_path,
                    progress_callback=self._update_progress,
                    cancellation_token=self._cancel_event,
                    output_dir=output_dir,
                    config=config
                )
            )
            
            # 检查是否被取消
            if self._is_cancelled:
                logger.info("图片处理已被取消")
                return
            
            # 发送结果
            self.finished.emit(no_bg_path, colors)
            
        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}", exc_info=True)
            error_message = str(e)
            if isinstance(e, ImageLoadError):
                error_message = f"无法加载图片: {str(e)}"
            elif isinstance(e, BackgroundRemovalError):
                error_message = f"背景移除失败: {str(e)}"
            elif isinstance(e, ColorExtractionError):
                error_message = f"颜色提取失败: {str(e)}"
            elif isinstance(e, ValueError):
                error_message = str(e)
            else:
                error_message = f"处理图片时出错: {str(e)}"
            self.error.emit(error_message)
        finally:
            self._cleanup()
    
    def _update_progress(self, message: str, value: int):
        """更新进度"""
        self.progress.emit(message, value)
    
    def cancel(self):
        """取消处理任务"""
        logger.info("请求取消图片处理")
        self._is_cancelled = True
        self._cancel_event.set()
        if self._loop and self._loop.is_running():
            self._loop.stop()
    
    def _cleanup(self):
        """清理资源"""
        try:
            # 关闭事件循环
            if self._loop:
                if self._loop.is_running():
                    self._loop.stop()
                self._loop.close()
                self._loop = None
        except Exception as e:
            logger.error(f"清理资源时出错: {str(e)}")

class ProcessingPreferencesDialog(BaseDialog):
    """图片处理偏好设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("处理偏好设置")
        self.setModal(True)
        
        # 加载当前设置
        self.settings = QSettings("MiaoDao", "WardrobeManager")
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 图片处理选项
        processing_group = QGroupBox("图片处理选项")
        processing_layout = QFormLayout()
        
        # 颜色数量
        self.color_count = QSpinBox()
        self.color_count.setRange(1, 10)
        self.color_count.setValue(self.settings.value("processing/color_count", 5, int))
        processing_layout.addRow("提取颜色数量:", self.color_count)
        
        # 图片质量
        self.image_quality = QSpinBox()
        self.image_quality.setRange(60, 100)
        self.image_quality.setValue(self.settings.value("processing/image_quality", 90, int))
        processing_layout.addRow("图片质量:", self.image_quality)
        
        # 自动处理选项
        self.auto_process = QCheckBox("选择图片后自动开始处理")
        self.auto_process.setChecked(self.settings.value("processing/auto_process", True, bool))
        processing_layout.addRow(self.auto_process)
        
        # 大图片警告
        self.warn_large_images = QCheckBox("处理大图片时显示警告")
        self.warn_large_images.setChecked(self.settings.value("processing/warn_large_images", True, bool))
        processing_layout.addRow(self.warn_large_images)
        
        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """保存设置"""
        self.settings.setValue("processing/color_count", self.color_count.value())
        self.settings.setValue("processing/image_quality", self.image_quality.value())
        self.settings.setValue("processing/auto_process", self.auto_process.isChecked())
        self.settings.setValue("processing/warn_large_images", self.warn_large_images.isChecked())
        self.accept()

class AddClothingDialog(BaseDialog):
    """添加衣物对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("初始化添加衣物对话框")
        self.setWindowTitle("添加衣物")
        self.setModal(True)
        
        # 加载设置
        self.settings = QSettings("MiaoDao", "WardrobeManager")
        
        # 初始化变量
        self.processed_image_path = None
        self.detected_colors = None
        self.process_thread = None
        self.original_image_path = None
        self.progress_dialog = None
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 图片预览区域
        image_layout = QHBoxLayout()
        
        # 原图预览
        original_group = QGroupBox("原图")
        original_layout = QVBoxLayout()
        self.original_preview = QLabel()
        self.original_preview.setFixedSize(200, 200)
        self.original_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_preview.setStyleSheet("border: 1px dashed #ccc;")
        self.original_preview.setText("原图预览")
        original_layout.addWidget(self.original_preview)
        original_group.setLayout(original_layout)
        image_layout.addWidget(original_group)
        
        # 处理后预览
        processed_group = QGroupBox("去背景")
        processed_layout = QVBoxLayout()
        self.processed_preview = QLabel()
        self.processed_preview.setFixedSize(200, 200)
        self.processed_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processed_preview.setStyleSheet("border: 1px dashed #ccc;")
        self.processed_preview.setText("去背景预览")
        processed_layout.addWidget(self.processed_preview)
        processed_group.setLayout(processed_layout)
        image_layout.addWidget(processed_group)
        
        # 图片操作按钮
        button_layout = QVBoxLayout()
        
        # 选择图片按钮
        upload_btn = QPushButton("选择图片")
        upload_btn.setIcon(QIcon.fromTheme("document-open"))
        upload_btn.clicked.connect(self.on_image_selected)
        button_layout.addWidget(upload_btn)
        
        # 处理图片按钮
        self.process_btn = QPushButton("处理图片")
        self.process_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        # 设置按钮
        settings_btn = QPushButton("处理设置")
        settings_btn.setIcon(QIcon.fromTheme("preferences-system"))
        settings_btn.clicked.connect(self.show_preferences)
        button_layout.addWidget(settings_btn)
        
        # 添加弹性空间
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        image_layout.addLayout(button_layout)
        layout.addLayout(image_layout)
        
        # 表单区域
        form_layout = QFormLayout()
        
        # 名称
        self.name_input = QLineEdit()
        form_layout.addRow("名称:", self.name_input)
        
        # 分类
        self.category_combo = QComboBox()
        self.category_combo.addItems(["上衣", "裤子", "裙子", "外套", "连体服"])
        form_layout.addRow("分类:", self.category_combo)
        
        # 子分类
        self.subcategory_combo = QComboBox()
        form_layout.addRow("子分类:", self.subcategory_combo)
        
        # 颜色选择和预览
        color_layout = QHBoxLayout()
        self.color_combo = QComboBox()
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 20)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 3px;")
        color_layout.addWidget(self.color_combo)
        color_layout.addWidget(self.color_preview)
        form_layout.addRow("颜色:", color_layout)
        
        # 尺码
        self.size_combo = QComboBox()
        self.size_combo.addItems(["XS", "S", "M", "L", "XL", "XXL"])
        form_layout.addRow("尺码:", self.size_combo)
        
        # 季节
        self.season_combo = QComboBox()
        self.season_combo.addItems(["春季", "夏季", "秋季", "冬季", "四季"])
        form_layout.addRow("季节:", self.season_combo)
        
        # 品牌
        self.brand_input = QLineEdit()
        form_layout.addRow("品牌:", self.brand_input)
        
        # 材质
        self.material_input = QLineEdit()
        form_layout.addRow("材质:", self.material_input)
        
        # 购买日期
        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        form_layout.addRow("购买日期:", self.purchase_date)
        
        # 价格
        self.price_input = QSpinBox()
        self.price_input.setRange(0, 99999)
        form_layout.addRow("价格:", self.price_input)
        
        # 描述
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        form_layout.addRow("描述:", self.desc_input)
        
        layout.addLayout(form_layout)
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # 连接信号
        self.category_combo.currentIndexChanged.connect(self.update_subcategories)
        self.color_combo.currentIndexChanged.connect(self.update_color_preview)
        
        # 初始化子分类
        self.update_subcategories(0)
        
        # 信号定义
        self.image_selected_for_recognition = pyqtSignal(str)
        
    def update_subcategories(self, index):
        """更新子分类选项"""
        self.subcategory_combo.clear()
        if self.category_combo.currentText() == "上衣":
            self.subcategory_combo.addItems(["T恤", "衬衫", "毛衣"])
        elif self.category_combo.currentText() == "裤子":
            self.subcategory_combo.addItems(["牛仔裤", "休闲裤", "短裤"])
        elif self.category_combo.currentText() == "裙子":
            self.subcategory_combo.addItems(["连衣裙", "半身裙", "短裙"])
        elif self.category_combo.currentText() == "外套":
            self.subcategory_combo.addItems(["夹克", "大衣", "风衣"])
        elif self.category_combo.currentText() == "连体服":
            self.subcategory_combo.addItems(["连体衣", "连体裤", "连体裙"])
    
    def on_image_selected(self):
        """处理图片选择"""
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(
            self,
            "选择衣物图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if image_path:
            logger.info(f"用户选择了图片: {image_path}")
            
            # 保存原始图片路径
            self.original_image_path = image_path
            
            # 显示原图预览
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logger.error(f"无法加载图片: {image_path}")
                QMessageBox.warning(self, "错误", "无法加载所选图片")
                return
            
            # 检查图片大小
            file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
            if file_size > 5 and self.settings.value("processing/warn_large_images", True, bool):
                response = QMessageBox.warning(
                    self,
                    "大图片警告",
                    f"所选图片较大 ({file_size:.1f}MB)，处理可能需要较长时间。是否继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if response == QMessageBox.StandardButton.No:
                    return
                
            scaled_pixmap = pixmap.scaled(
                200,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.original_preview.setPixmap(scaled_pixmap)
            self.original_preview.setToolTip(image_path)
            
            # 启用处理按钮
            self.process_btn.setEnabled(True)
            
            # 如果设置了自动处理，开始处理
            if self.settings.value("processing/auto_process", True, bool):
                self.start_processing()
        else:
            logger.info("用户取消了图片选择")
    
    def start_processing(self):
        """开始处理图片"""
        if not self.original_image_path:
            return
            
        # 创建进度对话框
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setWindowTitle("处理图片")
        self.progress_dialog.setLabelText("准备处理...")
        self.progress_dialog.setRange(0, 100)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setAutoClose(False)
        
        # 自定义取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.cancel_processing)
        self.progress_dialog.setCancelButton(cancel_button)
        
        # 启动图片处理线程
        logger.info("启动图片处理线程")
        self.process_thread = ImageProcessThread(self.original_image_path)
        self.process_thread.finished.connect(self.on_image_processed)
        self.process_thread.error.connect(self.on_process_error)
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.start()
        
        # 禁用处理按钮
        self.process_btn.setEnabled(False)
    
    def update_progress(self, message: str, value: int):
        """更新进度对话框"""
        if self.progress_dialog:
            self.progress_dialog.setLabelText(message)
            self.progress_dialog.setValue(value)
            
            # 添加详细信息
            if value == 20:
                self.progress_dialog.setLabelText(f"{message}\n正在使用AI模型分析图片...")
            elif value == 60:
                self.progress_dialog.setLabelText(f"{message}\n正在进行颜色聚类分析...")
            
            if value >= 100:
                self.progress_dialog.close()
                self.progress_dialog = None
                # 重新启用处理按钮
                self.process_btn.setEnabled(True)
    
    def on_process_error(self, error_message: str):
        """处理图片处理错误"""
        logger.error(f"图片处理错误: {error_message}")
        
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # 显示友好的错误提示
        error_title = "处理错误"
        if "太大" in error_message:
            error_title = "图片太大"
        elif "不支持的格式" in error_message:
            error_title = "格式不支持"
        elif "无法加载" in error_message:
            error_title = "加载失败"
        
        QMessageBox.warning(self, error_title, error_message)
        
        # 清理预览
        self.processed_preview.clear()
        self.processed_preview.setText("去背景预览")
        
        # 重置颜色选择
        self.color_combo.clear()
        self.color_preview.setStyleSheet("background: none; border: 1px solid #ccc;")
        
        # 重新启用处理按钮
        self.process_btn.setEnabled(True)
    
    def get_processing_config(self) -> dict:
        """获取处理配置"""
        return {
            'num_colors': self.settings.value("processing/color_count", 5, int),
            'quality': self.settings.value("processing/image_quality", 90, int),
            'min_size': (100, 100),
            'max_size': (4000, 4000),
            'allowed_formats': ['jpg', 'jpeg', 'png', 'bmp']
        }
    
    def on_image_processed(self, processed_path, colors):
        """处理完成的回调"""
        try:
            print(f"图片处理完成回调：\n- 处理后路径：{processed_path}\n- 识别颜色：{colors}")
            
            # 保存处理后的图片路径
            self.processed_image_path = processed_path
            self.detected_colors = colors
            
            # 显示处理后的图片
            if not os.path.exists(processed_path):
                raise FileNotFoundError(f"处理后的图片文件不存在：{processed_path}")
                
            pixmap = QPixmap(processed_path)
            if pixmap.isNull():
                raise ValueError(f"无法加载处理后的图片：{processed_path}")
                
            scaled_pixmap = pixmap.scaled(
                200,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.processed_preview.setPixmap(scaled_pixmap)
            
            # 更新颜色选项
            self.color_combo.clear()
            for color_name, hex_code, percentage in colors:
                # 添加颜色选项，显示名称和占比
                display_text = f"{color_name} ({percentage:.1f}%)"
                self.color_combo.addItem(display_text)
                # 存储hex_code作为用户数据
                self.color_combo.setItemData(
                    self.color_combo.count() - 1,
                    hex_code,
                    Qt.ItemDataRole.UserRole
                )
            
            # 选择第一个颜色
            if self.color_combo.count() > 0:
                self.color_combo.setCurrentIndex(0)
                self.update_color_preview(0)
                
        except Exception as e:
            print(f"处理图片结果时出错：{str(e)}")
            QMessageBox.warning(self, "错误", f"处理图片结果时出错：{str(e)}")
    
    def update_color_preview(self, index):
        """更新颜色预览"""
        try:
            if index >= 0:
                hex_code = self.color_combo.itemData(index, Qt.ItemDataRole.UserRole)
                if hex_code:
                    print(f"更新颜色预览：{hex_code}")
                    self.color_preview.setStyleSheet(f"""
                        QLabel {{
                            background: {hex_code};
                            border: 1px solid #ccc;
                            border-radius: 3px;
                            padding: 2px;
                        }}
                    """)
                else:
                    print(f"警告：颜色索引 {index} 没有关联的颜色代码")
            else:
                print(f"警告：无效的颜色索引 {index}")
        except Exception as e:
            print(f"更新颜色预览时出错：{str(e)}")
            
    def cancel_processing(self):
        """取消图片处理"""
        if self.process_thread and self.process_thread.isRunning():
            logger.info("用户取消了图片处理")
            self.process_thread.cancel()
            self.process_thread.wait()  # 等待线程结束
            self.progress_dialog.close()
            self.progress_dialog = None
            QMessageBox.information(self, "已取消", "图片处理已取消")
    
    def show_preferences(self):
        """显示偏好设置对话框"""
        dialog = ProcessingPreferencesDialog(self)
        if dialog.exec():
            logger.info("用户更新了处理偏好设置")
    
    def get_clothing_data(self) -> dict:
        """获取衣物数据"""
        try:
            logger.info("正在收集衣物数据")
            
            # 获取并验证名称
            name = self.name_input.text().strip()
            if not name:
                logger.warning("衣物名称为空，使用默认名称")
                name = "未命名衣物"
            
            # 获取分类信息
            category = self.category_combo.currentText()
            subcategory = self.subcategory_combo.currentText()
            
            # 获取颜色信息
            color_data = {"name": "未知", "hex_code": "#000000"}
            color_index = self.color_combo.currentIndex()
            if color_index >= 0:
                color_text = self.color_combo.currentText()
                color_name = color_text.split(' (')[0] if ' (' in color_text else color_text
                color_hex = self.color_combo.itemData(color_index, Qt.ItemDataRole.UserRole)
                if color_hex:
                    color_data = {
                        "name": color_name,
                        "hex_code": color_hex
                    }
                    logger.debug(f"已获取颜色信息: {color_data}")
                else:
                    logger.warning(f"颜色索引 {color_index} 没有关联的颜色代码，使用默认值")
            else:
                logger.warning("没有选择颜色，使用默认值")
            
            # 获取尺码信息
            size = self.size_combo.currentText()
            if not size:
                logger.warning("尺码为空，使用默认值 'M'")
                size = "M"
            
            # 获取品牌信息
            brand = self.brand_input.text().strip()
            
            # 获取材质信息
            material = self.material_input.text().strip()
            
            # 获取购买日期
            purchase_date = self.purchase_date.date().toString("yyyy-MM-dd")
            if purchase_date == self.purchase_date.minimumDate().toString("yyyy-MM-dd"):
                logger.debug("未设置购买日期，使用空值")
                purchase_date = ""
            
            # 获取价格
            price = self.price_input.value()
            
            # 获取描述
            description = self.desc_input.toPlainText().strip()
            
            # 验证图片路径
            if not self.processed_image_path:
                logger.warning("没有处理后的图片路径")
                if hasattr(self, 'original_image_path'):
                    logger.info("使用原始图片路径")
                    image_path = self.original_image_path
                else:
                    logger.warning("没有任何图片路径")
                    image_path = ""
            else:
                image_path = self.processed_image_path
            
            data = {
                "name": name,
                "category": category,
                "subcategory": subcategory,
                "color": color_data,
                "size": size,
                "season": self.season_combo.currentText(),
                "brand": brand,
                "material": material,
                "purchase_date": purchase_date,
                "price": price,
                "description": description,
                "image_path": image_path
            }
            
            logger.info(f"收集到的衣物数据: {data}")
            return data
            
        except Exception as e:
            logger.error(f"获取衣物数据时出错: {str(e)}", exc_info=True)
            # 返回默认值
            return {
                "name": "未命名衣物",
                "category": self.category_combo.currentText() or "未分类",
                "subcategory": self.subcategory_combo.currentText() or "",
                "color": {
                    "name": "未知",
                    "hex_code": "#000000"
                },
                "size": "M",
                "season": "四季",
                "brand": "",
                "material": "",
                "purchase_date": "",
                "price": 0,
                "description": "",
                "image_path": self.processed_image_path if hasattr(self, 'processed_image_path') else ""
            }

    def closeEvent(self, event):
        """关闭对话框时清理资源"""
        if self.process_thread and self.process_thread.isRunning():
            logger.info("关闭对话框，取消正在进行的处理")
            self.cancel_processing()
            self.process_thread.wait()
        event.accept() 