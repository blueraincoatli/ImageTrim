# -*- coding: utf-8 -*-
"""
图片处理工具类
统一的图片操作功能，包括格式转换、压缩、编辑等
"""

import os
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    from PIL import Image, ImageOps, ImageFilter, ImageEnhance
    from PIL.ExifTags import ORIENTATION
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Image utilities will be limited.")

from .error_handler import safe_operation, safe_image_processing, ProcessingError


class ImageFormat(Enum):
    """支持的图片格式"""
    JPEG = "JPEG"
    JPG = "JPG"
    PNG = "PNG"
    WEBP = "WEBP"
    BMP = "BMP"
    GIF = "GIF"
    TIFF = "TIFF"
    AVIF = "AVIF"  # 需要Pillow-AVIF插件


class ImageSize(Enum):
    """预设图片尺寸"""
    THUMBNAIL = (80, 80)
    SMALL = (160, 160)
    MEDIUM = (320, 320)
    LARGE = (640, 640)
    HD = (1280, 720)
    FULL_HD = (1920, 1080)


@dataclass
class ImageInfo:
    """图片信息数据类"""
    file_path: str
    format: str
    size: Tuple[int, int]
    file_size: int
    mode: str
    has_transparency: bool = False
    exif_data: Optional[Dict] = None


@dataclass
class ConversionOptions:
    """图片转换选项"""
    output_format: ImageFormat
    quality: int = 85  # 1-100
    optimize: bool = True
    preserve_exif: bool = False
    resize_to: Optional[Tuple[int, int]] = None
    maintain_aspect_ratio: bool = True
    background_color: str = "#FFFFFF"  # 用于透明背景


