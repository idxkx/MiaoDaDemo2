"""
穿搭相关命令
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from .base import Command
from ..dtos.outfit_dtos import OutfitCreateDTO, OutfitUpdateDTO


class CreateOutfitCommand(Command):
    """创建穿搭命令"""
    owner_id: UUID
    data: OutfitCreateDTO


class UpdateOutfitCommand(Command):
    """更新穿搭命令"""
    outfit_id: UUID
    owner_id: UUID
    data: OutfitUpdateDTO


class DeleteOutfitCommand(Command):
    """删除穿搭命令"""
    outfit_id: UUID
    owner_id: UUID


class AddItemToOutfitCommand(Command):
    """添加衣物到穿搭命令"""
    outfit_id: UUID
    owner_id: UUID
    item_id: UUID
    layer: int = 1


class RemoveItemFromOutfitCommand(Command):
    """从穿搭中移除衣物命令"""
    outfit_id: UUID
    owner_id: UUID
    item_id: UUID


class UpdateItemLayerCommand(Command):
    """更新穿搭中衣物层级命令"""
    outfit_id: UUID
    owner_id: UUID
    item_id: UUID
    layer: int


class RateOutfitCommand(Command):
    """评分穿搭命令"""
    outfit_id: UUID
    owner_id: UUID
    rating: int  # 1-5


class ToggleOutfitFavoriteCommand(Command):
    """切换穿搭收藏状态命令"""
    outfit_id: UUID
    owner_id: UUID
    is_favorite: bool 