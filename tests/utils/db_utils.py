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
from sqlalchemy import create_engine, inspect, text, event
from uuid import uuid4, UUID
from datetime import datetime, date
from pathlib import Path # Import Path
import pytest # Import pytest for fixture
import json

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

# --- JSON Serializer Helper ---
def json_serializer_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError (f"Type {type(obj)} not serializable")

# --- Import Base for type hinting, models imported later dynamically --- 
try:
    # This import is primarily for type hinting if needed elsewhere
    from src.infrastructure.persistence.models import Base
except ImportError:
    print("Warning: Could not import Base for hinting at module level.")
    Base = None # Placeholder

# --- Use Absolute Path ---
# Get project root assuming db_utils.py is in tests/utils/
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_FILE_PATH = PROJECT_ROOT / "test.db" # Absolute path to test.db in project root
TEST_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE_PATH.as_posix()}"
TEST_SYNC_DATABASE_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}" # Synchronous URL

print(f"Using ASYNC database URL: {TEST_ASYNC_DATABASE_URL}")
print(f"Using SYNC database URL: {TEST_SYNC_DATABASE_URL}")

# --- Async Engine (for tests) --- 
async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    echo=True,
    # connect_args={"check_same_thread": False} # May not be needed with aiosqlite
    json_serializer=lambda obj: json.dumps(obj, default=json_serializer_default) 
)

