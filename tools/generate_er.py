from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import Base

def generate_er_diagram():
    """生成ER图"""
    # 确保docs目录存在
    os.makedirs('docs', exist_ok=True)
    
    # 创建图表
    graph = create_schema_graph(
        metadata=Base.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir='LR',  # 左到右的布局
        concentrate=False  # 不要合并关系线
    )
    
    # 保存图表
    graph.write_png('docs/database_er.png') 