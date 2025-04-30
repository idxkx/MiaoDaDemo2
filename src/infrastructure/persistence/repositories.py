from typing import List, Optional, Type, TypeVar
from uuid import UUID
import json
import re

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
    Style,
    Size
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
            price=item.price,
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
            wardrobe_id=model.wardrobe_id,
            parent_id=model.parent_id,
            description=model.description
        )
        category._version = model.version
        category._created_at = model.created_at
        category._updated_at = model.updated_at
        return category
    
    def _clothing_item_to_domain(self, model: ClothingItemModel) -> ClothingItem:
        """将衣物数据模型转换为领域模型"""
        # Parse dimension JSON from model
        dimension_data = json.loads(model.dimension) if isinstance(model.dimension, str) else model.dimension
        size_obj = Size(value=dimension_data.get('size', '')) # Create Size object
        dimension_obj = Dimension(size=dimension_data.get('size', ''), measurement=dimension_data.get('measurement')) # Create Dimension object
        
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            wardrobe_id=model.wardrobe_id,
            color=self._from_json(model.color, Color),
            size=size_obj, # Pass Size object
            dimension=dimension_obj, # Pass Dimension object
            brand=self._from_json(model.brand, Brand),
            material=self._from_json(model.material, Material),
            style=self._from_json(model.style, Style),
            # Pass purchase_date (using model.created_at as placeholder)
            purchase_date=model.created_at, 
            price=item.price,
            # Pass image_metadata object
            image_metadata=self._from_json(model.image_metadata, ImageMetadata),
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
        # Parse dimension JSON from model
        dimension_data = json.loads(model.dimension) if isinstance(model.dimension, str) else model.dimension
        size_obj = Size(value=dimension_data.get('size', '')) # Create Size object
        dimension_obj = Dimension(size=dimension_data.get('size', ''), measurement=dimension_data.get('measurement')) # Create Dimension object
        
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            wardrobe_id=model.wardrobe_id,
            color=self._from_json(model.color, Color),
            size=size_obj, # Pass Size object
            dimension=dimension_obj, # Pass Dimension object
            brand=self._from_json(model.brand, Brand),
            material=self._from_json(model.material, Material),
            style=self._from_json(model.style, Style),
            # Pass purchase_date (using model.created_at as placeholder)
            purchase_date=model.created_at, 
            price=model.price,
            # Pass image_metadata object
            image_metadata=self._from_json(model.image_metadata, ImageMetadata),
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
        """保存或更新衣物"""
        existing_model = await self.session.get(ClothingItemModel, item.id)
        
        # 准备序列化的数据
        size_value = item.size.value if item.size else "M"
        if not re.match(r"^(XS|S|M|L|XL|XXL|XXXL)$", size_value):
            size_value = "M"
            
        size_dict = {"value": size_value}
        dimension_dict = {
            "size": size_dict,
            "measurement": item.dimension.measurement if item.dimension else None
        }
        
        # 准备颜色数据
        color_data = {
            "name": item.color.name if item.color else "黑色",
            "hex_code": item.color.hex_code if item.color else "#000000"
        }
        
        # 准备其他值对象数据
        brand_data = {
            "name": item.brand.name if item.brand else "未知品牌",
            "country": item.brand.country if item.brand and hasattr(item.brand, 'country') else None
        }
        
        material_data = {
            "name": item.material.name if item.material else "未知材质",
            "composition": item.material.composition if item.material else {"未知": 100.0}
        }
        
        style_data = {
            "name": item.style.name if item.style else "休闲",
            "tags": item.style.tags if item.style else ["休闲"]
        }
        
        # 将所有值对象转换为 JSON 字符串
        serialized_data = {
            "color": json.dumps(color_data),
            "dimension": json.dumps(dimension_dict),
            "brand": json.dumps(brand_data),
            "material": json.dumps(material_data),
            "style": json.dumps(style_data),
            "image_metadata": json.dumps(self._to_json(item.image_metadata)) if item.image_metadata else "null",
            "tags": json.dumps(item.tags) if item.tags else "[]"
        }
        
        if existing_model:
            # Update existing model
            existing_model.name = item.name
            existing_model.category_id = item.category_id
            existing_model.wardrobe_id = item.wardrobe_id
            existing_model.color = serialized_data["color"]
            existing_model.dimension = serialized_data["dimension"]
            existing_model.brand = serialized_data["brand"]
            existing_model.material = serialized_data["material"]
            existing_model.style = serialized_data["style"]
            existing_model.image_metadata = serialized_data["image_metadata"]
            existing_model.price = item.price
            existing_model.description = item.description
            existing_model.tags = serialized_data["tags"]
            existing_model.is_favorite = item.is_favorite
            existing_model.version = item.version
            model_to_save = existing_model
        else:
            # Create new model
            model_to_save = ClothingItemModel(
                id=item.id,
                name=item.name,
                category_id=item.category_id,
                wardrobe_id=item.wardrobe_id,
                color=serialized_data["color"],
                dimension=serialized_data["dimension"],
                brand=serialized_data["brand"],
                material=serialized_data["material"],
                style=serialized_data["style"],
                image_metadata=serialized_data["image_metadata"],
                price=item.price,
                description=item.description,
                tags=serialized_data["tags"],
                is_favorite=item.is_favorite,
                version=item.version
            )
        self.session.add(model_to_save)
        await self.session.flush()
    
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
        """将衣物数据模型转换为领域模型"""
        # 解析 JSON 字符串为字典
        try:
            color_dict = json.loads(model.color)
            dimension_dict = json.loads(model.dimension)
            brand_dict = json.loads(model.brand)
            material_dict = json.loads(model.material)
            style_dict = json.loads(model.style)
            image_metadata_dict = json.loads(model.image_metadata)
            tags = json.loads(model.tags)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"JSON 解析错误: {e}")
            # 提供默认值
            color_dict = {"name": "黑色", "hex_code": "#000000"}
            dimension_dict = {"size": {"value": "M"}, "measurement": None}
            brand_dict = {"name": "未知品牌"}
            material_dict = {"name": "未知材质", "composition": {"未知": 100.0}}
            style_dict = {"name": "休闲", "tags": ["休闲"]}
            image_metadata_dict = {}
            tags = []
        
        # 创建 Color 对象
        try:
            color = Color(
                name=color_dict.get("name", "黑色"),
                hex_code=color_dict.get("hex_code", "#000000")
            )
        except (ValueError, KeyError, TypeError):
            color = Color(name="黑色", hex_code="#000000")
        
        # 从 dimension_dict 中提取 size 信息
        size_dict = dimension_dict.get("size", {})
        size_value = size_dict.get("value", "M") if isinstance(size_dict, dict) else "M"
        if not re.match(r"^(XS|S|M|L|XL|XXL|XXXL)$", size_value):
            size_value = "M"
        size_obj = Size(value=size_value)
        
        # 创建 Dimension 对象
        dimension_obj = Dimension(
            size=size_value,
            measurement=dimension_dict.get("measurement")
        )
        
        # 创建其他值对象
        try:
            brand = Brand(
                name=brand_dict.get("name", "未知品牌"),
                country=brand_dict.get("country")
            )
        except (ValueError, KeyError, TypeError):
            brand = Brand(name="未知品牌")
            
        try:
            material = Material(
                name=material_dict.get("name", "未知材质"),
                composition=material_dict.get("composition", {"未知": 100.0})
            )
        except (ValueError, KeyError, TypeError):
            material = Material(name="未知材质", composition={"未知": 100.0})
            
        try:
            style = Style(
                name=style_dict.get("name", "休闲"),
                tags=style_dict.get("tags", ["休闲"])
            )
        except (ValueError, KeyError, TypeError):
            style = Style(name="休闲", tags=["休闲"])
        
        item = ClothingItem(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            wardrobe_id=model.wardrobe_id,
            color=color,
            size=size_obj,
            dimension=dimension_obj,
            brand=brand,
            material=material,
            style=style,
            purchase_date=model.created_at,
            price=model.price,
            image_metadata=self._from_json(image_metadata_dict, ImageMetadata) if image_metadata_dict else None,
            description=model.description
        )
        item._tags = tags
        item._is_favorite = model.is_favorite
        item._version = model.version
        item._created_at = model.created_at
        item._updated_at = model.updated_at
        return item

