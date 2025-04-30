"""仓储层单元测试"""

import pytest
import asyncio
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession

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
    """测试按分类查询衣物"""
    async with async_session() as session:
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        category_repo = SQLAlchemyCategoryRepository(session)
        await populate_test_data(session)
        categories = await category_repo.find_all()
        tshirt_category = next((c for c in categories if c.name == "T恤"), None)
        assert tshirt_category is not None, "'T恤' category not found in test data"
        items = await clothing_repo.find_by_category_id(tshirt_category.id)
        assert len(items) > 0
        for item in items:
            assert item.category_id == tshirt_category.id

@pytest.mark.asyncio
async def test_create_outfit(db):
    """测试创建穿搭"""
    async with async_session() as session:
        outfit_repo = SQLAlchemyOutfitRepository(session)
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session)
        items = await clothing_repo.find_all()
        assert len(items) >= 2, "Need at least 2 clothing items in test data"
        selected_items = items[:2]
        outfit_id = uuid4()
        # Assuming Outfit domain object creation is correct
        outfit = Outfit(
            id=outfit_id,
            name="测试穿搭",
            description="这是一个测试穿搭",
            occasion="daily",
            season="spring",
            weather="sunny",
            owner_id=uuid4() # Add owner_id if required by Outfit
        )
        for idx, item in enumerate(selected_items):
            assert item.id is not None
            outfit.add_clothing(item.id, layer_order=idx+1) # Assuming Outfit takes item ID
        await outfit_repo.save(outfit)
        saved_outfit = await outfit_repo.find_by_id(outfit.id)
        assert saved_outfit is not None
        assert saved_outfit.name == outfit.name
        # Assuming outfit.items relationship works for checking saved items
        assert len(saved_outfit.items) == len(selected_items)
        saved_item_ids = {item.clothing_item_id for item in saved_outfit.items}
        selected_item_ids = {item.id for item in selected_items}
        assert saved_item_ids == selected_item_ids

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
        item.name = new_name # Assuming domain object has setter or direct attribute access
        await clothing_repo.save(item) # Pass the updated domain object
        # Re-fetch to verify
        updated_item = await clothing_repo.find_by_id(item.id)
        assert updated_item is not None
        assert updated_item.name == new_name
        assert updated_item.name != original_name
        assert updated_item.version == original_version + 1

@pytest.mark.asyncio
async def test_delete_category(db):
    """测试删除分类"""
    async with async_session() as session:
        category_repo = SQLAlchemyCategoryRepository(session)
        clothing_repo = SQLAlchemyClothingItemRepository(session)
        await populate_test_data(session) # Ensure data exists

        # Create a new category specifically for deletion test
        new_category_id = uuid4()
        # Fetch a valid wardrobe_id from existing data or create one
        # Let's assume populate_test_data ensures at least one wardrobe exists
        # and we can somehow get its ID. This setup is fragile.
        # A better way would be a fixture that provides a test wardrobe.
        # For now, get one from the first category found.
        all_categories = await category_repo.find_all()
        if not all_categories:
             pytest.skip("Skipping delete test as no categories found to get wardrobe_id")
        wardrobe_id_for_test = all_categories[0].wardrobe_id # Get wardrobe_id from existing category

        new_category_domain = Category(id=new_category_id, name=f"待删除分类_{uuid4()}", parent_id=None, wardrobe_id=wardrobe_id_for_test) # Pass wardrobe_id
        await category_repo.save(new_category_domain)

        created_category = await category_repo.find_by_id(new_category_id)
        assert created_category is not None

        # Delete the newly created category
        delete_result = await category_repo.delete(new_category_id)
        assert delete_result is True

        deleted_category = await category_repo.find_by_id(new_category_id)
        assert deleted_category is None

        # --- Test deleting categories with constraints ---
        categories = await category_repo.find_all() # Re-fetch categories

        # Test deleting a category with children
        parent_category = next((c for c in categories if c.name == "上装" and any(sub.parent_id == c.id for sub in categories)), None)
        if parent_category:
            with pytest.raises(Exception): # Expecting an error due to FK constraints
                 await category_repo.delete(parent_category.id)

        # Test deleting a category with associated items
        tshirt_category = next((c for c in categories if c.name == "T恤"), None)
        if tshirt_category:
            items_in_category = await clothing_repo.find_by_category_id(tshirt_category.id)
            if items_in_category:
                 with pytest.raises(Exception): # Expecting an error due to FK constraints
                     await category_repo.delete(tshirt_category.id) 