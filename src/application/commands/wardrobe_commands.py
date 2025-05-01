"""
衣橱相关命令
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from .base import Command
from ..dtos.wardrobe_dtos import ClothingItemCreateDTO, ClothingItemUpdateDTO


class CreateWardrobeCommand(Command):
    """创建衣橱命令"""
    owner_id: UUID


class AddCategoryCommand(Command):
    """添加分类命令"""
    wardrobe_id: UUID
    name: str
    parent_id: Optional[UUID] = None
    description: Optional[str] = None


class UpdateCategoryCommand(Command):
    """更新分类命令"""
    category_id: UUID
    wardrobe_id: UUID
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    description: Optional[str] = None


class DeleteCategoryCommand(Command):
    """删除分类命令"""
    category_id: UUID
    wardrobe_id: UUID


class AddClothingItemCommand(Command):
    """添加衣物命令"""
    wardrobe_id: UUID
    data: ClothingItemCreateDTO


class UpdateClothingItemCommand(Command):
    """更新衣物命令"""
    item_id: UUID
    wardrobe_id: UUID
    data: ClothingItemUpdateDTO


class DeleteClothingItemCommand(Command):
    """删除衣物命令"""
    item_id: UUID
    wardrobe_id: UUID


class ToggleFavoriteCommand(Command):
    """切换收藏状态命令"""
    item_id: UUID
    wardrobe_id: UUID
    is_favorite: bool


class AddTagToItemCommand(Command):
    """添加标签命令"""
    item_id: UUID
    wardrobe_id: UUID
    tag_name: str
    tag_category: str


class RemoveTagFromItemCommand(Command):
    """移除标签命令"""
    item_id: UUID
    wardrobe_id: UUID
    tag_name: str
    tag_category: str


@dataclass(frozen=True)
class AddClothingCommand:
    """添加衣物的命令"""
    user_id: UUID
    name: str
    category_name: str
    color_name: str
    color_hex: str
    size_value: str
    brand_name: str
    material_name: str
    purchase_date: datetime
    price: float
    description: Optional[str] = None
    image_path: Optional[str] = None 