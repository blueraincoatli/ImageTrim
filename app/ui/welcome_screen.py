#!/usr/bin/env python3
"""
欢迎屏幕组件 - 右侧工作区纯图片显示
"""

import random
import time
import urllib.request
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.theme import Theme


# 全局变量用于存储预加载的图片和加载状态
preloaded_pixmap = None
preloaded_image_loading_completed = False
early_image_loader = None


class GlobalImageLoader:
    """全局图片加载控制器"""
    
    _instance = None
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._lock = None
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.preloaded_pixmap = None
            self.loading_completed = False
            self.image_loader = None
    
    def start_early_download(self):
        """启动早期图片下载"""
        if self.image_loader is None or not self.image_loader.isRunning():
            self.image_loader = ImageLoader()
            # Connect to store the result in global variables
            self.image_loader.image_loaded.connect(self._on_image_loaded)
            self.image_loader.loading_completed.connect(self._on_loading_completed)
            self.image_loader.start()
    
    def _on_image_loaded(self, pixmap: QPixmap):
        """图片加载完成回调"""
        global preloaded_pixmap
        self.preloaded_pixmap = pixmap
        preloaded_pixmap = pixmap  # Update global variable too
    
    def _on_loading_completed(self):
        """加载完成回调"""
        global preloaded_image_loading_completed
        self.loading_completed = True
        preloaded_image_loading_completed = True
    
    def get_preloaded_image(self):
        """获取预加载的图片"""
        return self.preloaded_pixmap if self.preloaded_pixmap else None
    
    def is_loading_completed(self):
        """检查是否加载完成"""
        return self.loading_completed


class ImageLoader(QThread):
    """异步图片加载线程"""

    image_loaded = pyqtSignal(QPixmap)
    loading_completed = pyqtSignal()

    def __init__(self, timeout_seconds: float = 3, max_attempt_duration: float = 5, max_urls: int = 2):
        super().__init__()
        self.timeout_seconds = timeout_seconds
        self.max_attempt_duration = max_attempt_duration
        self.max_urls = max_urls
        self.urls = self._generate_reliable_urls()

    def _generate_reliable_urls(self) -> list[str]:
        """生成可靠的高清图片URL"""
        seeds = ["nature", "architecture", "technology", "abstract", "landscape", "minimal", "gradient"]
        selected_seed = random.choice(seeds)

        primary_urls = [
            f"https://picsum.photos/seed/{selected_seed}/1920/1080.jpg",
            f"https://picsum.photos/1920/1080?random={random.randint(1, 1000)}",
        ]

        backup_urls = [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1920&h=1080&fit=crop",
        ]

        return primary_urls + backup_urls

    def run(self) -> None:
        """在后台线程加载图片"""
        print("开始加载网络图片...")
        start_time = time.monotonic()

        try:
            for index, url in enumerate(self.urls[: self.max_urls], start=1):
                if time.monotonic() - start_time >= self.max_attempt_duration:
                    print("超过图片下载的时间预算，停止请求")
                    break

                try:
                    print(f"正在尝试加载第 {index} 个图片源: {url}")
                    request = urllib.request.Request(
                        url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        },
                    )
                    with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                        image_data = response.read()
                        print(f"成功下载图片数据，大小 {len(image_data)} 字节")

                    image = QImage()
                    if not image.loadFromData(image_data):
                        print("图片数据解析失败")
                        continue

                    pixmap = QPixmap.fromImage(image)
                    if pixmap.isNull():
                        print("图片转换失败，pixmap 为空")
                        continue

                    print(f"成功转换图片，尺寸 {pixmap.width()}x{pixmap.height()}")
                    
                    # 保存到全局变量供后续使用
                    global preloaded_pixmap
                    preloaded_pixmap = pixmap
                    
                    self.image_loaded.emit(pixmap)
                    self.loading_completed.emit()
                    return
                except Exception as exc:
                    print(f"URL {url} 加载失败: {exc}")

            print("所有网络图片加载失败，使用本地兜底图片")
            self.image_loaded.emit(QPixmap())
            self.loading_completed.emit()
        except Exception as exc:
            print(f"图片加载异常: {exc}")
            self.image_loaded.emit(QPixmap())
            self.loading_completed.emit()