class ImageProcessor:
    """图片处理器 - 统一的图片操作接口"""

    def __init__(self, enable_avif: bool = True):
        self.enable_avif = enable_avif and self._check_avif_support()
        self.supported_formats = self._get_supported_formats()

    def _check_avif_support(self) -> bool:
        """检查AVIF支持"""
        if not PIL_AVAILABLE:
            return False

        try:
            from PIL import features
            return features.check('avif')
        except:
            return False

    def _get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        if not PIL_AVAILABLE:
            return []

        formats = ['JPEG', 'PNG', 'WEBP', 'BMP', 'GIF', 'TIFF']
        if self.enable_avif:
            formats.append('AVIF')

        return formats

    @safe_image_processing
    def get_image_info(self, file_path: str) -> Optional[ImageInfo]:
        """
        获取图片信息

        Args:
            file_path: 图片文件路径

        Returns:
            图片信息对象或None
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="get_image_info")

        if not os.path.exists(file_path):
            raise ProcessingError(f"File not found: {file_path}", operation="get_image_info")

        with Image.open(file_path) as img:
            # 获取基本信息
            file_size = os.path.getsize(file_path)
            has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info

            # 尝试获取EXIF数据
            exif_data = None
            try:
                exif = img._getexif()
                if exif:
                    exif_data = {ORIENTATION.get(tag, tag): value for tag, value in exif.items()}
            except:
                pass

            return ImageInfo(
                file_path=file_path,
                format=img.format,
                size=img.size,
                file_size=file_size,
                mode=img.mode,
                has_transparency=has_transparency,
                exif_data=exif_data
            )

    @safe_image_processing
    def create_thumbnail(self, file_path: str, size: Tuple[int, int] = ImageSize.THUMBNAIL.value,
                        maintain_aspect: bool = True) -> Optional[Image.Image]:
        """
        创建缩略图

        Args:
            file_path: 图片文件路径
            size: 目标尺寸
            maintain_aspect: 是否保持纵横比

        Returns:
            缩略图PIL对象或None
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="create_thumbnail")

        with Image.open(file_path) as img:
            # 转换模式
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            if maintain_aspect:
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(size, Image.Resampling.LANCZOS)

            return img.copy()

    @safe_image_processing
    def resize_image(self, file_path: str, target_size: Tuple[int, int],
                    maintain_aspect: bool = True, resample: int = Image.Resampling.LANCZOS) -> Optional[Image.Image]:
        """
        调整图片大小

        Args:
            file_path: 图片文件路径
            target_size: 目标尺寸
            maintain_aspect: 是否保持纵横比
            resample: 重采样方法

        Returns:
            调整后的图片对象或None
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="resize_image")

        with Image.open(file_path) as img:
            if maintain_aspect:
                # 计算保持纵横比的尺寸
                original_width, original_height = img.size
                target_width, target_height = target_size

                # 计算缩放比例
                scale = min(target_width / original_width, target_height / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                img = img.resize((new_width, new_height), resample)
            else:
                img = img.resize(target_size, resample)

            return img.copy()

    @safe_image_processing
    def convert_format(self, file_path: str, output_path: str,
                      options: ConversionOptions) -> bool:
        """
        转换图片格式

        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径
            options: 转换选项

        Returns:
            是否成功
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="convert_format")

        with Image.open(file_path) as img:
            # 处理EXIF方向
            img = self._apply_exif_orientation(img)

            # 调整大小
            if options.resize_to:
                if options.maintain_aspect_ratio:
                    img.thumbnail(options.resize_to, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(options.resize_to, Image.Resampling.LANCZOS)

            # 处理透明背景
            output_image = img
            if (img.mode in ('RGBA', 'LA') and
                options.output_format.value in ('JPEG', 'JPG') and
                options.background_color):
                # 创建白色背景
                background = Image.new('RGB', img.size, options.background_color)
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img.convert('L'))
                output_image = background

            # 保存参数
            save_params = {
                'format': options.output_format.value,
                'optimize': options.optimize,
            }

            # 根据格式添加特定参数
            if options.output_format in [ImageFormat.JPEG, ImageFormat.JPG]:
                save_params['quality'] = options.quality
                save_params['progressive'] = True
            elif options.output_format == ImageFormat.PNG:
                save_params['compress_level'] = min(9, max(0, (100 - options.quality) // 10))
            elif options.output_format == ImageFormat.WEBP:
                save_params['quality'] = options.quality
                save_params['method'] = 6  # 最佳压缩
            elif options.output_format == ImageFormat.AVIF:
                save_params['quality'] = options.quality
                save_params['speed'] = 6  # 平衡速度和质量

            # 保存图片
            output_image.save(output_path, **save_params)
            return True

    @safe_image_processing
    def optimize_image(self, file_path: str, output_path: str,
                      target_quality: int = 85) -> bool:
        """
        优化图片（减少文件大小）

        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径
            target_quality: 目标质量（1-100）

        Returns:
            是否成功
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="optimize_image")

        # 获取原始文件大小
        original_size = os.path.getsize(file_path)

        with Image.open(file_path) as img:
            # 转换模式
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # 保存参数
            save_params = {
                'format': 'JPEG',
                'quality': target_quality,
                'optimize': True,
                'progressive': True
            }

            # 保存优化后的图片
            img.save(output_path, **save_params)

        # 检查优化效果
        optimized_size = os.path.getsize(output_path)
        reduction = (1 - optimized_size / original_size) * 100

        return reduction > 0  # 只在确实减少了文件大小时返回成功

    @safe_image_processing
    def calculate_hash(self, file_path: str, hash_type: str = "perceptual") -> Optional[str]:
        """
        计算图片哈希值

        Args:
            file_path: 图片文件路径
            hash_type: 哈希类型 ("perceptual", "average", "difference", "md5")

        Returns:
            哈希字符串或None
        """
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL not available", operation="calculate_hash")

        if hash_type == "md5":
            return self._calculate_file_hash(file_path)

        try:
            import imagehash

            with Image.open(file_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 计算不同类型的哈希
                if hash_type == "perceptual":
                    hash_obj = imagehash.phash(img)
                elif hash_type == "average":
                    hash_obj = imagehash.average_hash(img)
                elif hash_type == "difference":
                    hash_obj = imagehash.dhash(img)
                else:
                    raise ProcessingError(f"Unsupported hash type: {hash_type}", operation="calculate_hash")

                return str(hash_obj)

        except ImportError:
            raise ProcessingError("imagehash library not available", operation="calculate_hash")

    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> Optional[str]:
        """计算文件内容的MD5哈希"""
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            raise ProcessingError(f"Failed to calculate file hash: {str(e)}", operation="calculate_file_hash")

    def _apply_exif_orientation(self, img: Image.Image) -> Image.Image:
        """应用EXIF方向信息"""
        try:
            exif = img._getexif()
            if exif:
                orientation = exif.get(ORIENTATION, 1)

                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass

        return img

    def is_valid_image(self, file_path: str) -> bool:
        """
        检查文件是否为有效图片

        Args:
            file_path: 文件路径

        Returns:
            是否为有效图片
        """
        return safe_operation(
            self._check_image_validity,
            ErrorLevel.DEBUG,
            ProcessingError,
            {"file_path": file_path},
            False,
            file_path
        )

    def _check_image_validity(self, file_path: str) -> bool:
        """实际检查图片有效性"""
        if not PIL_AVAILABLE:
            return False

        if not os.path.exists(file_path):
            return False

        try:
            with Image.open(file_path) as img:
                img.verify()  # 验证图片完整性
                return True
        except Exception:
            return False

    def get_optimal_format(self, file_path: str, prefer_quality: bool = True) -> ImageFormat:
        """
        获取最优的输出格式

        Args:
            file_path: 输入文件路径
            prefer_quality: 是否优先考虑质量

        Returns:
            推荐的图片格式
        """
        try:
            info = self.get_image_info(file_path)
            if not info:
                return ImageFormat.JPEG

            # 根据图片特征推荐格式
            if info.has_transparency:
                return ImageFormat.PNG if prefer_quality else ImageFormat.WEBP

            if info.size[0] * info.size[1] > 2000000:  # 大图片
                return ImageFormat.WEBP if self.enable_avif else ImageFormat.JPEG

            return ImageFormat.JPEG if prefer_quality else ImageFormat.WEBP

        except Exception:
            return ImageFormat.JPEG


class ImageBatchProcessor:
    """批量图片处理器"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.processor = ImageProcessor()

    def convert_directory(self, input_dir: str, output_dir: str,
                         options: ConversionOptions,
                         progress_callback: Optional[Callable[[int, int], None]] = None) -> Dict[str, Any]:
        """
        批量转换目录中的图片

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            options: 转换选项
            progress_callback: 进度回调函数 (current, total)

        Returns:
            处理结果统计
        """
        if not os.path.exists(input_dir):
            raise ProcessingError(f"Input directory not found: {input_dir}")

        os.makedirs(output_dir, exist_ok=True)

        # 收集图片文件
        image_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self.processor.is_valid_image(file_path):
                    image_files.append(file_path)

        total_files = len(image_files)
        if total_files == 0:
            return {"processed": 0, "failed": 0, "skipped": 0}

        results = {"processed": 0, "failed": 0, "skipped": 0}

        for i, file_path in enumerate(image_files):
            try:
                # 构造输出路径
                relative_path = os.path.relpath(file_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)

                # 更改文件扩展名
                base_name = os.path.splitext(output_path)[0]
                extension = options.output_format.value.lower()
                if extension == 'jpeg':
                    extension = 'jpg'
                output_path = f"{base_name}.{extension}"

                # 创建输出目录
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # 转换图片
                if self.processor.convert_format(file_path, output_path, options):
                    results["processed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                results["failed"] += 1

            # 更新进度
            if progress_callback:
                progress_callback(i + 1, total_files)

        return results


# 便利函数
def get_image_thumbnail(file_path: str, size: Tuple[int, int] = (80, 80)) -> Optional[Any]:
    """获取图片缩略图的便利函数"""
    processor = ImageProcessor()
    return processor.create_thumbnail(file_path, size)


def convert_image_format(file_path: str, output_path: str,
                        output_format: str = "JPEG", quality: int = 85) -> bool:
    """转换图片格式的便利函数"""
    processor = ImageProcessor()
    options = ConversionOptions(
        output_format=ImageFormat(output_format.upper()),
        quality=quality
    )
    return processor.convert_format(file_path, output_path, options)


def is_image_file(file_path: str) -> bool:
    """检查是否为图片文件的便利函数"""
    processor = ImageProcessor()
    return processor.is_valid_image(file_path)


# 导出
__all__ = [
    'ImageFormat', 'ImageSize', 'ImageInfo', 'ConversionOptions',
    'ImageProcessor', 'ImageBatchProcessor',
    'get_image_thumbnail', 'convert_image_format', 'is_image_file'
]