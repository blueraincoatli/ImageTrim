#!/usr/bin/env python3
"""高级内存缩略图缓存管理器"""

from __future__ import annotations

import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional

from PIL import Image, ImageFile
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPainter, QPixmap


ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass(frozen=True)
class _CacheKey:
    """缓存关键字"""

    path: str
    width: int
    height: int


class _ThumbnailTaskSignals(QObject):
    """缩略图生成任务信号"""

    finished = pyqtSignal(str, int, int, object, str)


class _ThumbnailTask(QRunnable):
    """后台生成缩略图任务"""

    def __init__(self, file_path: str, width: int, height: int):
        super().__init__()
        self.file_path = file_path
        self.width = width
        self.height = height
        self.signals = _ThumbnailTaskSignals()

    def run(self):
        """执行生成逻辑"""
        try:
            qimage = self._load_qimage(self.file_path, self.width, self.height)
            self.signals.finished.emit(self.file_path, self.width, self.height, qimage, "")
        except Exception as exc:  # pylint: disable=broad-except
            self.signals.finished.emit(self.file_path, self.width, self.height, None, str(exc))

    @staticmethod
    def _load_qimage(file_path: str, target_width: int, target_height: int) -> QImage:
        """读取文件并转换为QImage"""
        with Image.open(file_path) as img:
            if img.width <= 0 or img.height <= 0:
                raise ValueError("无效的图像尺寸")

            # 限制极端大图到合理范围
            max_side = max(target_width * 4, target_height * 4, 4096)
            if img.width > max_side or img.height > max_side:
                img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

            # 统一转换到支持的模式
            if img.mode in ("RGBA", "LA"):
                converted = img.convert("RGBA")
                fmt = QImage.Format.Format_RGBA8888
                bytes_per_line = converted.width * 4
                buffer_mode = "RGBA"
            else:
                converted = img.convert("RGB")
                fmt = QImage.Format.Format_RGB888
                bytes_per_line = converted.width * 3
                buffer_mode = "RGB"

            # 根据目标尺寸等比缩放
            converted.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            width, height = converted.size
            if converted.mode == "RGBA":
                fmt = QImage.Format.Format_RGBA8888
                bytes_per_line = width * 4
                buffer_mode = "RGBA"
            else:
                fmt = QImage.Format.Format_RGB888
                bytes_per_line = width * 3
                buffer_mode = "RGB"

            buffer = converted.tobytes("raw", buffer_mode)

        qimage = QImage(buffer, width, height, bytes_per_line, fmt)
        return qimage.copy()


class ImageCacheManager(QObject):
    """内存缩略图缓存管理"""

    thumbnail_ready = pyqtSignal(str, int, int, QPixmap)

    def __init__(self, max_entries: int = 256):
        super().__init__()
        self._max_entries = max_entries
        self._cache: "OrderedDict[_CacheKey, QPixmap]" = OrderedDict()
        self._loading: Dict[_CacheKey, int] = {}
        self._lock = threading.Lock()
        self._thread_pool = QThreadPool.globalInstance()

    def get_thumbnail_pixmap(self, file_path: str, width: int, height: int) -> Optional[QPixmap]:
        """获取或异步生成缩略图"""
        key = _CacheKey(file_path, width, height)

        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]

            if key in self._loading:
                return None

            self._loading[key] = 1

        task = _ThumbnailTask(file_path, width, height)
        task.signals.finished.connect(self._on_task_finished)
        self._thread_pool.start(task)
        return None

    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def _on_task_finished(self, file_path: str, width: int, height: int, qimage: Optional[QImage], error: str):
        key = _CacheKey(file_path, width, height)

        with self._lock:
            self._loading.pop(key, None)

        if qimage is None or qimage.isNull():
            pixmap = self._create_placeholder(width, height, error)
        else:
            pixmap = QPixmap.fromImage(qimage)

        with self._lock:
            self._cache[key] = pixmap
            if len(self._cache) > self._max_entries:
                self._cache.popitem(last=False)

        self.thumbnail_ready.emit(file_path, width, height, pixmap)

    @staticmethod
    def _create_placeholder(width: int, height: int, error: str) -> QPixmap:
        """生成占位图"""
        image = QImage(max(width, 1), max(height, 1), QImage.Format.Format_RGB32)
        image.fill(0xFF2D2D2D)

        if error:
            painter = QPainter(image)
            painter.setPen(QColor('#FF6B6B'))
            painter.drawText(image.rect(), Qt.AlignmentFlag.AlignCenter, "🚫")
            painter.end()

        return QPixmap.fromImage(image)


_singleton_cache: Optional[ImageCacheManager] = None


def get_image_cache() -> ImageCacheManager:
    """获取单例缓存管理器"""
    global _singleton_cache
    if _singleton_cache is None:
        _singleton_cache = ImageCacheManager()
    return _singleton_cache
