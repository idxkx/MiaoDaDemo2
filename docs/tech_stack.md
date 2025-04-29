# 技术栈说明文档

## 核心技术栈

### GUI框架
- Python 3.10+
- PyQt6 - 主界面框架
- Qt Designer - UI设计工具
- QSS - 界面样式

### 数据存储
- SQLite - 本地数据库
- JSON - 配置文件
- 文件系统 - 图片存储

### AI相关
- PyTorch - 深度学习框架
- OpenCV - 图像处理
- NumPy - 数学计算
- Pillow - 图像处理

### 工具库
- python-dotenv - 环境变量管理
- coloredlogs - 日志美化
- tqdm - 进度条显示

## 开发工具

### IDE和编辑器
- Visual Studio Code
- PyCharm（可选）
- Qt Designer

### 版本控制
- Git
- GitHub

### 测试工具
- pytest - 单元测试
- pytest-qt - Qt应用测试
- pytest-cov - 测试覆盖率

### 文档工具
- Markdown
- PlantUML - 架构图
- Graphviz - 流程图

## 打包与部署

### 打包工具
- PyInstaller - 应用打包
- cx_Freeze（备选）

### 自动化构建
- GitHub Actions - CI/CD
- make - 构建工具

## 开发环境要求

### 系统要求
- Windows 10/11
- 8GB+ RAM
- Python 3.10+
- NVIDIA GPU（推荐）

### Python环境
- virtualenv/venv - 虚拟环境
- pip - 包管理器

### 开发依赖
- black - 代码格式化
- flake8 - 代码检查
- mypy - 类型检查
- isort - 导入排序

## 版本控制规范

### 分支管理
- main - 主分支
- develop - 开发分支
- feature/* - 功能分支
- bugfix/* - 修复分支

### 提交规范
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

## 文档规范

### 代码文档
- 类型注解
- 函数文档字符串
- 模块文档

### 项目文档
- README.md
- 架构文档
- 部署文档
- 用户手册

## 测试规范

### 单元测试
- 控制器测试
- 工具类测试
- 模型测试

### 集成测试
- 界面测试
- 功能测试
- 数据库测试

### UI测试
- 界面布局测试
- 交互功能测试
- 样式测试

## 性能优化

### 启动优化
- 延迟加载
- 资源预加载
- 配置优化

### 运行时优化
- 内存管理
- 图片缓存
- 数据库索引

### 界面优化
- 异步加载
- 分页显示
- 动画效果 