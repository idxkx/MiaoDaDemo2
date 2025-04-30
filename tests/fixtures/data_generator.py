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
import dataclasses
from uuid import UUID

from src.domain.model.value_objects import (
    ImageMetadata,
    Dimension,
    Color,
    Price,
    Brand,
    Material,
    Style,
    Size
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
        
        # Create Value Objects first
        color_vo = Color(name=color, hex_code="#FFFFFF")
        brand_vo = Brand(name=brand, country="未知")
        material_vo = Material(name=material, composition={material: 100.0})
        price_vo = Price(amount=price, currency="CNY")
        image_metadata_vo = ImageMetadata(
            width=800,
            height=1200,
            format="JPEG",
            size=random.randint(100000, 500000),
            created_at=datetime.now(),
            location=f"storage/images/{uuid4()}.jpg"
        )
        size_vo = Size("M")
        # Assuming default Dimension and Style VOs are needed
        dimension_vo = Dimension(size="M") # Default Dimension
        style_vo = Style(name="休闲", tags=["日常"]) # Default Style

        item_data = {
            "id": uuid4(),
            "name": f"{brand}{category_name}",
            "category_id": category_id,
            "color": dataclasses.asdict(color_vo),
            "brand": dataclasses.asdict(brand_vo),
            "material": dataclasses.asdict(material_vo),
            "price": dataclasses.asdict(price_vo),
            "image_metadata": dataclasses.asdict(image_metadata_vo),
            "dimension": dataclasses.asdict(dimension_vo),
            "style": dataclasses.asdict(style_vo),
            "description": f"一件漂亮的{brand}{category_name}",
            "tags": [],
            "is_favorite": random.choice([True, False]),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        # Note: Check if the Model needs wardrobe_id, if so, add it here.
        # Assuming populate_test_data handles adding to session and wardrobe association
        items.append(item_data)
    return items

def generate_outfits(clothing_items: List[Dict], owner_id: UUID, count: int = 3) -> List[Dict]:
    """生成穿搭数据"""
    outfits = []
    occasions = ["daily", "work", "party", "sport"]
    seasons = ["spring", "summer", "autumn", "winter"]
    weathers = ["sunny", "rainy", "cloudy", "snowy"]
    
    if len(clothing_items) < 2:
        print("Warning: Not enough clothing items to generate outfits. Skipping outfit generation.")
        return [] # Return empty list if not enough items

    for _ in range(count):
        # Ensure sample size is not larger than population
        max_sample_size = min(4, len(clothing_items))
        sample_size = random.randint(2, max_sample_size) 
        outfit_items_sample = random.sample(clothing_items, sample_size) 
        outfit = {
            "id": uuid4(), # Use UUID object directly
            "name": f"搭配{_ + 1}",
            "owner_id": owner_id, # Use the provided owner_id
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
                    "outfit_id": None,  # Will be set during saving
                    "item_id": item["id"],
                    "layer": idx + 1
                }
                for idx, item in enumerate(outfit_items_sample)
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