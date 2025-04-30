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
from sqlalchemy import create_engine, inspect, text
from uuid import uuid4, UUID
from datetime import datetime
from pathlib import Path # Import Path
import pytest # Import pytest for fixture

# Import Base and ALL models explicitly from the correct location
from src.infrastructure.persistence.models import Base, WardrobeModel, OutfitModel, OutfitItemModel, ClothingItemModel, CategoryModel 

# Import data generation functions
from tests.fixtures.data_generator import (\
    # generate_personas, # Still removed
    generate_categories,\
    generate_clothing_items,\
    generate_outfits,\
    # generate_tags # Still removed
)

# --- Use Absolute Path ---
# Get project root assuming db_utils.py is in tests/utils/
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_FILE_PATH = PROJECT_ROOT / "test.db" # Absolute path to test.db in project root
TEST_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE_PATH.as_posix()}?cache=shared"
TEST_SYNC_DATABASE_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}?cache=shared" # Synchronous URL

print(f"Using ASYNC database URL: {TEST_ASYNC_DATABASE_URL}")
print(f"Using SYNC database URL: {TEST_SYNC_DATABASE_URL}")

# --- Async Engine (for tests) --- 
async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    echo=True,
    # connect_args={"check_same_thread": False} # Still potentially needed for SQLite 
)

# --- Sync Engine (for setup/teardown) ---
sync_engine = create_engine(
    TEST_SYNC_DATABASE_URL,
    echo=True
)

# Async sessionmaker (for tests)
async_session = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

# --- Synchronous Setup/Teardown Functions --- 
def init_test_db_sync():
    """初始化测试数据库 - 使用同步引擎"""
    # Ensure the models module is imported right before init 
    # to force model registration into Base.metadata
    print("[init_test_db_sync] Importing models module...")
    import src.infrastructure.persistence.models
    # Access Base through the imported module
    _Base = src.infrastructure.persistence.models.Base 
    print(f"[init_test_db_sync] Using Base object with id: {id(_Base)}") 

    print(f"[init_test_db_sync] Attempting drop/create for: {TEST_SYNC_DATABASE_URL}")
    
    try:
        print("[init_test_db_sync] Dropping all tables...")
        _Base.metadata.drop_all(bind=sync_engine)
        print("[init_test_db_sync] Creating all tables...")
        # Print known tables before creating
        print(f"[init_test_db_sync] Metadata tables BEFORE create: {list(_Base.metadata.tables.keys())}") 
        _Base.metadata.create_all(bind=sync_engine)
        print("[init_test_db_sync] create_all executed.")
        
        # Verify tables existence using sync inspector
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        print(f"[init_test_db_sync] Tables found by inspector AFTER create: {tables}")
        if "categories" not in tables:
            print("[init_test_db_sync] ERROR: categories table NOT found AFTER create!")
            # Consider raising an error here if table creation is critical
            # raise RuntimeError("Failed to create database tables synchronously.")
            
    except Exception as e:
        print(f"[init_test_db_sync] Error during sync init: {e}")
        raise # Re-raise the exception to fail the setup

def cleanup_test_db_sync():
    """清理测试数据库 - 使用同步引擎"""
    # Re-import locally if needed, ensures Base is the right one
    import src.infrastructure.persistence.models
    _Base = src.infrastructure.persistence.models.Base
    print(f"[cleanup_test_db_sync] Attempting to drop tables for: {TEST_SYNC_DATABASE_URL} using Base id {id(_Base)}")
    try:
        _Base.metadata.drop_all(bind=sync_engine)
        print(f"[cleanup_test_db_sync] Tables dropped successfully.")
    except Exception as e:
        print(f"[cleanup_test_db_sync] Error during sync cleanup: {e}")
        # Don't raise here, allow other tests to run
    # Clean up the sync engine connection pool if necessary
    sync_engine.dispose()

