from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from .value_objects import ImageMetadata, Dimension, Color, Price, Brand, Material, Style

class Entity:
    """实体基类"""
    def __init__(self, id: UUID = None):
        self._id = id or uuid4()
        self._version = 0
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def version(self) -> int:
        return self._version

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

class ClothingItem(Entity):
    """衣物实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        category_id: UUID,
        color: Color,
        dimension: Dimension,
        brand: Brand,
        material: Material,
        style: Style,
        image_metadata: ImageMetadata,
        price: Optional[Price] = None,
        description: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._category_id = category_id
        self._color = color
        self._dimension = dimension
        self._brand = brand
        self._material = material
        self._style = style
        self._image_metadata = image_metadata
        self._price = price
        self._description = description
        self._tags: List[str] = []
        self._is_favorite = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def category_id(self) -> UUID:
        return self._category_id

    @property
    def color(self) -> Color:
        return self._color

    @property
    def dimension(self) -> Dimension:
        return self._dimension

    @property
    def brand(self) -> Brand:
        return self._brand

    @property
    def material(self) -> Material:
        return self._material

    @property
    def style(self) -> Style:
        return self._style

    @property
    def image_metadata(self) -> ImageMetadata:
        return self._image_metadata

    @property
    def price(self) -> Optional[Price]:
        return self._price

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def tags(self) -> List[str]:
        return self._tags.copy()

    @property
    def is_favorite(self) -> bool:
        return self._is_favorite

    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self._version += 1

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self._tags:
            self._tags.remove(tag)
            self._version += 1

    def toggle_favorite(self) -> None:
        """切换收藏状态"""
        self._is_favorite = not self._is_favorite
        self._version += 1

    def update_image(self, image_metadata: ImageMetadata) -> None:
        """更新图片"""
        self._image_metadata = image_metadata
        self._version += 1

    def update_price(self, price: Price) -> None:
        """更新价格"""
        self._price = price
        self._version += 1

    def update_description(self, description: str) -> None:
        """更新描述"""
        self._description = description
        self._version += 1

class Category(Entity):
    """分类实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        parent_id: Optional[UUID] = None,
        description: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._parent_id = parent_id
        self._description = description
        self._subcategories: List[UUID] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent_id(self) -> Optional[UUID]:
        return self._parent_id

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def subcategories(self) -> List[UUID]:
        return self._subcategories.copy()

    def add_subcategory(self, category_id: UUID) -> None:
        """添加子分类"""
        if category_id not in self._subcategories:
            self._subcategories.append(category_id)
            self._version += 1

    def remove_subcategory(self, category_id: UUID) -> None:
        """移除子分类"""
        if category_id in self._subcategories:
            self._subcategories.remove(category_id)
            self._version += 1

    def update_description(self, description: str) -> None:
        """更新描述"""
        self._description = description
        self._version += 1 