#!/usr/bin/env python3
"""
图片处理工具
"""

import os
from typing import List, Tuple, Dict
from PIL import Image, ImageFile
import imagehash
import numpy as np

# 尝试导入AVIF支持
try:
    import pillow_avif
except ImportError:
    pass  # 如果没有安装AVIF插件，继续运行但不支持AVIF

# 设置图像加载限制，防止DOS攻击
Image.MAX_IMAGE_PIXELS = 178956970  # 默认限制


class ImageUtils:
    """
    图片处理工具类
    """

    @staticmethod
    def get_image_files(path: str, include_subdirs: bool = True, progress_callback=None) -> List[str]:
        """
        获取目录中的所有图片文件

        Args:
            path: 目录路径
            include_subdirs: 是否包含子目录
            progress_callback: 进度回调函数 callback(count) 每找到一个文件调用

        Returns:
            List[str]: 图片文件路径列表
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.avif'}
        image_files = []

        if os.path.isfile(path):
            if os.path.splitext(path)[1].lower() in image_extensions:
                image_files.append(path)
                if progress_callback:
                    progress_callback(1)
        elif os.path.isdir(path):
            if include_subdirs:
                for root, _, files in os.walk(path):
                    for file in files:
                        if os.path.splitext(file)[1].lower() in image_extensions:
                            image_files.append(os.path.join(root, file))
                            # 每找到一个文件就回调一次
                            if progress_callback:
                                progress_callback(len(image_files))
            else:
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in image_extensions:
                        image_files.append(file_path)
                        # 每找到一个文件就回调一次
                        if progress_callback:
                            progress_callback(len(image_files))

        return image_files

    @staticmethod
    def calculate_hash(file_path: str) -> imagehash.ImageHash:
        """
        计算图片哈希值

        Args:
            file_path: 图片文件路径

        Returns:
            imagehash.ImageHash: 图片哈希值
        """
        try:
            # 设置加载截断处理，避免因截断图像导致的错误
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            with Image.open(file_path) as img:
                # 检查图像尺寸是否超过限制
                if img.width * img.height > Image.MAX_IMAGE_PIXELS:
                    raise Exception(f"图像尺寸过大 ({img.width}x{img.height}={img.width * img.height} pixels)，超过限制 {Image.MAX_IMAGE_PIXELS} pixels")
                
                # 调整图像大小以提高处理速度并减少内存使用
                max_dimension = 512
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                return imagehash.phash(img)
        except Exception as e:
            raise Exception(f"计算图片哈希值失败: {file_path}, 错误: {str(e)}")

    @staticmethod
    def calculate_similarity(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
        """
        计算两个哈希值的相似度

        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值

        Returns:
            float: 相似度 (0-1)
        """
        # 计算汉明距离
        hamming_distance = hash1 - hash2
        # 转换为相似度 (0-1)
        similarity = 1 - (hamming_distance / len(hash1.hash) ** 2)
        return similarity

    @staticmethod
    def find_duplicates(image_files: List[str], threshold: float = 0.95, progress_callback=None, should_stop=None) -> Dict[str, List[str]]:
        """
        查找重复图片

        Args:
            image_files: 图片文件路径列表
            threshold: 相似度阈值
            progress_callback: 进度回调函数 callback(progress, message)
            should_stop: 停止检查函数 should_stop() -> bool

        Returns:
            Dict[str, List[str]]: 重复图片组，键为主图片路径，值为相似图片路径列表
        """
        if len(image_files) < 2:
            return {}

        total_files = len(image_files)

        # 阶段1: 计算所有图片的哈希值 (40% - 70%)
        hashes = {}
        for idx, file_path in enumerate(image_files):
            # 检查是否需要停止
            if should_stop and should_stop():
                return {}

            try:
                hashes[file_path] = ImageUtils.calculate_hash(file_path)

                # 更新进度
                if progress_callback:
                    progress = 40 + (idx + 1) / total_files * 30  # 40-70%
                    progress_callback(progress, f"计算图片哈希值... {idx+1}/{total_files}")

            except Exception as e:
                print(f"警告: 无法处理文件 {file_path}: {e}")

        if not hashes:
            return {}

        # 阶段2: 查找重复项 (70% - 100%)
        duplicates = {}
        processed = set()
        hash_items = list(hashes.items())
        total_comparisons = len(hash_items)

        for i, (file1, hash1) in enumerate(hash_items):
            # 检查是否需要停止
            if should_stop and should_stop():
                return duplicates

            if file1 in processed:
                continue

            group = [file1]
            processed.add(file1)

            for file2, hash2 in hash_items[i+1:]:
                if file2 in processed:
                    continue

                try:
                    similarity = ImageUtils.calculate_similarity(hash1, hash2)
                    if similarity >= threshold:
                        group.append(file2)
                        processed.add(file2)
                except Exception as e:
                    print(f"警告: 比较文件时出错 {file1} 和 {file2}: {e}")

            # 如果组中有多个文件，则认为是重复项
            if len(group) > 1:
                duplicates[group[0]] = group[1:]

            # 更新进度
            if progress_callback:
                progress = 70 + (i + 1) / total_comparisons * 30  # 70-100%
                progress_callback(progress, f"查找重复项... {i+1}/{total_comparisons}")

        return duplicates

    @staticmethod
    def get_thumbnail(file_path: str, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """
        获取图片缩略图

        Args:
            file_path: 图片文件路径
            size: 缩略图尺寸

        Returns:
            Image.Image: 缩略图
        """
        try:
            # 设置加载截断处理，避免因截断图像导致的错误
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            with Image.open(file_path) as img:
                # 检查图像尺寸是否超过限制
                if img.width * img.height > Image.MAX_IMAGE_PIXELS:
                    raise Exception(f"图像尺寸过大 ({img.width}x{img.height}={img.width * img.height} pixels)，超过限制 {Image.MAX_IMAGE_PIXELS} pixels")
                
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return img.copy()
        except Exception as e:
            # 返回默认图像或空白图像
            return Image.new('RGB', size, color='gray')

    @staticmethod
    def convert_to_avif(source_path: str, target_path: str, quality: int = 85):
        """
        将图片转换为AVIF格式

        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            quality: 质量 (1-100)
        """
        try:
            # 尝试导入AVIF支持
            try:
                import pillow_avif
            except ImportError:
                raise Exception("未安装pillow-avif-plugin，请安装该插件以支持AVIF格式")
                
            # 设置加载截断处理，避免因截断图像导致的错误
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            with Image.open(source_path) as img:
                # 检查图像尺寸是否超过限制
                if img.width * img.height > Image.MAX_IMAGE_PIXELS:
                    raise Exception(f"图像尺寸过大 ({img.width}x{img.height}={img.width * img.height} pixels)，超过限制 {Image.MAX_IMAGE_PIXELS} pixels")
                
                # 转换为RGB模式（如果需要）
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                    
                # 保存为AVIF格式
                img.save(target_path, 'AVIF', quality=quality)
        except Exception as e:
            raise Exception(f"转换图片失败: {source_path} -> {target_path}, 错误: {str(e)}")

    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """
        获取图片信息

        Args:
            file_path: 图片文件路径

        Returns:
            dict: 图片信息
        """
        try:
            # 设置加载截断处理，避免因截断图像导致的错误
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            with Image.open(file_path) as img:
                # 检查图像尺寸是否超过限制
                if img.width * img.height > Image.MAX_IMAGE_PIXELS:
                    raise Exception(f"图像尺寸过大 ({img.width}x{img.height}={img.width * img.height} pixels)，超过限制 {Image.MAX_IMAGE_PIXELS} pixels")
                
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
        except Exception as e:
            return {
                'format': 'Unknown',
                'mode': 'Unknown',
                'size': (0, 0),
                'width': 0,
                'height': 0,
                'error': str(e)
            }