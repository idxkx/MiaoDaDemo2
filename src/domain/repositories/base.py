from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class Repository(Generic[T], ABC):
    """仓储接口基类"""
    
    @abstractmethod
    async def save(self, entity: T) -> None:
        """保存实体"""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """删除实体"""
        pass
    
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[T]:
        """根据ID查找实体"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[T]:
        """查找所有实体"""
        pass 