# src/application/services/wardrobe_service.py

import uuid
from datetime import datetime
from typing import List, Optional

# 导入领域模型
from src.domain.model.entities import ClothingItem, User, Tag # 假设需要 User 和 Tag
from src.domain.model.value_objects import Color, Size, Brand, Material # 导入值对象
# --- 修改：导入仓储接口和实现（暂时）---
from src.domain.repositories.wardrobe_repository import WardrobeRepository
from src.infrastructure.persistence.json_wardrobe_repository import JsonWardrobeRepository # 临时直接导入实现
# ---

# 导入命令
from ..commands.wardrobe_commands import AddClothingCommand, AddTagToItemCommand # <-- 导入 AddTagToItemCommand

class WardrobeApplicationService:
    """衣橱管理应用服务"""

    # --- 修改：注入仓储 --- 
    def __init__(self, wardrobe_repo: WardrobeRepository):
        self.wardrobe_repo = wardrobe_repo
        print("WardrobeApplicationService initialized")
    # ---

    def add_clothing(self, command: AddClothingCommand) -> ClothingItem:
        """处理添加衣物命令"""
        print(f"Handling AddClothingCommand for user {command.user_id}")

        # --- 数据转换和实体创建 --- 
        # 1. 将命令中的字符串转换为领域值对象 (需要健壮的转换逻辑)
        #    - 这里暂时使用简单的直接创建，实际应用需要查找或创建分类ID，处理颜色/尺码/品牌/材质等
        #    - 需要处理无效输入（例如颜色名称不存在）
        try:
            # --- 修改：为空字符串的名称提供默认值 --- 
            color_name = command.color_name if command.color_name else "未知"
            brand_name = command.brand_name if command.brand_name else "未知"
            material_name = command.material_name if command.material_name else "未知"
            # ---

            # --- 修改：使用处理后的名称创建值对象 --- 
            color_obj = Color(color_name, "#000000") # 假设 Color 需要 hex，待确认
            size_obj = Size(command.size_value) # 尺码通常是必选或有默认值，暂不处理空
            brand_obj = Brand(brand_name)
            material_obj = Material(material_name, {"未知": 100.0}) # 假设 Material 需要成分，待确认
            # ---
            
            # 查找或创建 category_id (仍然是临时 ID)
            category_id = uuid.uuid4()
            print(f"Warning: Using temporary category ID: {category_id}")
        except ValueError as e:
            print(f"Error converting command data to value objects: {e}")
            # 在实际应用中应该抛出应用层异常
            raise ApplicationException(f"无效的衣物数据: {e}") from e

        # 2. 创建 ClothingItem 实体
        item_id = uuid.uuid4()
        clothing_item = ClothingItem(
            id=item_id,
            name=command.name,
            category_id=category_id,
            color=color_obj,
            size=size_obj,
            brand=brand_obj,
            material=material_obj,
            purchase_date=command.purchase_date,
            price=command.price,
            description=command.description,
            # image_url 需要在处理完图片上传/移动后设置
        )
        print(f"Created ClothingItem entity: {clothing_item.id}, Name: {clothing_item.name}")

        # 3. 处理图片 (如果提供了路径)
        if command.image_path:
            # TODO: 实现图片处理逻辑
            # 1. 验证图片文件是否存在且有效
            # 2. 将图片移动/复制到 storage/images 目录 (使用用户ID和衣物ID组织？)
            # 3. 生成缩略图到 storage/images/thumbnails
            # 4. 更新 clothing_item 的 image_url 属性
            print(f"TODO: Process image at path: {command.image_path}")
            # 假设处理后得到 URL
            # processed_image_url = f"/storage/images/{command.user_id}/{item_id}.jpg"
            # clothing_item.update_image_url(processed_image_url)

        # --- 修改：调用仓储保存 --- 
        try:
            self.wardrobe_repo.add_item(command.user_id, clothing_item)
            print(f"衣物 {clothing_item.id} 已成功调用仓储添加。")
        except Exception as e:
            # 仓储层可能抛出异常，应用服务需要处理或再次抛出
            print(f"Error persisting clothing item {clothing_item.id}: {e}")
            raise ApplicationException(f"保存衣物时出错: {e}") from e
        # ---

        # 返回创建的实体 (或其 ID)
        return clothing_item

    # --- 新增：添加标签到衣物的方法 --- 
    def add_tag_to_item(self, command: AddTagToItemCommand) -> None:
        """处理添加标签到衣物的命令"""
        print(f"Handling AddTagToItemCommand for item {command.item_id} in wardrobe {command.wardrobe_id}")
        
        # 1. 获取衣物实体
        item = self.wardrobe_repo.get_item_by_id(command.wardrobe_id, command.item_id)
        if not item:
            print(f"错误: 未找到用户 {command.wardrobe_id} 的衣物 {command.item_id}")
            raise ApplicationException(f"未找到要添加标签的衣物 (ID: {command.item_id})")

        # 2. 创建 Tag 实体 (使用新的 UUID)
        #    注意：这里的 Tag ID 是新生成的，因为它代表"这个衣物被打上了这个标签"这一事实，
        #    而不是引用一个全局共享的标签库（如果需要共享标签库，逻辑会更复杂）。
        tag_entity = Tag(
            id=uuid.uuid4(),
            name=command.tag_name,
            category=command.tag_category
            # description 可以留空
        )
        print(f"Created Tag entity: {tag_entity.id}, Name: {tag_entity.name}, Category: {tag_entity.category}")

        # 3. 调用领域方法添加标签
        try:
            item.add_tag(tag_entity)
            print(f"Tag {tag_entity.id} added to item {item.id} in domain model.")
        except Exception as e:
            # 领域模型内部可能出错？不太可能，但加上保护
            print(f"错误: 调用 item.add_tag 时出错: {e}")
            raise ApplicationException(f"添加标签到实体时出错: {e}") from e

        # 4. 调用仓储更新衣物
        try:
            self.wardrobe_repo.update_item(command.wardrobe_id, item)
            print(f"Item {item.id} with new tag updated in repository.")
        except Exception as e:
            print(f"错误: 更新带标签的衣物时出错: {e}")
            raise ApplicationException(f"保存带标签的衣物时出错: {e}") from e
    # ---

# --- 简单的应用层异常 (可以放到单独文件) --- 
class ApplicationException(Exception):
    pass 