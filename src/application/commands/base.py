"""
基础命令定义
"""

from typing import Generic, TypeVar, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


T = TypeVar('T')


class Command(BaseModel):
    """命令基类"""
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class CommandResult(Generic[T]):
    """命令结果基类"""
    
    def __init__(
        self,
        success: bool = True,
        value: Optional[T] = None,
        message: Optional[str] = None,
        error_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.value = value
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {} 