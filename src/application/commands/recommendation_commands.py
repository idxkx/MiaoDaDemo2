"""
推荐相关命令
"""

from typing import Optional, List
from uuid import UUID

from .base import Command


class GetOutfitRecommendationsCommand(Command):
    """获取穿搭推荐命令"""
    user_id: UUID
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    style_preference: Optional[str] = None
    color_preference: Optional[str] = None
    max_results: int = 5


class GetStyleRecommendationsCommand(Command):
    """获取风格推荐命令"""
    user_id: UUID
    max_styles: int = 3


class GetOccasionRecommendationsCommand(Command):
    """获取场合推荐命令"""
    user_id: UUID
    max_occasions: int = 3


class GetSeasonRecommendationsCommand(Command):
    """获取季节推荐命令"""
    user_id: UUID
    season: str
    max_outfits: int = 5


class SaveRecommendationCommand(Command):
    """保存推荐结果命令"""
    user_id: UUID
    outfit_id: UUID
    recommendation_type: str  # 'outfit', 'style', 'occasion', 'season'
    feedback: Optional[str] = None 