# Event listener to enable foreign keys for SQLite connections
@event.listens_for(async_engine.sync_engine, "connect", insert=True)
def _enable_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key support for SQLite connections."""
    # Check if the driver is SQLite
    if async_engine.url.drivername.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON;")
            print("[DB Event] PRAGMA foreign_keys=ON executed.")
        finally:
            cursor.close()

# --- Sync Engine (for setup/teardown) ---
sync_engine = create_engine(
    TEST_SYNC_DATABASE_URL,
    echo=True,
    json_serializer=lambda obj: json.dumps(obj, default=json_serializer_default) 
)

# Also enable foreign keys for the synchronous engine used in setup/teardown
@event.listens_for(sync_engine, "connect")
def _sync_enable_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key support for SYNC SQLite connections."""
    if sync_engine.url.drivername.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON;")
            print("[DB Event Sync] PRAGMA foreign_keys=ON executed.")
        finally:
            cursor.close()

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
    raw_categories = generate_categories()
    clothing_items = []
    default_wardrobe_id = uuid4()
    default_owner_id = uuid4()

    # 1. 保存 Wardrobe
    from src.infrastructure.persistence.models import WardrobeModel, CategoryModel, ClothingItemModel, OutfitModel, OutfitItemModel
    wardrobe_model = WardrobeModel(id=default_wardrobe_id, owner_id=default_owner_id)
    session.add(wardrobe_model)
    try:
        await session.flush() # Flush to get the wardrobe ID persisted
        print("[populate_test_data] Wardrobe flushed.")
    except Exception as e:
        print(f"Error flushing wardrobe: {e}")
        await session.rollback()
        raise

    # 2. 保存父分类
    parent_categories_data = [cat for cat in raw_categories if cat["parent_id"] is None]
    parent_category_models = []
    for category_data in parent_categories_data:
        # Ensure ID is UUID, only convert if it's a string
        if isinstance(category_data.get('id'), str):
            category_data['id'] = UUID(category_data['id'])
        category_data['wardrobe_id'] = default_wardrobe_id
        model = CategoryModel(**category_data)
        session.add(model)
        parent_category_models.append(model)
    try:
        await session.flush() # Flush parent categories
        print("[populate_test_data] Parent categories flushed.")
    except Exception as e:
        print(f"Error flushing parent categories: {e}")
        await session.rollback()
        raise

    # 3. 保存子分类
    child_categories_data = [cat for cat in raw_categories if cat["parent_id"] is not None]
    child_category_models = []
    all_category_models = parent_category_models[:]
    for category_data in child_categories_data:
        # Ensure IDs are UUID, only convert if they are strings
        if isinstance(category_data.get('id'), str):
            category_data['id'] = UUID(category_data['id'])
        if isinstance(category_data.get('parent_id'), str):
            category_data['parent_id'] = UUID(category_data['parent_id'])
        category_data['wardrobe_id'] = default_wardrobe_id
        
        # Check if parent exists before adding
        if any(p_cat.id == category_data['parent_id'] for p_cat in parent_category_models):
            model = CategoryModel(**category_data)
            session.add(model)
            child_category_models.append(model)
            all_category_models.append(model)
        else:
            print(f"Skipping child category due to missing parent in batch: {category_data.get('name')}")
            
    try:
        await session.flush() # Flush child categories
        print("[populate_test_data] Child categories flushed.")
    except Exception as e:
        print(f"Error flushing child categories: {e}")
        await session.rollback()
        raise

    # 4. 生成并保存衣物
    clothing_item_models = []
    generated_clothing_data = [] # Store the generated data dictionaries
    for category_model in all_category_models:
        if category_model.parent_id is not None: 
            items_for_category = generate_clothing_items(category_model.id, count=3)
            for item_data in items_for_category:
                # Ensure IDs are UUID, only convert if they are strings
                if isinstance(item_data.get('id'), str):
                     item_data['id'] = UUID(item_data['id'])
                item_data['wardrobe_id'] = default_wardrobe_id
                item_data['category_id'] = category_model.id
                
                # Store the original data (should contain Python objects like dicts, datetime)
                generated_clothing_data.append(item_data.copy()) 

                # Create and add the model - Pass Python objects directly
                # Extract the float amount from the price dictionary
                price_amount = item_data['price'].get('amount') if isinstance(item_data.get('price'), dict) else item_data.get('price', 0.0)
                try:
                    price_amount = float(price_amount) if price_amount is not None else None
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert price {price_amount} to float for item {item_data.get('name')}. Setting to None.")
                    price_amount = None
                
                # Convert Dimension/Size objects to basic dict for JSON serialization
                dimension_dict = None 
                raw_dimension = item_data.get('dimension')
                if raw_dimension:
                    size_value = None
                    measurement = None
                    if isinstance(raw_dimension, dict):
                        # If it's a dict, try to extract values, potentially handling nested Size object
                        raw_size = raw_dimension.get('size')
                        if hasattr(raw_size, 'value'): # Check if size itself is a Size object
                            size_value = raw_size.value
                        elif isinstance(raw_size, str): # Or just a string value
                            size_value = raw_size
                        measurement = raw_dimension.get('measurement')
                    elif hasattr(raw_dimension, 'size') and hasattr(raw_dimension, 'measurement'):
                        # It's a Dimension object
                        size_value = raw_dimension.size.value if raw_dimension.size else None
                        measurement = raw_dimension.measurement
                    else:
                         print(f"Warning: Unknown dimension format {raw_dimension} for item {item_data.get('name')}. Setting dimension to None.")
                    
                    # Only create dict if we have valid data
                    if size_value is not None or measurement is not None:
                        dimension_dict = {
                            'size': size_value,
                            'measurement': measurement
                        }

                model = ClothingItemModel(
                    id=item_data['id'],
                    name=item_data['name'],
                    category_id=item_data['category_id'],
                    wardrobe_id=item_data['wardrobe_id'],
                    color=item_data['color'], 
                    dimension=dimension_dict, # Pass the serializable dict or None
                    brand=item_data['brand'], 
                    material=item_data['material'],
                    style=item_data['style'],
                    image_metadata=item_data['image_metadata'], 
                    price=price_amount, 
                    description=item_data.get('description'),
                    tags=item_data.get('tags', []), 
                    is_favorite=item_data.get('is_favorite', False),
                    version=item_data.get('version', 1),
                    created_at=item_data.get('created_at', datetime.now()),
                    updated_at=item_data.get('updated_at', datetime.now())
                )
                session.add(model)
                clothing_item_models.append(model)

    try:
        await session.flush() # Flush clothing items
        print("[populate_test_data] Clothing items flushed.")
    except Exception as e:
        print(f"Error flushing clothing items: {e}")
        await session.rollback()
        raise

    # 5. 生成并保存穿搭 (use generated_clothing_data)
    outfits_data = generate_outfits(clothing_items=generated_clothing_data, owner_id=default_owner_id, count=3)
    print("[populate_test_data] Saving outfits...")
    for outfit_data in outfits_data:
        outfit_items_data = outfit_data.pop("items")
        # Ensure ID is UUID, only convert if string
        if isinstance(outfit_data.get('id'), str):
            outfit_data['id'] = UUID(outfit_data['id'])
        outfit_data['owner_id'] = default_owner_id

        outfit_model = OutfitModel(**outfit_data)
        session.add(outfit_model)
        
        try:
            await session.flush()
        except Exception as e:
            print(f"Error flushing outfit {outfit_data.get('name')}: {e}")
            await session.rollback()
            continue

        outfit_id = outfit_model.id

        # 保存穿搭项
        for item_assoc_data in outfit_items_data:
            # Ensure IDs are UUID, only convert if string
            if isinstance(item_assoc_data.get('item_id'), str):
                 item_assoc_data['item_id'] = UUID(item_assoc_data['item_id'])
            item_assoc_data["outfit_id"] = outfit_id
            
            if any(c_item.id == item_assoc_data['item_id'] for c_item in clothing_item_models):
                item_model = OutfitItemModel(**item_assoc_data)
                session.add(item_model)
            else:
                 print(f"Skipping outfit item due to missing clothing item: outfit {outfit_id}, item {item_assoc_data['item_id']}")
    
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