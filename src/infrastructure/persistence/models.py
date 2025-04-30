from datetime import datetime
from typing import Optional
from uuid import UUID
import json

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class WardrobeModel(Base):
    """衣橱数据模型"""
    __tablename__ = 'wardrobes'
    
    id = Column(PGUUID, primary_key=True)
    owner_id = Column(PGUUID, nullable=False)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    items = relationship("ClothingItemModel", back_populates="wardrobe")
    categories = relationship("CategoryModel", back_populates="wardrobe")

class OutfitModel(Base):
    """穿搭组合数据模型"""
    __tablename__ = 'outfits'
    
    id = Column(PGUUID, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(PGUUID, nullable=False)
    occasion = Column(String, nullable=False)
    season = Column(String, nullable=False)
    weather = Column(String, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    is_favorite = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    items = relationship("OutfitItemModel", back_populates="outfit")

class OutfitItemModel(Base):
    """穿搭组合项数据模型"""
    __tablename__ = 'outfit_items'
    
    outfit_id = Column(PGUUID, ForeignKey('outfits.id'), primary_key=True)
    item_id = Column(PGUUID, ForeignKey('clothing_items.id'), primary_key=True)
    layer = Column(Integer, nullable=False)
    
    outfit = relationship("OutfitModel", back_populates="items")
    item = relationship("ClothingItemModel")

class ClothingItemModel(Base):
    """衣物数据模型"""
    __tablename__ = 'clothing_items'
    
    id = Column(PGUUID, primary_key=True)
    name = Column(String, nullable=False)
    category_id = Column(PGUUID, ForeignKey('categories.id'), nullable=False)
    wardrobe_id = Column(PGUUID, ForeignKey('wardrobes.id'), nullable=False)
    color = Column(JSON, nullable=False)  # Color值对象
    dimension = Column(JSON, nullable=False)  # Dimension值对象
    brand = Column(JSON, nullable=False)  # Brand值对象
    material = Column(JSON, nullable=False)  # Material值对象
    style = Column(JSON, nullable=False)  # Style值对象
    image_metadata = Column(JSON, nullable=False)  # ImageMetadata值对象
    price = Column(Float)  # Changed from JSON to Float
    description = Column(String)
    tags = Column(JSON, nullable=False, default=list)
    is_favorite = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    category = relationship("CategoryModel", back_populates="items")
    wardrobe = relationship("WardrobeModel", back_populates="items")

class CategoryModel(Base):
    """分类数据模型"""
    __tablename__ = 'categories'
    
    id = Column(PGUUID, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(PGUUID, ForeignKey('categories.id'))
    wardrobe_id = Column(PGUUID, ForeignKey('wardrobes.id'), nullable=False)
    description = Column(String)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    items = relationship("ClothingItemModel", back_populates="category")
    wardrobe = relationship("WardrobeModel", back_populates="categories")
    parent = relationship("CategoryModel", remote_side=[id], back_populates="children")
    children = relationship("CategoryModel", back_populates="parent", passive_deletes=True)

# Print Base ID at the end of the file to see its ID upon module import
print(f"[models.py] Base object id after definitions: {id(Base)}") 