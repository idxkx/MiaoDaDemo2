"""
应用服务基类
"""

from typing import TypeVar, Generic, Type, Dict, Any
from uuid import UUID

from ..commands.base import Command, CommandResult


T = TypeVar('T')


class ApplicationService:
    """应用服务基类"""

    async def execute(self, command: Command) -> CommandResult:
        """执行命令"""
        try:
            handler_method = self._find_handler(command)
            if not handler_method:
                return CommandResult(
                    success=False,
                    message=f"找不到命令处理器: {command.__class__.__name__}",
                    error_code=404
                )
            
            result = await handler_method(command)
            return result
        except Exception as e:
            # 实际应用中应该使用日志记录错误
            return CommandResult(
                success=False,
                message=str(e),
                error_code=500
            )
    
    def _find_handler(self, command: Command):
        """查找命令处理器"""
        command_name = command.__class__.__name__
        handler_name = f"handle_{command_name}"
        
        if hasattr(self, handler_name) and callable(getattr(self, handler_name)):
            return getattr(self, handler_name)
        
        return None 