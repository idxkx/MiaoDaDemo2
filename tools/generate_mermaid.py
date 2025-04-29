import inspect
import os
import sys
import importlib
import re
from sqlalchemy import inspect as sqla_inspect
# from sqlalchemy.orm.properties import RelationshipProperty # RelationshipProperty is not directly used now
from sqlalchemy.sql.sqltypes import ARRAY
from sqlalchemy.schema import UniqueConstraint # Import UniqueConstraint

# --- 配置 ---
# 根据你的项目调整模型目录和Base类的导入路径
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'models')
BASE_IMPORT_PATH = "app.db.base" # 从 backend/ 目录开始的路径
MODEL_MODULE_PREFIX = "app.models." # 模型模块的导入前缀

# 添加 backend 目录到 Python 路径，以便导入 app.*
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

# --- 辅助函数 ---

def get_column_comment(column_proxy):
    """尝试从列定义的源代码注释中提取中文名"""
    try:
        # 获取定义该列的模型类
        model_class = column_proxy.class_attribute.parent.class_
        # 获取模型类的源代码
        source_lines = inspect.getsourcelines(model_class)[0]
        # 查找定义该列的行
        col_name = column_proxy.key
        for i, line in enumerate(source_lines):
            # Make matching robust against slight variations in Column definition
            if col_name in line and ('Column(' in line or f'{col_name} =' in line):
                # 尝试匹配注释 # 中文名, 或 # 中文名\n
                # Corrected Regex: look for #, optional space, then capture non-comma/newline chars
                match = re.search(r'#\s*([^,\n]+)', line)
                if match:
                    comment = match.group(1).strip()
                    # 避免提取到过长的注释或非名称部分
                    if len(comment) < 30 and not comment.startswith(('主键', '外键', '系统', '例如')):
                         return comment
                # 如果上一行是注释行，也尝试提取 (针对多行定义的情况)
                if i > 0:
                     prev_line = source_lines[i-1].strip()
                     if prev_line.startswith('#'):
                         comment = prev_line[1:].strip()
                         if len(comment) < 30 and not comment.startswith(('主键', '外键', '系统', '例如')):
                             return comment
                break # 找到定义行就停止
    except Exception as e:
        # Print exception during comment parsing for debugging, but don't stop script
        print(f"Debug: Error parsing comment for {column_proxy.key}: {e}", file=sys.stderr)
        pass # 忽略所有错误，获取不到注释就算了
    return column_proxy.key # 返回英文名作为后备

def format_type(col_type):
    """格式化SQLAlchemy类型为Mermaid兼容的字符串"""
    if isinstance(col_type, ARRAY):
        # Handle potential complexity in item_type (e.g., String(length=...))
        item_type_name = getattr(col_type.item_type, '__visit_name__', col_type.item_type.__class__.__name__)
        return f"ARRAY_{item_type_name}"
    # Use __visit_name__ for more specific types like VARCHAR, INTEGER if available
    return getattr(col_type, '__visit_name__', col_type.__class__.__name__)

# --- 主逻辑 ---