# --- Populate Test Data (remains async) --- 
async def populate_test_data(session: AsyncSession):
    """填充测试数据"""
    print("[populate_test_data] Checking table existence before population...")
    # Check tables using async connection (should exist now)
    async with async_engine.connect() as conn_check:
        def check_tables_sync_before_populate(sync_conn):
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            print(f"[populate_test_data] Tables found by inspector: {tables}")
            # Use a table name defined in the actual models
            if not tables:
                print("[populate_test_data] ERROR: No tables found before population!")
                # This should ideally not happen if sync setup worked
            elif "categories" not in tables: 
                print("[populate_test_data] ERROR: categories table NOT found before population!")
                # This should ideally not happen if sync setup worked
            else:
                print("[populate_test_data] Required tables seem to exist.")
        await conn_check.run_sync(check_tables_sync_before_populate)

    # 生成数据
    print("[populate_test_data] Generating test data...")
    categories = generate_categories()
    clothing_items = []
    default_wardrobe_id = uuid4()
    
    # Assign wardrobe_id to categories (ensure it's done correctly)
    for category_data in categories:
        category_data['wardrobe_id'] = default_wardrobe_id

    for category in categories:
        if category["parent_id"] is not None:
            generated_items = generate_clothing_items(category["id"], count=3)
            for item in generated_items:
                item['wardrobe_id'] = default_wardrobe_id
            clothing_items.extend(generated_items)
            
    default_owner_id = uuid4()
    outfits = generate_outfits(clothing_items=clothing_items, owner_id=default_owner_id, count=3)
    
    print("[populate_test_data] Adding data to session...")
    # Import models needed for saving data
    from src.infrastructure.persistence.models import CategoryModel, ClothingItemModel, OutfitModel, OutfitItemModel

    # 保存分类
    category_models = []
    for category_data in categories:
        if isinstance(category_data.get('id'), str):
             category_data['id'] = UUID(category_data['id'])
        if isinstance(category_data.get('parent_id'), str):
             category_data['parent_id'] = UUID(category_data['parent_id'])
        if not isinstance(category_data.get('wardrobe_id'), UUID):
             print(f"Warning: Re-assigning default wardrobe_id for category {category_data.get('name')}")
             category_data['wardrobe_id'] = default_wardrobe_id
        
        model = CategoryModel(**category_data)
        session.add(model)
        category_models.append(model)
    
    # 保存衣物
    clothing_item_models = []
    for item_data in clothing_items:
        if isinstance(item_data.get('id'), str):
             item_data['id'] = UUID(item_data['id'])
        if isinstance(item_data.get('category_id'), str):
             item_data['category_id'] = UUID(item_data['category_id'])
        if not isinstance(item_data.get('wardrobe_id'), UUID):
             print(f"Warning: Re-assigning default wardrobe_id for item {item_data.get('name')}")
             item_data['wardrobe_id'] = default_wardrobe_id

        category_id = item_data.get('category_id')
        if category_id:
            if any(cat.id == category_id for cat in category_models):
                model = ClothingItemModel(**item_data)
                session.add(model)
                clothing_item_models.append(model)
            else:
                 print(f"Skipping item due to missing category in current batch: {item_data.get('name')}")
        else:
            print(f"Skipping item due to missing category_id: {item_data.get('name')}")

    # Flush before adding outfits
    try:
        print("[populate_test_data] Flushing categories and items...")
        await session.flush()
        print("[populate_test_data] Flush successful.")
    except Exception as e:
        print(f"Error during initial flush: {e}")
        await session.rollback()
        raise

    # 保存穿搭
    print("[populate_test_data] Saving outfits...")
    for outfit_data in outfits:
        outfit_items_data = outfit_data.pop("items")
        if isinstance(outfit_data.get('id'), str):
             outfit_data['id'] = UUID(outfit_data['id'])
        if not isinstance(outfit_data.get('owner_id'), UUID):
             print(f"Warning: Re-assigning default owner_id for outfit {outfit_data.get('name')}")
             outfit_data['owner_id'] = default_owner_id

        model = OutfitModel(**outfit_data)
        session.add(model)
        
        # Flush each outfit to get its ID before adding items
        try:
            await session.flush() 
        except Exception as e:
            print(f"Error flushing outfit {outfit_data.get('name')}: {e}")
            await session.rollback()
            # Decide how to handle this - skip outfit? raise?
            continue # Skip this outfit

        outfit_id = model.id # Get the ID after flushing

        # 保存穿搭项
        for item_assoc_data in outfit_items_data:
            if isinstance(item_assoc_data.get('outfit_id'), str):
                 item_assoc_data['outfit_id'] = UUID(item_assoc_data['outfit_id'])
            if isinstance(item_assoc_data.get('item_id'), str):
                 item_assoc_data['item_id'] = UUID(item_assoc_data['item_id'])
                 
            item_assoc_data["outfit_id"] = outfit_id # Use the flushed outfit_id
            item_id = item_assoc_data.get('item_id')
            if any(item.id == item_id for item in clothing_item_models):
                item_model = OutfitItemModel(**item_assoc_data)
                session.add(item_model)
            else:
                 print(f"Skipping outfit item due to missing clothing item in current batch: outfit {outfit_id}, item {item_id}")
    
    # 提交事务
    try:
        print("[populate_test_data] Committing transaction...")
        await session.commit()
        print("[populate_test_data] Data committed successfully.")
    except Exception as e:
        print(f"Error during final commit in populate_test_data: {e}")
        try:
             await session.rollback()
        except Exception as rb_e:
             print(f"Error during rollback: {rb_e}")
        raise 