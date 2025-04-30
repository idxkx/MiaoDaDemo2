"""
用户相关命令
"""

from typing import Optional
from uuid import UUID

from .base import Command
from ..dtos.user_dtos import UserCreateDTO, UserUpdateDTO, UserLoginDTO


class RegisterUserCommand(Command):
    """注册用户命令"""
    data: UserCreateDTO


class UpdateUserCommand(Command):
    """更新用户命令"""
    user_id: UUID
    data: UserUpdateDTO


class LoginCommand(Command):
    """用户登录命令"""
    data: UserLoginDTO


class LogoutCommand(Command):
    """用户退出命令"""
    user_id: UUID
    token: Optional[str] = None


class UpdatePasswordCommand(Command):
    """更新密码命令"""
    user_id: UUID
    old_password: str
    new_password: str


class ResetPasswordCommand(Command):
    """重置密码命令"""
    email: str 