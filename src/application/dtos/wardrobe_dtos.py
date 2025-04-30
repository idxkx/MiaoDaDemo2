"""
衣橱数据传输对象
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseDTO


class CategoryDTO(BaseDTO):
    """分类数据传输对象"""
    id: UUID
    name: str
    parent_id: Optional[UUID] = None
    description: Optional[str] = None
    subcategories: List[UUID] = []
    item_count: int = 0


class ClothingItemDTO(BaseDTO):
    """衣物数据传输对象"""
    id: UUID
    name: str
    category_id: UUID
    category_name: Optional[str] = None
    color: Dict[str, Any]
    size: Dict[str, Any]
    brand: Dict[str, Any]
    material: Dict[str, Any]
    dimension: Dict[str, Any]
    image_metadata: Dict[str, Any]
    image_url: Optional[str] = None
    price: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: List[Dict[str, Any]] = []
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime


class ClothingItemCreateDTO(BaseDTO):
    """衣物创建数据传输对象"""
    name: str
    category_id: UUID
    color_name: str
    color_hex: str
    size_value: str
    brand_name: str
    material_name: str
    material_composition: Dict[str, float]
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    unit: str = "cm"
    image_url: Optional[str] = None
    image_data: Optional[str] = None  # Base64编码的图片数据
    price_amount: Optional[float] = None
    price_currency: str = "CNY"
    description: Optional[str] = None
    tags: List[Dict[str, Any]] = []


class ClothingItemUpdateDTO(BaseDTO):
    """衣物更新数据传输对象"""
    name: Optional[str] = None
    category_id: Optional[UUID] = None
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    size_value: Optional[str] = None
    brand_name: Optional[str] = None
    material_name: Optional[str] = None
    material_composition: Optional[Dict[str, float]] = None
    dimension: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    price_amount: Optional[float] = None
    price_currency: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    is_favorite: Optional[bool] = None


class WardrobeDTO(BaseDTO):
    """衣橱数据传输对象"""
    id: UUID
    owner_id: UUID
    categories: List[CategoryDTO] = []
    items: List[ClothingItemDTO] = []
    created_at: datetime
    updated_at: datetime


class WardrobeStatsDTO(BaseDTO):
    """衣橱统计数据传输对象"""
    total_items: int = 0
    category_distribution: Dict[str, int] = {}
    color_distribution: Dict[str, int] = {}
    brand_distribution: Dict[str, int] = {}
    material_distribution: Dict[str, int] = {}
    style_distribution: Dict[str, int] = {}
    season_distribution: Dict[str, int] = {} 