from typing import List, Optional
from uuid import UUID

from .base import Repository
from ..model.aggregates import Wardrobe, Outfit
from ..model.entities import ClothingItem, Category

class WardrobeRepository(Repository[Wardrobe]):
    """衣橱仓储接口"""
    
    async def find_by_owner_id(self, owner_id: UUID) -> Optional[Wardrobe]:
        """根据用户ID查找衣橱"""
        pass

class OutfitRepository(Repository[Outfit]):
    """穿搭组合仓储接口"""
    
    async def find_by_owner_id(self, owner_id: UUID) -> List[Outfit]:
        """根据用户ID查找穿搭组合"""
        pass
    
    async def find_favorites_by_owner_id(self, owner_id: UUID) -> List[Outfit]:
        """查找用户收藏的穿搭组合"""
        pass

class ClothingItemRepository(Repository[ClothingItem]):
    """衣物仓储接口"""
    
    async def find_by_category(self, category_id: UUID) -> List[ClothingItem]:
        """根据分类查找衣物"""
        pass
    
    async def find_by_tags(self, tags: List[str]) -> List[ClothingItem]:
        """根据标签查找衣物"""
        pass
    
    async def find_favorites(self) -> List[ClothingItem]:
        """查找收藏的衣物"""
        pass

class CategoryRepository(Repository[Category]):
    """分类仓储接口"""
    
    async def find_by_parent_id(self, parent_id: Optional[UUID]) -> List[Category]:
        """根据父分类ID查找子分类"""
        pass
    
    async def find_root_categories(self) -> List[Category]:
        """查找根分类"""
        return await self.find_by_parent_id(None) 