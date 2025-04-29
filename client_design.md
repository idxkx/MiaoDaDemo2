# 智能穿搭助手客户端设计文档

## 设计理念

- **简洁易用**: 界面设计简单直观，操作流程清晰
- **本地化体验**: 充分利用桌面应用优势，提供快速响应和离线功能
- **个性化定制**: 支持界面主题切换和布局调整
- **流畅交互**: 采用异步操作处理耗时任务，确保界面响应流畅

## 技术架构

### 核心框架
- PyQt6: 主要GUI框架
- Qt Designer: UI界面设计工具
- QSS: 界面样式设计

### 系统要求
- 操作系统: Windows 10/11
- Python版本: 3.10+
- 屏幕分辨率: 最低1366x768

## 界面结构

### 主窗口 (MainWindow)
- 位置：`client/ui/main_window.py`
- 功能：
  - 程序主入口
  - 导航菜单
  - 状态栏
  - 工具栏
  - 主内容区域

### 角色管理界面 (PersonaWindow)
- 位置：`client/ui/persona_window.py`
- 功能：
  - 角色列表展示
  - 角色选择
  - 角色信息查看
  - 角色偏好设置

### 衣橱管理界面 (ClosetWindow)
- 位置：`client/ui/closet_window.py`
- 功能：
  - 服装网格展示
  - 分类筛选面板
  - 服装详情查看
  - 服装编辑表单
  - 批量操作工具栏

### 服装上传界面 (UploadDialog)
- 位置：`client/ui/upload_dialog.py`
- 功能：
  - 图片选择/拖拽上传
  - 图片预览和裁剪
  - 服装信息表单
  - 上传进度显示

### 穿搭推荐界面 (RecommendWindow)
- 位置：`client/ui/recommend_window.py`
- 功能：
  - 场景选择
  - 穿搭方案展示
  - 搭配建议展示
  - 方案保存功能

## 控制器设计

### 主控制器 (MainController)
- 位置：`client/controllers/main_controller.py`
- 职责：
  - 窗口管理
  - 导航控制
  - 全局状态管理
  - 配置管理

### 角色控制器 (PersonaController)
- 位置：`client/controllers/persona_controller.py`
- 职责：
  - 角色数据管理
  - 角色切换逻辑
  - 角色偏好同步

### 衣橱控制器 (ClosetController)
- 位置：`client/controllers/closet_controller.py`
- 职责：
  - 服装数据CRUD
  - 分类筛选逻辑
  - 图片管理
  - 批量操作处理

### 上传控制器 (UploadController)
- 位置：`client/controllers/upload_controller.py`
- 职责：
  - 图片上传处理
  - 图片预处理
  - 表单验证
  - 进度管理

### 推荐控制器 (RecommendController)
- 位置：`client/controllers/recommend_controller.py`
- 职责：
  - 推荐请求处理
  - 结果展示管理
  - 方案保存处理

## 数据模型

### 本地数据模型
- 位置：`client/models/`
- 包含：
  - 角色模型
  - 服装模型
  - 穿搭模型
  - 配置模型

### 缓存设计
- 位置：`client/utils/cache.py`
- 功能：
  - 图片缓存
  - 数据缓存
  - 配置缓存

## 工具类

### 网络工具 (NetworkUtils)
- 位置：`client/utils/network.py`
- 功能：
  - HTTP请求封装
  - 错误处理
  - 重试机制

### 图片工具 (ImageUtils)
- 位置：`client/utils/image.py`
- 功能：
  - 图片压缩
  - 格式转换
  - 图片处理

### 配置工具 (ConfigUtils)
- 位置：`client/utils/config.py`
- 功能：
  - 配置读写
  - 默认配置
  - 配置验证

## 资源管理

### 图标资源
- 位置：`client/resources/icons/`
- 类型：
  - 工具栏图标
  - 状态图标
  - 操作图标

### 样式资源
- 位置：`client/resources/styles/`
- 类型：
  - 主题样式
  - 组件样式
  - 自定义样式

## 异常处理

### 全局异常处理
- 位置：`client/utils/error_handler.py`
- 功能：
  - 异常捕获
  - 错误提示
  - 日志记录

### 错误提示
- 类型：
  - 对话框提示
  - 状态栏提示
  - 气泡提示

## 性能优化

### 图片加载优化
- 延迟加载
- 图片缓存
- 压缩策略

### 数据加载优化
- 分页加载
- 后台预加载
- 数据缓存

### UI响应优化
- 异步操作
- 进度反馈
- 防抖节流

## 测试规范

### 单元测试
- 位置：`client/tests/unit/`
- 范围：
  - 控制器测试
  - 工具类测试
  - 模型测试

### 集成测试
- 位置：`client/tests/integration/`
- 范围：
  - 界面集成测试
  - 功能流程测试

### UI测试
- 位置：`client/tests/ui/`
- 范围：
  - 界面布局测试
  - 交互功能测试
  - 样式测试 