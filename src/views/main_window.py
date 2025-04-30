from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QStatusBar,
    QMenuBar,
    QMenu,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, pyqtSlot, QThread
from PyQt6.QtGui import QAction, QIcon, QActionGroup, QCloseEvent

# --- 修改：导入 User 实体和 uuid ---
import uuid
from src.domain.model.entities import User
# ---

from .wardrobe.wardrobe_view import WardrobeView
from .settings_view import SettingsView
from .user_management_view import UserManagementView

# --- 新增导入 json, os, Path --- 
import json
import os
from pathlib import Path
# ---

# --- 新增：导入应用服务和命令 ---
from src.application.commands.wardrobe_commands import AddClothingCommand, AddTagToItemCommand
from src.application.services.wardrobe_service import WardrobeApplicationService, ApplicationException
from src.views.dialogs.add_clothing_dialog import AddClothingDialog
# ---

# --- 新增：导入 JSON 仓储实现 --- 
from src.infrastructure.persistence.json_wardrobe_repository import JsonWardrobeRepository
# ---

# --- 新增导入 AI 识别服务和 Worker ---
from src.application.services.recognition_service import ClothingRecognitionService, RecognitionWorker
# ---

# --- 创建简单的占位符视图 ---
class PlaceholderView(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(f"这里是 {text} 视图")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setStyleSheet("background-color: #eee;") # 给点背景色区分

# -----------------------------

# --- 定义用户数据文件路径 ---
STORAGE_DIR = Path("storage")
USERS_FILE = STORAGE_DIR / "users.json"
# ---

class MainWindow(QMainWindow):
    """主窗口类 - 使用 User 对象并持久化，并集成 AI 识别"""

    # --- 新增信号：识别完成 ---
    recognition_completed = pyqtSignal(dict)
    # ---

    def __init__(self):
        super().__init__()
        self.last_recognition_result: dict | None = None # 用于存储识别结果

        # --- 确保存储目录存在 ---
        self._ensure_storage_dir()
        # ---

        # --- 修改：加载用户数据 --- 
        self._users: list[User] = self._load_users()
        self.current_user: User | None = self._users[0] if self._users else None
        # ---

        # --- 新增：初始化识别服务 ---
        self.recognition_service = ClothingRecognitionService()
        # ---

        self.setWindowTitle("智能穿搭助手")
        self.setMinimumSize(1024, 768)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_menu_bar()
        self.create_navigation_panel()
        self.create_content_area()
        self.create_status_bar()

        self.nav_list.currentRowChanged.connect(self.on_navigation_changed)
        if self.current_user:
            self.update_user_display()
            self.nav_list.setCurrentRow(0)
        else:
            self.current_user_label.setText("无用户")

        if hasattr(self, 'user_management_view'):
             self.user_management_view.users_changed.connect(self.on_users_changed)
        else:
             print("错误：user_management_view 未在正确的时间实例化。")

        # --- 修改：连接 WardrobeView 的信号 --- 
        # 获取 WardrobeView 实例
        wardrobe_view_instance = self.nav_items.get("我的衣橱")
        if wardrobe_view_instance and isinstance(wardrobe_view_instance, WardrobeView):
             # 连接添加衣物请求信号
             wardrobe_view_instance.add_clothing_requested.connect(self.on_new_clothing)
             # 你也可以在这里连接 category_selected 或 item_selected 信号（如果需要）
             # wardrobe_view_instance.category_selected.connect(self.on_category_selected)
        # ---

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        try:
            STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"错误: 无法创建存储目录 '{STORAGE_DIR}': {e}")
            # 也许弹窗提示用户？

    def _load_users(self) -> list[User]:
        """从 JSON 文件加载用户列表"""
        if not USERS_FILE.exists():
            print("用户文件不存在，将使用默认用户列表。")
            # 返回默认用户列表 (如果需要)
            return [
                User(id=uuid.uuid4(), username="xiaoming", email="xm@example.com", password_hash="hash1", nickname="小明"),
                User(id=uuid.uuid4(), username="default", email="def@example.com", password_hash="hash4", nickname="默认用户"),
            ]
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                # 确保加载的是列表
                if isinstance(users_data, list):
                    loaded_users = [User.from_dict(data) for data in users_data]
                    print(f"成功从 {USERS_FILE} 加载了 {len(loaded_users)} 个用户。")
                    return loaded_users
                else:
                    print(f"错误: {USERS_FILE} 文件格式不正确（不是列表），将使用默认用户。")
                    return [User(id=uuid.uuid4(), username="default", email="def@example.com", password_hash="hash4", nickname="默认用户")]
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"错误: 加载用户文件 '{USERS_FILE}' 时出错: {e}")
            # 出错时也返回默认用户
            return [User(id=uuid.uuid4(), username="default", email="def@example.com", password_hash="hash4", nickname="默认用户")]

    def _save_users(self):
        """将当前用户列表保存到 JSON 文件"""
        try:
            users_data = [user.to_dict() for user in self._users]
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=4, ensure_ascii=False)
            print(f"用户数据已保存到 {USERS_FILE}")
        except Exception as e:
            print(f"错误: 保存用户文件 '{USERS_FILE}' 时出错: {e}")
            # 这里可以弹窗提示用户保存失败

    def create_menu_bar(self):
        """创建菜单栏 (精简版)"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def create_navigation_panel(self):
        """创建左侧导航面板 (包含用户切换和功能列表)"""
        nav_panel = QWidget()
        nav_panel.setFixedWidth(180)
        nav_panel.setStyleSheet("background-color: #f0f0f0; border: none;")

        panel_layout = QVBoxLayout(nav_panel)
        panel_layout.setContentsMargins(0, 10, 0, 0)
        panel_layout.setSpacing(0)

        # --- 用户切换区域 ---
        user_area = QWidget()
        user_layout = QHBoxLayout(user_area)
        user_layout.setContentsMargins(10, 0, 10, 10)

        # --- 修改：显示当前用户的昵称或用户名 ---
        current_display_name = self.current_user.nickname if self.current_user and self.current_user.nickname else (self.current_user.username if self.current_user else "无用户")
        self.current_user_label = QLabel(f"用户: {current_display_name}")
        # ---
        self.current_user_label.setStyleSheet("font-weight: bold;")
        user_layout.addWidget(self.current_user_label, stretch=1)

        self.switch_user_button = QPushButton("切换")
        self.switch_user_button.setFixedWidth(50)
        self.switch_user_button.clicked.connect(self.on_show_user_menu)
        user_layout.addWidget(self.switch_user_button)
        panel_layout.addWidget(user_area)
        # --- 用户切换区域结束 ---

        # --- 分隔线 ---
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #d0d0d0;")
        panel_layout.addWidget(separator)
        # --- 分隔线结束 ---

        # --- 功能导航列表 ---
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: none;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #d0d0d0;
                font-weight: bold;
                color: #333;
            }
            QListWidget::item:hover:!selected {
                background-color: #e8e8e8;
            }
        """)

        # --- 修改：实例化 UserManagementView 时传递 User 对象列表 ---
        self.user_management_view = UserManagementView(self._users, self.current_user)
        # ---

        self.nav_items = {
            "我的衣橱": WardrobeView(),
            "我的穿搭": PlaceholderView("我的穿搭"),
            "搭配推荐": PlaceholderView("搭配推荐"),
            "用户管理": self.user_management_view,
            "设置": SettingsView()
        }

        for name in self.nav_items.keys():
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.nav_list.addItem(item)

        panel_layout.addWidget(self.nav_list, stretch=1)
        # --- 功能导航列表结束 ---

        self.main_layout.addWidget(nav_panel)

    def create_content_area(self):
        """创建右侧主要内容区"""
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack, stretch=1)

        # <--- 修改：确保添加顺序与 nav_items 字典顺序一致 ---
        # Python 3.7+ 字典保持插入顺序，所以 values() 顺序是可靠的
        for view_key in self.nav_items:
             view_widget = self.nav_items[view_key]
             self.content_stack.addWidget(view_widget)
             # print(f"Adding widget for {view_key} at index {self.content_stack.count() - 1}") # 调试用

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def update_user_display(self):
        """更新侧边栏的用户标签"""
        # --- 修改：使用 User 对象更新显示 ---
        if self.current_user:
            display_name = self.current_user.nickname if self.current_user.nickname else self.current_user.username
            self.current_user_label.setText(f"用户: {display_name}")
        else:
            self.current_user_label.setText("无用户")
        # ---
        # print(f"当前用户已切换为: {display_name if self.current_user else 'None'}")

    def on_show_user_menu(self):
        """点击'切换'按钮时，显示用户选择菜单"""
        user_menu = QMenu(self)
        user_group = QActionGroup(self)
        user_group.setExclusive(True)
        local_user_actions = {} # 局部变量存储动作

        # --- 修改：基于 User 对象列表创建菜单项 ---
        for user in self._users:
            display_name = user.nickname if user.nickname else user.username
            action = QAction(display_name, self)
            action.setCheckable(True)
            action.setData(user) # <--- 存储 User 对象
            action.triggered.connect(self.on_switch_user)
            user_menu.addAction(action)
            user_group.addAction(action)
            local_user_actions[user.id] = action # 用 ID 索引
            if self.current_user and user.id == self.current_user.id:
                action.setChecked(True)
        # ---

        button_pos = self.switch_user_button.mapToGlobal(self.switch_user_button.rect().bottomLeft())
        user_menu.exec(button_pos)

    # --- 事件处理方法 ---

    def on_navigation_changed(self, index):
        """处理导航列表项切换"""
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            current_item_text = self.nav_list.item(index).text()
            self.status_bar.showMessage(f"已切换到: {current_item_text}")
            # --- 新增：如果切换到"我的衣橱"，加载内容 --- 
            if current_item_text == "我的衣橱":
                self._load_and_display_wardrobe()
            # ---

    def on_switch_user(self):
        """处理用户切换菜单的选项点击"""
        action = self.sender()
        if action and isinstance(action, QAction):
            selected_user: User = action.data()
            if selected_user and (not self.current_user or selected_user.id != self.current_user.id):
                self.current_user = selected_user
                self.update_user_display()
                self.user_management_view.update_view(self._users, self.current_user)
                display_name = self.current_user.nickname if self.current_user.nickname else self.current_user.username
                self.status_bar.showMessage(f"已切换到用户: {display_name}")
                # --- 新增：如果当前在衣橱视图，重新加载 --- 
                current_widget = self.content_stack.currentWidget()
                if isinstance(current_widget, WardrobeView):
                     print("用户已切换，重新加载衣橱...")
                     self._load_and_display_wardrobe()
                # ---

    def on_new_clothing(self):
        """处理添加新衣物的请求，打开对话框并连接 AI 识别信号，添加衣物后尝试添加 AI 标签"""
        if not self.current_user:
            QMessageBox.warning(self, "无用户", "请先选择或创建一个用户。")
            return

        dialog = AddClothingDialog(self)
        self.last_recognition_result = None # 重置上次结果

        dialog.image_selected_for_recognition.connect(self.handle_image_recognition_request)
        self.recognition_completed.connect(dialog.update_fields_from_recognition)
        
        self.current_recognition_thread = None
        self.current_recognition_worker = None

        if dialog.exec():
            data = dialog.get_clothing_data()
            print(f"Add Clothing Dialog Accepted. Data: {data}") # 调试信息

            # --- 修改：使用正确的参数名创建 Command，并处理日期 --- 
            from datetime import datetime # 确保导入
            purchase_date_obj = None
            purchase_date_str = data.get('purchase_date')
            if purchase_date_str:
                try:
                    purchase_date_obj = datetime.strptime(purchase_date_str, '%Y-%m-%d')
                except ValueError:
                    # 对话框验证时应该已经处理，这里可以记录警告或忽略
                    print(f"警告: 无法解析日期 '{purchase_date_str}', 将忽略购买日期。")
            
            command = AddClothingCommand(
                user_id=self.current_user.id,
                name=data['name'],
                category_name=data['category'],
                color_name=data['color'],
                size_value=data['size'],
                brand_name=data.get('brand') or "",
                material_name=data.get('material') or "",
                purchase_date=purchase_date_obj,
                price=data.get('price') or 0.0,
                description=data.get('description'),
                image_path=data.get('image_path')
            )
            # ---

            # 初始化仓储和应用服务
            repo = JsonWardrobeRepository()
            service = WardrobeApplicationService(repo)
            new_item_id = None # 用于存储新衣物的 ID

            try:
                # --- 修改：调用 add_clothing 并获取返回的 ID --- 
                # (假设 add_clothing 返回新项目的 ID，如果不是，需要修改服务)
                created_item = service.add_clothing(command) # 假设返回 ClothingItem 实例或 ID
                if hasattr(created_item, 'id'): # 如果返回的是对象
                     new_item_id = created_item.id
                elif isinstance(created_item, uuid.UUID): # 如果直接返回 ID
                     new_item_id = created_item
                else:
                     print("警告: WardrobeApplicationService.add_clothing 未按预期返回新项目的 ID，无法添加 AI 标签。")
                     # 即使没有 ID，也提示成功
                     QMessageBox.information(self, "成功", f"衣物 '{command.name}' 添加成功！(标签未添加)")
                     return # 提前返回，不执行标签逻辑
                     
                QMessageBox.information(self, "成功", f"衣物 '{command.name}' 添加成功！")
                # ---

                # --- 新增：衣物添加成功后，尝试添加 AI 标签 --- 
                if new_item_id and self.last_recognition_result and 'tag_category' in self.last_recognition_result:
                     print(f"尝试为新衣物 (ID: {new_item_id}) 添加 AI 类别标签...")
                     tag_command = AddTagToItemCommand(
                         item_id=new_item_id,
                         wardrobe_id=self.current_user.id, # 假设 wardrobe_id 就是 user_id
                         tag_name=self.last_recognition_result['tag_category'],
                         tag_category="AI识别类别" # 定义标签的类别
                     )
                     try:
                         # --- 取消注释，实际调用服务 --- 
                         service.add_tag_to_item(tag_command)
                         # ---
                         print(f"标签 '{tag_command.tag_name}' 已通过服务成功添加。")
                         self.status_bar.showMessage(f"AI 类别标签 '{tag_command.tag_name}' 已添加", 3000)
                     except AttributeError:
                          print("错误: WardrobeApplicationService 中缺少 add_tag_to_item 方法。") # 这个理论上不会发生了
                          self.status_bar.showMessage("AI 类别标签添加失败 (服务未实现)", 3000)
                     except Exception as tag_err:
                          print(f"错误: 添加 AI 标签时出错: {tag_err}")
                          self.status_bar.showMessage("AI 类别标签添加失败", 3000)
                # ---

                # --- 修改：添加成功后刷新衣橱视图 --- 
                print("衣物添加/标签处理完成，正在刷新衣橱视图...")
                self._load_and_display_wardrobe()
                # ---

            except ApplicationException as e:
                 QMessageBox.critical(self, "错误", f"添加衣物失败: {e}")
            except Exception as e: # 捕获其他意外错误
                 QMessageBox.critical(self, "严重错误", f"发生意外错误: {e}")
                 print(f"Unexpected error adding clothing: {e}") # 打印详细错误到控制台
        else:
             # --- 新增：如果用户取消对话框，尝试停止可能在运行的识别线程 ---
             self.stop_recognition_thread()
             # ---

        # --- 修改：在 finally 块中清理识别结果和线程 --- 
        self.last_recognition_result = None # 确保清理
        self.stop_recognition_thread() # 确保线程退出
        # 断开信号连接也最好放在 finally 中，以防 accept/reject 时出错
        try:
            dialog.image_selected_for_recognition.disconnect(self.handle_image_recognition_request)
        except TypeError:
            pass
        try:
            self.recognition_completed.disconnect(dialog.update_fields_from_recognition)
        except TypeError:
            pass
        # ---

    def on_import_clothing(self):
        """导入衣物 - 待实现"""
        self.status_bar.showMessage("导入衣物功能待实现")

    def on_about(self):
        """显示关于信息"""
        QMessageBox.about(self, "关于", "喵搭智能穿搭助手\n版本 1.0\n一个帮你管理衣橱的好帮手！")

    # --- 修改：处理来自 UserManagementView 的 User 对象列表 ---
    def on_users_changed(self, updated_users: list[User], new_current_user: User | None):
        """当用户管理视图中的用户列表或当前用户发生变化时调用"""
        print("MainWindow: 接收到 users_changed 信号 (User 对象)")
        self._users = updated_users[:]
        changed_current = False
        if self.current_user != new_current_user:
             self.current_user = new_current_user
             changed_current = True

        if changed_current:
             self.update_user_display()

        self.status_bar.showMessage("用户列表已更新")
    # ---

    # --- 新增：停止识别线程的方法 ---
    def stop_recognition_thread(self):
        if hasattr(self, 'current_recognition_thread') and self.current_recognition_thread and self.current_recognition_thread.isRunning():
            print("请求停止识别线程...")
            self.current_recognition_thread.quit() # 请求事件循环退出
            self.current_recognition_thread.wait(1000) # 等待最多1秒
            if self.current_recognition_thread.isRunning(): # 如果还在运行，强制终止
                 print("警告：识别线程未能正常退出，将强制终止。")
                 self.current_recognition_thread.terminate()
                 self.current_recognition_thread.wait()
            print("识别线程已停止。")
        self.current_recognition_thread = None
        self.current_recognition_worker = None
    # ---

    # --- 修改：处理图片识别请求的方法，使用后台线程 ---
    @pyqtSlot(str)
    def handle_image_recognition_request(self, image_path: str):
        """
        接收信号，创建 Worker 和 Thread，在后台执行 AI 识别。
        """
        print(f"MainWindow received recognition request for: {image_path}. Starting background thread...")
        # 先停止任何可能正在运行的旧线程
        self.stop_recognition_thread()

        # 1. 创建线程和 Worker
        self.current_recognition_thread = QThread()
        # 传递识别服务实例和图片路径给 Worker
        self.current_recognition_worker = RecognitionWorker(self.recognition_service, image_path)
        # 2. 将 Worker 移动到新线程
        self.current_recognition_worker.moveToThread(self.current_recognition_thread)

        # 3. 连接信号与槽
        #    - Worker 完成后，调用 on_recognition_finished 处理结果
        self.current_recognition_worker.finished.connect(self.on_recognition_finished)
        #    - Worker 出错后，调用 on_recognition_error 显示错误
        self.current_recognition_worker.error.connect(self.on_recognition_error)
        #    - 线程启动后，执行 Worker 的 run 方法
        self.current_recognition_thread.started.connect(self.current_recognition_worker.run)
        #    - Worker 完成后，请求线程退出
        self.current_recognition_worker.finished.connect(self.current_recognition_thread.quit)
        #    - 线程结束后，清理 Worker 和 Thread 对象
        self.current_recognition_thread.finished.connect(self.current_recognition_worker.deleteLater)
        self.current_recognition_thread.finished.connect(self.current_recognition_thread.deleteLater)
        #    - 清理后重置引用
        self.current_recognition_thread.finished.connect(lambda: setattr(self, 'current_recognition_thread', None))
        self.current_recognition_thread.finished.connect(lambda: setattr(self, 'current_recognition_worker', None))


        # 4. 启动线程
        self.current_recognition_thread.start()
        self.status_bar.showMessage("正在识别图片，请稍候...") # 提示用户
    # ---

    @pyqtSlot(dict)
    def on_recognition_finished(self, result: dict):
        """后台识别完成时调用，存储结果并发出 recognition_completed 信号"""
        print(f"Recognition finished in background thread. Result: {result}")
        self.status_bar.showMessage("图片识别完成。", 3000)
        # --- 新增：存储识别结果 --- 
        self.last_recognition_result = result.copy() # 存储副本
        # ---
        if result:
            self.recognition_completed.emit(result)
        else:
            print("Recognition service returned no result.")
            QMessageBox.warning(self, "识别提醒", "未能从图片中识别出有效信息。")
            self.last_recognition_result = None # 清空结果

    @pyqtSlot(str)
    def on_recognition_error(self, error_message: str):
        """后台识别出错时调用，清空识别结果"""
        print(f"Recognition error in background thread: {error_message}")
        self.status_bar.showMessage("图片识别失败！", 3000)
        QMessageBox.critical(self, "识别错误", f"AI 识别过程中发生错误:\n{error_message}")
        # --- 新增：清空识别结果 --- 
        self.last_recognition_result = None
        # ---

    # --- 新增：处理窗口关闭事件 --- 
    def closeEvent(self, event: QCloseEvent): 
        """重写 closeEvent，在关闭前保存用户数据"""
        print("正在关闭应用程序，保存用户数据...")
        self._save_users()
        event.accept() # 接受关闭事件
    # ---

    # --- 新增：加载并显示衣橱内容的方法 --- 
    def _load_and_display_wardrobe(self):
        """加载当前用户的衣物并更新 WardrobeView"""
        if not self.current_user:
            print("无法加载衣橱：无当前用户。")
            # 可能需要清空 WardrobeView？
            wardrobe_view = self.nav_items.get("我的衣橱")
            if wardrobe_view and isinstance(wardrobe_view, WardrobeView):
                 wardrobe_view.display_items([]) # 显示空列表
            return
        
        wardrobe_view = self.nav_items.get("我的衣橱")
        if not wardrobe_view or not isinstance(wardrobe_view, WardrobeView):
            print("错误：无法找到 WardrobeView 实例。")
            return
            
        print(f"正在为用户 {self.current_user.id} 加载衣橱...")
        try:
            repo = JsonWardrobeRepository()
            items = repo.get_all_items(self.current_user.id)
            print(f"从仓储加载了 {len(items)} 件衣物。")
            wardrobe_view.display_items(items)
            self.status_bar.showMessage(f"衣橱已加载 ({len(items)} 件)", 2000)
        except Exception as e:
             print(f"错误：加载或显示衣橱时出错: {e}")
             QMessageBox.critical(self, "加载错误", f"加载衣橱失败: {e}")
             wardrobe_view.display_items([]) # 出错时显示空列表
    # ---

    # 移除了 create_tool_bar, populate_user_menu, update_user_menu_checkmark,
    # update_user_display, on_switch_user, on_manage_users, on_preferences,
    # on_view_wardrobe, on_view_outfits, on_recommend, on_manual
    # setup_style 也暂时注释掉了