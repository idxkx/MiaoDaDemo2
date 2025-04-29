from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from .entities import Entity, ClothingItem, Category
from .value_objects import ImageMetadata, Dimension, Color, Price, Brand, Material, Style

class AggregateRoot(Entity):
    """聚合根基类"""
    def __init__(self, id: UUID = None):
        super().__init__(id)
        self._domain_events = []

    def add_domain_event(self, event: "DomainEvent"):
        """添加领域事件"""
        self._domain_events.append(event)

    def clear_domain_events(self):
        """清除领域事件"""
        self._domain_events.clear()

class Wardrobe(AggregateRoot):
    """衣橱聚合根"""
    def __init__(self, id: UUID, owner_id: UUID):
        super().__init__(id)
        self._owner_id = owner_id
        self._items: Dict[UUID, ClothingItem] = {}
        self._categories: Dict[UUID, Category] = {}

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def items(self) -> List[ClothingItem]:
        return list(self._items.values())

    @property
    def categories(self) -> List[Category]:
        return list(self._categories.values())

    def add_item(self, item: ClothingItem) -> None:
        """添加衣物"""
        if item.id not in self._items:
            self._items[item.id] = item
            self._version += 1
            self.add_domain_event(ClothingItemAdded(self.id, item.id))

    def remove_item(self, item_id: UUID) -> None:
        """移除衣物"""
        if item_id in self._items:
            del self._items[item_id]
            self._version += 1
            self.add_domain_event(ClothingItemRemoved(self.id, item_id))

    def add_category(self, category: Category) -> None:
        """添加分类"""
        if category.id not in self._categories:
            self._categories[category.id] = category
            self._version += 1
            self.add_domain_event(CategoryAdded(self.id, category.id))

    def remove_category(self, category_id: UUID) -> None:
        """移除分类"""
        if category_id in self._categories:
            # 检查是否有衣物使用此分类
            for item in self._items.values():
                if item.category_id == category_id:
                    raise ValueError("Cannot remove category that has items")
            del self._categories[category_id]
            self._version += 1
            self.add_domain_event(CategoryRemoved(self.id, category_id))

    def get_items_by_category(self, category_id: UUID) -> List[ClothingItem]:
        """获取指定分类的衣物"""
        return [item for item in self._items.values() if item.category_id == category_id]

    def get_items_by_tags(self, tags: List[str]) -> List[ClothingItem]:
        """获取包含指定标签的衣物"""
        return [item for item in self._items.values() if any(tag in item.tags for tag in tags)]

class Outfit(AggregateRoot):
    """穿搭组合聚合根"""
    def __init__(
        self,
        id: UUID,
        name: str,
        owner_id: UUID,
        occasion: str,
        season: str,
        weather: str
    ):
        super().__init__(id)
        self._name = name
        self._owner_id = owner_id
        self._occasion = occasion
        self._season = season
        self._weather = weather
        self._items: Dict[UUID, ClothingItem] = {}
        self._layer_order: Dict[UUID, int] = {}
        self._rating: float = 0.0
        self._is_favorite = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def occasion(self) -> str:
        return self._occasion

    @property
    def season(self) -> str:
        return self._season

    @property
    def weather(self) -> str:
        return self._weather

    @property
    def items(self) -> List[ClothingItem]:
        return list(self._items.values())

    @property
    def rating(self) -> float:
        return self._rating

    @property
    def is_favorite(self) -> bool:
        return self._is_favorite

    def add_item(self, item: ClothingItem, layer: int) -> None:
        """添加衣物"""
        if item.id not in self._items:
            self._items[item.id] = item
            self._layer_order[item.id] = layer
            self._version += 1
            self.add_domain_event(OutfitItemAdded(self.id, item.id))

    def remove_item(self, item_id: UUID) -> None:
        """移除衣物"""
        if item_id in self._items:
            del self._items[item_id]
            del self._layer_order[item_id]
            self._version += 1
            self.add_domain_event(OutfitItemRemoved(self.id, item_id))

    def update_layer(self, item_id: UUID, layer: int) -> None:
        """更新穿搭层次"""
        if item_id in self._items:
            self._layer_order[item_id] = layer
            self._version += 1

    def rate(self, rating: float) -> None:
        """评分"""
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        self._rating = rating
        self._version += 1

    def toggle_favorite(self) -> None:
        """切换收藏状态"""
        self._is_favorite = not self._is_favorite
        self._version += 1
        if self._is_favorite:
            self.add_domain_event(OutfitFavorited(self.id))
        else:
            self.add_domain_event(OutfitUnfavorited(self.id))

# 领域事件
class DomainEvent:
    """领域事件基类"""
    def __init__(self, aggregate_id: UUID):
        self.aggregate_id = aggregate_id
        self.occurred_on = datetime.now()

class ClothingItemAdded(DomainEvent):
    def __init__(self, wardrobe_id: UUID, item_id: UUID):
        super().__init__(wardrobe_id)
        self.item_id = item_id

class ClothingItemRemoved(DomainEvent):
    def __init__(self, wardrobe_id: UUID, item_id: UUID):
        super().__init__(wardrobe_id)
        self.item_id = item_id

class CategoryAdded(DomainEvent):
    def __init__(self, wardrobe_id: UUID, category_id: UUID):
        super().__init__(wardrobe_id)
        self.category_id = category_id

class CategoryRemoved(DomainEvent):
    def __init__(self, wardrobe_id: UUID, category_id: UUID):
        super().__init__(wardrobe_id)
        self.category_id = category_id

class OutfitItemAdded(DomainEvent):
    def __init__(self, outfit_id: UUID, item_id: UUID):
        super().__init__(outfit_id)
        self.item_id = item_id

class OutfitItemRemoved(DomainEvent):
    def __init__(self, outfit_id: UUID, item_id: UUID):
        super().__init__(outfit_id)
        self.item_id = item_id

class OutfitFavorited(DomainEvent):
    def __init__(self, outfit_id: UUID):
        super().__init__(outfit_id)

class OutfitUnfavorited(DomainEvent):
    def __init__(self, outfit_id: UUID):
        super().__init__(outfit_id) 