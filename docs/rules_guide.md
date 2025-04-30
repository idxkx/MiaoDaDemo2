# 项目规则使用指南

<!-- 
本文档遵循 development-experience 规则
确保文档结构清晰、内容详尽、示例具体
-->

本文档详细介绍了喵搭智能穿搭助手项目中使用的MDC规则文件的用途和使用方法。

## 什么是MDC文件

MDC(Markdown Cursor)文件是Cursor IDE中用于定义项目规则和开发约定的特殊格式文件。这些文件使用Markdown语法编写，存放在项目的`.cursor/rules/`目录下，文件扩展名为`.mdc`。

MDC规则文件的主要作用是：
1. 定义项目的开发规范和最佳实践
2. 提供代码和文档编写的标准化指南
3. 确保团队成员遵循统一的开发流程
4. 减少重复错误和提升代码质量

## 项目规则列表

本项目包含以下核心规则文件：

| 规则名称 | 文件路径 | 主要用途 |
|---------|--------|--------|
| development-experience | .cursor/rules/development-experience.mdc | 开发经验总结与指南 |
| project-structure | .cursor/rules/project-structure.mdc | 项目目录结构和文件组织规范 |
| api-design-principles | .cursor/rules/api-design-principles.mdc | 后端API设计规范和约定 |
| ddd-principles | .cursor/rules/ddd-principles.mdc | 领域驱动设计原则和实践指南 |
| coding-standards | .cursor/rules/coding-standards.mdc | 代码开发规范和约定 |
| model-management | .cursor/rules/model-management.mdc | AI模型管理规范 |
| ui-design-guidelines | .cursor/rules/ui-design-guidelines.mdc | UI设计和用户体验规范 |
| deployment-guidelines | .cursor/rules/deployment-guidelines.mdc | 项目部署与环境配置规范 |

## 规则调用方式

在开发过程中，可以通过以下方式引用和遵循规则：

### 1. 在代码注释中引用规则

```python
# 遵循 development-experience 规则
def ensure_storage_dirs():
    """确保所有存储目录存在"""
    dirs = [
        'storage/images',
        'storage/images/processed',
        'storage/temp'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
```

### 2. 在文档中引用规则

```markdown
<!-- 遵循 project-structure 规则 -->
## 项目结构

项目采用DDD分层架构，主要包括以下层次：
- 领域层（Domain）
- 应用层（Application）
- 基础设施层（Infrastructure）
- 接口层（Interface）
```

### 3. 在代码编辑器中查看规则

在Cursor IDE中，可以通过以下方式查看规则内容：
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "View Rule" 并选择对应选项
3. 输入规则名称（如 "development-experience"）
4. 查看规则详细内容

## 关键规则详解

### development-experience 规则

**用途**：定义开发过程中的最佳实践和经验总结

**主要内容**：
- Windows环境下的命令执行规范
- 存储目录管理
- 错误处理和日志记录
- 图片处理和存储

**示例**：
```python
# 遵循 development-experience 规则进行存储目录管理
def ensure_storage_dirs():
    dirs = [
        'storage/images',
        'storage/images/processed',
        'storage/temp'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
```

### project-structure 规则

**用途**：定义项目目录结构和文件组织方式

**主要内容**：
- 源代码目录结构
- 文件命名规范
- 模块划分原则
- 技术栈约定

**示例**：
```python
# 遵循 project-structure 规则组织存储服务代码
# src/infrastructure/storage/
from .storage_service import StorageService
from .local_storage_service import LocalStorageService
from .image_storage_service import ImageStorageService
```

### ddd-principles 规则

**用途**：定义领域驱动设计的实践原则

**主要内容**：
- 实体、值对象、聚合根的定义和实现规范
- 领域服务的设计原则
- 仓储接口和实现规范
- 领域事件的使用方式

**示例**：
```python
# 遵循 ddd-principles 规则实现值对象
@dataclass(frozen=True)
class Color(ValueObject):
    """颜色值对象"""
    name: str  # 颜色名称
    hex_code: str  # 十六进制颜色代码
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Color name cannot be empty")
        if not re.match(r"^#[0-9A-Fa-f]{6}$", self.hex_code):
            raise ValueError("Invalid hex color code")
```

## 规则使用最佳实践

为了充分利用项目规则，建议遵循以下最佳实践：

1. **开发前查看相关规则**：在开始开发新功能前，先查看相关规则文件，了解开发规范和约定

2. **引用具体规则**：在代码和文档中引用具体的规则，而不是笼统地提及"遵循规则"

3. **规则一致性**：确保代码和文档的风格与规则保持一致

4. **更新规则**：如果发现规则需要更新或补充，及时与团队沟通并更新规则文件

5. **规则优先级**：当规则之间存在冲突时，遵循以下优先级：
   - ddd-principles > project-structure > coding-standards > 其他规则

## 规则文件示例

以下是`development-experience.mdc`文件的部分内容示例：

```markdown
# 开发经验总结与指南

{
  "type": "agent_requested",
  "title": "开发经验总结与指南",
  "description": "本文档包含了项目开发过程中的最佳实践、经验总结和规范指南",
  "version": "1.0.0",
  "author": "MiaoDao Team",
  "priority": "high"
}

## Windows PowerShell命令执行规则
- 严禁使用 `&&` 连接多个命令，这在PowerShell中是无效的
- 必须使用以下方式之一执行多个命令：
  1. 使用分号 `;` 分隔命令
  2. 分别执行每个命令
  3. 使用PowerShell管道 `|`
  4. 创建函数或脚本封装多个命令

示例：
```powershell
# ❌ 错误示例 - 永远不要这样做
cd backend && pip install -r requirements.txt

# ✅ 正确示例 1 - 使用分号
cd backend; pip install -r requirements.txt

# ✅ 正确示例 2 - 分别执行
cd backend
pip install -r requirements.txt
```
```

## 常见问题与解答

**Q: 为什么要使用MDC规则文件？**  
A: MDC规则文件提供了一种标准化的方式来定义和共享开发规范，确保团队成员遵循一致的开发流程和最佳实践。

**Q: 如何查看所有可用的规则？**  
A: 可以在项目的`.cursor/rules/`目录下查看所有MDC规则文件，或者使用Cursor IDE的"View Rule"命令查看。

**Q: 规则文件可以修改吗？**  
A: 可以修改，但应该与团队成员沟通并获得一致意见后再进行修改。规则文件修改后应当通知所有团队成员。

**Q: 如果发现代码与规则不一致怎么办？**  
A: 应当根据情况决定是修改代码以符合规则，还是更新规则以适应新的开发需求。无论哪种情况，都应该与团队讨论后再做决定。

**Q: 如何创建新的规则文件？**  
A: 在`.cursor/rules/`目录下创建新的`.mdc`文件，按照已有规则文件的格式编写新规则，然后在README.md中更新规则列表。 