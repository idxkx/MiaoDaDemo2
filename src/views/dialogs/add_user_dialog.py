# src/views/dialogs/add_user_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QLabel, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from typing import Optional
import uuid # 需要导入 uuid 来生成 ID

# 导入 User 实体用于类型提示和创建
from src.domain.model.entities import User

class AddUserDialog(QDialog):
    """添加新用户的对话框"""

    def __init__(self, existing_usernames: list[str], parent=None):
        super().__init__(parent)
        self.existing_usernames = existing_usernames # 用于检查用户名是否重复
        self.setWindowTitle("添加新用户")
        self.setMinimumWidth(350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 用户名 (必填)
        self.username_input = QLineEdit()
        form_layout.addRow("用户名*:", self.username_input)

        # 密码 (必填, 暂时明文，实际应用需加密)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("密码*:", self.password_input)

        # 昵称 (可选, 默认为用户名)
        self.nickname_input = QLineEdit()
        form_layout.addRow("昵称:", self.nickname_input)

        # 邮箱 (可选)
        self.email_input = QLineEdit()
        form_layout.addRow("邮箱:", self.email_input)

        # 性别 (可选)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["未设置", "男", "女", "其他"])
        form_layout.addRow("性别:", self.gender_combo)

        # 生日 (可选)
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_edit.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
        # 设置一个非特定日期作为空/默认值
        self.birth_date_edit.setDate(QDate(1900, 1, 1))
        self.birth_date_edit.setSpecialValueText(" ") # 显示为空白而不是日期
        form_layout.addRow("生日:", self.birth_date_edit)

        # 头像 URL (可选)
        self.avatar_url_input = QLineEdit()
        form_layout.addRow("头像URL:", self.avatar_url_input)

        layout.addLayout(form_layout)

        # OK 和 Cancel 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        """处理点击 OK 按钮，进行数据验证"""
        username = self.username_input.text().strip()
        password = self.password_input.text() # 密码通常不 strip
        email = self.email_input.text().strip()

        # --- 基本验证 ---
        if not username:
            QMessageBox.warning(self, "输入错误", "用户名不能为空。")
            return
        if not password:
            QMessageBox.warning(self, "输入错误", "密码不能为空。")
            return
        if username in self.existing_usernames:
            QMessageBox.warning(self, "输入错误", f"用户名 '{username}' 已存在。")
            return
        if email and "@" not in email:
             QMessageBox.warning(self, "输入错误", "请输入有效的邮箱地址。")
             return
        # --- 验证结束 ---

        # 验证通过，接受对话框
        super().accept()

    def get_new_user_data(self) -> dict:
        """获取对话框中输入的新用户信息"""
        nickname = self.nickname_input.text().strip()
        # 如果昵称为空，则默认使用用户名
        if not nickname:
            nickname = self.username_input.text().strip()

        gender = self.gender_combo.currentText()
        birth_date_qdate = self.birth_date_edit.date()
        # 检查是否为我们设置的默认/空值日期
        birth_date_obj = birth_date_qdate.toPyDate() if birth_date_qdate.isValid() and birth_date_qdate != QDate(1900, 1, 1) else None

        # --- 重要：密码处理 ---
        # 在真实应用中，这里应该对 password 进行哈希处理
        # password_hash = hash_password(self.password_input.text())
        # 目前我们暂时直接存储（非常不安全！）或用一个占位符
        password_hash = "hashed_" + self.password_input.text() # 极简占位符

        return {
            "id": uuid.uuid4(), # 生成新的 UUID
            "username": self.username_input.text().strip(),
            "password_hash": password_hash,
            "nickname": nickname or None,
            "email": self.email_input.text().strip() or None,
            "gender": gender if gender != "未设置" else None,
            "birth_date": birth_date_obj,
            "avatar_url": self.avatar_url_input.text().strip() or None
        } 