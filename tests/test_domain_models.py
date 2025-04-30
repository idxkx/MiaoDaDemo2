"""领域模型单元测试"""

import pytest
from uuid import UUID
from datetime import datetime
import time

from src.domain.model.aggregates import Outfit, Wardrobe, UserProfile, OutfitRecommendation
from src.domain.model.entities import ClothingItem, Category, Tag, User, Comment, Favorite
from src.domain.model.value_objects import Color, Size, Material, Brand
from src.domain.model.exceptions import (
    OutfitItemLimitExceeded,
    InvalidOutfitConfiguration,
    DuplicateClothingItem
)

TEST_WARDROBE_ID = UUID(int=99) # Define a test wardrobe ID

def create_test_category():
    """创建测试分类"""
    return Category(
        id=UUID(int=1),
        name="T恤",
        description="上衣类别-T恤",
        parent_id=UUID(int=2),  # 假设2是"上装"分类的ID
        wardrobe_id=TEST_WARDROBE_ID # Add wardrobe_id
    )

def create_test_clothing():
    """创建测试衣物"""
    return ClothingItem(
        id=UUID(int=3),
        name="基础白色T恤",
        description="简约风格的白色T恤",
        category_id=UUID(int=1),  # T恤分类
        wardrobe_id=TEST_WARDROBE_ID, # Add wardrobe_id
        color=Color("白色", "#FFFFFF"),
        size=Size("M"),
        brand=Brand("优衣库"),
        material=Material("棉", {"棉": 100.0}),
        purchase_date=datetime.now(),
        price=99.00,
        image_url="http://example.com/tshirt.jpg"
    )

