from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID, uuid4

from .entities import Entity, ClothingItem, Category
from .value_objects import ImageMetadata, Dimension, Color, Price, Brand, Material, Style
from .exceptions import OutfitItemLimitExceeded, InvalidOutfitConfiguration, DuplicateClothingItem

class AggregateRoot(Entity):
    """聚合根基类"""
    def __init__(self, id: UUID = None):
        super().__init__(id)
        self._domain_events = []
        self._version = 1  # 初始版本号为1

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
        if item.id in self._items:
            raise DuplicateClothingItem(f"衣物 {item.name} 已存在")
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
    MAX_ITEMS = 5  # 最大衣物数量

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
        # 检查数量限制
        if len(self._items) >= self.MAX_ITEMS:
            raise OutfitItemLimitExceeded(f"穿搭最多只能包含 {self.MAX_ITEMS} 件衣物")

        # 检查是否已有同类别的衣物
        for existing_item in self._items.values():
            if existing_item.category_id == item.category_id:
                raise InvalidOutfitConfiguration(f"已存在类别为 {item.category_id} 的衣物")

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

class UserRegistered(DomainEvent):
    def __init__(self, user_profile_id: UUID, user_id: UUID, username: str):
        super().__init__(user_profile_id)
        self.user_id = user_id
        self.username = username

class UserLoggedIn(DomainEvent):
    def __init__(self, user_profile_id: UUID, user_id: UUID):
        super().__init__(user_profile_id)
        self.user_id = user_id
        self.login_time = datetime.now()

class UserProfile(AggregateRoot):
    """用户聚合根"""
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        display_name: str,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ):
        super().__init__(id)
        self._user_id = user_id
        self._display_name = display_name
        self._bio = bio
        self._avatar_url = avatar_url
        self._favorites: Dict[UUID, UUID] = {}  # 收藏的Outfit ID映射
        self._following: List[UUID] = []  # 关注的用户ID列表
        self._followers: List[UUID] = []  # 粉丝用户ID列表
        self._style_preferences: List[str] = []  # 风格偏好
        self._color_preferences: List[Color] = []  # 颜色偏好
        self._last_login = datetime.now()

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def bio(self) -> Optional[str]:
        return self._bio

    @property
    def avatar_url(self) -> Optional[str]:
        return self._avatar_url

    @property
    def favorites(self) -> List[UUID]:
        return list(self._favorites.values())

    @property
    def following(self) -> List[UUID]:
        return self._following.copy()

    @property
    def followers(self) -> List[UUID]:
        return self._followers.copy()

    @property
    def style_preferences(self) -> List[str]:
        return self._style_preferences.copy()

    @property
    def color_preferences(self) -> List[Color]:
        return self._color_preferences.copy()

    @property
    def last_login(self) -> datetime:
        return self._last_login

    def update_profile(
        self,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> None:
        """更新个人资料"""
        if display_name:
            self._display_name = display_name
        if bio is not None:  # 允许将bio设置为空字符串
            self._bio = bio
        if avatar_url is not None:  # 允许将头像URL设置为空字符串
            self._avatar_url = avatar_url
        self._version += 1

    def add_favorite(self, outfit_id: UUID) -> None:
        """添加收藏"""
        if outfit_id not in self._favorites.values():
            # 使用uuid4()创建新的UUID
            self._favorites[uuid4()] = outfit_id
            self._version += 1

    def remove_favorite(self, outfit_id: UUID) -> None:
        """移除收藏"""
        to_remove = None
        for key, value in self._favorites.items():
            if value == outfit_id:
                to_remove = key
                break
        
        if to_remove:
            del self._favorites[to_remove]
            self._version += 1

    def follow_user(self, user_id: UUID) -> None:
        """关注用户"""
        if user_id != self._user_id and user_id not in self._following:
            self._following.append(user_id)
            self._version += 1

    def unfollow_user(self, user_id: UUID) -> None:
        """取消关注用户"""
        if user_id in self._following:
            self._following.remove(user_id)
            self._version += 1

    def add_follower(self, user_id: UUID) -> None:
        """添加粉丝"""
        if user_id != self._user_id and user_id not in self._followers:
            self._followers.append(user_id)
            self._version += 1

    def remove_follower(self, user_id: UUID) -> None:
        """移除粉丝"""
        if user_id in self._followers:
            self._followers.remove(user_id)
            self._version += 1

    def add_style_preference(self, style: str) -> None:
        """添加风格偏好"""
        if style and style not in self._style_preferences:
            self._style_preferences.append(style)
            self._version += 1

    def remove_style_preference(self, style: str) -> None:
        """移除风格偏好"""
        if style in self._style_preferences:
            self._style_preferences.remove(style)
            self._version += 1

    def add_color_preference(self, color: Color) -> None:
        """添加颜色偏好"""
        if color and color not in self._color_preferences:
            self._color_preferences.append(color)
            self._version += 1

    def remove_color_preference(self, color: Color) -> None:
        """移除颜色偏好"""
        if color in self._color_preferences:
            self._color_preferences.remove(color)
            self._version += 1

    def record_login(self) -> None:
        """记录登录"""
        self._last_login = datetime.now()
        self._version += 1
        self.add_domain_event(UserLoggedIn(self.id, self._user_id))

class OutfitRecommendation(AggregateRoot):
    """搭配推荐聚合根"""
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        occasion: str,
        season: str,
        weather: str,
        style_preference: Optional[str] = None
    ):
        super().__init__(id)
        self._user_id = user_id
        self._occasion = occasion
        self._season = season
        self._weather = weather
        self._style_preference = style_preference
        self._recommended_outfits: List[UUID] = []  # 推荐的穿搭ID列表
        self._rejected_outfits: List[UUID] = []  # 被拒绝的穿搭ID列表
        self._accepted_outfits: List[UUID] = []  # 被接受的穿搭ID列表
        self._created_at = datetime.now()
        self._is_processed = False
        self._processing_time: Optional[float] = None

    @property
    def user_id(self) -> UUID:
        return self._user_id

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
    def style_preference(self) -> Optional[str]:
        return self._style_preference

    @property
    def recommended_outfits(self) -> List[UUID]:
        return self._recommended_outfits.copy()

    @property
    def rejected_outfits(self) -> List[UUID]:
        return self._rejected_outfits.copy()

    @property
    def accepted_outfits(self) -> List[UUID]:
        return self._accepted_outfits.copy()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_processed(self) -> bool:
        return self._is_processed

    @property
    def processing_time(self) -> Optional[float]:
        return self._processing_time

    def add_recommended_outfit(self, outfit_id: UUID) -> None:
        """添加推荐的穿搭"""
        if outfit_id not in self._recommended_outfits:
            self._recommended_outfits.append(outfit_id)
            self._version += 1

    def clear_recommendations(self) -> None:
        """清除所有推荐"""
        self._recommended_outfits.clear()
        self._version += 1

    def accept_outfit(self, outfit_id: UUID) -> None:
        """接受推荐的穿搭"""
        if outfit_id in self._recommended_outfits and outfit_id not in self._accepted_outfits:
            self._accepted_outfits.append(outfit_id)
            self._version += 1

    def reject_outfit(self, outfit_id: UUID) -> None:
        """拒绝推荐的穿搭"""
        if outfit_id in self._recommended_outfits and outfit_id not in self._rejected_outfits:
            self._rejected_outfits.append(outfit_id)
            self._version += 1

    def mark_as_processed(self, processing_time: float) -> None:
        """标记为已处理"""
        self._is_processed = True
        self._processing_time = processing_time
        self._version += 1 