def generate_mermaid_er_diagram():
    """生成Mermaid ER图代码"""
    try:
        # 动态导入 Base
        base_module = importlib.import_module(BASE_IMPORT_PATH)
        Base = getattr(base_module, 'Base')
    except (ImportError, AttributeError) as e:
        print(f"Error: 无法导入Base类 '{BASE_IMPORT_PATH}'. 请检查路径配置. Error: {e}", file=sys.stderr)
        return None

    # 动态导入所有模型文件
    model_classes = {}
    print(f"Debug: Searching for models in: {MODELS_DIR}", file=sys.stderr)
    for filename in os.listdir(MODELS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            full_module_name = MODEL_MODULE_PREFIX + module_name
            print(f"Debug: Trying to import: {full_module_name}", file=sys.stderr)
            try:
                module = importlib.import_module(full_module_name)
                for name, obj in inspect.getmembers(module):
                    # Ensure it's a class, subclass of Base, not Base itself, and defined in *this* module
                    if inspect.isclass(obj) and issubclass(obj, Base) and obj is not Base and obj.__module__ == full_module_name:
                        print(f"Debug: Found model: {name} in {full_module_name}", file=sys.stderr)
                        model_classes[obj.__name__] = obj
            except ImportError as e:
                print(f"Warning: 无法导入模型模块 '{full_module_name}'. Error: {e}", file=sys.stderr)
                continue # 跳过无法导入的模块
            except Exception as e:
                 print(f"Warning: 处理模块时出错 '{full_module_name}'. Error: {e}", file=sys.stderr)
                 continue

    if not model_classes:
        print("Error: 未在指定目录找到任何有效模型类。", file=sys.stderr)
        return None
    print(f"Debug: Found {len(model_classes)} model classes: {list(model_classes.keys())}", file=sys.stderr)

    # 使用 SQLAlchemy inspect 获取元数据
    metadata = Base.metadata

    if not metadata.tables:
         print("Error: 未在 Base.metadata 中找到任何表。请确保模型已正确导入并注册。", file=sys.stderr)
         return None
    print(f"Debug: Found {len(metadata.tables)} tables in metadata: {list(metadata.tables.keys())}", file=sys.stderr)

    mermaid_lines = ["erDiagram"]
    relationships = []

    # 1. 生成表定义
    for table in metadata.tables.values():
        table_name = table.name
        mermaid_lines.append(f"    {table_name} {{")

        # 获取定义该表的模型类 (可能不唯一，取第一个找到的)
        model_class = None
        for mc in model_classes.values():
            # Check __tablename__ attribute if it exists
            if hasattr(mc, '__tablename__') and mc.__tablename__ == table_name:
                model_class = mc
                break

        mapper = sqla_inspect(model_class) if model_class else None
        # Fallback to inspecting the table directly if model_class not found (e.g., association table)
        table_inspector = sqla_inspect(table)

        for column in table.columns:
            col_name = column.name
            col_type_str = format_type(column.type)
            flags = []
            if column.primary_key:
                flags.append("PK")
            if column.foreign_keys:
                flags.append("FK")

            # Check for UniqueConstraint containing this column
            # Corrected check using table_inspector
            unique_constraints = [c for c in table_inspector.constraints if isinstance(c, UniqueConstraint) and column in c.columns]
            if unique_constraints:
                flags.append("UK")

            # 尝试获取中文名注释
            comment = col_name # 默认用英文名
            if mapper:
                # Find the corresponding ColumnProperty using the mapper
                prop = mapper.get_property_by_column(column)
                if prop:
                    comment = get_column_comment(prop)
            # else: # If no model/mapper, maybe try parsing table comments if available? (Future enhancement)
            #    pass

            flags_str = ", ".join(flags) if flags else ""
            # Escape quotes within the comment string for Mermaid
            escaped_comment = comment.replace('"', '#quot;')
            mermaid_lines.append(f'        {col_type_str} {col_name} {flags_str} "{escaped_comment}"')

        mermaid_lines.append("    }")
        mermaid_lines.append("") # Add blank line between tables

    # 2. 生成关系 (基于外键)
    for table in metadata.tables.values():
        for column in table.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    # fk.column points to the referenced column
                    target_table = fk.column.table.name
                    source_table = table.name
                    # Basic relationship: One-to-Many (target has PK, source has FK pointing to it)
                    # Mermaid format: PK_Table ||--o{ FK_Table : "label"
                    # Use FK column name as label for clarity
                    relationships.append(f"    {target_table} ||--o{{ {source_table} : \"{column.name}\"")

    # Add relationships, ensuring uniqueness
    mermaid_lines.extend(sorted(list(set(relationships))))

    return "\n".join(mermaid_lines)

# --- 执行 ---
if __name__ == "__main__":
    print("Debug: Starting Mermaid generation script...", file=sys.stderr)
    mermaid_code = generate_mermaid_er_diagram()
    if mermaid_code:
        # Print the final code to standard output
        print(mermaid_code)
    else:
        print("Error: Failed to generate Mermaid code.", file=sys.stderr)
        sys.exit(1) 