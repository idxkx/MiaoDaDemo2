"""
推荐数据传输对象
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseDTO
from .outfit_dtos import OutfitDTO


class StyleRecommendationDTO(BaseDTO):
    """风格推荐数据传输对象"""
    style_name: str
    style_tags: List[str] = []
    confidence: float = 0.0
    description: Optional[str] = None
    sample_outfits: List[OutfitDTO] = []


class OccasionRecommendationDTO(BaseDTO):
    """场合推荐数据传输对象"""
    occasion_name: str
    occasion_description: str
    dress_code: str
    formality_level: int
    suitable_time: List[str]
    indoor: bool
    confidence: float = 0.0
    sample_outfits: List[OutfitDTO] = []


class SeasonRecommendationDTO(BaseDTO):
    """季节推荐数据传输对象"""
    season_name: str
    temperature_range: List[int]
    key_colors: List[str]
    key_materials: List[str]
    key_pieces: List[str]
    sample_outfits: List[OutfitDTO] = []


class OutfitRecommendationRequestDTO(BaseDTO):
    """穿搭推荐请求数据传输对象"""
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    style_preference: Optional[str] = None
    color_preference: Optional[str] = None
    max_results: int = 5


class OutfitRecommendationResponseDTO(BaseDTO):
    """穿搭推荐响应数据传输对象"""
    outfits: List[OutfitDTO] = []
    explanation: Optional[str] = None 