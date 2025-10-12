#!/usr/bin/env python3
"""
欢迎屏幕组件 - 右侧工作区纯图片显示
"""

import urllib.request
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from pathlib import Path
from app.ui.theme import Theme


class ImageLoader(QThread):
    """异步图片加载线程"""
    image_loaded = pyqtSignal(QPixmap)
    loading_completed = pyqtSignal()  # 新增：加载完成信号

    def __init__(self):
        super().__init__()
        # 使用稳定的图片源，移除不稳定的Unsplash API
        self.urls = self._generate_reliable_urls()
        self.current_url_index = 0

    def _generate_reliable_urls(self):
        """生成可靠的高清图片URL"""
        urls = []

        # 使用Picsum作为主要图片源，稳定性高，速度快
        # 添加不同种子的图片URL以获得多样化图片
        seeds = ["nature", "architecture", "technology", "abstract", "landscape", "minimal", "gradient"]
        selected_seed = random.choice(seeds)

        # 主图片源
        primary_urls = [
            f"https://picsum.photos/seed/{selected_seed}/1920/1080.jpg",
            f"https://picsum.photos/1920/1080?random={random.randint(1, 1000)}"
        ]
        urls.extend(primary_urls)
        print(f"生成主要图片源: {len(primary_urls)} 个")

        # 备用图片源（更高质量）
        backup_urls = [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1920&h=1080&fit=crop"
        ]
        urls.extend(backup_urls)
        print(f"添加备用图片源: {len(backup_urls)} 个")

        return urls

    def run(self):
        """在后台线程加载图片"""
        print("开始加载网络图片...")
        try:
            # 尝试所有URL直到成功，使用较短的超时时间
            for i, url in enumerate(self.urls):
                try:
                    print(f"正在尝试加载 URL {i+1}: {url}")
                    req = urllib.request.Request(
                        url,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    # 缩短超时时间到8秒，提高启动速度
                    with urllib.request.urlopen(req, timeout=8) as response:
                        image_data = response.read()
                        print(f"成功下载图片数据，大小: {len(image_data)} 字节")

                    # 转换为QPixmap
                    qimage = QImage()
                    qimage.loadFromData(image_data)
                    pixmap = QPixmap.fromImage(qimage)

                    if not pixmap.isNull():
                        print(f"成功转换图片，尺寸: {pixmap.width()}x{pixmap.height()}")
                        # 发送成功信号
                        self.image_loaded.emit(pixmap)
                        self.loading_completed.emit()  # 发送加载完成信号
                        return
                    else:
                        print("图片转换失败，pixmap为空")
                except Exception as e:
                    print(f"URL {url} 加载失败: {e}")
                    continue

            # 所有网络图片都加载失败，发送空pixmap触发本地兜底
            print("所有网络图片加载失败，使用本地兜底图片")
            self.image_loaded.emit(QPixmap())
            self.loading_completed.emit()  # 即使失败也发送完成信号

        except Exception as e:
            print(f"图片加载异常: {e}")
            self.image_loaded.emit(QPixmap())
            self.loading_completed.emit()  # 即使异常也发送完成信号


class WelcomeScreen(QWidget):
    """
    欢迎屏幕 - 在右侧工作区显示撑满的图片
    优先网络高清图片，失败时回退到本地图片
    """
    # 新增：图片加载完成信号，用于通知主窗口
    image_loading_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_loader = None
        self.init_ui()
        self.load_image()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建图片显示标签 - 撑满整个区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.BG_DARK};
                margin: 0;
                padding: 0;
            }}
        """)
        self.image_label.setText("正在加载高清背景图片...")
        layout.addWidget(self.image_label)

    def load_image(self):
        """异步加载图片"""
        self.image_loader = ImageLoader()
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.loading_completed.connect(self.on_loading_completed)
        self.image_loader.start()

    def on_image_loaded(self, pixmap):
        """图片加载完成回调"""
        if not pixmap.isNull():
            # 加载网络图片成功 - 保持宽高比并裁剪
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            # 网络图片加载失败，使用本地兜底图片
            self.load_local_image()

    def on_loading_completed(self):
        """图片加载完成（无论成功或失败）"""
        print("图片加载流程完成，通知主窗口可以显示")
        # 发送信号通知主窗口图片加载完成
        self.image_loading_completed.emit()

    def load_local_image(self):
        """加载本地兜底图片"""
        # 尝试多种本地图片路径
        image_paths = [
            Path(__file__).parent.parent / "resources" / "images" / "placeholder.png",
            Path(__file__).parent.parent / "resources" / "icons" / "imagetrim.ico"
        ]

        for path in image_paths:
            if path.exists():
                try:
                    pixmap = QPixmap(str(path))
                    # 缩放以撑满区域 - 保持宽高比并裁剪
                    scaled_pixmap = pixmap.scaled(
                        self.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    return
                except Exception as e:
                    print(f"加载本地图片失败 {path}: {e}")

        # 所有图片都加载失败，显示提示
        self.image_label.setText("🖼️\n\n无法加载图片\n请稍后重试")
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.BG_DARK};
                color: {Theme.TEXT_DISABLED};
                font-size: 48px;
            }}
        """)

    def resizeEvent(self, event):
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)

        if hasattr(self, 'image_label') and self.image_label.pixmap() and not self.image_label.pixmap().isNull():
            # 重新缩放当前图片以适应新尺寸 - 保持宽高比并裁剪
            current_pixmap = self.image_label.pixmap()
            scaled_pixmap = current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        elif hasattr(self, 'image_label') and self.image_label.text() and "正在加载" in self.image_label.text():
            # 重新尝试加载图片（如果正在加载状态）
            self.load_image()