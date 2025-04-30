from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..model.entities import ClothingItem

class WardrobeRepository(ABC):
    """衣橱仓储接口 (抽象基类)"""

    @abstractmethod
    def add_item(self, user_id: UUID, item: ClothingItem) -> None:
        """向指定用户的衣橱中添加衣物"""
        pass

    @abstractmethod
    def get_item_by_id(self, user_id: UUID, item_id: UUID) -> Optional[ClothingItem]:
        """根据 ID 获取指定用户的衣物"""
        pass

    @abstractmethod
    def get_all_items(self, user_id: UUID) -> List[ClothingItem]:
        """获取指定用户的所有衣物"""
        pass

    @abstractmethod
    def update_item(self, user_id: UUID, item: ClothingItem) -> None:
        """更新指定用户的衣物信息"""
        pass

    @abstractmethod
    def delete_item(self, user_id: UUID, item_id: UUID) -> None:
        """从指定用户的衣橱中删除衣物"""
        pass 