def test_create_outfit():
    """测试创建穿搭"""
    # 创建穿搭
    outfit = Outfit(
        id=UUID(int=4),
        name="简约日常穿搭",
        owner_id=UUID(int=5),
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    assert outfit.id == UUID(int=4)
    assert outfit.name == "简约日常穿搭"
    assert len(outfit.items) == 0
    assert outfit.version == 1

def test_add_clothing_to_outfit():
    """测试向穿搭添加衣物"""
    outfit = Outfit(
        id=UUID(int=4),
        name="简约日常穿搭",
        owner_id=UUID(int=5),
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    # 添加衣物
    clothing = create_test_clothing()
    outfit.add_item(clothing, layer=1)
    
    assert len(outfit.items) == 1
    assert outfit.items[0] == clothing

def test_outfit_item_limit():
    """测试穿搭衣物数量限制"""
    outfit = Outfit(
        id=UUID(int=4),
        name="简约日常穿搭",
        owner_id=UUID(int=5),
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    # 添加超过限制数量的衣物
    with pytest.raises(OutfitItemLimitExceeded):
        for i in range(10):  # 假设限制是5件
            clothing = ClothingItem(
                id=UUID(int=10+i),
                name=f"测试衣物{i}",
                category_id=UUID(int=100+i),  # 使用不同的类别ID
                wardrobe_id=TEST_WARDROBE_ID, # Add wardrobe_id
                color=Color("白色", "#FFFFFF"),
                size=Size("M"),
                brand=Brand("测试品牌"),
                material=Material("棉", {"棉": 100.0}),
                purchase_date=datetime.now(),
                price=99.00
            )
            outfit.add_item(clothing, layer=i+1)

def test_wardrobe_management():
    """测试衣橱管理"""
    # 创建衣橱
    wardrobe = Wardrobe(
        id=UUID(int=5),
        owner_id=UUID(int=6)
    )
    
    # 添加衣物
    clothing = create_test_clothing()
    wardrobe.add_item(clothing)
    
    assert len(wardrobe.items) == 1
    
    # 测试添加重复衣物
    with pytest.raises(DuplicateClothingItem):
        wardrobe.add_item(clothing)
    
    # 移除衣物
    wardrobe.remove_item(clothing.id)
    assert len(wardrobe.items) == 0

def test_outfit_validation():
    """测试穿搭验证"""
    outfit = Outfit(
        id=UUID(int=4),
        name="简约日常穿搭",
        owner_id=UUID(int=5),
        occasion="daily",
        season="spring",
        weather="sunny"
    )
    
    # 添加相同类别的衣物（例如两件上衣）
    top1 = ClothingItem(
        id=UUID(int=6),
        name="白色T恤1",
        category_id=UUID(int=1),  # T恤分类
        wardrobe_id=TEST_WARDROBE_ID, # Add wardrobe_id
        color=Color("白色", "#FFFFFF"),
        size=Size("M"),
        brand=Brand("品牌A"),
        material=Material("棉", {"棉": 100.0}),
        purchase_date=datetime.now(),
        price=99.00
    )
    
    top2 = ClothingItem(
        id=UUID(int=7),
        name="白色T恤2",
        category_id=UUID(int=1),  # T恤分类
        wardrobe_id=TEST_WARDROBE_ID, # Add wardrobe_id
        color=Color("白色", "#FFFFFF"),
        size=Size("M"),
        brand=Brand("品牌B"),
        material=Material("棉", {"棉": 100.0}),
        purchase_date=datetime.now(),
        price=99.00
    )
    
    outfit.add_item(top1, layer=1)
    
    # 添加同类别的第二件衣物应该引发异常
    with pytest.raises(InvalidOutfitConfiguration):
        outfit.add_item(top2, layer=2)

def test_tag_management():
    """测试标签管理"""
    # 创建衣物
    clothing = create_test_clothing()
    
    # 创建并添加标签
    tag1 = Tag(id=UUID(int=8), name="简约", category="style")
    tag2 = Tag(id=UUID(int=9), name="百搭", category="style")
    
    clothing.add_tag(tag1)
    clothing.add_tag(tag2)
    
    assert len(clothing.tags) == 2
    assert tag1 in clothing.tags
    assert tag2 in clothing.tags
    
    # 移除标签
    clothing.remove_tag(tag1.id)
    assert len(clothing.tags) == 1
    assert tag1 not in clothing.tags
    assert tag2 in clothing.tags

def test_user_entity():
    """测试用户实体"""
    # 创建用户
    user = User(
        id=UUID(int=10),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        nickname="测试用户",
        avatar_url="http://example.com/avatar.jpg",
        gender="male",
        birth_date=datetime(1990, 1, 1)
    )
    
    assert user.id == UUID(int=10)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.nickname == "测试用户"
    assert user.avatar_url == "http://example.com/avatar.jpg"
    assert user.gender == "male"
    assert user.birth_date == datetime(1990, 1, 1)
    assert user.is_active == True
    assert user.last_login is None
    
    # 测试更新信息
    user.update_nickname("新昵称")
    assert user.nickname == "新昵称"
    
    user.update_email("new@example.com")
    assert user.email == "new@example.com"
    
    # 测试用户偏好
    user.set_preference("favorite_color", "blue")
    user.set_preference("favorite_style", "casual")
    
    assert user.preferences == {
        "favorite_color": "blue",
        "favorite_style": "casual"
    }
    
    user.remove_preference("favorite_color")
    assert "favorite_color" not in user.preferences
    assert "favorite_style" in user.preferences
    
    # 测试账户状态
    user.deactivate()
    assert user.is_active == False
    
    user.activate()
    assert user.is_active == True
    
    # 测试登录记录
    assert user.last_login is None
    user.record_login()
    assert user.last_login is not None

def test_comment_entity():
    """测试评论实体"""
    # 创建评论
    comment = Comment(
        id=UUID(int=11),
        content="这是一条测试评论",
        user_id=UUID(int=10),
        target_id=UUID(int=4),  # 穿搭ID
        target_type="outfit"
    )
    
    assert comment.id == UUID(int=11)
    assert comment.content == "这是一条测试评论"
    assert comment.user_id == UUID(int=10)
    assert comment.target_id == UUID(int=4)
    assert comment.target_type == "outfit"
    assert comment.parent_id is None
    assert comment.likes_count == 0
    assert comment.is_deleted == False
    
    # 测试评论编辑
    comment.edit_content("修改后的评论内容")
    assert comment.content == "修改后的评论内容"
    
    # 测试点赞
    comment.add_like()
    assert comment.likes_count == 1
    
    comment.add_like()
    assert comment.likes_count == 2
    
    comment.remove_like()
    assert comment.likes_count == 1
    
    # 测试删除和恢复
    comment.delete()
    assert comment.is_deleted == True
    
    # 删除后不能编辑
    with pytest.raises(ValueError):
        comment.edit_content("尝试编辑已删除的评论")
    
    comment.restore()
    assert comment.is_deleted == False
    
    # 恢复后可以编辑
    comment.edit_content("恢复后编辑的内容")
    assert comment.content == "恢复后编辑的内容"

def test_nested_comment():
    """测试嵌套评论"""
    parent_comment = Comment(
        id=UUID(int=11),
        content="父评论",
        user_id=UUID(int=10),
        target_id=UUID(int=4),
        target_type="outfit"
    )
    
    reply_comment = Comment(
        id=UUID(int=12),
        content="回复评论",
        user_id=UUID(int=13),
        target_id=UUID(int=4),
        target_type="outfit",
        parent_id=UUID(int=11)  # 指向父评论
    )
    
    assert reply_comment.parent_id == UUID(int=11)
    assert reply_comment.target_id == parent_comment.target_id
    assert reply_comment.target_type == parent_comment.target_type

def test_favorite_entity():
    """测试收藏实体"""
    # 创建收藏
    favorite = Favorite(
        id=UUID(int=14),
        user_id=UUID(int=10),
        target_id=UUID(int=4),  # 穿搭ID
        target_type="outfit",
        note="我喜欢这个搭配"
    )
    
    assert favorite.id == UUID(int=14)
    assert favorite.user_id == UUID(int=10)
    assert favorite.target_id == UUID(int=4)
    assert favorite.target_type == "outfit"
    assert favorite.note == "我喜欢这个搭配"
    assert favorite.is_public == True
    assert len(favorite.tags) == 0
    
    # 测试收藏备注更新
    favorite.update_note("这是更新后的备注")
    assert favorite.note == "这是更新后的备注"
    
    # 测试公开/私密切换
    favorite.toggle_public()
    assert favorite.is_public == False
    
    favorite.toggle_public()
    assert favorite.is_public == True
    
    # 测试标签管理
    favorite.add_tag("春季")
    favorite.add_tag("通勤")
    assert "春季" in favorite.tags
    assert "通勤" in favorite.tags
    
    favorite.remove_tag("春季")
    assert "春季" not in favorite.tags
    assert "通勤" in favorite.tags
    
    favorite.clear_tags()
    assert len(favorite.tags) == 0

def test_user_profile():
    """测试用户个人资料聚合根"""
    # 创建用户个人资料
    user_profile = UserProfile(
        id=UUID(int=15),
        user_id=UUID(int=10),
        display_name="测试用户",
        bio="这是一个测试用户",
        avatar_url="http://example.com/avatar.jpg"
    )
    
    assert user_profile.id == UUID(int=15)
    assert user_profile.user_id == UUID(int=10)
    assert user_profile.display_name == "测试用户"
    assert user_profile.bio == "这是一个测试用户"
    assert user_profile.avatar_url == "http://example.com/avatar.jpg"
    assert len(user_profile.favorites) == 0
    assert len(user_profile.following) == 0
    assert len(user_profile.followers) == 0
    
    # 测试更新个人资料
    user_profile.update_profile(
        display_name="新昵称",
        bio="更新后的简介",
        avatar_url="http://example.com/new_avatar.jpg"
    )
    
    assert user_profile.display_name == "新昵称"
    assert user_profile.bio == "更新后的简介"
    assert user_profile.avatar_url == "http://example.com/new_avatar.jpg"
    
    # 测试收藏管理
    outfit_id = UUID(int=4)
    user_profile.add_favorite(outfit_id)
    assert len(user_profile.favorites) == 1
    assert outfit_id in user_profile.favorites
    
    user_profile.remove_favorite(outfit_id)
    assert len(user_profile.favorites) == 0
    
    # 测试关注/粉丝管理
    other_user_id = UUID(int=20)
    user_profile.follow_user(other_user_id)
    assert other_user_id in user_profile.following
    
    user_profile.add_follower(other_user_id)
    assert other_user_id in user_profile.followers
    
    user_profile.unfollow_user(other_user_id)
    assert other_user_id not in user_profile.following
    
    user_profile.remove_follower(other_user_id)
    assert other_user_id not in user_profile.followers
    
    # 测试风格和颜色偏好
    user_profile.add_style_preference("casual")
    user_profile.add_style_preference("formal")
    assert "casual" in user_profile.style_preferences
    assert "formal" in user_profile.style_preferences
    
    color = Color("蓝色", "#0000FF")
    user_profile.add_color_preference(color)
    assert color in user_profile.color_preferences
    
    user_profile.remove_style_preference("casual")
    assert "casual" not in user_profile.style_preferences
    
    user_profile.remove_color_preference(color)
    assert color not in user_profile.color_preferences
    
    # 测试登录记录
    initial_login = user_profile.last_login
    time.sleep(0.01)  # 添加10毫秒延迟
    user_profile.record_login()
    assert user_profile.last_login > initial_login

def test_outfit_recommendation():
    """测试搭配推荐聚合根"""
    # 创建搭配推荐
    recommendation = OutfitRecommendation(
        id=UUID(int=16),
        user_id=UUID(int=10),
        occasion="work",
        season="spring",
        weather="sunny",
        style_preference="business casual"
    )
    
    assert recommendation.id == UUID(int=16)
    assert recommendation.user_id == UUID(int=10)
    assert recommendation.occasion == "work"
    assert recommendation.season == "spring"
    assert recommendation.weather == "sunny"
    assert recommendation.style_preference == "business casual"
    assert len(recommendation.recommended_outfits) == 0
    assert len(recommendation.accepted_outfits) == 0
    assert len(recommendation.rejected_outfits) == 0
    assert recommendation.is_processed == False
    assert recommendation.processing_time is None
    
    # 测试添加推荐
    outfit_id1 = UUID(int=4)
    outfit_id2 = UUID(int=5)
    
    recommendation.add_recommended_outfit(outfit_id1)
    recommendation.add_recommended_outfit(outfit_id2)
    
    assert len(recommendation.recommended_outfits) == 2
    assert outfit_id1 in recommendation.recommended_outfits
    assert outfit_id2 in recommendation.recommended_outfits
    
    # 测试接受和拒绝推荐
    recommendation.accept_outfit(outfit_id1)
    recommendation.reject_outfit(outfit_id2)
    
    assert outfit_id1 in recommendation.accepted_outfits
    assert outfit_id2 in recommendation.rejected_outfits
    
    # 测试清除推荐
    recommendation.clear_recommendations()
    assert len(recommendation.recommended_outfits) == 0
    
    # 测试处理完成
    recommendation.mark_as_processed(0.5)  # 处理时间0.5秒 