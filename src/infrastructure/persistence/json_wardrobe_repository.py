# src/infrastructure/persistence/json_wardrobe_repository.py
import json
import os
import logging
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from src.domain.model.entities import ClothingItem
from src.domain.repositories.wardrobe_repository import WardrobeRepository

logger = logging.getLogger(__name__)

# 定义存储衣物数据的目录
WARDROBE_STORAGE_DIR = Path("storage") / "wardrobes"

class JsonWardrobeRepository(WardrobeRepository):
    """使用 JSON 文件实现衣橱仓储"""

    def __init__(self):
        logger.info("初始化JSON衣橱仓储")
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        try:
            WARDROBE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"确保存储目录存在: {WARDROBE_STORAGE_DIR}")
        except OSError as e:
            error_msg = f"无法创建衣橱存储目录 '{WARDROBE_STORAGE_DIR}': {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _get_user_file_path(self, user_id: UUID) -> Path:
        """获取指定用户的 JSON 文件路径"""
        return WARDROBE_STORAGE_DIR / f"{user_id}_items.json"

    def _load_items(self, user_id: UUID) -> List[ClothingItem]:
        """从文件加载指定用户的衣物列表"""
        file_path = self._get_user_file_path(user_id)
        logger.info(f"正在从文件加载用户 {user_id} 的衣物列表")
        
        if not file_path.exists():
            logger.warning(f"用户 {user_id} 的衣物文件不存在，返回空列表")
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                
            if not isinstance(items_data, list):
                error_msg = f"文件 {file_path} 格式错误，不是列表"
                logger.error(error_msg)
                return []
            
            loaded_items = []
            for item_data in items_data:
                try:
                    item = ClothingItem.from_dict(item_data)
                    loaded_items.append(item)
                except Exception as item_error:
                    logger.error(f"加载衣物数据时出错，跳过此项: {item_error}")
                    continue
            
            logger.info(f"成功从文件加载了 {len(loaded_items)} 件衣物")
            return loaded_items
                
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败 '{file_path}': {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except FileNotFoundError as e:
            error_msg = f"文件不存在 '{file_path}': {e}"
            logger.error(error_msg)
            return []
        except Exception as e:
            error_msg = f"加载衣物文件时出现未知错误 '{file_path}': {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _save_items(self, user_id: UUID, items: List[ClothingItem]) -> None:
        """将指定用户的衣物列表保存到文件"""
        file_path = self._get_user_file_path(user_id)
        logger.info(f"正在保存用户 {user_id} 的衣物列表")
        
        try:
            # 创建临时备份
            backup_path = file_path.with_suffix('.json.bak')
            if file_path.exists():
                file_path.rename(backup_path)
            
            # 保存新数据
            items_data = [item.to_dict() for item in items]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, indent=4, ensure_ascii=False)
            
            # 保存成功后删除备份
            if backup_path.exists():
                backup_path.unlink()
                
            logger.info(f"成功保存了 {len(items)} 件衣物到文件")
            
        except Exception as e:
            error_msg = f"保存衣物文件 '{file_path}' 时出错: {e}"
            logger.error(error_msg)
            
            # 如果有备份，尝试恢复
            if backup_path.exists():
                try:
                    backup_path.rename(file_path)
                    logger.info("已恢复备份文件")
                except Exception as restore_error:
                    logger.error(f"恢复备份失败: {restore_error}")
            
            raise RuntimeError(error_msg)

    def add_item(self, user_id: UUID, item: ClothingItem) -> None:
        logger.info(f"正在添加衣物 {item.id} 到用户 {user_id} 的衣橱")
        items = self._load_items(user_id)
        
        # 检查 ID 是否重复
        if any(existing_item.id == item.id for existing_item in items):
            logger.warning(f"衣物 ID {item.id} 已存在于用户 {user_id} 的衣橱中，将覆盖")
            items = [existing_item for existing_item in items if existing_item.id != item.id]
        
        items.append(item)
        self._save_items(user_id, items)
        logger.info(f"衣物 {item.id} 已成功添加到用户 {user_id} 的衣橱")

    def get_item_by_id(self, user_id: UUID, item_id: UUID) -> Optional[ClothingItem]:
        logger.info(f"正在查找用户 {user_id} 衣橱中的衣物 {item_id}")
        items = self._load_items(user_id)
        for item in items:
            if item.id == item_id:
                logger.info(f"找到衣物 {item_id}")
                return item
        logger.warning(f"未找到衣物 {item_id}")
        return None

    def get_all_items(self, user_id: UUID) -> List[ClothingItem]:
        logger.info(f"正在获取用户 {user_id} 的所有衣物")
        return self._load_items(user_id)

    def update_item(self, user_id: UUID, item_to_update: ClothingItem) -> None:
        logger.info(f"正在更新用户 {user_id} 衣橱中的衣物 {item_to_update.id}")
        items = self._load_items(user_id)
        updated = False
        
        for i, item in enumerate(items):
            if item.id == item_to_update.id:
                items[i] = item_to_update
                updated = True
                break
                
        if updated:
            self._save_items(user_id, items)
            logger.info(f"衣物 {item_to_update.id} 更新成功")
        else:
            error_msg = f"尝试更新用户 {user_id} 衣橱中不存在的衣物 ID: {item_to_update.id}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def delete_item(self, user_id: UUID, item_id: UUID) -> None:
        logger.info(f"正在删除用户 {user_id} 衣橱中的衣物 {item_id}")
        items = self._load_items(user_id)
        original_length = len(items)
        items = [item for item in items if item.id != item_id]
        
        if len(items) < original_length:
            self._save_items(user_id, items)
            logger.info(f"衣物 {item_id} 删除成功")
        else:
            error_msg = f"尝试删除用户 {user_id} 衣橱中不存在的衣物 ID: {item_id}"
            logger.warning(error_msg)
            raise ValueError(error_msg) 