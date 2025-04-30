"""领域服务模块"""

from typing import List, Optional, Dict, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime
import random

from .entities import ClothingItem, Category, Tag
from .value_objects import Color, Style, Season, Occasion, Weather
from .aggregates import Outfit, Wardrobe, UserProfile, OutfitRecommendation


class OutfitMatchingService:
    """衣物搭配服务
    
    负责根据用户衣橱中的衣物创建合适的穿搭组合
    """
    
    # 必要的衣物类别 - 基本穿搭必须包含这些类别
    ESSENTIAL_CATEGORIES = ["上衣", "裤子", "鞋子"]
    
    # 场合与风格的映射
    OCCASION_STYLE_MAP = {
        "casual": ["休闲", "简约", "运动"],
        "work": ["商务", "正式", "简约"],
        "formal": ["正式", "奢华", "经典"],
        "party": ["时尚", "前卫", "华丽"],
        "dating": ["休闲", "浪漫", "时尚"],
        "sport": ["运动", "功能", "简约"]
    }
    
    # 季节与颜色的映射
    SEASON_COLOR_MAP = {
        "spring": ["#F7CAC9", "#AEC6CF", "#C1E1C1"],  # 粉色、淡蓝、淡绿
        "summer": ["#FFFFFF", "#87CEEB", "#FFFF99"],  # 白色、天蓝、淡黄
        "autumn": ["#D2691E", "#CD5C5C", "#F4A460"],  # 棕色、深红、沙色
        "winter": ["#000000", "#808080", "#4B0082"]   # 黑色、灰色、深紫
    }
    
    def match_outfits(
        self, 
        wardrobe: Wardrobe, 
        occasion: str,
        season: str,
        weather: str,
        style_preference: Optional[str] = None,
        max_outfits: int = 5
    ) -> List[Outfit]:
        """根据条件匹配衣物创建穿搭
        
        Args:
            wardrobe: 用户衣橱
            occasion: 场合
            season: 季节
            weather: 天气
            style_preference: 风格偏好
            max_outfits: 最大返回数量
            
        Returns:
            匹配的穿搭列表
        """
        # 获取衣橱中所有衣物
        all_items = wardrobe.items
        
        # 按类别分组衣物
        items_by_category = self._group_items_by_category(all_items)
        
        # 检查是否有足够的基础衣物类别
        if not self._has_essential_categories(items_by_category):
            return []
        
        # 基于条件过滤适合的衣物
        filtered_items = self._filter_suitable_items(
            items_by_category,
            occasion,
            season,
            weather,
            style_preference
        )
        
        # 如果过滤后没有足够的衣物类别，则无法创建穿搭
        if not self._has_essential_categories(filtered_items):
            return []
        
        # 创建穿搭组合
        outfits = self._create_outfit_combinations(
            filtered_items,
            occasion,
            season,
            weather,
            style_preference,
            max_outfits,
            wardrobe.owner_id
        )
        
        return outfits
    
    def _group_items_by_category(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """按类别对衣物进行分组"""
        result = {}
        category_ids = set()
        
        # 首先收集所有类别ID
        for item in items:
            category_ids.add(item.category_id)
        
        # 然后按类别分组
        for category_id in category_ids:
            category_items = [item for item in items if item.category_id == category_id]
            if category_items:
                # 使用第一个衣物的类别名称作为键（简化处理）
                # 在实际系统中，应该通过仓储查询类别名称
                category_name = f"category_{category_id}"
                result[category_name] = category_items
        
        return result
    
    def _has_essential_categories(self, items_by_category: Dict[str, List[ClothingItem]]) -> bool:
        """检查是否有必要的衣物类别"""
        # 简化检查：至少有3个不同类别
        return len(items_by_category) >= 3
    
    def _filter_suitable_items(
        self,
        items_by_category: Dict[str, List[ClothingItem]],
        occasion: str,
        season: str, 
        weather: str,
        style_preference: Optional[str]
    ) -> Dict[str, List[ClothingItem]]:
        """过滤出符合条件的衣物"""
        result = {}
        
        # 获取场合对应的风格
        suitable_styles = self.OCCASION_STYLE_MAP.get(occasion.lower(), [])
        if style_preference and style_preference not in suitable_styles:
            suitable_styles.append(style_preference)
        
        # 获取季节对应的颜色
        suitable_colors = self.SEASON_COLOR_MAP.get(season.lower(), [])
        
        for category, items in items_by_category.items():
            # 过滤符合条件的衣物
            filtered = []
            for item in items:
                # 检查风格标签
                item_has_style = False
                for tag in item.tags:
                    if tag.category == "style" and tag.name in suitable_styles:
                        item_has_style = True
                        break
                
                # 检查季节标签
                item_has_season = False
                for tag in item.tags:
                    if tag.category == "season" and tag.name.lower() == season.lower():
                        item_has_season = True
                        break
                
                # 简化处理：如果同时符合风格和季节，或者没有相关标签，则添加
                if (item_has_style and item_has_season) or (not item_has_style and not item_has_season):
                    filtered.append(item)
            
            if filtered:
                result[category] = filtered
        
        return result
    
    def _create_outfit_combinations(
        self,
        filtered_items: Dict[str, List[ClothingItem]],
        occasion: str,
        season: str,
        weather: str,
        style_preference: Optional[str],
        max_outfits: int,
        owner_id: UUID
    ) -> List[Outfit]:
        """创建穿搭组合"""
        outfits = []
        
        # 简化实现：为每个类别随机选择一件衣物，组成一个穿搭
        for i in range(min(max_outfits, 3)):  # 最多生成3个穿搭
            # 为每个类别随机选择一件衣物
            selected_items = []
            for category, items in filtered_items.items():
                if items:
                    selected_items.append(random.choice(items))
            
            # 如果选择的衣物不足3件，跳过
            if len(selected_items) < 3:
                continue
            
            # 创建穿搭
            outfit = Outfit(
                id=uuid4(),
                name=f"{season.capitalize()} {occasion.capitalize()} Outfit {i+1}",
                owner_id=owner_id,
                occasion=occasion,
                season=season,
                weather=weather
            )
            
            # 添加衣物到穿搭
            for layer, item in enumerate(selected_items):
                try:
                    outfit.add_item(item, layer + 1)
                except Exception:
                    # 如果添加失败（例如，类别冲突），跳过该衣物
                    continue
            
            # 如果穿搭中至少有3件衣物，添加到结果
            if len(outfit.items) >= 3:
                outfits.append(outfit)
        
        return outfits


class StyleRecommendationService:
    """风格推荐服务
    
    负责根据用户特征、喜好和衣橱内容推荐合适的风格
    """
    
    # 预定义风格
    DEFINED_STYLES = {
        "休闲": ["舒适", "日常", "随意"],
        "正式": ["商务", "庄重", "精致"],
        "简约": ["极简", "清爽", "基础"],
        "运动": ["活力", "功能", "舒适"],
        "时尚": ["潮流", "前沿", "流行"],
        "复古": ["怀旧", "经典", "复古"],
        "浪漫": ["柔美", "优雅", "梦幻"],
        "街头": ["潮流", "个性", "叛逆"],
        "学院": ["知性", "传统", "规整"],
        "波西米亚": ["自由", "多彩", "民族"]
    }
    
    # 风格与颜色的关联
    STYLE_COLOR_MAP = {
        "休闲": ["#FFFFFF", "#0000FF", "#87CEEB", "#A0A0A0"],  # 白色、蓝色、天蓝色、灰色
        "正式": ["#000000", "#FFFFFF", "#000080", "#A0A0A0"],  # 黑色、白色、深蓝色、灰色
        "简约": ["#FFFFFF", "#000000", "#A0A0A0", "#F5F5DC"],  # 白色、黑色、灰色、米色
        "运动": ["#FF0000", "#0000FF", "#FFFFFF", "#000000"],  # 红色、蓝色、白色、黑色
        "时尚": ["#FF00FF", "#00FFFF", "#FFFF00", "#000000"],  # 紫色、青色、黄色、黑色
        "复古": ["#8B4513", "#DEB887", "#F5F5DC", "#A0522D"],  # 棕色、浅棕色、米色、红棕色
        "浪漫": ["#FFC0CB", "#F08080", "#FFB6C1", "#FFFFFF"],  # 粉色、浅红色、浅粉色、白色
        "街头": ["#000000", "#FF0000", "#FFFFFF", "#808080"],  # 黑色、红色、白色、灰色
        "学院": ["#000080", "#8B0000", "#F5F5DC", "#000000"],  # 深蓝色、深红色、米色、黑色
        "波西米亚": ["#FF7F00", "#800080", "#FFD700", "#8B4513"]  # 橙色、紫色、金色、棕色
    }
    
    def recommend_styles(
        self, 
        user_profile: UserProfile, 
        wardrobe: Wardrobe,
        max_styles: int = 3
    ) -> List[Style]:
        """推荐风格
        
        Args:
            user_profile: 用户资料
            wardrobe: 用户衣橱
            max_styles: 最大推荐数量
            
        Returns:
            推荐的风格列表
        """
        # 分析衣橱中的风格趋势
        wardrobe_styles = self._analyze_wardrobe_styles(wardrobe)
        
        # 获取用户已有风格偏好
        existing_preferences = user_profile.style_preferences
        
        # 分析用户颜色偏好
        color_preferences = [color.name for color in user_profile.color_preferences]
        
        # 基于用户喜好和衣橱内容生成推荐
        recommended_styles = self._generate_style_recommendations(
            existing_preferences,
            wardrobe_styles,
            color_preferences,
            max_styles
        )
        
        return recommended_styles
    
    def _analyze_wardrobe_styles(self, wardrobe: Wardrobe) -> Dict[str, int]:
        """分析衣橱中的风格趋势"""
        style_count = {}
        
        # 统计衣物标签中的风格
        for item in wardrobe.items:
            for tag in item.tags:
                if tag.category == "style":
                    if tag.name not in style_count:
                        style_count[tag.name] = 0
                    style_count[tag.name] += 1
        
        # 如果没有找到任何风格标签，则基于颜色和材质推断风格
        if not style_count:
            # 根据颜色统计
            color_count = {}
            for item in wardrobe.items:
                color_name = item.color.name
                if color_name not in color_count:
                    color_count[color_name] = 0
                color_count[color_name] += 1
            
            # 基于颜色推断风格
            for style, colors in self.STYLE_COLOR_MAP.items():
                for color_hex in colors:
                    color_name = self._get_color_name_from_hex(color_hex)
                    if color_name in color_count:
                        if style not in style_count:
                            style_count[style] = 0
                        style_count[style] += color_count[color_name]
        
        return style_count
    
    def _get_color_name_from_hex(self, hex_code: str) -> str:
        """从十六进制代码获取颜色名称（简化实现）"""
        color_map = {
            "#FFFFFF": "白色",
            "#000000": "黑色",
            "#FF0000": "红色",
            "#00FF00": "绿色",
            "#0000FF": "蓝色",
            "#FFFF00": "黄色",
            "#FF00FF": "紫色",
            "#00FFFF": "青色",
            "#808080": "灰色",
            "#A0A0A0": "浅灰色",
            "#FFC0CB": "粉色",
            "#A52A2A": "棕色",
            "#000080": "深蓝色",
            "#8B0000": "深红色"
        }
        return color_map.get(hex_code.upper(), "未知")
    
    def _generate_style_recommendations(
        self,
        existing_preferences: List[str],
        wardrobe_styles: Dict[str, int],
        color_preferences: List[str],
        max_styles: int
    ) -> List[Style]:
        """生成风格推荐"""
        # 基于已有风格和衣橱分析，找出潜在的风格建议
        recommended_styles = []
        
        # 1. 首先考虑用户已有的风格偏好
        for style in existing_preferences:
            # 创建风格值对象
            tags = self.DEFINED_STYLES.get(style, [style])
            recommended_styles.append(Style(style, tags))
        
        # 2. 添加衣橱中最常见的风格（如果不在现有偏好中）
        sorted_wardrobe_styles = sorted(wardrobe_styles.items(), key=lambda x: x[1], reverse=True)
        for style, count in sorted_wardrobe_styles:
            if style not in existing_preferences and len(recommended_styles) < max_styles:
                tags = self.DEFINED_STYLES.get(style, [style])
                recommended_styles.append(Style(style, tags))
                
        # 3. 如果还不够，基于颜色偏好推荐风格
        if len(recommended_styles) < max_styles:
            for style, color_hexes in self.STYLE_COLOR_MAP.items():
                if style not in existing_preferences and not any(s.name == style for s in recommended_styles):
                    color_names = [self._get_color_name_from_hex(hex_code) for hex_code in color_hexes]
                    if any(color in color_names for color in color_preferences):
                        tags = self.DEFINED_STYLES.get(style, [style])
                        recommended_styles.append(Style(style, tags))
                        if len(recommended_styles) >= max_styles:
                            break
        
        # 4. 如果还不够，添加通用风格建议
        default_styles = ["休闲", "简约", "时尚"]
        for style in default_styles:
            if style not in existing_preferences and not any(s.name == style for s in recommended_styles):
                if len(recommended_styles) < max_styles:
                    tags = self.DEFINED_STYLES.get(style, [style])
                    recommended_styles.append(Style(style, tags))
        
        # 限制返回数量
        return recommended_styles[:max_styles]


class OccasionRecommendationService:
    """场合推荐服务
    
    负责基于用户衣橱内容推荐适合的场合穿搭
    """
    
    # 预定义场合
    OCCASION_DEFINITIONS = {
        "casual": {
            "name": "休闲",
            "dress_code": "随意舒适",
            "formality_level": 1,
            "suitable_time": ["上午", "下午", "晚上"],
            "indoor": True
        },
        "work": {
            "name": "工作",
            "dress_code": "商务整洁",
            "formality_level": 3,
            "suitable_time": ["上午", "下午"],
            "indoor": True
        },
        "formal": {
            "name": "正式场合",
            "dress_code": "正装",
            "formality_level": 5,
            "suitable_time": ["下午", "晚上"],
            "indoor": True
        },
        "dating": {
            "name": "约会",
            "dress_code": "精致时尚",
            "formality_level": 3,
            "suitable_time": ["下午", "晚上"],
            "indoor": True
        },
        "party": {
            "name": "派对",
            "dress_code": "时尚活力",
            "formality_level": 3,
            "suitable_time": ["晚上"],
            "indoor": True
        },
        "sport": {
            "name": "运动",
            "dress_code": "舒适功能",
            "formality_level": 1,
            "suitable_time": ["上午", "下午"],
            "indoor": False
        },
        "travel": {
            "name": "旅行",
            "dress_code": "舒适实用",
            "formality_level": 1,
            "suitable_time": ["上午", "下午", "晚上"],
            "indoor": False
        }
    }
    
    # 场合与衣物特征的映射
    OCCASION_CLOTHING_FEATURES = {
        "casual": {
            "required_categories": ["上衣", "裤子", "鞋子"],
            "preferred_styles": ["休闲", "简约", "运动"],
            "avoided_styles": ["正式", "奢华"]
        },
        "work": {
            "required_categories": ["上衣", "裤子", "鞋子"],
            "preferred_styles": ["商务", "正式", "简约"],
            "avoided_styles": ["运动", "街头"]
        },
        "formal": {
            "required_categories": ["上衣", "裤子", "鞋子", "外套"],
            "preferred_styles": ["正式", "奢华", "经典"],
            "avoided_styles": ["休闲", "运动", "街头"]
        },
        "dating": {
            "required_categories": ["上衣", "裤子", "鞋子"],
            "preferred_styles": ["休闲", "浪漫", "时尚"],
            "avoided_styles": ["运动", "功能"]
        },
        "party": {
            "required_categories": ["上衣", "裤子", "鞋子"],
            "preferred_styles": ["时尚", "前卫", "华丽"],
            "avoided_styles": ["商务", "运动"]
        },
        "sport": {
            "required_categories": ["上衣", "裤子", "鞋子"],
            "preferred_styles": ["运动", "功能", "休闲"],
            "avoided_styles": ["正式", "奢华"]
        },
        "travel": {
            "required_categories": ["上衣", "裤子", "鞋子", "帽子"],
            "preferred_styles": ["休闲", "简约", "功能"],
            "avoided_styles": ["正式", "奢华"]
        }
    }
    
    def recommend_occasions(
        self, 
        wardrobe: Wardrobe,
        max_occasions: int = 3
    ) -> List[Tuple[Occasion, List[Outfit]]]:
        """推荐场合及对应穿搭
        
        Args:
            wardrobe: 用户衣橱
            max_occasions: 最大推荐场合数量
            
        Returns:
            场合和对应穿搭列表的元组列表
        """
        # 分析衣橱中适合的场合
        occasion_suitability = self._analyze_occasion_suitability(wardrobe)
        
        # 找出最适合的场合
        best_occasions = self._select_best_occasions(occasion_suitability, max_occasions)
        
        # 为每个场合生成穿搭
        result = []
        for occasion_key in best_occasions:
            # 创建场合值对象
            occasion_def = self.OCCASION_DEFINITIONS[occasion_key]
            occasion = Occasion(
                occasion_key,
                dress_code=occasion_def["dress_code"],
                formality_level=occasion_def["formality_level"],
                suitable_time=occasion_def["suitable_time"],
                indoor=occasion_def["indoor"]
            )
            
            # 为该场合生成穿搭
            outfits = self._generate_outfits_for_occasion(wardrobe, occasion_key)
            
            if outfits:
                result.append((occasion, outfits))
        
        return result
    
    def _analyze_occasion_suitability(self, wardrobe: Wardrobe) -> Dict[str, float]:
        """分析衣橱中适合各场合的程度"""
        # 初始化场合适合度评分
        occasion_scores = {k: 0.0 for k in self.OCCASION_DEFINITIONS.keys()}
        
        # 没有衣物的情况
        if not wardrobe.items:
            return occasion_scores
        
        # 按类别分组衣物
        items_by_category = {}
        for item in wardrobe.items:
            # 简化：假设已知类别名称
            # 实际系统中应查询类别仓储
            category_name = f"category_{item.category_id}"
            if category_name not in items_by_category:
                items_by_category[category_name] = []
            items_by_category[category_name].append(item)
        
        # 分析每个场合的适合度
        for occasion_key, features in self.OCCASION_CLOTHING_FEATURES.items():
            # 检查所需类别是否都有
            required_categories = features["required_categories"]
            category_score = sum(1 for cat in required_categories if any(cat in c for c in items_by_category.keys())) / len(required_categories)
            
            # 检查风格匹配度
            style_score = 0.0
            style_items_count = 0
            
            for items in items_by_category.values():
                for item in items:
                    style_items_count += 1
                    
                    # 检查标签
                    item_style_score = 0.0
                    has_style_tag = False
                    
                    for tag in item.tags:
                        if tag.category == "style":
                            has_style_tag = True
                            if tag.name in features["preferred_styles"]:
                                item_style_score = 1.0
                            elif tag.name in features["avoided_styles"]:
                                item_style_score = -0.5
                    
                    style_score += item_style_score if has_style_tag else 0
            
            # 平均风格得分
            if style_items_count > 0:
                style_score = max(0, style_score / style_items_count)
            
            # 计算总得分（类别占60%，风格占40%）
            total_score = category_score * 0.6 + style_score * 0.4
            occasion_scores[occasion_key] = total_score
        
        return occasion_scores
    
    def _select_best_occasions(self, occasion_suitability: Dict[str, float], max_occasions: int) -> List[str]:
        """选择最适合的场合"""
        sorted_occasions = sorted(occasion_suitability.items(), key=lambda x: x[1], reverse=True)
        # 过滤掉得分太低的场合（低于0.3分）
        filtered_occasions = [o[0] for o in sorted_occasions if o[1] >= 0.3]
        return filtered_occasions[:max_occasions]
    
    def _generate_outfits_for_occasion(self, wardrobe: Wardrobe, occasion_key: str) -> List[Outfit]:
        """为指定场合生成穿搭"""
        # 使用OutfitMatchingService生成穿搭
        # 这里简化实现，实际应该注入服务或使用工厂
        matching_service = OutfitMatchingService()
        
        # 简化：使用固定的季节和天气
        # 实际系统应考虑当前季节和天气
        outfits = matching_service.match_outfits(
            wardrobe=wardrobe,
            occasion=occasion_key,
            season="spring",  # 简化：固定使用春季
            weather="sunny",  # 简化：固定使用晴天
            style_preference=None,  # 不指定风格偏好
            max_outfits=3  # 每个场合最多3个穿搭
        )
        
        return outfits


class SeasonRecommendationService:
    """季节推荐服务
    
    负责基于季节特点推荐适合的穿搭
    """
    
    # 季节特征配置
    SEASON_FEATURES = {
        "spring": {
            "temperature_range": (10, 25),
            "key_colors": ["#C1E1C1", "#F7CAC9", "#AEC6CF"],  # 清新色系
            "key_materials": ["cotton", "linen"],
            "layer_count": 2,
            "key_pieces": ["轻薄外套", "衬衫", "长裤", "运动鞋"],
            "avoid_pieces": ["厚重大衣", "羽绒服"]
        },
        "summer": {
            "temperature_range": (25, 40),
            "key_colors": ["#FFFFFF", "#87CEEB", "#FFFF99"],  # 明亮色系
            "key_materials": ["cotton", "linen"],
            "layer_count": 1,
            "key_pieces": ["T恤", "短裤", "凉鞋", "遮阳帽"],
            "avoid_pieces": ["厚外套", "长靴", "羊毛衫"]
        },
        "autumn": {
            "temperature_range": (10, 25),
            "key_colors": ["#D2691E", "#CD5C5C", "#F4A460"],  # 暖色系
            "key_materials": ["cotton", "wool", "leather"],
            "layer_count": 2,
            "key_pieces": ["风衣", "针织衫", "牛仔裤", "靴子"],
            "avoid_pieces": ["短袖T恤", "短裤", "凉鞋"]
        },
        "winter": {
            "temperature_range": (-10, 10),
            "key_colors": ["#000000", "#808080", "#4B0082"],  # 深色系
            "key_materials": ["wool", "down", "leather"],
            "layer_count": 3,
            "key_pieces": ["羽绒服", "毛衣", "围巾", "保暖靴"],
            "avoid_pieces": ["短袖", "凉鞋", "薄款衣物"]
        }
    }
    
    def recommend_for_season(
        self, 
        wardrobe: Wardrobe,
        season: str,
        max_outfits: int = 5
    ) -> List[Outfit]:
        """为指定季节推荐穿搭
        
        Args:
            wardrobe: 用户衣橱
            season: 季节名称
            max_outfits: 最大推荐数量
            
        Returns:
            适合该季节的穿搭列表
        """
        # 获取季节特征
        season_features = self._get_season_features(season)
        if not season_features:
            return []
        
        # 过滤适合该季节的衣物
        suitable_items = self._filter_season_suitable_items(wardrobe.items, season)
        if len(suitable_items) < 3:  # 至少需要3件衣物才能组成穿搭
            return []
        
        # 创建穿搭
        outfits = self._create_season_outfits(suitable_items, season, max_outfits, wardrobe.owner_id)
        
        return outfits
    
    def _get_season_features(self, season: str) -> Dict[str, any]:
        """获取季节特征"""
        return self.SEASON_FEATURES.get(season.lower(), {})
    
    def _filter_season_suitable_items(self, items: List[ClothingItem], season: str) -> List[ClothingItem]:
        """过滤适合该季节的衣物"""
        if not items:
            return []
        
        season_lower = season.lower()
        season_features = self._get_season_features(season_lower)
        if not season_features:
            return []
        
        suitable_items = []
        
        for item in items:
            # 1. 检查是否有季节标签
            has_season_tag = False
            for tag in item.tags:
                if tag.category == "season" and tag.name.lower() == season_lower:
                    has_season_tag = True
                    suitable_items.append(item)
                    break
            
            # 2. 如果没有季节标签，通过材质和特征判断
            if not has_season_tag:
                # 检查材质
                material_suitable = False
                if hasattr(item, 'material') and item.material:
                    material_name = item.material.name.lower()
                    if any(key_mat in material_name for key_mat in season_features["key_materials"]):
                        material_suitable = True
                
                # 检查颜色是否接近季节推荐色系
                color_suitable = False
                if hasattr(item, 'color') and item.color and hasattr(item.color, 'hex_code'):
                    # 简化：只检查是否使用季节推荐色系之一
                    color_suitable = item.color.hex_code in season_features["key_colors"]
                
                # 如果材质或颜色符合季节特征，则添加
                if material_suitable or color_suitable:
                    suitable_items.append(item)
        
        return suitable_items
    
    def _create_season_outfits(
        self,
        suitable_items: List[ClothingItem],
        season: str,
        max_outfits: int,
        owner_id: UUID
    ) -> List[Outfit]:
        """创建季节穿搭"""
        if not suitable_items:
            return []
        
        season_features = self._get_season_features(season)
        layer_count = season_features.get("layer_count", 2)
        
        # 按类别分组衣物
        items_by_category = {}
        for item in suitable_items:
            category_name = f"category_{item.category_id}"
            if category_name not in items_by_category:
                items_by_category[category_name] = []
            items_by_category[category_name].append(item)
        
        # 检查是否有足够的类别
        if len(items_by_category) < 3:  # 至少需要3个类别
            return []
        
        outfits = []
        
        # 创建指定数量的穿搭
        for i in range(min(max_outfits, 3)):  # 简化：最多创建3个穿搭
            # 为每个穿搭选择不同的场合
            occasions = ["casual", "work", "dating"]
            occasion = occasions[i % len(occasions)]
            
            # 创建穿搭
            outfit = Outfit(
                id=uuid4(),
                name=f"{season.capitalize()} {occasion.capitalize()} {i+1}",
                owner_id=owner_id,
                occasion=occasion,
                season=season,
                weather="sunny"  # 简化：固定使用晴天
            )
            
            # 根据季节需要的层数，添加对应层数的衣物
            added_categories = set()
            layer = 1
            
            # 选择关键单品
            for category, items in items_by_category.items():
                if len(added_categories) < layer_count + 1:  # +1 for shoes
                    # 避免重复类别
                    if category in added_categories:
                        continue
                    
                    # 随机选择一件衣物
                    if items:
                        chosen_item = random.choice(items)
                        try:
                            outfit.add_item(chosen_item, layer)
                            added_categories.add(category)
                            layer += 1
                        except Exception:
                            # 如果添加失败，继续尝试其他衣物
                            continue
            
            # 如果穿搭包含足够的衣物，添加到结果
            if len(outfit.items) >= min(3, layer_count + 1):
                outfits.append(outfit)
        
        return outfits 