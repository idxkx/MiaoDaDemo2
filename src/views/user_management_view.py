from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QInputDialog, QLabel,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal

# --- 新增：导入 User 和 uuid ---
import uuid
# --- 修改：将 datetime 导入移到顶部 ---
from datetime import datetime 
# ---
from src.domain.model.entities import User
# ---

# --- 新增：导入编辑对话框 ---
from .dialogs.edit_user_dialog import EditUserDialog
# ---

# --- 新增：导入添加对话框 ---
from .dialogs.add_user_dialog import AddUserDialog
# ---

class UserManagementView(QWidget):
    """用户管理视图 - 使用表格显示详细信息"""
    users_changed = pyqtSignal(list, User) # list[User], User | None

    def __init__(self, initial_users: list[User], current_user: User | None, parent=None):
        super().__init__(parent)
        self._users = initial_users[:]
        self._current_user = current_user
        # --- 修改：列定义 ---
        self.columns = ["昵称/用户名", "邮箱", "性别", "创建时间"] # 定义表格列
        self.column_map = { # 方便按名称引用列索引
            "display_name": 0,
            "email": 1,
            "gender": 2,
            "created_at": 3,
        }
        # ---
        self.init_ui()
        self.populate_user_table() # <--- 修改：调用新方法

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title_label = QLabel("用户管理")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()

        # --- 修改：创建 QTableWidget ---
        self.user_table_widget = QTableWidget()
        self.user_table_widget.setColumnCount(len(self.columns))
        self.user_table_widget.setHorizontalHeaderLabels(self.columns)
        self.user_table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # 整行选择
        self.user_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection) # 单选
        self.user_table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # 禁止直接编辑表格
        self.user_table_widget.verticalHeader().setVisible(False) # 隐藏行号
        # 设置列宽自动调整
        header = self.user_table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # 所有列平均伸展
        header.setStretchLastSection(True) # 最后一列填充剩余空间 (可选)
        content_layout.addWidget(self.user_table_widget, stretch=1)
        # ---

        # --- 按钮布局保持不变 ---
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.add_button = QPushButton("添加用户")
        self.add_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_button)
        self.edit_button = QPushButton("编辑用户")
        self.edit_button.clicked.connect(self.edit_user)
        button_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton("删除用户")
        self.delete_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        content_layout.addLayout(button_layout)
        # ---

        main_layout.addLayout(content_layout, stretch=1)
        self.setLayout(main_layout)

    # --- 修改：重命名并实现 populate_user_table ---
    def populate_user_table(self):
        """用当前用户列表填充 QTableWidget"""
        self.user_table_widget.setRowCount(0) # 清空表格
        self.user_table_widget.setRowCount(len(self._users))

        for row, user in enumerate(self._users):
            display_name = user.nickname if user.nickname else user.username
            email = user.email if user.email else "-"
            gender = user.gender if user.gender else "-"
            created_at_str = user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else "-" # 格式化时间

            # 创建表格项
            item_name = QTableWidgetItem(display_name)
            item_email = QTableWidgetItem(email)
            item_gender = QTableWidgetItem(gender)
            item_created = QTableWidgetItem(created_at_str)

            # --- 重要：将 User 对象存储在第一列的 UserRole 中 ---
            item_name.setData(Qt.ItemDataRole.UserRole, user)

            # 设置单元格内容居中 (可选)
            # item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # item_email.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # ...

            # 填充表格行
            self.user_table_widget.setItem(row, self.column_map["display_name"], item_name)
            self.user_table_widget.setItem(row, self.column_map["email"], item_email)
            self.user_table_widget.setItem(row, self.column_map["gender"], item_gender)
            self.user_table_widget.setItem(row, self.column_map["created_at"], item_created)

            # 标记当前用户 (例如设置行背景色)
            if self._current_user and user.id == self._current_user.id:
                for col in range(self.user_table_widget.columnCount()):
                    item = self.user_table_widget.item(row, col)
                    if item:
                        # 设置背景色来高亮当前用户行 (颜色可以调整)
                        item.setBackground(Qt.GlobalColor.lightGray)

        # self.user_table_widget.resizeColumnsToContents() # 调整列宽适应内容 (如果上面没用 Stretch)
    # ---

    def add_user(self):
        """添加新用户"""
        # --- 修改：使用 AddUserDialog ---
        existing_usernames = [u.username for u in self._users]
        dialog = AddUserDialog(existing_usernames, self)
        if dialog.exec(): # 如果用户点击 OK 并且验证通过
            new_user_data = dialog.get_new_user_data()

            # --- 修改：使用完整数据创建 User 对象 ---
            # 注意：这里直接使用了字典解包，需要确保 User 的 __init__ 能接受这些参数
            # 或者显式地传递每个参数
            try:
                 # 处理 birth_date 可能需要转换回 datetime
                 birth_date = None
                 if new_user_data["birth_date"]:
                     # from datetime import datetime # <--- 不再需要在这里导入
                     birth_date = datetime.combine(new_user_data["birth_date"], datetime.min.time())

                 new_user = User(
                     id=new_user_data["id"],
                     username=new_user_data["username"],
                     email=new_user_data["email"],
                     password_hash=new_user_data["password_hash"],
                     nickname=new_user_data["nickname"],
                     avatar_url=new_user_data["avatar_url"],
                     gender=new_user_data["gender"],
                     birth_date=birth_date
                 )
                 self._users.append(new_user)
                 self.populate_user_table() # 更新表格显示
                 self.users_changed.emit(self._users[:], self._current_user) # 通知主窗口
            except Exception as e:
                 # 捕获创建 User 对象时可能发生的错误
                 print(f"创建新用户时出错: {e}")
                 QMessageBox.critical(self, "错误", f"无法创建新用户：\n{e}")
            # ---
        # ---

    def edit_user(self):
        """编辑选中的用户"""
        selected_row = self.user_table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "未选择", "请先在表格中选择要编辑的用户行。")
            return

        item_with_data = self.user_table_widget.item(selected_row, self.column_map["display_name"])
        if not item_with_data:
             print("错误：无法获取表格项")
             return
        user_to_edit: User | None = item_with_data.data(Qt.ItemDataRole.UserRole)

        if not user_to_edit:
             print("错误：无法从表格项获取用户数据。")
             return

        # --- 修改：使用 EditUserDialog ---
        existing_usernames = [u.username for u in self._users]
        dialog = EditUserDialog(user_to_edit, existing_usernames, self)
        if dialog.exec(): # 如果用户点击 OK 并且验证通过
            updated_data = dialog.get_updated_user_data()

            # 更新 User 对象 (简化，直接修改属性)
            # 实际应用中应调用领域方法或应用服务来确保业务规则
            user_to_edit._nickname = updated_data["nickname"]
            user_to_edit._email = updated_data["email"] # 需要验证唯一性！
            user_to_edit._gender = updated_data["gender"]
            # 注意：birth_date 返回的是 date 对象，User 实体需要 datetime
            # 暂时忽略时间部分，或根据需要处理
            if updated_data["birth_date"]:
                 user_to_edit._birth_date = datetime.combine(updated_data["birth_date"], datetime.min.time())
            else:
                 user_to_edit._birth_date = None
            user_to_edit._avatar_url = updated_data["avatar_url"]
            user_to_edit._version += 1 # 增加版本号 (如果需要)
            user_to_edit._updated_at = datetime.now() # 更新时间

            self.populate_user_table() # 更新表格显示
            self.users_changed.emit(self._users[:], self._current_user) # 通知主窗口
        # ---

    def delete_user(self):
        """删除选中的用户"""
        selected_row = self.user_table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "未选择", "请先在表格中选择要删除的用户行。")
            return

        # --- 修改：从表格项获取 User 对象 ---
        item_with_data = self.user_table_widget.item(selected_row, self.column_map["display_name"])
        if not item_with_data:
            print("错误：无法获取表格项")
            return
        user_to_delete: User | None = item_with_data.data(Qt.ItemDataRole.UserRole)
        # ---

        if not user_to_delete:
            print("错误：无法从表格项获取用户数据进行删除。")
            return
        display_name_to_delete = user_to_delete.nickname if user_to_delete.nickname else user_to_delete.username

        if len(self._users) <= 1:
            QMessageBox.critical(self, "删除失败", "不能删除最后一个用户。")
            return

        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除用户 '{display_name_to_delete}' 吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self._users = [u for u in self._users if u.id != user_to_delete.id]
            new_current_user = self._current_user
            if self._current_user and user_to_delete.id == self._current_user.id:
                new_current_user = self._users[0] if self._users else None
                self._current_user = new_current_user

            self.populate_user_table() # <--- 修改：调用表格填充
            self.users_changed.emit(self._users[:], new_current_user)

    def update_view(self, users: list[User], current_user: User | None):
        """外部调用此方法来更新视图状态"""
        self._users = users[:]
        self._current_user = current_user
        self.populate_user_table() # <--- 修改：调用表格填充
    # --- 