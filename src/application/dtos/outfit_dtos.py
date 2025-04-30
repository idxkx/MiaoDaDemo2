"""
穿搭数据传输对象
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseDTO
from .wardrobe_dtos import ClothingItemDTO


class OutfitItemDTO(BaseDTO):
    """穿搭项数据传输对象"""
    item: ClothingItemDTO
    layer: int = 1


class OutfitDTO(BaseDTO):
    """穿搭组合数据传输对象"""
    id: UUID
    name: str
    owner_id: UUID
    items: List[OutfitItemDTO] = []
    occasion: str
    season: str
    weather: str
    rating: int = 0
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime


class OutfitCreateDTO(BaseDTO):
    """穿搭创建数据传输对象"""
    name: str
    occasion: str
    season: str
    weather: str
    items: List[Dict[str, Any]] = []  # [{item_id: UUID, layer: int}]


class OutfitUpdateDTO(BaseDTO):
    """穿搭更新数据传输对象"""
    name: Optional[str] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    rating: Optional[int] = None
    is_favorite: Optional[bool] = None


class OutfitItemAddDTO(BaseDTO):
    """添加穿搭项数据传输对象"""
    item_id: UUID
    layer: int = 1


class OutfitItemRemoveDTO(BaseDTO):
    """移除穿搭项数据传输对象"""
    item_id: UUID


class OutfitListDTO(BaseDTO):
    """穿搭列表数据传输对象"""
    outfits: List[OutfitDTO] = []
    total: int = 0


class OutfitSearchDTO(BaseDTO):
    """穿搭搜索数据传输对象"""
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    is_favorite: Optional[bool] = None
    page: int = 1
    size: int = 10 