# 项目结构与目录规范

## 目录结构
项目分为两个主要部分：

- `app/` - 主应用程序代码
- `models/` - AI模型相关代码

主要入口文件：
- 应用程序入口：`app/main.py`

## 重要约定

1. **应用程序代码组织**
   - 界面定义必须在 `app/ui/` 目录下
   - 控制器必须在 `app/controllers/` 目录下
   - 数据模型必须在 `app/models/` 目录下
   - 工具函数必须在 `app/utils/` 目录下
   - 资源文件必须在 `app/resources/` 目录下
   - 数据库必须在 `app/data/` 目录下
   - 配置文件必须在 `app/config/` 目录下

2. **AI模型代码组织**
   - 服装识别模型相关代码必须在 `models/clothing_recognition/` 目录下
   - 图像生成模型相关代码必须在 `models/image_generation/` 目录下

## 文件命名规范

1. **应用程序文件命名**
   - Python文件名使用下划线命名法（snake_case）
   - UI文件必须以`_window.py`或`_dialog.py`结尾
   - 控制器文件必须以`_controller.py`结尾
   - 模型文件必须以`_model.py`结尾
   - 工具类文件必须以`_utils.py`结尾
   - 数据库文件必须以`.db`结尾
   - 配置文件必须以`.ini`或`.json`结尾

## 技术栈

1. **应用程序**
   - PyQt6 - GUI框架
   - Qt Designer - UI设计工具
   - SQLite - 本地数据库
   - PyInstaller - 应用打包
   - Pillow - 图像处理
   - OpenCV - 图像处理

2. **AI模型**
   - PyTorch - 深度学习框架
   - OpenCV - 图像处理
   - NumPy - 数学计算
   - Pillow - 图像处理

## 设计模式

1. **应用程序设计模式**
   - MVC架构
   - 单例模式（配置管理、数据库连接）
   - 观察者模式（UI更新）
   - 工厂模式（对象创建）
   - 策略模式（AI模型切换）

## 数据流

1. **本地数据流**
   ```
   UI层 <-> 控制器层 <-> 数据模型层 <-> 本地存储层
   ```

2. **AI处理流**
   ```
   图像输入 -> 预处理 -> AI模型处理 -> 结果后处理 -> 数据存储
   ```

## 数据模型

### 角色 (Persona)
```python
class Persona:
    def __init__(self):
        self.id = None
        self.name = ""
        self.gender = ""  # male, female
        self.age = 0
        self.occupation = ""
        self.height = 0  # cm
        self.weight = 0  # kg
        self.body_type = ""  # slim, athletic, full, etc
        self.style_preference = {}  # preferred styles
        self.color_preference = {}  # preferred colors
        self.occasion_preference = {}  # preferred occasions
        self.season_adaptation = ""  # preferred seasons
        self.description = ""
```

### 服装 (Clothes)
```python
class Clothes:
    def __init__(self):
        self.id = None
        self.persona_id = None
        self.name = ""
        self.category = ""  # tops, bottoms, dresses, etc
        self.subcategory = ""
        self.color = ""
        self.pattern = ""
        self.season = ""
        self.occasion = {}
        self.brand = ""
        self.description = ""
        self.is_favorite = False
        self.image_path = ""
        self.created_at = None
```

### 穿搭 (Outfit)
```python
class Outfit:
    def __init__(self):
        self.id = None
        self.persona_id = None
        self.name = ""
        self.occasion = ""
        self.season = ""
        self.style = ""
        self.description = ""
        self.clothes_ids = []  # List of clothes IDs
        self.created_at = None
```

## 本地存储

### SQLite数据库表结构
```sql
-- 角色表
CREATE TABLE personas (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    occupation TEXT,
    height INTEGER,
    weight INTEGER,
    body_type TEXT,
    style_preference TEXT,  -- JSON
    color_preference TEXT,  -- JSON
    occasion_preference TEXT,  -- JSON
    season_adaptation TEXT,
    description TEXT
);

-- 服装表
CREATE TABLE clothes (
    id INTEGER PRIMARY KEY,
    persona_id INTEGER,
    name TEXT,
    category TEXT,
    subcategory TEXT,
    color TEXT,
    pattern TEXT,
    season TEXT,
    occasion TEXT,  -- JSON
    brand TEXT,
    description TEXT,
    is_favorite INTEGER,
    image_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas (id)
);

-- 穿搭表
CREATE TABLE outfits (
    id INTEGER PRIMARY KEY,
    persona_id INTEGER,
    name TEXT,
    occasion TEXT,
    season TEXT,
    style TEXT,
    description TEXT,
    clothes_ids TEXT,  -- JSON array of clothes IDs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas (id)
);
```

## 重要文件引用
- 应用程序设计：[app_design.md](mdc:app_design.md)
- 用户流程设计：[user_flow.md](mdc:user_flow.md)
- AI模型设计：[ai_models_design.md](mdc:ai_models_design.md) 