class SQLAlchemyCategoryRepository(CategoryRepository, SQLAlchemyRepository):
    """分类仓储实现"""
    
    async def save(self, category: Category) -> None:
        """保存或更新分类"""
        # Try to find existing model
        existing_model = await self.session.get(CategoryModel, category.id)
        if existing_model:
            # Update existing model
            existing_model.name = category.name
            existing_model.parent_id = category.parent_id
            existing_model.description = category.description
            existing_model.version = category.version
            # Ensure wardrobe_id is updated if it changes (though unlikely for existing)
            existing_model.wardrobe_id = category.wardrobe_id 
            model_to_save = existing_model
        else:
            # Create new model
            model_to_save = CategoryModel(
                id=category.id,
                name=category.name,
                parent_id=category.parent_id,
                wardrobe_id=category.wardrobe_id, # Ensure wardrobe_id is passed here
                description=category.description,
                version=category.version
            )
        self.session.add(model_to_save)
        await self.session.flush()
    
    async def delete(self, id: UUID) -> bool:
        """删除分类
        
        在删除分类之前检查：
        1. 是否有子分类
        2. 是否有关联的衣物
        
        如果有任何关联数据，将引发 IntegrityError
        """
        # 首先检查是否存在子分类
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.parent_id == id)
        )
        if result.scalars().first():
            return False  # 有子分类，不能删除
            
        # 检查是否有关联的衣物
        result = await self.session.execute(
            select(ClothingItemModel).where(ClothingItemModel.category_id == id)
        )
        if result.scalars().first():
            return False  # 有关联衣物，不能删除
            
        # 如果没有关联数据，执行删除
        model = await self.session.get(CategoryModel, id)
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False
    
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
            wardrobe_id=model.wardrobe_id,
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