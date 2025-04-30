"""仓储层单元测试"""

import pytest
import asyncio
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
import sqlalchemy # Import sqlalchemy

# Import domain models needed for tests
from src.domain.model.aggregates import Outfit, Wardrobe
from src.domain.model.entities import ClothingItem, Category

# Import repositories to instantiate in tests
from src.infrastructure.persistence.repositories import (
    SQLAlchemyWardrobeRepository,
    SQLAlchemyOutfitRepository,
    SQLAlchemyClothingItemRepository,
    SQLAlchemyCategoryRepository
)
# Import db utils for setup/teardown and session factory
from tests.utils.db_utils import (
    # Remove unused direct imports of setup/teardown functions
    # init_test_db, 
    async_session, # Import the sessionmaker factory
    # cleanup_test_db, 
    populate_test_data
)

# REMOVE the explicit db fixture definition here, 
# as the one in db_utils is autouse=True and handles setup/teardown.
# @pytest.fixture(scope="function", autouse=True)
# async def db():
#     """数据库fixture (function scope, auto-applied)"""
#     await init_test_db()
#     yield
#     await cleanup_test_db()

# Session and Repo fixtures are removed

@pytest.mark.asyncio
async def test_find_all_categories(db): # Depend on db fixture only
    """测试查询所有分类"""
    async with async_session() as session: # Create session inside test using the factory
        category_repo = SQLAlchemyCategoryRepository(session) # Create repo inside test
        await populate_test_data(session) # Pass the created session
        categories = await category_repo.find_all()
        assert len(categories) > 0
        parent_categories = [c for c in categories if c.parent_id is None]
        assert len(parent_categories) >= 3
        child_categories = [c for c in categories if c.parent_id is not None]
        assert len(child_categories) > 0

@pytest.mark.asyncio
async def test_find_clothing_by_category(db):
    """测试根据分类查找衣物"""
    async with async_session() as session:
        category_repo = SQLAlchemyCategoryRepository(session)
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session)

        # Find a subcategory
        all_categories = await category_repo.find_all()
        subcategory = next((c for c in all_categories if c.parent_id is not None), None)
        assert subcategory is not None, "Need a subcategory to test"

        # Use the correct method name
        items = await clothing_repo.find_by_category(subcategory.id) 
        assert isinstance(items, list)
        # We expect 3 items per subcategory based on populate_test_data
        assert len(items) >= 3, "Expected at least 3 items for the subcategory"
        for item in items:
            assert item.category_id == subcategory.id

@pytest.mark.asyncio
async def test_create_outfit(db):
    """测试创建穿搭"""
    async with async_session() as session:
        outfit_repo = SQLAlchemyOutfitRepository(session)
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session)
        
        # Find clothing items from *different* categories
        all_items = await clothing_repo.find_all()
        items_by_category = {}
        for item in all_items:
            if item.category_id not in items_by_category:
                items_by_category[item.category_id] = item
        
        selected_items = list(items_by_category.values())[:3] # Take up to 3 items from different categories
        if len(selected_items) < 2:
             pytest.skip("Skipping outfit creation test: Need at least 2 items from different categories.")

        outfit_id = uuid4()
        outfit = Outfit(
            id=outfit_id,
            name="测试穿搭_不同类别",
            occasion="daily",
            season="spring",
            weather="sunny",
            owner_id=uuid4() # Add owner_id if required by Outfit
        )
        
        # Add items with layers
        for idx, item in enumerate(selected_items):
            assert item.id is not None
            outfit.add_item(item, layer=idx+1) # Pass the item object
            
        await outfit_repo.save(outfit)
        
        # Verify outfit creation
        created_outfit = await outfit_repo.find_by_id(outfit_id)
        assert created_outfit is not None
        assert created_outfit.id == outfit_id
        assert created_outfit.name == "测试穿搭_不同类别"
        assert len(created_outfit.items) == len(selected_items)
        
        # Verify items are correctly associated
        retrieved_item_ids = {item.id for item in created_outfit.items}
        selected_item_ids = {item.id for item in selected_items}
        assert retrieved_item_ids == selected_item_ids

@pytest.mark.asyncio
async def test_update_clothing(db):
    """测试更新衣物"""
    async with async_session() as session:
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session)
        items = await clothing_repo.find_all()
        assert len(items) > 0, "Need at least one clothing item in test data"
        item = items[0] # Assuming domain ClothingItem is returned
        original_version = item.version
        original_name = item.name
        new_name = f"更新后的衣物_{uuid4()}"
        # Update the domain object
        item.change_name(new_name)
        item._is_favorite = True
        await clothing_repo.save(item) # Pass the updated domain object
        # Re-fetch to verify
        updated_item = await clothing_repo.find_by_id(item.id)
        assert updated_item is not None
        assert updated_item.name == new_name
        assert updated_item.name != original_name
        assert updated_item.version == original_version + 1

@pytest.mark.asyncio
async def test_delete_category(db):
    """测试删除分类（包括约束）"""
    async with async_session() as session:
        category_repo = SQLAlchemyCategoryRepository(session)
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session)

        # --- Test deleting a standalone category ---
        standalone_category_id = uuid4()
        # Find a wardrobe_id to use
        all_categories = await category_repo.find_all()
        if not all_categories:
             pytest.skip("Skipping delete test as no categories found to get wardrobe_id")
        test_wardrobe_id = all_categories[0].wardrobe_id
        
        standalone_category = Category(
            id=standalone_category_id,
            name=f"独立分类_{uuid4()}",
            parent_id=None,
            wardrobe_id=test_wardrobe_id
        )
        await category_repo.save(standalone_category)
        created_category = await category_repo.find_by_id(standalone_category_id)
        assert created_category is not None
        
        # 删除没有关联的分类应该成功
        delete_result = await category_repo.delete(standalone_category_id)
        assert delete_result is True
        deleted_category = await category_repo.find_by_id(standalone_category_id)
        assert deleted_category is None

        # --- Test deleting a category with children ---
        all_categories = await category_repo.find_all()
        parent_cat = next((c for c in all_categories if c.parent_id is None), None)
        assert parent_cat, "Need a parent category for constraint test"
        
        child_cats = await category_repo.find_by_parent_id(parent_cat.id)
        assert child_cats, f"Parent category {parent_cat.name} ({parent_cat.id}) should have children for the test"
        
        # 尝试删除有子分类的父分类 - 应该返回 False
        delete_result = await category_repo.delete(parent_cat.id)
        assert delete_result is False, "Should not be able to delete category with children"
        
        # 验证父分类和子分类仍然存在
        parent_check = await category_repo.find_by_id(parent_cat.id)
        assert parent_check is not None, "Parent category should still exist"
        child_cats_after = await category_repo.find_by_parent_id(parent_cat.id)
        assert len(child_cats_after) == len(child_cats), "Children categories should still exist"

        # --- Test deleting a category with associated items ---
        # 找到一个有关联衣物的分类
        all_items = await clothing_repo.find_all()
        if not all_items:
            pytest.skip("Need clothing items to test category deletion constraint")
        
        test_item = all_items[0]
        category_with_items = await category_repo.find_by_id(test_item.category_id)
        assert category_with_items is not None
        
        # 尝试删除有关联衣物的分类 - 应该返回 False
        delete_result = await category_repo.delete(category_with_items.id)
        assert delete_result is False, "Should not be able to delete category with items"
        
        # 验证分类和衣物仍然存在
        category_check = await category_repo.find_by_id(category_with_items.id)
        assert category_check is not None, "Category should still exist"
        items_check = await clothing_repo.find_by_category(category_with_items.id)
        assert len(items_check) > 0, "Items should still exist" 