# 智能穿搭助手

一款基于Python和PyQt6开发的智能穿搭推荐桌面应用程序，集成AI技术，帮助用户管理个人衣橱并获取个性化穿搭建议。

## 文档导航

- [开发计划](docs/development_plan.md) - 项目开发规划和任务列表
- [技术栈](docs/tech_stack.md) - 使用的技术和框架说明
- [项目结构](docs/project_structure.md) - 详细的项目结构说明
- [AI模型设计](docs/ai_models_design.md) - AI模型架构和实现细节
- [客户端设计](docs/client_design.md) - 客户端UI和功能设计
- [用户流程](docs/user_flow.md) - 用户使用流程和场景
- [开发变更](docs/development_changes.md) - 开发过程中的重要变更记录
- [DDD实现指南](docs/ddd_implementation_guide.md) - 领域驱动设计实现指南

## 主要功能

- 🎭 虚拟角色系统：提供6个预设角色（3男3女），满足不同用户需求
- 👔 智能衣橱管理：轻松管理个人服装收藏
- 🤖 AI服装识别：自动识别服装类型、颜色、风格等特征
- 💡 智能穿搭推荐：基于场景和个人特征推荐合适搭配
- 💾 本地数据存储：保护用户隐私，支持离线使用
- 🎨 美观的界面：现代化的GUI设计，流畅的交互体验
- 📱 高性能：启动时间<3秒，界面响应<100ms，图片加载<200ms，AI推理<1秒

## 系统要求

- Windows 10/11
- Python 3.10+
- 8GB+ RAM
- 1366x768以上屏幕分辨率

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/idxkx/MiaoDaDemo2.git
cd MiaoDaDemo2
```

2. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
python src/main.py
```

## 使用说明

1. 首次启动时，选择一个虚拟角色
2. 进入主界面后，可以：
   - 添加服装到衣橱
   - 管理已有服装
   - 获取穿搭推荐
   - 收藏喜欢的搭配
   - 设置个人偏好
   - 备份重要数据

## 快捷键

- Ctrl+N: 新建服装
- Ctrl+E: 编辑选中
- Ctrl+D: 删除选中
- Ctrl+F: 搜索
- Ctrl+S: 保存
- F1: 帮助

## 项目结构

```
MiaoDaDemo2/
├── docs/             # 项目文档
├── models/           # AI模型文件
│   ├── Anno_fine/   # 细粒度标注模型
│   └── my_clothes_model/ # 服装识别模型
├── resources/        # 资源文件
│   ├── images/      # 图片资源
│   ├── styles/      # 样式文件
│   └── translations/ # 多语言文件
├── src/             # 源代码
│   ├── controllers/ # 控制器
│   ├── domain/      # 领域模型
│   ├── infrastructure/ # 基础设施
│   ├── models/      # 数据模型
│   ├── utils/       # 工具函数
│   └── views/       # 视图
├── storage/         # 数据存储
│   ├── images/      # 图片存储
│   ├── logs/        # 日志文件
│   └── temp/        # 临时文件
├── tests/           # 测试代码
└── tools/           # 开发工具
```

## 开发指南

### 环境配置

1. 安装开发工具
   - Visual Studio Code
   - Qt Designer
   - Git

2. 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

### 代码规范

- 使用black进行代码格式化
- 使用flake8进行代码检查
- 使用mypy进行类型检查
- 遵循PEP 8命名规范
- 所有功能必须有单元测试
- 代码提交前必须更新相关文档

### 提交规范

- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

## 测试

运行单元测试：
```bash
pytest tests/
```

运行UI测试：
```bash
pytest tests/ui/
```

## 构建

构建可执行文件：
```bash
pyinstaller src/main.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 问题反馈

如果你发现任何问题或有建议：

1. 提交 Issue
2. 在应用内使用反馈功能
3. 发送邮件到 support@litata.com

## 许可证

MIT License

## 作者

[MiaoDa Team](https://github.com/idxkx)

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/)
- [OpenCV](https://opencv.org/) 