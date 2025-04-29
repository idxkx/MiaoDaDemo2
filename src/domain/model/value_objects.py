from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
import re

@dataclass(frozen=True)
class ValueObject:
    """值对象基类"""
    def __eq__(self, other):
        if not isinstance(other, ValueObject):
            return False
        return self.__dict__ == other.__dict__

@dataclass(frozen=True)
class ImageMetadata(ValueObject):
    """图片元数据值对象"""
    width: int
    height: int
    format: str
    size: int  # in bytes
    created_at: datetime
    location: str  # 存储路径
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive")
        if self.size <= 0:
            raise ValueError("Image size must be positive")
        if not self.location:
            raise ValueError("Image location cannot be empty")

@dataclass(frozen=True)
class Dimension(ValueObject):
    """尺寸值对象"""
    size: str  # S, M, L, XL等
    measurement: Optional[str] = None  # 具体尺寸数据，如"88cm"
    
    def __post_init__(self):
        if not self.size:
            raise ValueError("Size cannot be empty")
        if self.measurement and not re.match(r"^\d+(\.\d+)?(cm|inch)$", self.measurement):
            raise ValueError("Invalid measurement format")

@dataclass(frozen=True)
class Color(ValueObject):
    """颜色值对象"""
    name: str  # 颜色名称
    hex_code: str  # 十六进制颜色代码
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Color name cannot be empty")
        if not re.match(r"^#[0-9A-Fa-f]{6}$", self.hex_code):
            raise ValueError("Invalid hex color code")

@dataclass(frozen=True)
class Price(ValueObject):
    """价格值对象"""
    amount: float
    currency: str = "CNY"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
        if not self.currency:
            raise ValueError("Currency cannot be empty")

@dataclass(frozen=True)
class Brand(ValueObject):
    """品牌值对象"""
    name: str
    country: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Brand name cannot be empty")

@dataclass(frozen=True)
class Material(ValueObject):
    """材质值对象"""
    name: str
    composition: dict[str, float]  # 材质成分及占比
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Material name cannot be empty")
        if not self.composition:
            raise ValueError("Composition cannot be empty")
        total = sum(self.composition.values())
        if not (99.5 <= total <= 100.5):  # 允许0.5%的误差
            raise ValueError("Composition percentages must sum to 100%")

@dataclass(frozen=True)
class Style(ValueObject):
    """风格值对象"""
    name: str
    tags: list[str]
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Style name cannot be empty")
        if not self.tags:
            raise ValueError("Style must have at least one tag") 