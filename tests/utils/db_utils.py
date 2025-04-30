"""数据库测试工具

提供数据库测试相关的工具函数，包括：
- 测试数据库初始化
- 测试数据填充
- 数据库清理
"""

import os
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.models import Base
from tests.fixtures.data_generator import (
    generate_personas,
    generate_categories,
    generate_clothing_items,
    generate_outfits,
    generate_tags
)

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 创建异步引擎
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True
)

# 创建异步会话工厂
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_test_db():
    """初始化测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """获取测试数据库会话"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def cleanup_test_db():
    """清理测试数据库"""
    if os.path.exists("test.db"):
        os.remove("test.db")

async def populate_test_data(session: AsyncSession):
    """填充测试数据"""
    # 生成数据
    personas = generate_personas()
    categories = generate_categories()
    clothing_items = []
    for category in categories:
        if category["parent_id"] is not None:  # 只为子分类生成衣物
            items = generate_clothing_items(category["id"], count=3)
            clothing_items.extend(items)
    outfits = generate_outfits(clothing_items)
    tags = generate_tags()
    
    # 保存数据
    from src.infrastructure.persistence.models import (
        PersonaModel,
        CategoryModel,
        ClothingItemModel,
        OutfitModel,
        OutfitItemModel,
        TagModel
    )
    
    # 保存角色
    for persona in personas:
        model = PersonaModel(**persona)
        session.add(model)
    
    # 保存分类
    for category in categories:
        model = CategoryModel(**category)
        session.add(model)
    
    # 保存衣物
    for item in clothing_items:
        model = ClothingItemModel(**item)
        session.add(model)
    
    # 保存穿搭
    for outfit in outfits:
        outfit_items = outfit.pop("items")
        model = OutfitModel(**outfit)
        session.add(model)
        await session.flush()  # 获取outfit_id
        
        # 保存穿搭项
        for item in outfit_items:
            item["outfit_id"] = model.id
            item_model = OutfitItemModel(**item)
            session.add(item_model)
    
    # 保存标签
    for tag in tags:
        model = TagModel(**tag)
        session.add(model)
    
    # 提交事务
    await session.commit() 