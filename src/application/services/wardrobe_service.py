# src/application/services/wardrobe_service.py

import uuid
import logging
from datetime import datetime
from typing import List, Optional
import random

# 导入领域模型
from src.domain.model.entities import ClothingItem, User, Tag # 假设需要 User 和 Tag
from src.domain.model.value_objects import Color, Size, Brand, Material # 导入值对象
# --- 修改：导入仓储接口和实现（暂时）---
from src.domain.repositories.wardrobe_repository import WardrobeRepository
from src.infrastructure.persistence.json_wardrobe_repository import JsonWardrobeRepository # 临时直接导入实现
# ---

# 导入命令
from ..commands.wardrobe_commands import AddClothingCommand, AddTagToItemCommand # <-- 导入 AddTagToItemCommand

logger = logging.getLogger(__name__)

class WardrobeApplicationService:
    """衣橱管理应用服务"""

    # --- 修改：注入仓储 --- 
    def __init__(self, wardrobe_repo: WardrobeRepository):
        self.wardrobe_repo = wardrobe_repo
        logger.info("WardrobeApplicationService 已初始化")
    # ---

    def add_clothing(self, command: AddClothingCommand) -> ClothingItem:
        """处理添加衣物命令"""
        logger.info(f"正在处理添加衣物命令，用户ID: {command.user_id}")

        try:
            # 验证命令参数
            if not command.name:
                raise ApplicationException("衣物名称不能为空")
            if not command.category_name:
                raise ApplicationException("衣物分类不能为空")
            
            # 处理颜色信息
            color_name = command.color_name if command.color_name else "未知"
            color_hex = command.color_hex if hasattr(command, 'color_hex') else "#000000"
            brand_name = command.brand_name if command.brand_name else "未知"
            material_name = command.material_name if command.material_name else "未知"

            logger.debug(f"处理颜色信息: 名称={color_name}, 代码={color_hex}")

            try:
                # 创建值对象
                color_obj = Color(color_name, color_hex)
                size_obj = Size(command.size_value)
                brand_obj = Brand(brand_name)
                material_obj = Material(material_name)
                
                logger.debug("值对象创建成功")
                
            except ValueError as ve:
                logger.error(f"创建值对象失败: {str(ve)}")
                raise ApplicationException(f"创建值对象失败: {str(ve)}")
            
            # 生成临时category_id（后续需要改进）
            category_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
            logger.warning(f"使用临时category_id: {category_id}")
            
            # 创建衣物实体
            clothing = ClothingItem(
                id=uuid.UUID(int=random.getrandbits(128)),
                name=command.name,
                category_id=category_id,
                wardrobe_id=command.user_id,
                color=color_obj,
                size=size_obj,
                brand=brand_obj,
                material=material_obj,
                purchase_date=command.purchase_date,
                price=command.price,
                description=command.description
            )
            
            logger.info(f"已创建衣物实体: ID={clothing.id}, 名称={clothing.name}")
            
            # 处理图片
            if command.image_path:
                logger.info(f"处理衣物图片: {command.image_path}")
                # TODO: 处理图片，生成缩略图等
            
            # 保存到仓储
            try:
                self.wardrobe_repo.add_item(command.user_id, clothing)
                logger.info(f"衣物 {clothing.id} 已成功保存到仓储")
            except Exception as e:
                logger.error(f"保存衣物到仓储失败: {str(e)}")
                raise ApplicationException(f"保存衣物失败: {str(e)}")
            
            return clothing
            
        except ApplicationException:
            # 直接向上抛出应用层异常
            raise
        except Exception as e:
            error_msg = f"添加衣物时发生未知错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ApplicationException(error_msg)

    # --- 新增：添加标签到衣物的方法 --- 
    def add_tag_to_item(self, command: AddTagToItemCommand) -> None:
        """处理添加标签到衣物的命令"""
        logger.info(f"正在处理添加标签命令: 衣物={command.item_id}, 衣橱={command.wardrobe_id}")
        
        try:
            # 验证命令参数
            if not command.tag_name:
                raise ApplicationException("标签名称不能为空")
            if not command.tag_category:
                raise ApplicationException("标签分类不能为空")
            
            # 获取衣物实体
            item = self.wardrobe_repo.get_item_by_id(command.wardrobe_id, command.item_id)
            if not item:
                error_msg = f"未找到衣物: ID={command.item_id}, 衣橱ID={command.wardrobe_id}"
                logger.error(error_msg)
                raise ApplicationException(error_msg)

            # 创建标签实体
            tag_entity = Tag(
                id=uuid.uuid4(),
                name=command.tag_name,
                category=command.tag_category
            )
            logger.info(f"已创建标签实体: ID={tag_entity.id}, 名称={tag_entity.name}, 分类={tag_entity.category}")

            # 添加标签到衣物
            try:
                item.add_tag(tag_entity)
                logger.info(f"标签 {tag_entity.id} 已添加到衣物 {item.id}")
            except Exception as e:
                logger.error(f"添加标签到衣物实体失败: {str(e)}")
                raise ApplicationException(f"添加标签失败: {str(e)}")

            # 更新仓储
            try:
                self.wardrobe_repo.update_item(command.wardrobe_id, item)
                logger.info(f"已更新带标签的衣物 {item.id}")
            except Exception as e:
                logger.error(f"更新带标签的衣物失败: {str(e)}")
                raise ApplicationException(f"保存带标签的衣物失败: {str(e)}")
                
        except ApplicationException:
            # 直接向上抛出应用层异常
            raise
        except Exception as e:
            error_msg = f"添加标签时发生未知错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ApplicationException(error_msg)
    # ---

# --- 简单的应用层异常 (可以放到单独文件) --- 
class ApplicationException(Exception):
    """应用层异常基类"""
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(f"应用层异常: {message}") 