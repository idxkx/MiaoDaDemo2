from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table, Text, Boolean, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr
import enum

Base = declarative_base()

# 值对象：性别
class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

# 值对象：季节
class Season(enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    ALL = "all"

# 值对象：场合
class Occasion(enum.Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BUSINESS = "business"
    SPORTS = "sports"
    PARTY = "party"
    OTHER = "other"

# 值对象：天气
class Weather(enum.Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    CLOUDY = "cloudy"
    SNOWY = "snowy"
    WINDY = "windy"

# 领域事件Mixin
class DomainEventMixin:
    """领域事件Mixin，用于追踪实体的重要变更"""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)  # 用于乐观锁和版本控制

# 聚合根标记Mixin
class AggregateRootMixin:
    """聚合根标记Mixin"""
    is_aggregate_root = True

# 关联表：角色-衣物（收藏关系）
persona_clothing = Table(
    'persona_clothing',
    Base.metadata,
    Column('persona_id', Integer, ForeignKey('personas.id'), primary_key=True),
    Column('clothing_id', Integer, ForeignKey('clothing.id'), primary_key=True)
)

# 关联表：角色-穿搭组合（收藏关系）
persona_outfit = Table(
    'persona_outfit',
    Base.metadata,
    Column('persona_id', Integer, ForeignKey('personas.id'), primary_key=True),
    Column('outfit_id', Integer, ForeignKey('outfits.id'), primary_key=True)
)

# 关联表：衣物-标签
clothing_tag = Table(
    'clothing_tag',
    Base.metadata,
    Column('clothing_id', Integer, ForeignKey('clothing.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Persona(Base, DomainEventMixin, AggregateRootMixin):
    """角色聚合根"""
    __tablename__ = 'personas'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    age = Column(Integer)
    style_preference = Column(String(100))
    current_season = Column(Enum(Season))
    preferred_occasion = Column(Enum(Occasion))
    is_default = Column(Boolean, default=False)
    
    # 领域关系
    wardrobe_items = relationship("Clothing", secondary=persona_clothing, back_populates="personas")
    favorite_outfits = relationship("Outfit", secondary=persona_outfit, back_populates="personas")

    def add_to_wardrobe(self, clothing):
        """领域行为：添加衣物到个人衣橱"""
        if clothing not in self.wardrobe_items:
            self.wardrobe_items.append(clothing)
            self.version += 1

    def remove_from_wardrobe(self, clothing):
        """领域行为：从个人衣橱移除衣物"""
        if clothing in self.wardrobe_items:
            self.wardrobe_items.remove(clothing)
            self.version += 1

class WardrobeCategory(Base, DomainEventMixin):
    """衣物分类实体"""
    __tablename__ = 'wardrobe_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('wardrobe_categories.id'))
    description = Column(String(200))
    
    # 自引用关系
    subcategories = relationship("WardrobeCategory")
    parent = relationship("WardrobeCategory", remote_side=[id])
    
    # 关联衣物
    clothing_items = relationship("Clothing", back_populates="category")

class Clothing(Base, DomainEventMixin, AggregateRootMixin):
    """衣物聚合根"""
    __tablename__ = 'clothing'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('wardrobe_categories.id'), nullable=False)
    color = Column(String(50))
    pattern = Column(String(50))
    suitable_season = Column(Enum(Season))
    brand = Column(String(100))
    material = Column(String(50))
    image_path = Column(String(255))
    is_favorite = Column(Boolean, default=False)
    notes = Column(Text)
    
    # 领域关系
    category = relationship("WardrobeCategory", back_populates="clothing_items")
    personas = relationship("Persona", secondary=persona_clothing, back_populates="wardrobe_items")
    outfit_items = relationship("OutfitItem", back_populates="clothing")
    tags = relationship("Tag", secondary=clothing_tag, back_populates="clothing_items")

    def add_tag(self, tag):
        """领域行为：添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.version += 1

    def remove_tag(self, tag):
        """领域行为：移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.version += 1

class Tag(Base, DomainEventMixin):
    """标签实体"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    category = Column(String(50))
    description = Column(String(200))
    is_system = Column(Boolean, default=False)
    
    # 领域关系
    clothing_items = relationship("Clothing", secondary=clothing_tag, back_populates="tags")

class Outfit(Base, DomainEventMixin, AggregateRootMixin):
    """穿搭组合聚合根"""
    __tablename__ = 'outfits'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    occasion = Column(Enum(Occasion))
    season = Column(Enum(Season))
    weather = Column(Enum(Weather))
    rating = Column(Float, default=0)
    is_favorite = Column(Boolean, default=False)
    
    # 领域关系
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    personas = relationship("Persona", secondary=persona_outfit, back_populates="favorite_outfits")

    def add_clothing(self, clothing, layer_order=None):
        """领域行为：添加衣物到穿搭组合"""
        item = OutfitItem(clothing=clothing, layer_order=layer_order)
        self.items.append(item)
        self.version += 1
        return item

    def remove_clothing(self, clothing):
        """领域行为：从穿搭组合移除衣物"""
        for item in self.items:
            if item.clothing == clothing:
                self.items.remove(item)
                self.version += 1
                break

class OutfitItem(Base, DomainEventMixin):
    """穿搭组合项实体（值对象）"""
    __tablename__ = 'outfit_items'

    id = Column(Integer, primary_key=True)
    outfit_id = Column(Integer, ForeignKey('outfits.id'), nullable=False)
    clothing_id = Column(Integer, ForeignKey('clothing.id'), nullable=False)
    layer_order = Column(Integer)  # 穿搭层次顺序
    
    # 领域关系
    outfit = relationship("Outfit", back_populates="items")
    clothing = relationship("Clothing", back_populates="outfit_items")

# 创建数据库引擎和表
def init_db():
    """初始化数据库"""
    engine = create_engine('sqlite:///storage/wardrobe.db', echo=True)
    Base.metadata.create_all(engine)
    return engine 