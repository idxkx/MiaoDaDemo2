from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from .value_objects import ImageMetadata, Dimension, Color, Price, Brand, Material, Style, Size

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

class Tag(Entity):
    """标签实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        category: str,
        description: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._category = category
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def description(self) -> Optional[str]:
        return self._description

    def update_description(self, description: str) -> None:
        """更新描述"""
        self._description = description
        self._version += 1

class ClothingItem(Entity):
    """衣物实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        category_id: UUID,
        color: Color,
        size: Size,
        brand: Brand,
        material: Material,
        purchase_date: datetime,
        price: float,
        description: Optional[str] = None,
        image_url: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._category_id = category_id
        self._color = color
        self._size = size
        self._brand = brand
        self._material = material
        self._purchase_date = purchase_date
        self._price = price
        self._description = description
        self._image_url = image_url
        self._tags: List[Tag] = []
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
    def size(self) -> Size:
        return self._size

    @property
    def brand(self) -> Brand:
        return self._brand

    @property
    def material(self) -> Material:
        return self._material

    @property
    def purchase_date(self) -> datetime:
        return self._purchase_date

    @property
    def price(self) -> float:
        return self._price

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def tags(self) -> List[Tag]:
        return self._tags.copy()

    @property
    def is_favorite(self) -> bool:
        return self._is_favorite

    def add_tag(self, tag: Tag) -> None:
        """添加标签"""
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self._version += 1

    def remove_tag(self, tag_id: UUID) -> None:
        """移除标签"""
        self._tags = [tag for tag in self._tags if tag.id != tag_id]
        self._version += 1

    def toggle_favorite(self) -> None:
        """切换收藏状态"""
        self._is_favorite = not self._is_favorite
        self._version += 1

    def update_image_url(self, image_url: str) -> None:
        """更新图片URL"""
        self._image_url = image_url
        self._version += 1

    def update_price(self, price: float) -> None:
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

class User(Entity):
    """用户实体"""
    def __init__(
        self,
        id: UUID,
        username: str,
        email: str,
        password_hash: str,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        gender: Optional[str] = None,
        birth_date: Optional[datetime] = None
    ):
        super().__init__(id)
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._nickname = nickname or username
        self._avatar_url = avatar_url
        self._gender = gender
        self._birth_date = birth_date
        self._is_active = True
        self._last_login = None
        self._preferences = {}

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def avatar_url(self) -> Optional[str]:
        return self._avatar_url

    @property
    def gender(self) -> Optional[str]:
        return self._gender

    @property
    def birth_date(self) -> Optional[datetime]:
        return self._birth_date

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login

    @property
    def preferences(self) -> dict:
        return self._preferences.copy()

    def update_nickname(self, nickname: str) -> None:
        """更新昵称"""
        self._nickname = nickname
        self._version += 1

    def update_avatar(self, avatar_url: str) -> None:
        """更新头像"""
        self._avatar_url = avatar_url
        self._version += 1

    def update_email(self, email: str) -> None:
        """更新邮箱"""
        self._email = email
        self._version += 1

    def update_password(self, password_hash: str) -> None:
        """更新密码哈希"""
        self._password_hash = password_hash
        self._version += 1

    def set_preference(self, key: str, value) -> None:
        """设置用户偏好"""
        self._preferences[key] = value
        self._version += 1

    def remove_preference(self, key: str) -> None:
        """移除用户偏好"""
        if key in self._preferences:
            del self._preferences[key]
            self._version += 1

    def deactivate(self) -> None:
        """停用账户"""
        self._is_active = False
        self._version += 1

    def activate(self) -> None:
        """激活账户"""
        self._is_active = True
        self._version += 1

    def record_login(self) -> None:
        """记录登录"""
        self._last_login = datetime.now()
        self._version += 1

class Comment(Entity):
    """评论实体"""
    def __init__(
        self,
        id: UUID,
        content: str,
        user_id: UUID,
        target_id: UUID,
        target_type: str,  # 'outfit', 'clothing', 等
        parent_id: Optional[UUID] = None
    ):
        super().__init__(id)
        self._content = content
        self._user_id = user_id
        self._target_id = target_id
        self._target_type = target_type
        self._parent_id = parent_id
        self._likes_count = 0
        self._is_deleted = False

    @property
    def content(self) -> str:
        return self._content

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def target_id(self) -> UUID:
        return self._target_id

    @property
    def target_type(self) -> str:
        return self._target_type

    @property
    def parent_id(self) -> Optional[UUID]:
        return self._parent_id

    @property
    def likes_count(self) -> int:
        return self._likes_count

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def edit_content(self, content: str) -> None:
        """编辑评论内容"""
        if self._is_deleted:
            raise ValueError("已删除的评论不能编辑")
        self._content = content
        self._version += 1

    def add_like(self) -> None:
        """增加点赞"""
        if not self._is_deleted:
            self._likes_count += 1
            self._version += 1

    def remove_like(self) -> None:
        """减少点赞"""
        if not self._is_deleted and self._likes_count > 0:
            self._likes_count -= 1
            self._version += 1

    def delete(self) -> None:
        """删除评论（软删除）"""
        self._is_deleted = True
        self._version += 1

    def restore(self) -> None:
        """恢复评论"""
        self._is_deleted = False
        self._version += 1

class Favorite(Entity):
    """收藏实体"""
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        target_id: UUID,
        target_type: str,  # 'outfit', 'clothing', 等
        note: Optional[str] = None
    ):
        super().__init__(id)
        self._user_id = user_id
        self._target_id = target_id
        self._target_type = target_type
        self._note = note
        self._is_public = True
        self._tags: List[str] = []

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def target_id(self) -> UUID:
        return self._target_id

    @property
    def target_type(self) -> str:
        return self._target_type

    @property
    def note(self) -> Optional[str]:
        return self._note

    @property
    def is_public(self) -> bool:
        return self._is_public

    @property
    def tags(self) -> List[str]:
        return self._tags.copy()

    def update_note(self, note: str) -> None:
        """更新收藏备注"""
        self._note = note
        self._version += 1

    def toggle_public(self) -> None:
        """切换公开/私密状态"""
        self._is_public = not self._is_public
        self._version += 1

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

    def clear_tags(self) -> None:
        """清空所有标签"""
        if self._tags:
            self._tags.clear()
            self._version += 1 