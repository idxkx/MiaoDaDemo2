"""
图片存储服务测试
"""

import pytest
import os
import shutil
from pathlib import Path
import base64
from io import BytesIO
from datetime import datetime

# 尝试导入PIL库，如果不可用则跳过需要PIL的测试
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from src.infrastructure.storage import (
    StorageService, 
    LocalStorageService, 
    ImageStorageService,
    StorageFactory
)
from src.domain.model.value_objects import ImageMetadata

# 测试目录
TEST_DIR = "tests/temp"
TEST_IMAGE_DIR = f"{TEST_DIR}/images"

@pytest.fixture(scope="function")
def setup_teardown():
    """设置和清理测试环境"""
    # 创建测试目录
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(TEST_IMAGE_DIR, exist_ok=True)
    
    yield
    
    # 清理测试目录
    shutil.rmtree(TEST_DIR)

@pytest.fixture
def test_image_data():
    """生成测试图片数据"""
    if not PIL_AVAILABLE:
        # 如果PIL不可用，返回一个简单的图片字节数据
        return b"test_image_data"
    
    # 创建一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()

@pytest.fixture
def test_image_file(test_image_data):
    """创建测试图片文件"""
    image_path = f"{TEST_IMAGE_DIR}/test.jpg"
    with open(image_path, "wb") as f:
        f.write(test_image_data)
    return image_path

@pytest.mark.asyncio
async def test_local_storage_service(setup_teardown, test_image_data):
    """测试本地存储服务"""
    # 创建本地存储服务
    storage = LocalStorageService(TEST_DIR)
    
    # 测试保存文件
    file_path = await storage.save_file("test_file.txt", b"test content")
    assert file_path == "test_file.txt"
    assert os.path.exists(os.path.join(TEST_DIR, "test_file.txt"))
    
    # 测试获取文件
    file_content = await storage.get_file("test_file.txt")
    assert file_content == b"test content"
    
    # 测试文件存在
    assert await storage.file_exists("test_file.txt")
    assert not await storage.file_exists("non_existent_file.txt")
    
    # 测试获取文件URL
    file_url = await storage.get_file_url("test_file.txt")
    assert TEST_DIR in file_url
    assert "test_file.txt" in file_url
    
    # 测试删除文件
    assert await storage.delete_file("test_file.txt")
    assert not await storage.file_exists("test_file.txt")
    assert not await storage.delete_file("non_existent_file.txt")

@pytest.mark.asyncio
@pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL库不可用，跳过图片处理测试")
async def test_image_storage_service(setup_teardown, test_image_data):
    """测试图片存储服务"""
    # 创建图片存储服务
    storage = ImageStorageService(
        base_dir=TEST_IMAGE_DIR,
        processed_dir=f"{TEST_IMAGE_DIR}/processed",
        auto_thumbnail=True
    )
    
    # 测试保存图片
    saved_path, metadata = await storage.save_image(
        test_image_data,
        filename="test_image.jpg",
        category="test"
    )
    
    # 验证返回值
    assert "test/20" in saved_path  # 应包含分类和日期
    assert "test_image.jpg" in saved_path
    
    # 验证元数据
    assert isinstance(metadata, ImageMetadata)
    assert metadata.width == 100
    assert metadata.height == 100
    assert metadata.format.lower() == "jpeg"
    assert metadata.size > 0
    assert isinstance(metadata.created_at, datetime)
    assert saved_path in metadata.location
    
    # 验证文件已保存
    full_path = os.path.join(TEST_IMAGE_DIR, saved_path)
    assert os.path.exists(full_path)
    
    # 测试获取图片和元数据
    image_data, retrieved_metadata = await storage.get_image_with_metadata(saved_path)
    assert image_data is not None
    assert retrieved_metadata is not None
    assert retrieved_metadata.width == 100
    assert retrieved_metadata.height == 100
    
    # 测试缩略图
    thumbnail_url = await storage.get_thumbnail_url(saved_path)
    assert thumbnail_url is not None
    assert "thumb" in thumbnail_url
    assert os.path.exists(thumbnail_url) or os.path.exists(thumbnail_url.replace("\\", "/"))
    
    # 测试base64编码
    base64_data = await storage.get_image_as_base64(saved_path)
    assert base64_data is not None
    assert base64_data.startswith("data:image/jpeg;base64,")
    
    # 测试删除图片
    assert await storage.delete_file(saved_path)
    assert not await storage.file_exists(saved_path)

@pytest.mark.asyncio
async def test_storage_factory(setup_teardown):
    """测试存储服务工厂"""
    # 确保存储目录
    StorageFactory.ensure_storage_dirs()
    
    # 获取本地存储服务
    local_storage = StorageFactory.get_local_storage(
        name="test",
        base_dir=TEST_DIR
    )
    assert isinstance(local_storage, LocalStorageService)
    
    # 获取图片存储服务
    image_storage = StorageFactory.get_image_storage(
        name="test",
        base_dir=TEST_IMAGE_DIR
    )
    assert isinstance(image_storage, ImageStorageService)
    
    # 测试获取同一实例
    local_storage2 = StorageFactory.get_local_storage(name="test")
    assert local_storage is local_storage2
    
    # 测试注册和获取自定义服务
    custom_storage = LocalStorageService(TEST_DIR + "/custom")
    StorageFactory.register_storage_service("custom", custom_storage)
    retrieved = StorageFactory.get_storage_service("custom")
    assert retrieved is custom_storage 