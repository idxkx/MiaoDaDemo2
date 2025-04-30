# 图片与文件存储服务

本文档描述了项目中使用的图片和文件存储服务的设计、实现和使用方法。

<!-- 
规则引导：
使用 development-experience 规则进行文档更新
确保按照项目规范修改和维护文档
遵循Windows环境下的路径处理最佳实践
-->

## 概述

存储服务是智能穿搭助手的核心基础设施，用于管理用户上传的衣物图片和其他文件资源。该服务实现了以下功能：

- 图片文件的存储和读取
- 图片元数据的提取和管理
- 缩略图的自动生成和管理
- 基于分类的存储目录组织
- 图片格式和大小的验证

## 架构设计

存储服务采用分层设计，主要包含以下组件：

1. **StorageService**：存储服务的抽象基类，定义通用接口
2. **LocalStorageService**：基于本地文件系统的存储实现
3. **ImageStorageService**：专门用于图片存储和处理的服务
4. **StorageServiceFactory**：创建和管理存储服务实例的工厂类

![存储服务架构](../resources/images/storage_service_arch.png)

## 目录结构

```
src/infrastructure/storage/
├── __init__.py           # 包初始化文件
├── storage_service.py    # 存储服务抽象基类
├── local_storage_service.py # 本地存储服务实现
├── image_storage_service.py # 图片存储服务实现
└── storage_factory.py    # 存储服务工厂

storage/               # 存储根目录
├── images/            # 图片存储目录
│   ├── processed/    # 处理后图片目录
│   └── thumbnails/   # 缩略图目录
├── logs/              # 日志文件目录
└── temp/              # 临时文件目录
```

## 规则与约定

<!-- 规则说明：使用MDC规则文件 -->

本项目使用MDC(Markdown Cursor)文件来定义开发规则和约定。在使用存储服务时，需要遵循以下规则：

### MDC文件使用指南

1. **规则位置**：所有规则文件存放在`.cursor/rules/`目录下
2. **规则格式**：规则使用`.mdc`扩展名，采用Markdown格式编写
3. **规则调用**：在开发过程中通过注释形式引用规则

### 关键规则引用

在开发存储服务相关功能时，请遵循以下规则：

