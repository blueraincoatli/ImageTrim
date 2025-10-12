#!/usr/bin/env python3
"""
图片缓存管理器
"""

from typing import Optional, Tuple
from collections import OrderedDict
from PIL import Image
from app.utils.image_utils import ImageUtils


class ImageCache:
    """
    图片缓存管理器
    使用LRU(最近最少使用)策略管理图片缓存
    """

    def __init__(self, max_size: int = 100):
        """
        初始化图片缓存

        Args:
            max_size: 缓存最大大小
        """
        self.max_size = max_size
        self.cache = OrderedDict()

    def get_image(self, file_path: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """
        获取图片

        Args:
            file_path: 文件路径
            size: 图片尺寸

        Returns:
            Image.Image: 图片对象，如果不存在则返回None
        """
        key = (file_path, size)
        
        if key in self.cache:
            # 移动到末尾（标记为最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        
        return None

    def put_image(self, file_path: str, size: Tuple[int, int], image: Image.Image):
        """
        存储图片

        Args:
            file_path: 文件路径
            size: 图片尺寸
            image: 图片对象
        """
        key = (file_path, size)
        
        # 如果缓存已满，删除最久未使用的项
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
            
        self.cache[key] = image

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    def get_cache_size(self) -> int:
        """
        获取缓存大小

        Returns:
            int: 缓存中图片数量
        """
        return len(self.cache)

    def get_or_create_thumbnail(self, file_path: str, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """
        获取或创建缩略图

        Args:
            file_path: 文件路径
            size: 缩略图尺寸

        Returns:
            Image.Image: 缩略图
        """
        # 尝试从缓存获取
        image = self.get_image(file_path, size)
        if image is not None:
            return image
            
        # 缓存中没有，创建新的缩略图
        try:
            image = ImageUtils.get_thumbnail(file_path, size)
            self.put_image(file_path, size, image)
            return image
        except Exception:
            # 出错时返回默认图像
            default_image = Image.new('RGB', size, color='gray')
            self.put_image(file_path, size, default_image)
            return default_image