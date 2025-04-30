# src/infrastructure/persistence/json_wardrobe_repository.py
import json
import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from src.domain.model.entities import ClothingItem
from src.domain.repositories.wardrobe_repository import WardrobeRepository

# 定义存储衣物数据的目录
WARDROBE_STORAGE_DIR = Path("storage") / "wardrobes"

class JsonWardrobeRepository(WardrobeRepository):
    """使用 JSON 文件实现衣橱仓储"""

    def __init__(self):
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        try:
            WARDROBE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"错误: 无法创建衣橱存储目录 '{WARDROBE_STORAGE_DIR}': {e}")

    def _get_user_file_path(self, user_id: UUID) -> Path:
        """获取指定用户的 JSON 文件路径"""
        return WARDROBE_STORAGE_DIR / f"{user_id}_items.json"

    def _load_items(self, user_id: UUID) -> List[ClothingItem]:
        """从文件加载指定用户的衣物列表"""
        file_path = self._get_user_file_path(user_id)
        if not file_path.exists():
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                if isinstance(items_data, list):
                    # 使用 ClothingItem.from_dict 进行转换
                    return [ClothingItem.from_dict(data) for data in items_data]
                else:
                    print(f"警告: 文件 {file_path} 格式错误，不是列表。")
                    return [] # 返回空列表而不是抛出错误
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"错误: 加载衣物文件 '{file_path}' 时出错: {e}")
            return [] # 出错时返回空列表

    def _save_items(self, user_id: UUID, items: List[ClothingItem]) -> None:
        """将指定用户的衣物列表保存到文件"""
        file_path = self._get_user_file_path(user_id)
        try:
            # 使用 ClothingItem.to_dict 进行转换
            items_data = [item.to_dict() for item in items]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"错误: 保存衣物文件 '{file_path}' 时出错: {e}")
            # 实际应用中可能需要抛出异常

    def add_item(self, user_id: UUID, item: ClothingItem) -> None:
        items = self._load_items(user_id)
        # 检查 ID 是否重复 (理论上 UUID 不会重复，但以防万一)
        if any(existing_item.id == item.id for existing_item in items):
            print(f"警告: 衣物 ID {item.id} 已存在于用户 {user_id} 的衣橱中，将覆盖。")
            items = [existing_item for existing_item in items if existing_item.id != item.id]
        
        items.append(item)
        self._save_items(user_id, items)
        print(f"衣物 {item.id} 已添加到用户 {user_id} 的 JSON 文件。")

    def get_item_by_id(self, user_id: UUID, item_id: UUID) -> Optional[ClothingItem]:
        items = self._load_items(user_id)
        for item in items:
            if item.id == item_id:
                return item
        return None

    def get_all_items(self, user_id: UUID) -> List[ClothingItem]:
        return self._load_items(user_id)

    def update_item(self, user_id: UUID, item_to_update: ClothingItem) -> None:
        items = self._load_items(user_id)
        updated = False
        for i, item in enumerate(items):
            if item.id == item_to_update.id:
                items[i] = item_to_update # 替换为新对象
                updated = True
                break
        if updated:
            self._save_items(user_id, items)
        else:
            print(f"警告: 尝试更新用户 {user_id} 衣橱中不存在的衣物 ID: {item_to_update.id}")
            # 或者可以选择抛出异常
            # raise ValueError(f"Item with id {item_to_update.id} not found for user {user_id}")

    def delete_item(self, user_id: UUID, item_id: UUID) -> None:
        items = self._load_items(user_id)
        original_length = len(items)
        items = [item for item in items if item.id != item_id]
        if len(items) < original_length:
            self._save_items(user_id, items)
        else:
            print(f"警告: 尝试删除用户 {user_id} 衣橱中不存在的衣物 ID: {item_id}") 