```
<!-- 引用存储目录管理规则 -->
按照development-experience规则确保存储目录存在:
```python
def ensure_storage_dirs():
    dirs = [
        'storage/images',
        'storage/images/processed',
        'storage/temp'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
```
```

```
<!-- Windows路径处理规则 -->
Windows环境下的路径处理:
- 使用反斜杠`\`或`Path`对象处理路径
- 不要使用`/`进行路径拼接
- 使用`os.path.join`或`pathlib.Path`进行路径组合
```

### 如何调用规则

在代码或文档中引用规则的正确方式：

1. **代码中引用**：
```python
# 引用development-experience规则进行存储目录初始化
from src.infrastructure.bootstrap import AppBootstrap
AppBootstrap.init_storage()  # 确保存储目录存在
```

2. **文档中引用**：
```markdown
<!-- 引用development-experience规则 -->
按照规范，初始化存储目录需要使用AppBootstrap类的init_storage方法。
```

3. **注释中引用**：
```python
# 遵循 project-structure 规则，将所有存储相关代码放在 infrastructure/storage 目录下
```

## 使用方法

### 初始化存储服务

在应用启动时初始化存储服务：

```python
from src.infrastructure.bootstrap import AppBootstrap

# 初始化应用（包括存储服务）
AppBootstrap.init_app()
```

### 获取存储服务实例

使用工厂类获取存储服务实例：

```python
from src.infrastructure.storage import StorageFactory

# 获取默认图片存储服务
image_storage = StorageFactory.get_image_storage()

# 获取自定义配置的图片存储服务
custom_image_storage = StorageFactory.get_image_storage(
    name="custom",            # 服务实例名称
    base_dir="custom/images", # 自定义存储目录
    max_size_mb=20.0,         # 最大图片大小（MB）
    auto_thumbnail=True,      # 自动生成缩略图
    thumbnail_size=(200, 200) # 缩略图尺寸
)

# 获取通用文件存储服务
file_storage = StorageFactory.get_local_storage()
```

### 存储和读取图片

**1. 保存图片**

```python
async def save_clothing_image(image_data, filename=None):
    """保存衣物图片"""
    # 图片数据可以是字节、文件对象或base64字符串
    saved_path, metadata = await image_storage.save_image(
        image_data=image_data,
        filename=filename,      # 可选，如果不提供则自动生成
        category="clothing",    # 分类目录
        generate_thumbnail=True # 是否生成缩略图
    )
    
    return saved_path, metadata
```

**2. 获取图片**

```python
async def get_clothing_image(image_path):
    """获取衣物图片和元数据"""
    # 获取图片数据和元数据
    image_data, metadata = await image_storage.get_image_with_metadata(image_path)
    
    # 获取缩略图URL
    thumbnail_url = await image_storage.get_thumbnail_url(image_path)
    
    # 获取图片的base64编码（用于前端显示）
    base64_data = await image_storage.get_image_as_base64(image_path)
    
    return image_data, metadata, thumbnail_url, base64_data
```

**3. 删除图片**

```python
async def delete_clothing_image(image_path):
    """删除衣物图片"""
    success = await image_storage.delete_file(image_path)
    return success
```

### 在实体中使用图片存储

下面是在衣物实体中使用图片存储服务的示例：

```python
from src.infrastructure.storage import StorageFactory
from src.domain.model.entities import ClothingItem

async def add_clothing_with_image(clothing_data, image_data):
    """添加带图片的衣物"""
    # 1. 保存图片
    image_storage = StorageFactory.get_image_storage()
    image_path, image_metadata = await image_storage.save_image(
        image_data,
        category="clothing"
    )
    
    # 2. 获取图片URL
    image_url = await image_storage.get_file_url(image_path)
    
    # 3. 创建衣物实体
    clothing = ClothingItem(
        id=clothing_data["id"],
        name=clothing_data["name"],
        category_id=clothing_data["category_id"],
        color=clothing_data["color"],
        size=clothing_data["size"],
        brand=clothing_data["brand"],
        material=clothing_data["material"],
        purchase_date=clothing_data["purchase_date"],
        price=clothing_data["price"],
        description=clothing_data.get("description"),
        image_url=image_url  # 设置图片URL
    )
    
    # 4. 设置图片元数据（可选）
    clothing.image_metadata = image_metadata
    
    # 5. 保存衣物实体
    # ... 
    
    return clothing
```

## 高级功能

### 图片处理

图片存储服务集成了Pillow库，提供以下图片处理功能：

1. **图片格式和大小验证**：确保图片格式符合要求，大小在限制范围内
2. **图片元数据提取**：获取图片的宽度、高度、格式、大小等信息
3. **缩略图生成**：自动生成适当尺寸的缩略图，用于列表展示
4. **Base64编码**：将图片转换为Base64编码，用于在Web界面显示

### 存储组织

图片按以下方式组织存储：

1. **分类目录**：根据图片类型（如clothing、outfit等）分类存储
2. **日期目录**：按照上传日期（YYYYMMDD）组织子目录
3. **唯一文件名**：使用UUID生成唯一文件名，避免冲突
4. **处理目录**：处理后的图片和缩略图存储在专门的目录中

### 错误处理

存储服务内置了完善的错误处理机制：

1. **日志记录**：所有操作都有详细的日志记录
2. **异常处理**：捕获和处理各种可能的异常
3. **权限检查**：验证存储目录的读写权限
4. **格式验证**：验证图片格式和大小是否符合要求

## 配置选项

图片存储服务支持以下配置选项：

| 选项 | 描述 | 默认值 |
|------|------|--------|
| base_dir | 基础存储目录 | storage/images |
| processed_dir | 处理后图片目录 | storage/images/processed |
| base_url | 基础URL路径 | 空（本地文件系统模式） |
| allowed_formats | 允许的图片格式 | jpg, jpeg, png, gif, webp |
| max_size_mb | 最大图片大小（MB） | 10.0 |
| auto_thumbnail | 是否自动生成缩略图 | True |
| thumbnail_size | 缩略图尺寸 | (300, 300) |

## 依赖项

存储服务依赖以下库：

- **Pillow**：用于图片处理（缩略图生成、元数据提取等）
- **aiofiles**：提供异步文件IO操作
- **python-dotenv**：用于配置环境变量

## 测试

存储服务包含完整的测试用例，位于`tests/test_image_storage.py`文件中，可以运行以下命令进行测试：

```bash
pytest tests/test_image_storage.py -v
```

## 未来规划

1. 云存储支持：添加S3、OSS等云存储服务的支持
2. 图片压缩：添加自动图片压缩功能，优化存储空间
3. 图片转换：支持在保存时转换图片格式
4. 批量操作：添加批量上传、下载、删除功能
5. 定时清理：自动清理临时文件和未使用的图片 