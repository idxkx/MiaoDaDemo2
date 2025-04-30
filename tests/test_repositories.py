"""仓储层单元测试"""

import pytest
import asyncio
from uuid import UUID

from src.infrastructure.persistence.repositories import (
    SQLAlchemyWardrobeRepository,
    SQLAlchemyOutfitRepository,
    SQLAlchemyClothingItemRepository,
    SQLAlchemyCategoryRepository
)
from tests.utils.db_utils import (
    init_test_db,
    get_test_session,
    cleanup_test_db,
    populate_test_data
)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db():
    """数据库fixture"""
    await init_test_db()
    yield
    await cleanup_test_db()

@pytest.fixture(scope="function")
async def session():
    """会话fixture"""
    async for session in get_test_session():
        await populate_test_data(session)
        yield session

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

@pytest.mark.asyncio
async def test_find_all_categories(category_repo):
    """测试查询所有分类"""
    categories = await category_repo.find_all()
    assert len(categories) > 0
    
    # 验证父分类
    parent_categories = [c for c in categories if c.parent_id is None]
    assert len(parent_categories) == 3  # 上装、下装、鞋子
    
    # 验证子分类
    child_categories = [c for c in categories if c.parent_id is not None]
    assert len(child_categories) > 0

@pytest.mark.asyncio
async def test_find_clothing_by_category(clothing_repo, category_repo):
    """测试按分类查询衣物"""
    # 获取T恤分类
    categories = await category_repo.find_all()
    tshirt_category = next(c for c in categories if c.name == "T恤")
    
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
    selected_items = items[:2]  # 选择前两件衣物
    
    # 创建新穿搭
    from src.domain.model.aggregates import Outfit
    outfit = Outfit(
        id=UUID(int=1),
        name="测试穿搭",
        description="这是一个测试穿搭",
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    # 添加衣物
    for idx, item in enumerate(selected_items):
        outfit.add_clothing(item, layer_order=idx+1)
    
    # 保存穿搭
    await outfit_repo.save(outfit)
    
    # 验证保存结果
    saved_outfit = await outfit_repo.find_by_id(outfit.id)
    assert saved_outfit is not None
    assert saved_outfit.name == outfit.name
    assert len(saved_outfit.items) == len(selected_items)

@pytest.mark.asyncio
async def test_update_clothing(clothing_repo):
    """测试更新衣物"""
    # 获取一件衣物
    items = await clothing_repo.find_all()
    item = items[0]
    
    # 更新信息
    original_name = item.name
    new_name = "更新后的衣物"
    item.name = new_name
    await clothing_repo.save(item)
    
    # 验证更新结果
    updated_item = await clothing_repo.find_by_id(item.id)
    assert updated_item is not None
    assert updated_item.name == new_name
    assert updated_item.name != original_name
    assert updated_item.version > item.version  # 版本号应该增加

@pytest.mark.asyncio
async def test_delete_category(category_repo):
    """测试删除分类"""
    # 获取一个没有子分类的分类
    categories = await category_repo.find_all()
    category = next(c for c in categories if c.parent_id is not None)
    
    # 删除分类
    await category_repo.delete(category.id)
    
    # 验证删除结果
    deleted_category = await category_repo.find_by_id(category.id)
    assert deleted_category is None 