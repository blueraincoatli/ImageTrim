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
from ui.theme import Theme


class ImageLoader(QThread):
    """异步图片加载线程"""
    image_loaded = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        # 定义艺术相关标签
        self.tags = ["art", "design", "illustration", "graphic"]
        # 生成多个随机URL以提高成功率
        self.urls = self._generate_random_urls()
        self.current_url_index = 0

    def _generate_random_urls(self):
        """生成随机艺术图片URL"""
        urls = []

        # Unsplash URLs (主要选择)
        for i in range(2):
            selected_tags = random.sample(self.tags, random.randint(1, 2))
            tag_string = selected_tags[0]  # 使用单个标签更稳定
            url = f"https://source.unsplash.com/featured/1920x1080/?{tag_string}"
            urls.append(url)
            print(f"生成的Unsplash URL {i+1}: {url}")

        # 备选的无版权图片源
        backup_urls = [
            "https://picsum.photos/1920/1080?random=1",
            "https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?w=1920&h=1080&fit=crop"
        ]
        urls.extend(backup_urls)
        print(f"添加备选图片源: {len(backup_urls)} 个")

        return urls

    def run(self):
        """在后台线程加载图片"""
        print("开始加载网络图片...")
        try:
            # 尝试所有URL直到成功
            for i, url in enumerate(self.urls):
                try:
                    print(f"正在尝试加载 URL {i+1}: {url}")
                    req = urllib.request.Request(
                        url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req, timeout=15) as response:
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
                        return
                    else:
                        print("图片转换失败，pixmap为空")
                except Exception as e:
                    print(f"URL {url} 加载失败: {e}")
                    continue

            # 所有网络图片都加载失败，发送空pixmap触发本地兜底
            print("所有网络图片加载失败，使用本地兜底图片")
            self.image_loaded.emit(QPixmap())

        except Exception as e:
            print(f"图片加载异常: {e}")
            self.image_loaded.emit(QPixmap())


class WelcomeScreen(QWidget):
    """
    欢迎屏幕 - 在右侧工作区显示撑满的图片
    优先网络高清图片，失败时回退到本地图片
    """

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
        self.image_label.setText("正在加载高清艺术图片...")
        layout.addWidget(self.image_label)

    def load_image(self):
        """异步加载图片"""
        self.image_loader = ImageLoader()
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.start()

    def on_image_loaded(self, pixmap):
        """图片加载完成回调"""
        if not pixmap.isNull():
            # 加载网络图片成功
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            # 网络图片加载失败，使用本地兜底图片
            self.load_local_image()

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
                    # 缩放以撑满区域
                    scaled_pixmap = pixmap.scaled(
                        self.size(),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
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
            # 重新缩放当前图片以适应新尺寸
            current_pixmap = self.image_label.pixmap()
            scaled_pixmap = current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        elif hasattr(self, 'image_label') and self.image_label.text() and "正在加载" in self.image_label.text():
            # 重新尝试加载图片（如果正在加载状态）
            self.load_image()