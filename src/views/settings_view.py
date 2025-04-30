# src/views/settings_view.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

# 定义 models 目录的相对路径 (根据实际情况调整)
MODELS_BASE_DIR = "models"
# 预定义的 LLM 服务商选项
LLM_PROVIDERS = ["None", "DeepSeek", "ChatGPT", "Ollama (Local)"]

class SettingsView(QWidget):
    """设置视图，用于配置模型"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_settings() # 加载现有设置

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20) # 添加边距，美观一些
        main_layout.setSpacing(15) # 组之间的间距

        # --- 服装识别模型设置 ---
        recognition_group = QGroupBox("服装识别模型设置")
        recognition_layout = QFormLayout(recognition_group)
        recognition_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows) # 自动换行

        self.recognition_model_combo = QComboBox()
        self.populate_recognition_models() # 填充下拉选项
        recognition_layout.addRow(QLabel("选择模型:"), self.recognition_model_combo)

        main_layout.addWidget(recognition_group)
        # --- 服装识别模型设置结束 ---

        # --- 穿搭生成模型 (LLM) 设置 ---
        llm_group = QGroupBox("穿搭生成模型 (LLM) 设置")
        llm_layout = QFormLayout(llm_group)
        llm_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(LLM_PROVIDERS)
        self.llm_provider_combo.currentIndexChanged.connect(self.on_llm_provider_changed) # 选择变化时更新界面
        llm_layout.addRow(QLabel("选择服务商:"), self.llm_provider_combo)

        # API Key 输入 (默认隐藏)
        self.llm_api_key_label = QLabel("API Key:")
        self.llm_api_key_input = QLineEdit()
        self.llm_api_key_input.setEchoMode(QLineEdit.EchoMode.Password) # 密码模式
        llm_layout.addRow(self.llm_api_key_label, self.llm_api_key_input)

        # 模型名称/Endpoint 输入 (默认隐藏)
        self.llm_endpoint_label = QLabel("模型/Endpoint:")
        self.llm_endpoint_input = QLineEdit()
        llm_layout.addRow(self.llm_endpoint_label, self.llm_endpoint_input)

        # 根据默认选项初始化字段可见性
        self.on_llm_provider_changed(0)

        main_layout.addWidget(llm_group)
        # --- 穿搭生成模型 (LLM) 设置结束 ---

        # --- 保存按钮 ---
        self.save_button = QPushButton("保存设置")
        self.save_button.setFixedWidth(120) # 固定宽度
        self.save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        # --- 保存按钮结束 ---

        # 添加伸缩项，让内容居中向上
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def populate_recognition_models(self):
        """扫描 models 目录并填充服装识别模型下拉菜单"""
        self.recognition_model_combo.clear()
        self.recognition_model_combo.addItem("None") # 提供不使用模型的选项
        try:
            if os.path.isdir(MODELS_BASE_DIR):
                # 获取 models 目录下的所有子文件夹名称
                models = [d for d in os.listdir(MODELS_BASE_DIR)
                          if os.path.isdir(os.path.join(MODELS_BASE_DIR, d))]
                if models:
                    self.recognition_model_combo.addItems(sorted(models))
            else:
                print(f"警告: 模型目录 '{MODELS_BASE_DIR}' 未找到。")
        except Exception as e:
            print(f"错误: 扫描模型目录时出错: {e}")
            # 可以在这里弹窗提示用户
            # QMessageBox.warning(self, "扫描模型错误", f"无法扫描模型目录 '{MODELS_BASE_DIR}':\n{e}")
            pass # 暂时忽略界面上的错误弹窗

    def on_llm_provider_changed(self, index):
        """当 LLM 服务商选择变化时，更新相关输入字段的可见性和标签"""
        provider = self.llm_provider_combo.itemText(index)

        # 先重置所有相关字段状态
        self.llm_api_key_label.setVisible(False)
        self.llm_api_key_input.setVisible(False)
        self.llm_endpoint_label.setVisible(False)
        self.llm_endpoint_input.setVisible(False)

        # 根据选择的服务商显示必要的字段
        if provider == "DeepSeek" or provider == "ChatGPT":
            self.llm_api_key_label.setText("API Key:")
            self.llm_api_key_label.setVisible(True)
            self.llm_api_key_input.setVisible(True)
            self.llm_endpoint_label.setText("模型名称 (可选):")
            self.llm_endpoint_label.setVisible(True)
            self.llm_endpoint_input.setVisible(True)
        elif provider == "Ollama (Local)":
            # Ollama 通常不需要 API Key，但需要指定模型名称
            self.llm_endpoint_label.setText("模型名称:")
            self.llm_endpoint_label.setVisible(True)
            self.llm_endpoint_input.setVisible(True)
        # elif provider == "None":
            # 不需要显示任何额外字段
            # pass

    def load_settings(self):
        """加载已保存的设置 (现在是占位符)"""
        # 在实际应用中，这里会从配置文件（如 settings.json 或 .env 文件）读取设置
        print("SettingsView: 正在加载设置 (占位符)...")
        # 暂时设置为默认值
        self.recognition_model_combo.setCurrentText("None")
        self.llm_provider_combo.setCurrentText("None")
        self.llm_api_key_input.clear()
        self.llm_endpoint_input.clear()
        self.on_llm_provider_changed(self.llm_provider_combo.currentIndex()) # 更新界面

    def save_settings(self):
        """保存当前设置 (现在是占位符)"""
        # 在实际应用中，这里会将设置写入配置文件
        selected_recognition_model = self.recognition_model_combo.currentText()
        selected_llm_provider = self.llm_provider_combo.currentText()
        api_key = self.llm_api_key_input.text() if self.llm_api_key_input.isVisible() else ""
        endpoint = self.llm_endpoint_input.text() if self.llm_endpoint_input.isVisible() else ""

        print("SettingsView: 正在保存设置 (占位符)...")
        print(f"  服装识别模型: {selected_recognition_model}")
        print(f"  穿搭生成 LLM: {selected_llm_provider}")
        if api_key:
            print(f"  API Key: {'*' * len(api_key)}")
        if endpoint:
             print(f"  模型/Endpoint: {endpoint}")

        # 这里可以加入实际的保存逻辑，例如写入 JSON 文件
        # config = {
        #     "recognition_model": selected_recognition_model,
        #     "llm_provider": selected_llm_provider,
        #     "llm_api_key": api_key, # 注意：实际应用中 API Key 需要更安全地存储
        #     "llm_endpoint": endpoint
        # }
        # import json
        # try:
        #     with open("settings.json", "w") as f:
        #         json.dump(config, f, indent=4)
        # except Exception as e:
        #     QMessageBox.critical(self, "保存失败", f"无法保存设置: {e}")
        #     return

        QMessageBox.information(self, "设置已保存", "设置已保存（目前为占位符）。\n程序需要重新启动或重新加载才能应用这些更改。") 