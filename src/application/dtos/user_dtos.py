"""
用户数据传输对象
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from .base import BaseDTO


class UserDTO(BaseDTO):
    """用户数据传输对象"""
    id: UUID
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None


class UserProfileDTO(BaseDTO):
    """用户个人资料数据传输对象"""
    id: UUID
    user_id: UUID
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    style_preferences: List[str] = []
    favorite_count: int = 0
    following_count: int = 0
    followers_count: int = 0
    last_login: Optional[datetime] = None


class UserCreateDTO(BaseDTO):
    """用户创建数据传输对象"""
    username: str
    email: str
    password: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None


class UserUpdateDTO(BaseDTO):
    """用户更新数据传输对象"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None


class UserLoginDTO(BaseDTO):
    """用户登录数据传输对象"""
    username: str
    password: str


class UserLoginResponseDTO(BaseDTO):
    """用户登录响应数据传输对象"""
    token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str
    user: UserDTO 