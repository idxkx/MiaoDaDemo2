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

    def to_dict(self) -> dict:
        """将 Tag 对象序列化为字典"""
        return {
            "id": str(self.id), # 将 UUID 转为字符串
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "version": self.version, # 通常不需要保存 version，但可以包含
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Tag':
        """从字典反序列化为 Tag 对象"""
        tag = cls(
            id=UUID(data['id']), # 从字符串转回 UUID
            name=data['name'],
            category=data['category'],
            description=data.get('description')
        )
        # 可选：恢复时间戳和版本（如果保存了）
        if 'created_at' in data:
            tag._created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            tag._updated_at = datetime.fromisoformat(data['updated_at'])
        if 'version' in data:
             tag._version = data['version']
        return tag

class ClothingItem(Entity):
    """衣物实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        category_id: UUID,
        wardrobe_id: UUID,
        color: Color,
        size: Size,
        brand: Brand,
        material: Material,
        purchase_date: datetime,
        price: float,
        dimension: Optional[Dimension] = None,
        style: Optional[Style] = None,
        image_metadata: Optional[ImageMetadata] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._category_id = category_id
        self._wardrobe_id = wardrobe_id
        self._color = color
        self._size = size
        self._brand = brand
        self._material = material
        self._purchase_date = purchase_date
        self._price = price
        self._dimension = dimension
        self._style = style
        self._image_metadata = image_metadata
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
    def wardrobe_id(self) -> UUID:
        return self._wardrobe_id

    @property
    def color(self) -> Color:
        return self._color

    @property
    def size(self) -> Size:
        return self._size

    @property
    def dimension(self) -> Optional[Dimension]:
        return self._dimension

    @property
    def brand(self) -> Brand:
        return self._brand

    @property
    def material(self) -> Material:
        return self._material

    @property
    def style(self) -> Optional[Style]:
        return self._style

    @property
    def image_metadata(self) -> Optional[ImageMetadata]:
        return self._image_metadata

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

    def change_name(self, new_name: str) -> None:
        """更改衣物名称"""
        if not new_name:
            raise ValueError("Name cannot be empty")
        self._name = new_name
        self._version += 1
        # Potential domain event can be added here

    def to_dict(self) -> dict:
        """将 ClothingItem 对象（包括 Tag）序列化为字典"""
        # 注意：Value Objects (Color, Size, Brand, Material) 也需要 to_dict
        # 这里暂时假设它们有 .value 属性或直接可序列化
        return {
            "id": str(self.id),
            "name": self.name,
            "category_id": str(self.category_id),
            # 假设值对象有 .value 属性或可直接序列化
            "color": self.color.to_dict() if hasattr(self.color, 'to_dict') else getattr(self.color, 'value', str(self.color)),
            "size": self.size.to_dict() if hasattr(self.size, 'to_dict') else getattr(self.size, 'value', str(self.size)),
            "dimension": self.dimension.to_dict() if hasattr(self.dimension, 'to_dict') else getattr(self.dimension, 'value', str(self.dimension)),
            "brand": self.brand.to_dict() if hasattr(self.brand, 'to_dict') else getattr(self.brand, 'value', str(self.brand)),
            "material": self.material.to_dict() if hasattr(self.material, 'to_dict') else getattr(self.material, 'value', str(self.material)),
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "price": self.price,
            "description": self.description,
            "image_url": self.image_url,
            "is_favorite": self.is_favorite,
            "tags": [tag.to_dict() for tag in self._tags], # 序列化 Tag 列表
            "version": self.version, 
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ClothingItem':
        """从字典反序列化为 ClothingItem 对象（包括 Tag）"""
        # 注意：Value Objects 需要从字典或值重建
        # 这里简化处理，假设可以直接从 data 中的值创建或需要 from_dict
        color_val = data.get('color')
        size_val = data.get('size')
        brand_val = data.get('brand')
        material_val = data.get('material')
        
        # 假设值对象可以直接通过值初始化或有 from_dict
        color = Color.from_dict(color_val) if isinstance(color_val, dict) and hasattr(Color, 'from_dict') else Color(color_val) if color_val else Color("")
        size = Size.from_dict(size_val) if isinstance(size_val, dict) and hasattr(Size, 'from_dict') else Size(size_val) if size_val else Size("")
        brand = Brand.from_dict(brand_val) if isinstance(brand_val, dict) and hasattr(Brand, 'from_dict') else Brand(brand_val) if brand_val else Brand("")
        material = Material.from_dict(material_val) if isinstance(material_val, dict) and hasattr(Material, 'from_dict') else Material(material_val) if material_val else Material("")

        purchase_date_obj = None
        if data.get('purchase_date'):
            try:
                purchase_date_obj = datetime.fromisoformat(data['purchase_date'])
            except (ValueError, TypeError):
                pass # 忽略无效日期格式
                
        item = cls(
            id=UUID(data['id']),
            name=data['name'],
            category_id=UUID(data['category_id']),
            wardrobe_id=UUID(data['wardrobe_id']),
            color=color,
            size=size,
            brand=brand,
            material=material,
            purchase_date=purchase_date_obj,
            price=data.get('price', 0.0),
            dimension=data.get('dimension'),
            style=data.get('style'),
            image_metadata=data.get('image_metadata'),
            description=data.get('description'),
            image_url=data.get('image_url')
        )
        item._is_favorite = data.get('is_favorite', False)
        # 反序列化 Tag 列表
        item._tags = [Tag.from_dict(tag_data) for tag_data in data.get('tags', [])]
        
        # 可选：恢复时间戳和版本
        if 'created_at' in data:
            item._created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            item._updated_at = datetime.fromisoformat(data['updated_at'])
        if 'version' in data:
             item._version = data['version']
             
        return item

class Category(Entity):
    """分类实体"""
    def __init__(
        self,
        id: UUID,
        name: str,
        wardrobe_id: UUID,
        parent_id: Optional[UUID] = None,
        description: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._parent_id = parent_id
        self._wardrobe_id = wardrobe_id
        self._description = description
        self._subcategories: List[UUID] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent_id(self) -> Optional[UUID]:
        return self._parent_id

    @property
    def wardrobe_id(self) -> UUID:
        return self._wardrobe_id

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

    def to_dict(self) -> dict:
        """将 User 对象转换为字典，用于持久化"""
        return {
            "id": str(self.id), # UUID 转字符串
            "username": self.username,
            "email": self.email,
            "password_hash": self._password_hash, # 注意：密码哈希应保密
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "gender": self.gender,
            # 日期时间转 ISO 格式字符串
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建 User 对象"""
        # 将字符串转回 UUID 和 datetime
        user_id = uuid4() # 默认生成新ID
        if "id" in data and data["id"]:
            try:
                user_id = UUID(data["id"])
            except ValueError:
                print(f"警告: 无效的用户ID格式 '{data['id']}'，将生成新ID。")

        birth_date = None
        if "birth_date" in data and data["birth_date"]:
            try:
                birth_date = datetime.fromisoformat(data["birth_date"])
            except (ValueError, TypeError):
                 print(f"警告: 无法解析生日日期 '{data['birth_date']}'")

        last_login = None
        if "last_login" in data and data["last_login"]:
             try:
                 last_login = datetime.fromisoformat(data["last_login"])
             except (ValueError, TypeError):
                 print(f"警告: 无法解析上次登录日期 '{data['last_login']}'")

        created_at = datetime.now() # 默认
        if "created_at" in data and data["created_at"]:
             try:
                 created_at = datetime.fromisoformat(data["created_at"])
             except (ValueError, TypeError):
                 print(f"警告: 无法解析创建日期 '{data['created_at']}'")

        updated_at = datetime.now() # 默认
        if "updated_at" in data and data["updated_at"]:
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                 print(f"警告: 无法解析更新日期 '{data['updated_at']}'")

        # 使用 ** 解包来传递参数，对于 User 没有的键会自动忽略 (如果 __init__ 允许)
        # 但最好还是显式传递已知参数
        user = cls(
            id=user_id,
            username=data.get("username", "unknown_user"),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            nickname=data.get("nickname"),
            avatar_url=data.get("avatar_url"),
            gender=data.get("gender"),
            birth_date=birth_date
        )
        # 恢复内部状态
        user._is_active = data.get("is_active", True)
        user._last_login = last_login
        user._preferences = data.get("preferences", {})
        user._version = data.get("version", 0)
        user._created_at = created_at # 设置从数据加载的创建时间
        user._updated_at = updated_at # 设置从数据加载的更新时间

        return user

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