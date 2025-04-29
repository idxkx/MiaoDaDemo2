# 智能穿搭助手

一款基于Python和PyQt6开发的智能穿搭推荐桌面应用程序，集成AI技术，帮助用户管理个人衣橱并获取个性化穿搭建议。

## 主要功能

- 🎭 虚拟角色系统：提供6个预设角色（3男3女），满足不同用户需求
- 👔 智能衣橱管理：轻松管理个人服装收藏
- 🤖 AI服装识别：自动识别服装类型、颜色、风格等特征
- 💡 智能穿搭推荐：基于场景和个人特征推荐合适搭配
- 💾 本地数据存储：保护用户隐私，支持离线使用
- 🎨 美观的界面：现代化的GUI设计，流畅的交互体验

## 系统要求

- Windows 10/11
- Python 3.10+
- 8GB+ RAM
- 1366x768以上屏幕分辨率

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/MiaoDaDemo2.git
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
python client/main.py
```

## 使用说明

1. 首次启动时，选择一个虚拟角色
2. 进入主界面后，可以：
   - 添加服装到衣橱
   - 管理已有服装
   - 获取穿搭推荐
   - 收藏喜欢的搭配

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
├── backend/           # 后端服务
├── client/           # 桌面客户端
│   ├── ui/          # 界面定义
│   ├── controllers/ # 控制器
│   ├── models/      # 数据模型
│   ├── utils/       # 工具函数
│   └── resources/   # 资源文件
├── models/           # AI模型
└── tools/            # 开发工具
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
pyinstaller client/main.py
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
3. 发送邮件到 support@example.com

## 许可证

MIT License

## 作者

[Your Name](https://github.com/yourusername)

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/)
- [OpenCV](https://opencv.org/) 