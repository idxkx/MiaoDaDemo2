from typing import List, Optional, Type, TypeVar
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.repositories.interfaces import (
    WardrobeRepository,
    OutfitRepository,
    ClothingItemRepository,
    CategoryRepository
)
from src.domain.model.aggregates import Wardrobe, Outfit
from src.domain.model.entities import ClothingItem, Category
from src.domain.model.value_objects import (
    ImageMetadata,
    Dimension,
    Color,
    Price,
    Brand,
    Material,
    Style
)
from .models import (
    WardrobeModel,
    OutfitModel,
    OutfitItemModel,
    ClothingItemModel,
    CategoryModel
)

T = TypeVar('T')
M = TypeVar('M')

class SQLAlchemyRepository:
    """SQLAlchemy仓储基类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_json(self, value_object: object) -> dict:
        """将值对象转换为JSON"""
        return {
            key.lstrip('_'): value
            for key, value in value_object.__dict__.items()
        }

    def _from_json(self, json_data: dict, value_object_class: Type[T]) -> T:
        """从JSON创建值对象"""
        return value_object_class(**json_data)

class SQLAlchemyWardrobeRepository(WardrobeRepository, SQLAlchemyRepository):
    """衣橱仓储实现"""
    
    async def save(self, wardrobe: Wardrobe) -> None:
        model = WardrobeModel(
            id=wardrobe.id,
            owner_id=wardrobe.owner_id,
            version=wardrobe.version
        )
        self.session.add(model)
        await self.session.flush()
        
        # 保存分类
        for category in wardrobe.categories:
            category_model = await self._save_category(category, wardrobe.id)
        
        # 保存衣物
        for item in wardrobe.items:
            item_model = await self._save_clothing_item(item, wardrobe.id)
    
    async def delete(self, id: UUID) -> None:
        await self.session.execute(
            select(WardrobeModel).where(WardrobeModel.id == id)
        )
    
    async def find_by_id(self, id: UUID) -> Optional[Wardrobe]:
        result = await self.session.execute(
            select(WardrobeModel)
            .options(selectinload(WardrobeModel.categories))
            .options(selectinload(WardrobeModel.items))
            .where(WardrobeModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def find_all(self) -> List[Wardrobe]:
        result = await self.session.execute(
            select(WardrobeModel)
            .options(selectinload(WardrobeModel.categories))
            .options(selectinload(WardrobeModel.items))
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_by_owner_id(self, owner_id: UUID) -> Optional[Wardrobe]:
        result = await self.session.execute(
            select(WardrobeModel)
            .options(selectinload(WardrobeModel.categories))
            .options(selectinload(WardrobeModel.items))
            .where(WardrobeModel.owner_id == owner_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    def _to_domain(self, model: WardrobeModel) -> Wardrobe:
        """将数据模型转换为领域模型"""
        wardrobe = Wardrobe(model.id, model.owner_id)
        wardrobe._version = model.version
        wardrobe._created_at = model.created_at
        wardrobe._updated_at = model.updated_at
        
        # 转换分类
        for category_model in model.categories:
            category = self._category_to_domain(category_model)
            wardrobe.add_category(category)
        
        # 转换衣物
        for item_model in model.items:
            item = self._clothing_item_to_domain(item_model)
            wardrobe.add_item(item)
        
        return wardrobe
    
    async def _save_category(self, category: Category, wardrobe_id: UUID) -> CategoryModel:
        """保存分类"""
        model = CategoryModel(
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
            wardrobe_id=wardrobe_id,
            description=category.description,
            version=category.version
        )
        self.session.add(model)
        return model
    
    async def _save_clothing_item(self, item: ClothingItem, wardrobe_id: UUID) -> ClothingItemModel:
        """保存衣物"""
        model = ClothingItemModel(
            id=item.id,
            name=item.name,
            category_id=item.category_id,
            wardrobe_id=wardrobe_id,
            color=self._to_json(item.color),
            dimension=self._to_json(item.dimension),
            brand=self._to_json(item.brand),
            material=self._to_json(item.material),
            style=self._to_json(item.style),
            image_metadata=self._to_json(item.image_metadata),
            price=self._to_json(item.price) if item.price else None,
            description=item.description,
            tags=item.tags,
            is_favorite=item.is_favorite,
            version=item.version
        )
        self.session.add(model)
        return model
    
    def _category_to_domain(self, model: CategoryModel) -> Category:
        """将分类数据模型转换为领域模型"""
        category = Category(
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            description=model.description
        )
        category._version = model.version
        category._created_at = model.created_at
        category._updated_at = model.updated_at
        return category
    
    def _clothing_item_to_domain(self, model: ClothingItemModel) -> ClothingItem:
        """将衣物数据模型转换为领域模型"""
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            color=self._from_json(model.color, Color),
            dimension=self._from_json(model.dimension, Dimension),
            brand=self._from_json(model.brand, Brand),
            material=self._from_json(model.material, Material),
            style=self._from_json(model.style, Style),
            image_metadata=self._from_json(model.image_metadata, ImageMetadata),
            price=self._from_json(model.price, Price) if model.price else None,
            description=model.description
        )
        item._tags = model.tags
        item._is_favorite = model.is_favorite
        item._version = model.version
        item._created_at = model.created_at
        item._updated_at = model.updated_at
        return item

class SQLAlchemyOutfitRepository(OutfitRepository, SQLAlchemyRepository):
    """穿搭组合仓储实现"""
    
    async def save(self, outfit: Outfit) -> None:
        model = OutfitModel(
            id=outfit.id,
            name=outfit.name,
            owner_id=outfit.owner_id,
            occasion=outfit.occasion,
            season=outfit.season,
            weather=outfit.weather,
            rating=outfit.rating,
            is_favorite=outfit.is_favorite,
            version=outfit.version
        )
        self.session.add(model)
        await self.session.flush()
        
        # 保存穿搭项
        for item_id, layer in outfit._layer_order.items():
            item_model = OutfitItemModel(
                outfit_id=outfit.id,
                item_id=item_id,
                layer=layer
            )
            self.session.add(item_model)
    
    async def delete(self, id: UUID) -> None:
        await self.session.execute(
            select(OutfitModel).where(OutfitModel.id == id)
        )
    
    async def find_by_id(self, id: UUID) -> Optional[Outfit]:
        result = await self.session.execute(
            select(OutfitModel)
            .options(selectinload(OutfitModel.items).selectinload(OutfitItemModel.item))
            .where(OutfitModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def find_all(self) -> List[Outfit]:
        result = await self.session.execute(
            select(OutfitModel)
            .options(selectinload(OutfitModel.items).selectinload(OutfitItemModel.item))
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_by_owner_id(self, owner_id: UUID) -> List[Outfit]:
        result = await self.session.execute(
            select(OutfitModel)
            .options(selectinload(OutfitModel.items).selectinload(OutfitItemModel.item))
            .where(OutfitModel.owner_id == owner_id)
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_favorites_by_owner_id(self, owner_id: UUID) -> List[Outfit]:
        result = await self.session.execute(
            select(OutfitModel)
            .options(selectinload(OutfitModel.items).selectinload(OutfitItemModel.item))
            .where(OutfitModel.owner_id == owner_id)
            .where(OutfitModel.is_favorite == True)
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    def _to_domain(self, model: OutfitModel) -> Outfit:
        """将数据模型转换为领域模型"""
        outfit = Outfit(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            occasion=model.occasion,
            season=model.season,
            weather=model.weather
        )
        outfit._rating = model.rating
        outfit._is_favorite = model.is_favorite
        outfit._version = model.version
        outfit._created_at = model.created_at
        outfit._updated_at = model.updated_at
        
        # 转换穿搭项
        for item_model in model.items:
            clothing_item = self._clothing_item_to_domain(item_model.item)
            outfit.add_item(clothing_item, item_model.layer)
        
        return outfit
    
    def _clothing_item_to_domain(self, model: ClothingItemModel) -> ClothingItem:
        """将衣物数据模型转换为领域模型"""
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            color=self._from_json(model.color, Color),
            dimension=self._from_json(model.dimension, Dimension),
            brand=self._from_json(model.brand, Brand),
            material=self._from_json(model.material, Material),
            style=self._from_json(model.style, Style),
            image_metadata=self._from_json(model.image_metadata, ImageMetadata),
            price=self._from_json(model.price, Price) if model.price else None,
            description=model.description
        )
        item._tags = model.tags
        item._is_favorite = model.is_favorite
        item._version = model.version
        item._created_at = model.created_at
        item._updated_at = model.updated_at
        return item

class SQLAlchemyClothingItemRepository(ClothingItemRepository, SQLAlchemyRepository):
    """衣物仓储实现"""
    
    async def save(self, item: ClothingItem) -> None:
        model = ClothingItemModel(
            id=item.id,
            name=item.name,
            category_id=item.category_id,
            wardrobe_id=item.wardrobe_id,
            color=self._to_json(item.color),
            dimension=self._to_json(item.dimension),
            brand=self._to_json(item.brand),
            material=self._to_json(item.material),
            style=self._to_json(item.style),
            image_metadata=self._to_json(item.image_metadata),
            price=self._to_json(item.price) if item.price else None,
            description=item.description,
            tags=item.tags,
            is_favorite=item.is_favorite,
            version=item.version
        )
        self.session.add(model)
    
    async def delete(self, id: UUID) -> None:
        await self.session.execute(
            select(ClothingItemModel).where(ClothingItemModel.id == id)
        )
    
    async def find_by_id(self, id: UUID) -> Optional[ClothingItem]:
        result = await self.session.execute(
            select(ClothingItemModel).where(ClothingItemModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def find_all(self) -> List[ClothingItem]:
        result = await self.session.execute(select(ClothingItemModel))
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_by_category(self, category_id: UUID) -> List[ClothingItem]:
        result = await self.session.execute(
            select(ClothingItemModel).where(ClothingItemModel.category_id == category_id)
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_by_tags(self, tags: List[str]) -> List[ClothingItem]:
        # 注意：这里的实现可能需要根据具体的数据库类型进行优化
        result = await self.session.execute(select(ClothingItemModel))
        items = []
        for model in result.scalars():
            if any(tag in model.tags for tag in tags):
                items.append(self._to_domain(model))
        return items
    
    async def find_favorites(self) -> List[ClothingItem]:
        result = await self.session.execute(
            select(ClothingItemModel).where(ClothingItemModel.is_favorite == True)
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    def _to_domain(self, model: ClothingItemModel) -> ClothingItem:
        """将数据模型转换为领域模型"""
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            color=self._from_json(model.color, Color),
            dimension=self._from_json(model.dimension, Dimension),
            brand=self._from_json(model.brand, Brand),
            material=self._from_json(model.material, Material),
            style=self._from_json(model.style, Style),
            image_metadata=self._from_json(model.image_metadata, ImageMetadata),
            price=self._from_json(model.price, Price) if model.price else None,
            description=model.description
        )
        item._tags = model.tags
        item._is_favorite = model.is_favorite
        item._version = model.version
        item._created_at = model.created_at
        item._updated_at = model.updated_at
        return item

class SQLAlchemyCategoryRepository(CategoryRepository, SQLAlchemyRepository):
    """分类仓储实现"""
    
    async def save(self, category: Category) -> None:
        model = CategoryModel(
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
            description=category.description,
            version=category.version
        )
        self.session.add(model)
    
    async def delete(self, id: UUID) -> None:
        await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == id)
        )
    
    async def find_by_id(self, id: UUID) -> Optional[Category]:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.children))
            .where(CategoryModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def find_all(self) -> List[Category]:
        result = await self.session.execute(
            select(CategoryModel).options(selectinload(CategoryModel.children))
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    async def find_by_parent_id(self, parent_id: Optional[UUID]) -> List[Category]:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.children))
            .where(CategoryModel.parent_id == parent_id)
        )
        return [self._to_domain(model) for model in result.scalars()]
    
    def _to_domain(self, model: CategoryModel) -> Category:
        """将数据模型转换为领域模型"""
        category = Category(
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            description=model.description
        )
        category._version = model.version
        category._created_at = model.created_at
        category._updated_at = model.updated_at
        
        # 添加子分类ID
        for child in model.children:
            category.add_subcategory(child.id)
        
        return category 