class WelcomeScreen(QWidget):
    """
    欢迎屏幕 - 在右侧工作区显示撑满的图片
    优先网络高清图片，失败时回退到本地图像
    """

    image_loading_completed = pyqtSignal()

    def __init__(self, parent=None, preloaded_pixmap_arg=None):
        super().__init__(parent)
        self.image_loader: ImageLoader | None = None
        self.original_pixmap: QPixmap | None = None
        self.base_label_style = f"""
            QLabel {{
                background-color: {Theme.BG_DARK};
                margin: 0;
                padding: 0;
            }}
        """
        self.init_ui()
        
        # Check if a preloaded pixmap is available through the global loader
        from .welcome_screen import GlobalImageLoader
        global_loader = GlobalImageLoader()
        
        # Check if a preloaded pixmap is available either as parameter or globally
        if preloaded_pixmap_arg is not None and not preloaded_pixmap_arg.isNull():
            print("欢迎屏幕: 使用传入的预加载图片")
            self.on_image_loaded(preloaded_pixmap_arg)
            self.on_loading_completed()
        elif global_loader.is_loading_completed() and global_loader.get_preloaded_image() is not None:
            print("欢迎屏幕: 使用全局预加载的图片")
            self.on_image_loaded(global_loader.get_preloaded_image())
            self.on_loading_completed()
        else:
            # If early download is still in progress, wait for it; otherwise start new download
            if global_loader.image_loader and global_loader.image_loader.isRunning():
                print("欢迎屏幕: 早期下载仍在进行，等待结果...")
                global_loader.image_loader.image_loaded.connect(self.on_image_loaded)
                global_loader.image_loader.loading_completed.connect(self.on_loading_completed)
            else:
                print("欢迎屏幕: 开始新的图片下载")
                self.load_image()

    def init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(self.base_label_style)
        self.image_label.setText("正在加载高清背景图片...")
        layout.addWidget(self.image_label)

    def load_image(self) -> None:
        """异步加载图片"""
        placeholder_loaded = self.load_local_image(show_failure_message=False)
        if not placeholder_loaded:
            self.image_label.setText("正在加载高清背景图片...")

        self.image_loader = ImageLoader()
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.loading_completed.connect(self.on_loading_completed)
        self.image_loader.start()

    def on_image_loaded(self, pixmap: QPixmap) -> None:
        """图片加载完成回调"""
        if pixmap.isNull():
            self.load_local_image()
            return

        self._apply_pixmap(pixmap)

    def on_loading_completed(self) -> None:
        """图片加载完成（无论成功或失败）"""
        print("图片加载流程完成，通知主窗口可以显示")
        self.image_loading_completed.emit()

    def load_local_image(self, show_failure_message: bool = True) -> bool:
        """加载本地兜底图片"""
        from app.utils.resource_path import get_resource_path

        # 尝试加载的资源文件列表
        resource_paths = [
            "images/placeholder.jpg",
            "icons/imagetrim.ico",
        ]

        for relative_path in resource_paths:
            path_str = get_resource_path(relative_path)
            if not path_str:
                continue

            path = Path(path_str)
            if not path.exists():
                continue

            try:
                pixmap = QPixmap(str(path))
            except Exception as exc:
                print(f"加载本地图片失败 {path}: {exc}")
                continue

            if pixmap.isNull():
                continue

            self._apply_pixmap(pixmap)
            return True

        if show_failure_message:
            self.original_pixmap = None
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("🖼️\n\n无法加载图片\n请稍后重试")
            self.image_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Theme.BG_DARK};
                    color: {Theme.TEXT_DISABLED};
                    font-size: 48px;
                }}
                """
            )

        return False

    def _apply_pixmap(self, pixmap: QPixmap) -> None:
        """根据窗口尺寸应用图片"""
        if pixmap.isNull():
            return

        self.original_pixmap = pixmap
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")
        self.image_label.setStyleSheet(self.base_label_style)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)

        if self.original_pixmap and not self.original_pixmap.isNull():
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
