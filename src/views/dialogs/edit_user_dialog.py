from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox,
    QComboBox, QLabel, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from typing import Optional

# --- 导入 User 实体 ---
from src.domain.model.entities import User
# ---

class EditUserDialog(QDialog):
    """编辑用户信息的对话框"""

    def __init__(self, user_to_edit: User, existing_usernames: list[str], parent=None):
        super().__init__(parent)
        self.user_to_edit = user_to_edit
        # 传入除当前编辑用户外的其他用户名列表，用于检查重复
        self.other_usernames = [name for name in existing_usernames if name != user_to_edit.username]
        self.setWindowTitle("编辑用户信息")
        self.setMinimumWidth(350)

        self.init_ui()
        self.populate_fields()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 用户名 (通常不允许直接修改，或需特殊处理，暂时设为只读)
        self.username_label = QLineEdit(self.user_to_edit.username)
        self.username_label.setReadOnly(True)
        self.username_label.setStyleSheet("background-color: #eee;") # 灰色背景提示只读
        form_layout.addRow("用户名:", self.username_label)

        # 昵称
        self.nickname_input = QLineEdit()
        form_layout.addRow("昵称:", self.nickname_input)

        # 邮箱
        self.email_input = QLineEdit()
        form_layout.addRow("邮箱:", self.email_input)

        # 性别
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["未设置", "男", "女", "其他"])
        form_layout.addRow("性别:", self.gender_combo)

        # 生日 (可选)
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        # 设置一个合理的日期范围，例如从1900年到今天
        self.birth_date_edit.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
        form_layout.addRow("生日:", self.birth_date_edit)

        # 头像 URL (暂时简单输入)
        self.avatar_url_input = QLineEdit()
        form_layout.addRow("头像URL:", self.avatar_url_input)


        layout.addLayout(form_layout)

        # OK 和 Cancel 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_fields(self):
        """用传入的用户数据填充对话框字段"""
        self.nickname_input.setText(self.user_to_edit.nickname or "")
        self.email_input.setText(self.user_to_edit.email or "")

        gender = self.user_to_edit.gender or "未设置"
        if gender in ["未设置", "男", "女", "其他"]:
             self.gender_combo.setCurrentText(gender)
        else:
             self.gender_combo.setCurrentText("未设置") # 处理未知值

        if self.user_to_edit.birth_date:
             # QDateEdit 需要 QDate 对象
             qdate = QDate(self.user_to_edit.birth_date.year,
                           self.user_to_edit.birth_date.month,
                           self.user_to_edit.birth_date.day)
             self.birth_date_edit.setDate(qdate)
        else:
             # 如果没有生日，可以设置一个默认日期或保持为空
             self.birth_date_edit.setDate(QDate(1990, 1, 1)) # 或其他默认值

        self.avatar_url_input.setText(self.user_to_edit.avatar_url or "")


    def accept(self):
        """处理点击 OK 按钮，进行数据验证"""
        # --- 数据验证 ---
        nickname = self.nickname_input.text().strip()
        email = self.email_input.text().strip()
        # 简单的邮箱格式验证 (可选，可以用正则表达式)
        if email and "@" not in email:
             QMessageBox.warning(self, "输入错误", "请输入有效的邮箱地址。")
             return

        # 其他验证可以加在这里...

        # 如果所有验证通过，则接受对话框
        super().accept()


    def get_updated_user_data(self) -> dict:
        """获取对话框中更新后的用户数据"""
        gender = self.gender_combo.currentText()
        birth_date_qdate = self.birth_date_edit.date()
        # 将 QDate 转换回 datetime.date 或 datetime.datetime 对象
        birth_date_obj = birth_date_qdate.toPyDate() if birth_date_qdate.isValid() and birth_date_qdate != QDate(1990, 1, 1) else None # 假设1990/1/1是默认/空值

        return {
            "nickname": self.nickname_input.text().strip() or None, # 空字符串转为 None
            "email": self.email_input.text().strip() or None,
            "gender": gender if gender != "未设置" else None,
            "birth_date": birth_date_obj,
            "avatar_url": self.avatar_url_input.text().strip() or None
        } 