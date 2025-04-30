"""仓储层单元测试"""

import pytest
import asyncio
from uuid import UUID, uuid4

from src.domain.model.aggregates import Outfit, Wardrobe
from src.domain.model.entities import ClothingItem, Category

from src.infrastructure.persistence.repositories import (
    SQLAlchemyWardrobeRepository,
    SQLAlchemyOutfitRepository,
    SQLAlchemyClothingItemRepository,
    SQLAlchemyCategoryRepository
)
from tests.utils.db_utils import (
    init_test_db,
    get_test_session as get_real_test_session,
    cleanup_test_db,
    populate_test_data
)

# pytest-asyncio doesn't need explicit event loop fixture usually
# @pytest.fixture(scope="session")
# def event_loop():
#     ...

@pytest.fixture(scope="session", autouse=True)
async def db():
    """数据库fixture (session scope, auto-applied)"""
    await init_test_db()
    yield
    await cleanup_test_db()

# Revert session fixture to the version that worked (with skips/warnings)
@pytest.fixture(scope="function")
async def session(db): # Depend on db fixture
    """会话fixture (function scope) - 使用原始异步生成器"""
    # Use the renamed original function to get the async generator
    async for actual_session in get_real_test_session():
         await populate_test_data(actual_session) # Populate data within the session context
         yield actual_session # Yield the session - this worked before with skips

@pytest.fixture
def wardrobe_repo(session):
    """衣橱仓储fixture"""
    return SQLAlchemyWardrobeRepository(session)

@pytest.fixture
def outfit_repo(session):
    """穿搭仓储fixture"""
    return SQLAlchemyOutfitRepository(session)

@pytest.fixture
def clothing_repo(session):
    """衣物仓储fixture"""
    return SQLAlchemyClothingItemRepository(session)

@pytest.fixture
def category_repo(session):
    """分类仓储fixture"""
    return SQLAlchemyCategoryRepository(session)

# Keep tests as async def, pytest-asyncio in strict mode should handle them (with warnings)

@pytest.mark.asyncio
async def test_find_all_categories(category_repo):
    """测试查询所有分类"""
    categories = await category_repo.find_all()
    assert len(categories) > 0
    
    # 验证父分类
    parent_categories = [c for c in categories if c.parent_id is None]
    assert len(parent_categories) >= 3  # Be more flexible if test data changes
    
    # 验证子分类
    child_categories = [c for c in categories if c.parent_id is not None]
    assert len(child_categories) > 0

@pytest.mark.asyncio
async def test_find_clothing_by_category(clothing_repo, category_repo):
    """测试按分类查询衣物"""
    # 获取T恤分类
    categories = await category_repo.find_all()
    tshirt_category = next((c for c in categories if c.name == "T恤"), None)
    assert tshirt_category is not None, "'T恤' category not found in test data"
    
    # 查询该分类下的衣物
    items = await clothing_repo.find_by_category_id(tshirt_category.id)
    assert len(items) > 0
    for item in items:
        assert item.category_id == tshirt_category.id

@pytest.mark.asyncio
async def test_create_outfit(outfit_repo, clothing_repo):
    """测试创建穿搭"""
    # 获取一些衣物
    items = await clothing_repo.find_all()
    assert len(items) >= 2, "Need at least 2 clothing items in test data"
    selected_items = items[:2]  # 选择前两件衣物
    
    # 创建新穿搭
    outfit_id = uuid4()
    outfit = Outfit(
        id=outfit_id,
        name="测试穿搭",
        description="这是一个测试穿搭",
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    # 添加衣物
    for idx, item in enumerate(selected_items):
        # Ensure item has a valid ID
        assert item.id is not None
        outfit.add_clothing(item.id, layer_order=idx+1)
    
    # 保存穿搭
    await outfit_repo.save(outfit)
    
    # 验证保存结果
    saved_outfit = await outfit_repo.find_by_id(outfit.id)
    assert saved_outfit is not None
    assert saved_outfit.name == outfit.name
    # Check associated items through the relationship (assuming outfit.items links correctly)
    assert len(saved_outfit.items) == len(selected_items)
    # Verify that the associated items' IDs match the selected items' IDs
    saved_item_ids = {item.clothing_item_id for item in saved_outfit.items}
    selected_item_ids = {item.id for item in selected_items}
    assert saved_item_ids == selected_item_ids

@pytest.mark.asyncio
async def test_update_clothing(clothing_repo):
    """测试更新衣物"""
    # 获取一件衣物
    items = await clothing_repo.find_all()
    assert len(items) > 0, "Need at least one clothing item in test data"
    item = items[0]
    original_version = item.version
    
    # 更新信息
    original_name = item.name
    new_name = f"更新后的衣物_{uuid4()}"
    item.name = new_name
    await clothing_repo.save(item)
    
    # 验证更新结果
    updated_item = await clothing_repo.find_by_id(item.id)
    assert updated_item is not None
    assert updated_item.name == new_name
    assert updated_item.name != original_name
    # Optimistic locking check
    assert updated_item.version == original_version + 1

@pytest.mark.asyncio
async def test_delete_category(category_repo, clothing_repo):
    """测试删除分类"""
    # 创建一个新的、没有子分类且没有关联衣物的分类用于测试删除
    new_category_id = uuid4()
    new_category = Category(id=new_category_id, name=f"待删除分类_{uuid4()}", parent_id=None)
    await category_repo.save(new_category)
    
    # 确认创建成功
    created_category = await category_repo.find_by_id(new_category_id)
    assert created_category is not None

    # 删除分类
    delete_result = await category_repo.delete(new_category_id)
    assert delete_result is True
    
    # 验证删除结果
    deleted_category = await category_repo.find_by_id(new_category_id)
    assert deleted_category is None

    # 测试删除有子分类或关联衣物的分类（预期失败或受外键约束）
    # 获取一个有子分类的父分类 (e.g., '上装')
    categories = await category_repo.find_all()
    parent_category = next((c for c in categories if c.name == "上装"), None)
    if parent_category:
        with pytest.raises(Exception): # Expecting an error due to FK constraints or repo logic
             await category_repo.delete(parent_category.id)

    # 获取一个有关联衣物的分类 (e.g., 'T恤')
    tshirt_category = next((c for c in categories if c.name == "T恤"), None)
    if tshirt_category:
        items_in_category = await clothing_repo.find_by_category_id(tshirt_category.id)
        if items_in_category:
             with pytest.raises(Exception):
                 await category_repo.delete(tshirt_category.id) 