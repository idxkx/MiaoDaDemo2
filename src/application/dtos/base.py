"""
基础DTO定义
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class BaseDTO(BaseModel):
    """基础数据传输对象"""
    
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class ResponseDTO(BaseDTO):
    """响应数据传输对象"""
    success: bool = True
    message: Optional[str] = None
    error_code: Optional[int] = None


class PageResponseDTO(ResponseDTO):
    """分页响应数据传输对象"""
    total: int = 0
    page: int = 1
    size: int = 10
    items: List[Any] = [] 