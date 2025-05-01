from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
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
    composition: Optional[dict[str, float]] = None  # 材质成分及占比
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Material name cannot be empty")
        if self.composition is not None:
            # 验证成分占比
            if not isinstance(self.composition, dict):
                raise ValueError("Composition must be a dictionary")
            if not all(isinstance(v, (int, float)) for v in self.composition.values()):
                raise ValueError("Composition values must be numbers")
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

@dataclass(frozen=True)
class Size(ValueObject):
    """尺码值对象"""
    value: str  # S, M, L, XL等
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Size value cannot be empty")
        if not re.match(r"^(XS|S|M|L|XL|XXL|XXXL)$", self.value):
            raise ValueError("Invalid size value")

class SeasonEnum(Enum):
    """季节枚举"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class WeatherEnum(Enum):
    """天气枚举"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    WINDY = "windy"
    HOT = "hot"
    COLD = "cold"

class OccasionEnum(Enum):
    """场合枚举"""
    DAILY = "daily"
    WORK = "work"
    FORMAL = "formal"
    PARTY = "party"
    SPORT = "sport"
    DATING = "dating"
    TRAVEL = "travel"
    HOME = "home"

@dataclass(frozen=True)
class Season(ValueObject):
    """季节值对象"""
    value: SeasonEnum
    temperature_range: tuple[float, float]  # (最低温度, 最高温度)
    humidity_range: tuple[float, float]  # (最低湿度%, 最高湿度%)
    
    def __post_init__(self):
        if not isinstance(self.value, SeasonEnum):
            object.__setattr__(self, 'value', SeasonEnum(self.value))
        
        min_temp, max_temp = self.temperature_range
        if min_temp >= max_temp:
            raise ValueError("最低温度必须小于最高温度")
        
        min_humidity, max_humidity = self.humidity_range
        if not (0 <= min_humidity <= max_humidity <= 100):
            raise ValueError("湿度必须在0-100%之间")

    @property
    def name(self) -> str:
        return self.value.value

    def is_suitable_temperature(self, temperature: float) -> bool:
        """判断温度是否适合当前季节"""
        min_temp, max_temp = self.temperature_range
        return min_temp <= temperature <= max_temp

    def is_suitable_humidity(self, humidity: float) -> bool:
        """判断湿度是否适合当前季节"""
        min_humidity, max_humidity = self.humidity_range
        return min_humidity <= humidity <= max_humidity

@dataclass(frozen=True)
class Weather(ValueObject):
    """天气值对象"""
    value: WeatherEnum
    temperature: float  # 温度
    humidity: float  # 湿度
    wind_speed: float  # 风速(m/s)
    precipitation: float  # 降水量(mm)
    
    def __post_init__(self):
        if not isinstance(self.value, WeatherEnum):
            object.__setattr__(self, 'value', WeatherEnum(self.value))
        
        if not (-50 <= self.temperature <= 50):
            raise ValueError("温度必须在-50到50度之间")
        
        if not (0 <= self.humidity <= 100):
            raise ValueError("湿度必须在0-100%之间")
        
        if self.wind_speed < 0:
            raise ValueError("风速不能为负")
        
        if self.precipitation < 0:
            raise ValueError("降水量不能为负")

    @property
    def name(self) -> str:
        return self.value.value

    def is_suitable_for_outdoor(self) -> bool:
        """判断是否适合户外活动"""
        return (
            self.value not in [WeatherEnum.RAINY, WeatherEnum.SNOWY] and
            self.wind_speed < 10 and
            self.precipitation < 5
        )

@dataclass(frozen=True)
class Occasion(ValueObject):
    """场合值对象"""
    value: OccasionEnum
    dress_code: str  # 着装要求
    formality_level: int  # 正式程度(1-5)
    suitable_time: List[str]  # 适合的时间段
    indoor: bool  # 是否室内场合
    
    def __post_init__(self):
        if not isinstance(self.value, OccasionEnum):
            object.__setattr__(self, 'value', OccasionEnum(self.value))
        
        if not self.dress_code:
            raise ValueError("着装要求不能为空")
        
        if not (1 <= self.formality_level <= 5):
            raise ValueError("正式程度必须在1-5之间")
        
        if not self.suitable_time:
            raise ValueError("适合的时间段不能为空")

    @property
    def name(self) -> str:
        return self.value.value
        
    def is_formal(self) -> bool:
        """判断是否为正式场合"""
        return self.formality_level >= 4
        
    def is_suitable_time(self, time: datetime) -> bool:
        """判断给定时间是否适合该场合"""
        current_hour = time.hour
        
        for time_range in self.suitable_time:
            start_hour, end_hour = map(int, time_range.split('-'))
            if start_hour <= current_hour <= end_hour:
                return True
                
        return False 