"""测试数据生成器

此模块用于生成测试用的模拟数据，包括：
- 角色数据
- 衣物数据
- 穿搭数据
- 分类数据
- 标签数据
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict
from uuid import uuid4

from src.domain.model.value_objects import (
    ImageMetadata,
    Dimension,
    Color,
    Price,
    Brand,
    Material,
    Style
)

# 模拟数据配置
PERSONA_CONFIGS = [
    {
        "name": "小明",
        "gender": "male",
        "age": 25,
        "style_preference": "casual",
        "current_season": "spring",
        "preferred_occasion": "daily",
        "is_default": True
    },
    {
        "name": "小红",
        "gender": "female",
        "age": 28,
        "style_preference": "elegant",
        "current_season": "summer",
        "preferred_occasion": "work",
        "is_default": False
    }
]

CATEGORY_CONFIGS = [
    {
        "name": "上装",
        "subcategories": ["T恤", "衬衫", "毛衣", "外套"]
    },
    {
        "name": "下装",
        "subcategories": ["牛仔裤", "休闲裤", "短裤", "裙子"]
    },
    {
        "name": "鞋子",
        "subcategories": ["运动鞋", "皮鞋", "凉鞋", "靴子"]
    }
]

CLOTHING_CONFIGS = {
    "T恤": {
        "colors": ["白色", "黑色", "灰色", "蓝色"],
        "patterns": ["纯色", "条纹", "印花"],
        "brands": ["优衣库", "H&M", "ZARA"],
        "materials": ["棉", "涤纶"],
        "prices": [99, 199, 299]
    },
    "牛仔裤": {
        "colors": ["蓝色", "黑色"],
        "patterns": ["纯色", "做旧"],
        "brands": ["李维斯", "优衣库", "H&M"],
        "materials": ["牛仔布"],
        "prices": [299, 399, 499]
    }
}

TAG_CONFIGS = [
    "休闲", "正装", "运动", "派对",
    "春季", "夏季", "秋季", "冬季",
    "百搭", "显瘦", "保暖", "透气"
]

def generate_personas() -> List[Dict]:
    """生成角色数据"""
    personas = []
    for config in PERSONA_CONFIGS:
        persona = {
            "id": str(uuid4()),
            **config,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": 1
        }
        personas.append(persona)
    return personas

def generate_categories() -> List[Dict]:
    """生成分类数据"""
    categories = []
    for config in CATEGORY_CONFIGS:
        parent_id = str(uuid4())
        parent = {
            "id": parent_id,
            "name": config["name"],
            "parent_id": None,
            "description": f"{config['name']}分类",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        categories.append(parent)
        
        for subcat in config["subcategories"]:
            child = {
                "id": str(uuid4()),
                "name": subcat,
                "parent_id": parent_id,
                "description": f"{subcat}分类",
                "version": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            categories.append(child)
    return categories

def generate_clothing_items(category_id: str, count: int = 5) -> List[Dict]:
    """生成衣物数据"""
    items = []
    category_name = next(
        (cat["subcategories"][0] for cat in CATEGORY_CONFIGS 
         if cat["subcategories"][0] in CLOTHING_CONFIGS),
        "T恤"
    )
    config = CLOTHING_CONFIGS[category_name]
    
    for _ in range(count):
        color = random.choice(config["colors"])
        pattern = random.choice(config["patterns"])
        brand = random.choice(config["brands"])
        material = random.choice(config["materials"])
        price = random.choice(config["prices"])
        
        item = {
            "id": str(uuid4()),
            "name": f"{brand}{category_name}",
            "category_id": category_id,
            "color": Color(color).to_dict(),
            "pattern": pattern,
            "brand": Brand(brand, "").to_dict(),
            "material": Material(material).to_dict(),
            "price": Price(price, "CNY").to_dict(),
            "image_metadata": ImageMetadata(
                path=f"storage/images/{uuid4()}.jpg",
                size=random.randint(100000, 500000),
                width=800,
                height=1200,
                format="JPEG"
            ).to_dict(),
            "is_favorite": random.choice([True, False]),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        items.append(item)
    return items

def generate_outfits(clothing_items: List[Dict], count: int = 3) -> List[Dict]:
    """生成穿搭数据"""
    outfits = []
    occasions = ["daily", "work", "party", "sport"]
    seasons = ["spring", "summer", "autumn", "winter"]
    weathers = ["sunny", "rainy", "cloudy", "snowy"]
    
    for _ in range(count):
        outfit_items = random.sample(clothing_items, random.randint(2, 4))
        outfit = {
            "id": str(uuid4()),
            "name": f"搭配{_ + 1}",
            "description": f"这是一套{random.choice(['休闲', '正式', '运动'])}搭配",
            "occasion": random.choice(occasions),
            "season": random.choice(seasons),
            "weather": random.choice(weathers),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "is_favorite": random.choice([True, False]),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "items": [
                {
                    "outfit_id": None,  # 将在保存时设置
                    "item_id": item["id"],
                    "layer": idx + 1
                }
                for idx, item in enumerate(outfit_items)
            ]
        }
        outfits.append(outfit)
    return outfits

def generate_tags() -> List[Dict]:
    """生成标签数据"""
    tags = []
    for tag_name in TAG_CONFIGS:
        tag = {
            "id": str(uuid4()),
            "name": tag_name,
            "category": random.choice(["style", "season", "feature"]),
            "description": f"{tag_name}标签",
            "is_system": True,
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        tags.append(tag)
    return tags 