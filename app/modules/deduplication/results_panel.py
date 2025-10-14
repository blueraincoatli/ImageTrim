#!/usr/bin/env python3
"""
图片去重结果面板
"""

import os
import shutil
from typing import Dict, List, Optional, Set, Tuple
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QScrollArea, QGridLayout, QProgressBar,
                             QFrame, QCheckBox, QSplitter, QFileDialog, QMessageBox,
                             QApplication, QDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QSlider, QRubberBand, QGraphicsDropShadowEffect)
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QCoreApplication, QEvent, QPoint, QRect
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QPainter, QColor, QPen, QScreen, QCursor
from app.utils.image_utils import ImageUtils
from app.utils.ui_helpers import UIHelpers
from app.ui.theme import Spacing


class ClickablePathLabel(QLabel):
    """可点击的路径标签"""
    
    def __init__(self, path: str, parent=None):
        super().__init__(path, parent)
        self.path = path
        self.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 12px;
                background-color: rgba(60, 60, 60, 200);
                padding: 2px;
                border-radius: 3px;
                border: none;
                margin: 0px;
            }
        """)
        self.setWordWrap(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tooltip_parent = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
    def set_tooltip_parent(self, tooltip_parent):
        """设置悬浮框父级，用于保持显示"""
        self._tooltip_parent = tooltip_parent
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file_location()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """鼠标进入事件 - 保持悬浮框显示"""
        # 防止悬浮框在鼠标移动到链接上时消失
        if self._tooltip_parent:
            # 重置悬浮框的隐藏定时器
            pass
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件 - 保持悬浮框显示"""
        # 鼠标离开链接时不需要特殊处理
        super().leaveEvent(event)
        
    def open_file_location(self):
        """在文件管理器中打开文件所在文件夹并选中文件"""
        try:
            import subprocess
            import platform
            import os
            from PyQt6.QtWidgets import QMessageBox
            
            # 规范化路径格式，确保在所有系统上都能正确处理
            normalized_path = os.path.normpath(self.path)
            print(f"原始路径: {self.path}")
            print(f"规范化路径: {normalized_path}")
            
            if not os.path.exists(normalized_path):
                print(f"文件不存在: {normalized_path}")
                QMessageBox.warning(None, "文件不存在", f"指定的文件不存在:\n{normalized_path}")
                return
                
            system = platform.system()
            print(f"系统类型: {system}, 文件路径: {normalized_path}")
            
            success = False
            if system == "Windows":
                # Windows: 使用explorer /select命令选中文件
                print(f"执行命令: explorer /select, {normalized_path}")
                # Windows explorer命令的行为比较特殊，总是会打开文件夹窗口
                # 我们直接执行命令，不检查返回值
                try:
                    subprocess.Popen(['explorer', '/select,', normalized_path])
                    success = True
                except Exception as e:
                    print(f"Windows命令执行异常: {e}")
                    # 备用方案：直接打开文件夹
                    folder = os.path.dirname(normalized_path)
                    print(f"备用方案 - 打开文件夹: {folder}")
                    subprocess.Popen(['explorer', folder])
                    success = True  # 备用方案也算成功
            elif system == "Darwin":  # macOS
                # macOS: 使用open -R命令
                print(f"执行命令: open -R {normalized_path}")
                result = subprocess.run(['open', '-R', normalized_path], capture_output=True, text=True)
                success = result.returncode == 0
                if not success:
                    print(f"macOS命令执行失败: {result.stderr}")
                    QMessageBox.warning(None, "打开失败", f"无法在Finder中打开文件位置:\n{normalized_path}\n错误: {result.stderr}")
            else:  # Linux和其他Unix-like系统
                # Linux: 打开文件所在文件夹（大多数文件管理器不支持直接选中文件）
                folder = os.path.dirname(normalized_path)
                print(f"执行命令: xdg-open {folder}")
                result = subprocess.run(['xdg-open', folder], capture_output=True, text=True)
                success = result.returncode == 0
                if not success:
                    print(f"Linux命令执行失败: {result.stderr}")
                    QMessageBox.warning(None, "打开失败", f"无法在文件管理器中打开文件夹:\n{folder}\n错误: {result.stderr}")
                
        except Exception as e:
            print(f"打开文件位置失败: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "错误", f"打开文件位置时发生错误:\n{str(e)}")


class ImagePathTooltip(QFrame):
    """图片路径提示工具窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 255);
                border: 1px solid #888888;
                border-radius: 6px;
                padding: 8px;
                min-width: 200px;
                min-height: 30px;
            }
        """)
        self.setMouseTracking(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(Spacing.XS)
        
        self.path_labels = []
        
    def show_paths(self, paths: List[str]):
        """显示路径列表"""
        # 清除现有标签
        for label in self.path_labels:
            label.setParent(None)
            label.deleteLater()
        self.path_labels.clear()
        
        # 为每个路径创建可点击的标签
        for path in paths:
            label = ClickablePathLabel(path)
            label.set_tooltip_parent(self)  # 设置父级引用，用于保持显示
            # 确保标签没有额外的布局边距
            label.setContentsMargins(0, 0, 0, 0)
            self.layout().addWidget(label)
            self.path_labels.append(label)
            
        # 调整窗口大小
        self.adjustSize()
        
        # 确保窗口尺寸在合理范围内
        min_width = 200
        min_height = 30
        max_width = 800
        max_height = 600
        
        current_width = self.width()
        current_height = self.height()
        
        # 限制尺寸在合理范围内
        new_width = max(min_width, min(current_width, max_width))
        new_height = max(min_height, min(current_height, max_height))
        
        if new_width != current_width or new_height != current_height:
            self.setFixedSize(new_width, new_height)

    def _close_and_notify(self):
        parent = self.parent()
        if parent and hasattr(parent, "tooltip_closed"):
            parent.tooltip_closed()
        if self.isVisible():
            self.hide()
        self.deleteLater()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._close_and_notify()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._close_and_notify()





class DuplicateImageWidget(QFrame):
    """重复图片控件 - 支持双击预览"""

    image_double_clicked = pyqtSignal(str)

    def __init__(self, file_path: str, width: int = 180, height: int = 120, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.width = width
        self.height = height
        self.thumbnail_width = width
        self.thumbnail_height = height
        self.is_selected = False
        self.group_widget: Optional["DuplicateGroupWidget"] = None
        self._image_cache = None
        self._thumbnail_signal_connected = False
        self._tooltip = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                qproperty-alignment: AlignCenter;
            }
        """)

        self._shadow_effect = QGraphicsDropShadowEffect(self.image_label)
        self._shadow_effect.setBlurRadius(18)
        self._shadow_effect.setOffset(0, 4)
        self._shadow_effect.setColor(QColor(0, 0, 0, 140))
        self.image_label.setGraphicsEffect(self._shadow_effect)
        layout.addWidget(self.image_label)

        try:
            from utils.image_cache_enhanced import get_image_cache
            self._image_cache = get_image_cache()
            if not self._thumbnail_signal_connected:
                self._image_cache.thumbnail_ready.connect(self._on_thumbnail_ready)
                self._thumbnail_signal_connected = True
            self._apply_placeholder(self.image_label)
            self._request_thumbnail()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"图片缓存加载失败: {exc}")
            self._create_image_label_fallback(self.image_label)

    def _apply_placeholder(self, label: QLabel):
        label.clear()
        label.setText("⌛")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 20px;
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

    def _apply_pixmap(self, pixmap: QPixmap):
        if not pixmap or pixmap.isNull():
            self._apply_placeholder(self.image_label)
            return

        # 确保image_label的尺寸正确设置
        self.image_label.setFixedSize(self.thumbnail_width, self.thumbnail_height)
        
        # 使用KeepAspectRatioByExpanding确保图片填满整个区域
        scaled = pixmap.scaled(
            self.thumbnail_width,
            self.thumbnail_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        
        # 计算居中显示的矩形区域
        pixmap_rect = scaled.rect()
        label_rect = QRect(0, 0, self.thumbnail_width, self.thumbnail_height)
        
        # 如果图片比例与标签比例不匹配，居中裁剪
        if pixmap_rect.width() > label_rect.width() or pixmap_rect.height() > label_rect.height():
            x = max(0, (pixmap_rect.width() - label_rect.width()) // 2)
            y = max(0, (pixmap_rect.height() - label_rect.height()) // 2)
            crop_rect = QRect(x, y, label_rect.width(), label_rect.height())
            scaled = scaled.copy(crop_rect)
        
        self.image_label.setPixmap(scaled)
        self.image_label.setText("")
        self.image_label.update()
        self.image_label.updateGeometry()

    def _request_thumbnail(self):
        if not self._image_cache:
            return

        pixmap = self._image_cache.get_thumbnail_pixmap(
            self.file_path,
            self.thumbnail_width,
            self.thumbnail_height,
        )
        if pixmap:
            self._apply_pixmap(pixmap)

    def _create_image_label_fallback(self, label: QLabel):
        try:
            from PIL import Image
            with Image.open(self.file_path) as img:
                original_width, original_height = img.size

            # 确保标签尺寸正确设置
            label.setFixedSize(self.thumbnail_width, self.thumbnail_height)

            # 使用居中裁剪的方式确保图片填满指定区域
            container_aspect_ratio = self.thumbnail_width / self.thumbnail_height
            image_aspect_ratio = original_width / original_height if original_height else 1

            if image_aspect_ratio > container_aspect_ratio:
                # 图片更宽，裁剪宽度
                new_height = self.thumbnail_height
                new_width = int(new_height * image_aspect_ratio)
                # 居中裁剪
                left = (new_width - self.thumbnail_width) // 2
                top = 0
                right = left + self.thumbnail_width
                bottom = new_height
            else:
                # 图片更高，裁剪高度
                new_width = self.thumbnail_width
                new_height = int(new_width / image_aspect_ratio)
                # 居中裁剪
                left = 0
                top = (new_height - self.thumbnail_height) // 2
                right = new_width
                bottom = top + self.thumbnail_height

            # 获取缩略图并进行裁剪
            thumbnail = ImageUtils.get_thumbnail(self.file_path, (new_width, new_height))
            if new_width != self.thumbnail_width or new_height != self.thumbnail_height:
                # 进行居中裁剪
                thumbnail = thumbnail.crop((left, top, right, bottom))
            
            thumbnail = thumbnail.convert("RGBA")
            data = thumbnail.tobytes("raw", "RGBA")
            qimage = QImage(data, thumbnail.width, thumbnail.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            label.setPixmap(pixmap)
        except Exception as exc:  # pylint: disable=broad-except
            label.setText("🚫")
            label.setStyleSheet("color: #dc3545; font-size: 24px; background-color: transparent; border: none;")
            print(f"直接加载缩略图失败: {exc}")

    def _on_thumbnail_ready(self, file_path: str, width: int, height: int, pixmap: QPixmap):
        if file_path != self.file_path:
            return
        if width != self.thumbnail_width or height != self.thumbnail_height:
            return
        self._apply_pixmap(pixmap)

    def update_thumbnail_size(self, width: int, height: int):
        self.thumbnail_width = max(1, width)
        self.thumbnail_height = max(1, height)
        self.width = self.thumbnail_width
        self.height = self.thumbnail_height
        # 确保控件本身也设置正确的尺寸
        self.setFixedSize(self.thumbnail_width, self.thumbnail_height)
        self.image_label.setFixedSize(self.thumbnail_width, self.thumbnail_height)
        self._apply_placeholder(self.image_label)
        self._request_thumbnail()

    def refresh_thumbnail(self):
        self._request_thumbnail()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.group_widget:
            self.group_widget.handle_selection_trigger(event.modifiers())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.image_double_clicked.emit(self.file_path)
        event.accept()
        
    def enterEvent(self, event):
        """鼠标进入事件 - 显示路径提示"""
        # 先调用父类方法确保正常处理
        super().enterEvent(event)
        
        if self.file_path:
            try:
                # 创建工具提示窗口
                if not self._tooltip:
                    self._tooltip = ImagePathTooltip(self)
                
                # 显示路径
                self._tooltip.show_paths([self.file_path])
                
                # 获取全局位置（更靠近鼠标位置）
                mouse_pos = QCursor.pos()
                tooltip_width = self._tooltip.width() if self._tooltip.width() > 0 else 300
                tooltip_height = self._tooltip.height() if self._tooltip.height() > 0 else 100
                
                # 将提示窗口定位在鼠标右上方附近，避免被鼠标遮挡
                screen = QCoreApplication.instance().primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    # 计算最佳位置，避免超出屏幕边界
                    x = min(mouse_pos.x() + 15, screen_geometry.right() - tooltip_width - 10)
                    y = min(mouse_pos.y() + 15, screen_geometry.bottom() - tooltip_height - 10)
                    self._tooltip.move(x, y)
                else:
                    # 如果无法获取屏幕信息，使用简单定位
                    self._tooltip.move(mouse_pos.x() + 15, mouse_pos.y() + 15)
                self._tooltip.show()
            except Exception as e:
                # 如果显示提示出错，不显示提示但不中断程序
                print(f"显示悬浮提示时出错: {e}")
                if self._tooltip:
                    try:
                        self._tooltip.hide()
                    except:
                        pass
                    self._tooltip = None
        
    def leaveEvent(self, event):
        """鼠标离开事件 - 隐藏路径提示"""
        # 先调用父类方法确保正常处理
        super().leaveEvent(event)
        
        if self._tooltip:
            try:
                # 延迟隐藏，让用户有时间点击路径
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(300, self._hide_tooltip)  # 缩短延迟时间
            except Exception as e:
                # 如果设置定时器出错，立即隐藏
                print(f"设置悬浮提示隐藏定时器时出错: {e}")
                try:
                    if self._tooltip.isVisible():
                        self._tooltip.hide()
                    self._tooltip.deleteLater()
                except Exception as inner_exc:  # pylint: disable=broad-except
                    print(f"立即隐藏悬浮提示时出错: {inner_exc}")
                self._tooltip = None
        
    def _hide_tooltip(self):
        """延迟隐藏提示框"""
        if self._tooltip:
            try:
                # 检查鼠标是否在提示框或其子元素上
                if self._tooltip.underMouse():
                    # 如果鼠标在提示框上，延迟再次检查
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(200, self._hide_tooltip)
                    return
                if self._tooltip.isVisible():
                    self._tooltip.hide()
                self._tooltip.deleteLater()
            except Exception as e:
                print(f"隐藏悬浮提示时出错: {e}")
            finally:
                self._tooltip = None

    def tooltip_closed(self):
        self._tooltip = None


class DuplicateGroupWidget(QFrame):
    """重复图片组控件"""

    selection_changed = pyqtSignal(list, bool)
    image_double_clicked = pyqtSignal(str)

    _STACK_ASPECT_RATIO = 4 / 3

    _BASE_STYLE = """
        QFrame {
            background-color: #1B1B1B;
            border: 1px solid #353535;
            border-radius: 8px;
        }
        QFrame:hover {
            background-color: #252525;
        }
    """

    _SELECTED_STYLE = """
        QFrame {
            background-color: #252525;
            border: 1px solid #FF8C00;
            border-radius: 8px;
        }
        QFrame:hover {
            background-color: #252525;
        }
    """

    def __init__(self, group_id: int, files: List[str], confidence: float, parent=None):
        super().__init__(parent)
        self.group_id = group_id
        self.files = files
        self.confidence = confidence
        self.is_selected = False
        self.image_widgets: List[DuplicateImageWidget] = []
        self.images_layout: Optional[QHBoxLayout] = None
        self.stack_widget: Optional[QFrame] = None
        self.badge_label: Optional[QLabel] = None
        self.card_height = 0
        self._tooltip = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(self._BASE_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        images_container = QFrame()
        images_container.setStyleSheet("background-color: transparent; border: none;")
        self.images_layout = QHBoxLayout(images_container)
        self.images_layout.setContentsMargins(0, 0, 0, 0)
        self.images_layout.setSpacing(0)

        self.stack_widget = QFrame(images_container)
        self.stack_widget.setStyleSheet("background-color: transparent; border: none;")
        self.stack_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.images_layout.addWidget(self.stack_widget)

        self.badge_label = QLabel(self)
        self.badge_label.setVisible(False)
        self.badge_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 160);
                color: white;
                font-size: 12px;
                padding: 2px 6px;
                border-radius: 10px;
            }
        """)

        main_layout.addWidget(images_container)

    def update_thumbnails(self, card_width: int):
        if self.images_layout is None or self.stack_widget is None:
            return

        # 使用更合理的卡片高度比例，保持2:1比例
        self.card_height = max(80, int(card_width / 2))  # 2:1比例，最小高度80px
        self.setFixedHeight(self.card_height)

        # 设置合理的内边距和间距，与卡片高度成比例
        padding = max(8, int(self.card_height / 10))
        spacing = max(4, int(self.card_height / 20))
        self.images_layout.setContentsMargins(padding, padding, padding, padding)
        self.images_layout.setSpacing(spacing)

        # 计算可用空间
        stack_width = max(60, card_width - 2 * padding)
        stack_height = max(60, self.card_height - 2 * padding)
        self.stack_widget.setFixedSize(stack_width, stack_height)

        # 确保图片控件数量正确
        current_count = len(self.image_widgets)
        target_count = len(self.files)

        if current_count > target_count:
            for widget in self.image_widgets[target_count:]:
                widget.setParent(None)
            self.image_widgets = self.image_widgets[:target_count]

        while len(self.image_widgets) < target_count:
            widget = DuplicateImageWidget(self.files[len(self.image_widgets)], stack_width, stack_height, self.stack_widget)
            widget.group_widget = self
            widget.image_double_clicked.connect(self.image_double_clicked.emit)
            widget.setParent(self.stack_widget)
            widget.show()
            self.image_widgets.append(widget)

        for idx, widget in enumerate(self.image_widgets):
            if idx >= target_count:
                widget.hide()
                continue
            widget.group_widget = self
            widget.file_path = self.files[idx]
            widget.update_thumbnail_size(stack_width, stack_height)
            widget.show()

        if not self.files:
            self.badge_label.hide()
            return

        total_count = len(self.files)

        # 根据文件数量调整显示方式
        if len(self.files) == 1:
            # 只有一张图片，居中显示
            if self.image_widgets:
                widget = self.image_widgets[0]
                # 使用卡片的大部分空间，与卡片尺寸成比例
                thumb_width = max(60, int(stack_width * 0.8))
                thumb_height = max(60, int(stack_height * 0.8))
                widget.update_thumbnail_size(thumb_width, thumb_height)
                # 居中放置
                x_pos = max(0, (stack_width - thumb_width) // 2)
                y_pos = max(0, (stack_height - thumb_height) // 2)
                widget.move(x_pos, y_pos)
                widget.show()
                widget.raise_()
        elif len(self.files) == 2:
            # 两张图片并列显示，使用更多空间
            if len(self.image_widgets) >= 2:
                # 计算每个图片的尺寸，使用更多可用空间
                thumb_width = max(50, int((stack_width - spacing) * 0.45))
                thumb_height = max(50, int(stack_height * 0.8))
                
                # 第一张图片放在左边
                widget1 = self.image_widgets[0]
                widget1.update_thumbnail_size(thumb_width, thumb_height)
                y_pos = max(0, (stack_height - thumb_height) // 2)
                widget1.move(int(stack_width * 0.05), y_pos)  # 左边距5%宽度
                widget1.show()
                widget1.raise_()
                
                # 第二张图片放在右边
                widget2 = self.image_widgets[1]
                widget2.update_thumbnail_size(thumb_width, thumb_height)
                x_pos = max(0, stack_width - thumb_width - int(stack_width * 0.05))  # 右边距5%宽度
                y_pos = max(0, (stack_height - thumb_height) // 2)
                widget2.move(x_pos, y_pos)
                widget2.show()
                widget2.raise_()
        else:
            # 三张或更多图片：第一张单独显示，其余堆叠显示
            # 第一张图片放在左边，使用更多空间
            if len(self.image_widgets) >= 1:
                thumb_width = max(50, int((stack_width - spacing) * 0.4))
                thumb_height = max(50, int(stack_height * 0.8))
                
                widget1 = self.image_widgets[0]
                widget1.update_thumbnail_size(thumb_width, thumb_height)
                y_pos = max(0, (stack_height - thumb_height) // 2)
                widget1.move(int(stack_width * 0.05), y_pos)  # 左边距5%宽度
                widget1.show()
                widget1.raise_()
            
            # 其余图片堆叠显示在右边
            remaining_count = len(self.files) - 1
            if remaining_count > 0:
                # 右侧区域使用剩余空间
                right_area_width = max(50, int(stack_width * 0.5))
                right_area_height = max(50, int(stack_height * 0.8))
                right_area_x = stack_width - right_area_width - int(stack_width * 0.05)
                right_area_y = max(0, (stack_height - right_area_height) // 2)
                
                # 堆叠图片的最大显示数量
                max_display = min(remaining_count, 5)
                overlap = min(max(5, int(right_area_width // 15)), 20)
                
                available_width = max(40, right_area_width - 10)
                available_height = max(40, right_area_height - 10)
                stacked_thumb_width, stacked_thumb_height = self._fit_size_with_aspect(
                    max(40, available_width - overlap * (max_display - 1)),
                    available_height,
                    self._STACK_ASPECT_RATIO,
                )
                total_stack_width = stacked_thumb_width + overlap * (max_display - 1)
                total_stack_height = stacked_thumb_height + overlap * (max_display - 1)
                base_x = right_area_x + max(0, (right_area_width - total_stack_width) // 2)
                base_y = right_area_y + max(0, (right_area_height - total_stack_height) // 2)
                
                # 显示堆叠的图片
                for i in range(max_display):
                    if i < remaining_count and (i + 1) < len(self.image_widgets):
                        widget = self.image_widgets[i + 1]
                        widget.update_thumbnail_size(stacked_thumb_width, stacked_thumb_height)
                        offset = overlap * i
                        widget.move(base_x + offset, base_y + offset)
                        widget.show()
                
                # 确保堆叠顺序正确（最后一张在最上面）
                for i in reversed(range(min(max_display, remaining_count))):
                    if (i + 1) < len(self.image_widgets):
                        self.image_widgets[i + 1].raise_()

        self._update_badge(total_count, card_width, padding)

    def refresh_thumbnails(self):
        for widget in self.image_widgets:
            widget.refresh_thumbnail()

    def handle_selection_trigger(self, modifiers: Qt.KeyboardModifier):
        ctrl_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        new_state = not self.is_selected if ctrl_pressed else True
        self.set_selected(new_state)

    def set_selected(self, selected: bool, propagate: bool = True):
        if self.is_selected == selected:
            return
        self.is_selected = selected
        if selected:
            self.setStyleSheet(self._SELECTED_STYLE)
        else:
            self.setStyleSheet(self._BASE_STYLE)
        self.style().unpolish(self)
        self.style().polish(self)

        if propagate:
            self.selection_changed.emit(self.files, selected)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_selection_trigger(event.modifiers())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # 如果双击事件没有被子组件处理，则传递给父类
        super().mouseDoubleClickEvent(event)

    def badge_text(self) -> str:
        return self.badge_label.text() if self.badge_label else ''

    def _update_badge(self, total_count: int, card_width: int, padding: int):
        if not self.badge_label or not self.stack_widget:
            return
        remaining_count = max(0, total_count - 1)
        if remaining_count <= 1:
            self.badge_label.hide()
            return

        self.badge_label.setText(f"×{remaining_count}")
        self.badge_label.adjustSize()

        badge_x = max(padding, card_width - self.badge_label.width() - padding)
        badge_y = padding
        self.badge_label.move(badge_x, badge_y)
        self.badge_label.raise_()
        self.badge_label.show()

    @staticmethod
    def _fit_size_with_aspect(max_width: int, max_height: int, aspect: float) -> Tuple[int, int]:
        if max_width <= 0 or max_height <= 0 or aspect <= 0:
            return max(1, max_width), max(1, max_height)
        height = min(max_height, int(max_width / aspect)) or 1
        width = min(max_width, int(height * aspect)) or 1
        if width > max_width:
            width = max_width
            height = max(1, int(width / aspect))
        if height > max_height:
            height = max_height
            width = max(1, int(height * aspect))
        return max(1, width), max(1, height)


class DeduplicationResultsPanel(QWidget):
    """
    图片去重结果面板
    """
    
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.duplicate_groups = []  # 存储所有重复组控件
        self.selected_files = set()  # 存储选中的文件
        self.grid_size = 3  # 网格列数 (1-8)
        self.thumbnail_size = 120  # 缩略图大小
        self._placeholder_label: Optional[QLabel] = None

        # 获取DPI缩放因子
        self.dpi_scale_factor = self.get_dpi_scale_factor()
        print(f"DPI调试: 初始化DPI缩放因子 = {self.dpi_scale_factor}")

        self.init_ui()
        self._selection_band = QRubberBand(QRubberBand.Shape.Rectangle, self.scroll_area.viewport())
        self._selection_band.hide()
        self._drag_selecting = False
        self._drag_additive = False
        self._drag_start_pos = QPoint()
        self.scroll_area.viewport().installEventFilter(self)
        self.connect_signals()

    def get_dpi_scale_factor(self):
        """获取DPI缩放因子"""
        try:
            # 获取主屏幕
            screen = QCoreApplication.instance().primaryScreen()
            if screen:
                # 获取逻辑DPI和物理DPI
                logical_dpi = screen.logicalDotsPerInch()
                physical_dpi = screen.physicalDotsPerInch()
                # 计算缩放因子
                scale_factor = logical_dpi / 96.0  # 96是标准DPI
                print(f"DPI调试: 逻辑DPI={logical_dpi}, 物理DPI={physical_dpi}, 缩放因子={scale_factor}")
                return scale_factor
        except Exception as e:
            print(f"获取DPI缩放因子时出错: {str(e)}")

        # 如果无法获取，使用默认值
        print("DPI调试: 无法获取DPI信息，使用默认缩放因子1.0")
        return 1.0
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(Spacing.SM)
        
        # 创建分割器用于结果区域和日志区域
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        # 连接分割器移动信号，以便在分割线移动时更新布局
        self.splitter.splitterMoved.connect(self.on_splitter_moved)
        layout.addWidget(self.splitter)
        
        # 顶部操作栏
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🔍 扫描结果")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # 全选/取消全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setStyleSheet(self._button_style(primary=True))
        self.select_all_btn.clicked.connect(self.select_all)
        top_layout.addWidget(self.select_all_btn)

        self.unselect_all_btn = QPushButton("取消全选")
        self.unselect_all_btn.setStyleSheet(self._button_style(primary=False))
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        top_layout.addWidget(self.unselect_all_btn)
        
        # 选中计数标签
        self.selection_count_label = QLabel("选中重复: 0")
        self.selection_count_label.setStyleSheet("color: white; margin: 0 10px;")
        top_layout.addWidget(self.selection_count_label)
        
        # 操作按钮
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.setStyleSheet(self._button_style(primary=True))
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        top_layout.addWidget(self.delete_btn)

        self.move_btn = QPushButton("📂 移动到...")
        self.move_btn.setStyleSheet(self._button_style(primary=True))
        self.move_btn.clicked.connect(self.move_selected)
        self.move_btn.setEnabled(False)
        top_layout.addWidget(self.move_btn)
        
        # 日志按钮
        self.log_btn = QPushButton("📋 日志")
        self.log_btn.setCheckable(True)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #F2F2F2;
                border: 1px solid #4C4C4C;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:checked {
                background-color: #4A4A4A;
                color: #F2F2F2;
                border: 1px solid #4C4C4C;
            }
        """)
        self.log_btn.clicked.connect(self.toggle_log)
        top_layout.addWidget(self.log_btn)
        
        # 网格列数控制
        self.grid_size_label = QLabel("网格列数:")
        self.grid_size_label.setStyleSheet("color: white; margin-left: 10px;")
        top_layout.addWidget(self.grid_size_label)

        self.grid_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_size_slider.setRange(1, 8)  # 1-8列
        self.grid_size_slider.setValue(3)  # 默认3列，更适合大多数屏幕
        self.grid_size_slider.setFixedWidth(120)
        self.grid_size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #404040, stop:1 #2a2a2a);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FF8C00, stop:0.5 #FF6B35, stop:1 #FF8C00);
                border: 2px solid #ffffff;
                width: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FFA500, stop:0.5 #FF8C00, stop:1 #FFA500);
                border: 2px solid #ffffff;
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FF6B35, stop:0.5 #FF4500, stop:1 #FF6B35);
                border: 2px solid #ffffff;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #FF8C00, stop:0.5 #FF6B35, stop:1 #FF8C00);
                border-radius: 3px;
                margin: 2px 0;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #404040, stop:1 #2a2a2a);
                border-radius: 3px;
                margin: 2px 0;
            }
        """)
        self.grid_size_slider.valueChanged.connect(self.on_grid_size_changed)
        top_layout.addWidget(self.grid_size_slider)

        # 显示当前列数的标签
        self.grid_size_value_label = QLabel("3")
        self.grid_size_value_label.setStyleSheet("""
            color: #FF8C00;
            font-weight: bold;
            font-size: 14px;
            min-width: 20px;
            padding: 2px 6px;
            background: rgba(255, 140, 0, 0.1);
            border: 1px solid rgba(255, 140, 0, 0.3);
            border-radius: 4px;
        """)
        top_layout.addWidget(self.grid_size_value_label)

        # 进度条（使用标准进度条）
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("准备就绪")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #454545;
                border-radius: 4px;
                text-align: center;
                background-color: #333337;
                color: white;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background-color: #FF8C00;
                border-radius: 3px;
            }
        """)

        # 重复项显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #353535;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 15px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(Spacing.SM)  # 设置网格间距
        self.grid_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)  # 设置网格边距
        
        self.scroll_area.setWidget(self.scroll_widget)
        
        # 日志区域（默认隐藏）
        self.log_area = QFrame()
        self.log_area.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border: 1px solid #3f3f46;
                border-radius: 6px;
            }
        """)
        self.log_area.setVisible(False)
        
        log_layout = QVBoxLayout(self.log_area)
        log_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        
        log_title = QLabel("📋 处理日志")
        log_title.setStyleSheet("font-weight: bold; color: white;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3f3f46;
                border-radius: 4px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # 创建顶部区域容器
        top_container = QWidget()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(0, 0, 0, 0)
        top_container_layout.setSpacing(Spacing.XS)
        top_container_layout.addWidget(top_bar)
        top_container_layout.addWidget(self.progress_bar)
        top_container_layout.addWidget(self.scroll_area)
        
        self.splitter.addWidget(top_container)
        self.splitter.addWidget(self.log_area)
        
        # 设置分割器比例
        self.splitter.setSizes([700, 200])

        # 初始化为空态视图
        self.reset_view()
        
    def connect_signals(self):
        """连接信号"""
        if self.module:
            self.module.progress_updated.connect(self.update_progress)
            self.module.log_message.connect(self.add_log_message)
            self.module.execution_finished.connect(self.show_results)

        # 延迟执行一次布局更新，确保窗口已经完全显示
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.delayed_layout_update)

    def _button_style(self, primary: bool = False) -> str:
        base_bg = '#3A3A3A'
        base_border = '#4C4C4C'
        base_text = '#F2F2F2'
        orange_text = '#FF8C00'

        if primary:
            return f"""
            QPushButton {{
                background-color: {base_bg};
                color: white;
                border: 1px solid {base_border};
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
                color: {orange_text};
            }}
            QPushButton:pressed {{
                background-color: #333333;
                color: {orange_text};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #A0A0A0;
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: {base_bg};
                color: {base_text};
                border: 1px solid {base_border};
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
                color: {orange_text};
            }}
            QPushButton:pressed {{
                background-color: #333333;
                color: {orange_text};
            }}
            QPushButton:disabled {{
                background-color: #2C2C2C;
                color: #7A7A7A;
                border-color: #3A3A3A;
            }}
            """

    def eventFilter(self, source, event):
        if source is self.scroll_area.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                if (event.button() == Qt.MouseButton.LeftButton and
                        event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._drag_selecting = True
                    self._drag_additive = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
                    self._drag_start_pos = event.position().toPoint()
                    self._selection_band.setGeometry(QRect(self._drag_start_pos, self._drag_start_pos))
                    self._selection_band.show()
                    return True
            elif event.type() == QEvent.Type.MouseMove and self._drag_selecting:
                current_pos = event.position().toPoint()
                selection_rect = QRect(self._drag_start_pos, current_pos).normalized()
                self._selection_band.setGeometry(selection_rect)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease and self._drag_selecting:
                current_pos = event.position().toPoint()
                selection_rect = QRect(self._drag_start_pos, current_pos).normalized()
                self._selection_band.hide()
                self._drag_selecting = False

                if selection_rect.width() < 3 and selection_rect.height() < 3:
                    selection_rect = QRect(current_pos - QPoint(2, 2), current_pos + QPoint(2, 2))

                self._apply_drag_selection(selection_rect.normalized(), self._drag_additive)
                return True

        return super().eventFilter(source, event)

    def _apply_drag_selection(self, selection_rect: QRect, toggle_mode: bool):
        if selection_rect.isNull() or not self.duplicate_groups:
            return

        for group_widget in self.duplicate_groups:
            top_left = group_widget.mapTo(self.scroll_area.viewport(), QPoint(0, 0))
            group_rect = QRect(top_left, group_widget.size())

            if selection_rect.intersects(group_rect):
                if toggle_mode:
                    group_widget.set_selected(not group_widget.is_selected)
                else:
                    group_widget.set_selected(True)

    def force_thumbnail_refresh(self):
        """强制刷新缩略图显示"""
        try:
            if hasattr(self, 'duplicate_groups') and self.duplicate_groups:
                print(f"强制刷新 {len(self.duplicate_groups)} 个重复组的缩略图")
                # 重新计算当前列宽并刷新所有缩略图
                columns = self.grid_size
                container_width = self.scroll_area.viewport().width()
                if container_width > 0:
                    column_width = container_width // columns

                    for group_widget in self.duplicate_groups:
                        if hasattr(group_widget, 'files') and group_widget.files:
                            self.update_group_widget_size(group_widget, column_width)
                            group_widget.refresh_thumbnails()

                    # 强制UI更新
                    self.scroll_area.viewport().update()
        except Exception as e:
            print(f"强制刷新缩略图时出错: {e}")

    def delayed_layout_update(self):
        """延迟布局更新，确保窗口已经完全显示"""
        if hasattr(self, 'grid_layout') and self.grid_layout:
            print("DPI调试: 执行延迟布局更新")
            self.update_grid_layout()
            
    def on_splitter_moved(self, pos, index):
        """处理分割器移动事件"""
        # 当分割器移动时，更新网格布局
        self.update_grid_layout()
            
    def update_progress(self, value: float, message: str):
        """更新进度（无动画，直接更新）"""
        self.progress_bar.setValue(int(value))
        self.progress_bar.setFormat(f"{message} ({int(value)}%)")
        
    def add_log_message(self, message: str, level: str):
        """添加日志消息"""
        formatted_message = f"[{level.upper()}] {message}"
        self.log_text.append(formatted_message)
        
    def show_results(self, result_data: dict):
        """显示结果"""
        self._clear_results_grid()

        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.unselect_all_btn.setEnabled(False)

        # 显示新结果
        duplicates = result_data.get('duplicates', {})
        if duplicates:
            self._hide_placeholder()
            # 使用滑块定义的列数
            columns = max(1, self.grid_size)  # 直接使用用户设置的列数

            # 计算每列的精确宽度（容器总宽度 / 列数）
            container_width = self.scroll_area.viewport().width()
            column_width = container_width // columns
            
            group_items = list(duplicates.items())
            for group_idx, (primary_file, duplicate_files) in enumerate(group_items):
                all_files = [primary_file] + duplicate_files
                # 计算实际的置信度（这里简化处理，实际应该从算法中获取）
                confidence = 0.95
                
                # 计算网格位置
                row = group_idx // columns
                col = group_idx % columns
                
                # 创建卡片
                group_widget = DuplicateGroupWidget(group_idx + 1, all_files, confidence)
                group_widget.thumbnail_size = self.thumbnail_size
                group_widget.selection_changed.connect(self.on_group_selection_changed)
                group_widget.image_double_clicked.connect(self.on_image_double_clicked)
                self.grid_layout.addWidget(group_widget, row, col, Qt.AlignmentFlag.AlignCenter)
                self.duplicate_groups.append(group_widget)

                # 立即设置正确的图片尺寸（关键修复！）
                if hasattr(self, 'scroll_area') and self.scroll_area:
                    self.update_group_widget_size(group_widget, column_width)
                
            # 设置列的拉伸因子，使列宽度相等
            for i in range(columns):
                self.grid_layout.setColumnStretch(i, 1)
                
            # 设置行的拉伸因子，使行高度相等
            rows = (len(group_items) + columns - 1) // columns
            for i in range(rows):
                self.grid_layout.setRowStretch(i, 1)

            # 强制刷新布局和缩略图显示（修复自动刷新问题）
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.force_thumbnail_refresh)
            
            # 再次刷新以确保所有缩略图都加载完成
            QTimer.singleShot(500, self.force_thumbnail_refresh)

            self.select_all_btn.setEnabled(True)
            self.unselect_all_btn.setEnabled(True)
        else:
            self._show_placeholder("\u672a\u627e\u5230\u91cd\u590d\u56fe\u7247\u3002\u8bf7\u8c03\u6574\u8def\u5f84\u6216\u9608\u503c\u540e\u91cd\u8bd5\u3002")
            
    def on_group_selection_changed(self, files, is_selected):
        payload = files[1:] if len(files) > 1 else []
        if is_selected:
            self.selected_files.update(payload)
        else:
            self.selected_files.difference_update(payload)

        self.update_selection_count()
        has_selection = len(self.selected_files) > 0
        self.delete_btn.setEnabled(has_selection)
        self.move_btn.setEnabled(has_selection)

    def on_image_double_clicked(self, file_path):
        """处理图片双击事件"""
        # 创建并显示图片查看器对话框
        try:
            # 使用系统默认图片查看器打开图片
            import subprocess
            import platform
            import os
            
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "文件不存在", f"文件不存在: {file_path}")
                return
                
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            print(f"打开图片时出错: {e}")
            QMessageBox.critical(self, "错误", f"无法打开图片: {str(e)}")
        
    def update_selection_count(self):
        count = len(self.selected_files)
        self.selection_count_label.setText(f"选中重复: {count}")

    def select_all(self):
        all_files: Set[str] = set()
        for group in self.duplicate_groups:
            group.set_selected(True)
            if len(group.files) > 1:
                all_files.update(group.files[1:])

        self.selected_files = all_files
        self.update_selection_count()
        has_selection = len(self.selected_files) > 0
        self.delete_btn.setEnabled(has_selection)
        self.move_btn.setEnabled(has_selection)

    def unselect_all(self):
        for group in self.duplicate_groups:
            group.set_selected(False)

        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)

    def reset_view(self):
        """重置结果面板为初始状态"""
        self._clear_results_grid()
        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.unselect_all_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("准备就绪")

        self.log_text.clear()
        self.log_area.setVisible(False)
        self.log_btn.setChecked(False)
        self.log_btn.setText("📋 日志")

        self._show_placeholder("\u62d6\u62fd\u6587\u4ef6\u5939\u5230\u5de6\u4fa7\u533a\u57df\uff0c\u6216\u5728\u5de6\u4fa7\u6dfb\u52a0\u626b\u63cf\u8def\u5f84\u4ee5\u5f00\u59cb\u65b0\u7684\u626b\u63cf\u3002")

    def _clear_results_grid(self):
        """移除结果网格中的所有控件"""
        self._hide_placeholder()
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if not item:
                continue
            widget = item.widget()
            if not widget:
                continue
            if hasattr(widget, 'selection_changed'):
                try:
                    widget.selection_changed.disconnect()
                except Exception:
                    pass
            if hasattr(widget, 'image_double_clicked'):
                try:
                    widget.image_double_clicked.disconnect()
                except Exception:
                    pass
            widget.setParent(None)
        self.duplicate_groups.clear()

    def _show_placeholder(self, message: str):
        if not self._placeholder_label:
            self._placeholder_label = QLabel()
            self._placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._placeholder_label.setWordWrap(True)
            self._placeholder_label.setStyleSheet(
                "color: white; font-size: 16px; font-weight: bold; padding: 48px;"
            )
        self._placeholder_label.setText(message)
        if self._placeholder_label.parent() is None:
            self.grid_layout.addWidget(
                self._placeholder_label,
                0,
                0,
                1,
                1,
                Qt.AlignmentFlag.AlignCenter,
            )
        self._placeholder_label.show()

    def _hide_placeholder(self):
        if not self._placeholder_label:
            return
        if self._placeholder_label.parent() is not None:
            self.grid_layout.removeWidget(self._placeholder_label)
        self._placeholder_label.hide()

    def delete_selected(self):
        """删除选中文件 - 按重复组仅保留第一张，其余文件执行删除"""
        if not self.selected_files:
            return
            
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除选中的 {len(self.selected_files)} 个重复文件吗？此操作不可撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            failed_files = []
            
            # 删除文件
            for file_path in self.selected_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        success_count += 1
                        if self.module:
                            self.module.log_message.emit(f"已删除: {file_path}", "info")
                    else:
                        failed_files.append(file_path)
                        if self.module:
                            self.module.log_message.emit(f"文件不存在: {file_path}", "warning")
                except Exception as e:
                    failed_files.append(file_path)
                    if self.module:
                        self.module.log_message.emit(f"删除失败 {file_path}: {str(e)}", "error")
                    
            # 显示结果
            message = f"成功删除 {success_count} 个文件"
            if failed_files:
                message += f"，失败 {len(failed_files)} 个文件"
                
            QMessageBox.information(self, "删除完成", message)
            
            # 从UI中移除已删除的文件
            self._remove_deleted_files_from_ui()
            
            # 清空选中
            self.selected_files.clear()
            self.update_selection_count()
            self.delete_btn.setEnabled(False)
            self.move_btn.setEnabled(False)

    def move_selected(self):
        """移动选中文件 - 按重复组仅保留第一张，其余文件执行移动"""
        if not self.selected_files:
            return
            
        # 选择目标目录
        target_dir = QFileDialog.getExistingDirectory(self, "选择目标目录")
        if not target_dir:
            return
            
        success_count = 0
        failed_files = []
        
        # 移动文件
        for file_path in self.selected_files:
            try:
                if os.path.exists(file_path):
                    # 生成目标文件路径
                    filename = os.path.basename(file_path)
                    target_path = os.path.join(target_dir, filename)
                    
                    # 如果目标文件已存在，添加序号
                    counter = 1
                    original_target_path = target_path
                    while os.path.exists(target_path):
                        name, ext = os.path.splitext(original_target_path)
                        target_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    shutil.move(file_path, target_path)
                    success_count += 1
                    if self.module:
                        self.module.log_message.emit(f"已移动: {file_path} -> {target_path}", "info")
                else:
                    failed_files.append(file_path)
                    if self.module:
                        self.module.log_message.emit(f"文件不存在: {file_path}", "warning")
            except Exception as e:
                failed_files.append(file_path)
                if self.module:
                    self.module.log_message.emit(f"移动失败 {file_path}: {str(e)}", "error")
                
        # 显示结果
        message = f"成功移动 {success_count} 个文件"
        if failed_files:
            message += f"，失败 {len(failed_files)} 个文件"
            
        QMessageBox.information(self, "移动完成", message)
        
        # 从UI中移除已移动的文件
        self._remove_deleted_files_from_ui()
        
        # 清空选中
        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)

    def _remove_deleted_files_from_ui(self):
        """从UI中移除已删除或已移动的文件"""
        # 创建新的重复组列表，移除不包含任何文件的组
        remaining_groups = []
        
        for group in self.duplicate_groups:
            # 过滤掉已删除的文件
            remaining_files = [f for f in group.files if os.path.exists(f) or f not in self.selected_files]
            
            if len(remaining_files) > 1:  # 仍然有重复文件
                group.files = remaining_files
                # 更新组内图片显示
                group.update_thumbnails(group.width())
                remaining_groups.append(group)
            elif len(remaining_files) == 1:  # 只剩一个文件，不再是重复组
                # 从布局中移除
                self.grid_layout.removeWidget(group)
                group.setParent(None)
                group.deleteLater()
        
        # 更新重复组列表
        self.duplicate_groups = remaining_groups
        
        # 重新布局
        self.update_grid_layout()

    def reload_all_thumbnails(self):
        """重新加载所有缩略图"""
        try:
            for group_widget in self.duplicate_groups:
                group_widget.refresh_thumbnails()

            # 触发UI刷新以反映最新缩略图
            self.scroll_area.viewport().update()
        except Exception as e:
            print(f"重新加载缩略图时出错: {e}")

    def update_grid_layout(self):
        """更新网格布局"""
        if not self.duplicate_groups:
            return

        try:
            # 使用滑块定义的列数
            columns = self.grid_size  # 直接使用用户设置的列数

            # 获取容器宽度和网格布局参数
            container_width = self.scroll_area.viewport().width()
            if container_width <= 0:
                return  # 避免除零错误

            # 获取网格布局的间距和边距
            grid_spacing = self.grid_layout.spacing()  # 网格间距（默认10px）
            margins = self.grid_layout.contentsMargins()
            left_margin = margins.left()
            right_margin = margins.right()
            top_margin = margins.top()
            bottom_margin = margins.bottom()
            total_horizontal_margin = left_margin + right_margin
            total_spacing_width = grid_spacing * (columns - 1)  # 列间距总数

            # 考虑DPI缩放因子调整容器宽度
            scaled_container_width = int(container_width / self.dpi_scale_factor)

            # 计算实际可用的宽度（容器宽度 - 边距 - 间距）
            available_width = scaled_container_width - total_horizontal_margin - total_spacing_width

            # 计算每列的实际可用宽度
            if available_width <= 0:
                print(f"DPI调试: 警告 - 可用宽度为负数或零: available_width={available_width}, 跳过布局更新")
                return  # 避免负数或零宽度

            # 确保最小列宽
            min_column_width = 100  # 最小列宽100px
            if available_width < columns * min_column_width:
                print(f"DPI调试: 警告 - 可用宽度不足以显示{columns}列, 最小需要{columns * min_column_width}px, 实际{available_width}px")
                # 自动减少列数以适应可用宽度
                columns = max(1, available_width // min_column_width)
                total_spacing_width = grid_spacing * (columns - 1)
                available_width = scaled_container_width - total_horizontal_margin - total_spacing_width
                print(f"DPI调试: 自动调整列数为{columns}, 新的可用宽度={available_width}px")

            actual_column_width = available_width // columns

            # 为了显示实际值，我们也保存原始逻辑宽度
            logical_container_width = container_width
            logical_available_width = logical_container_width - total_horizontal_margin - total_spacing_width
            logical_column_width = logical_available_width // columns

            print(f"DPI调试: 更新布局 - 列数={columns}, 容器宽度={container_width}, 缩放容器宽度={scaled_container_width}")
            print(f"DPI调试: 网格参数 - 左边距={left_margin}px, 右边距={right_margin}px, 总边距={total_horizontal_margin}px, 网格间距={grid_spacing}px, 总间距={total_spacing_width}px")
            print(f"DPI调试: 可用宽度 - 缩放可用={available_width}px, 逻辑可用={logical_available_width}px")
            print(f"DPI调试: 最终列宽 - 缩放列宽={actual_column_width}px, 逻辑列宽={logical_column_width}px, DPI缩放因子={self.dpi_scale_factor}")

            # 清除现有的行和列拉伸因子
            for i in range(self.grid_layout.rowCount()):
                self.grid_layout.setRowStretch(i, 0)
            for i in range(self.grid_layout.columnCount()):
                self.grid_layout.setColumnStretch(i, 0)

            # 清除现有布局中的所有控件
            for i in reversed(range(self.grid_layout.count())):
                widget = self.grid_layout.itemAt(i).widget()
                if widget:
                    self.grid_layout.removeWidget(widget)

            # 重新添加所有卡片到网格布局，并更新每个卡片的尺寸
            for i, group_widget in enumerate(self.duplicate_groups):
                # 计算新位置
                row = i // columns
                col = i % columns

                # 添加到新位置，居中对齐
                self.grid_layout.addWidget(group_widget, row, col, Qt.AlignmentFlag.AlignCenter)

                # 更新这个重复组卡片的宽度并重新计算内部图片大小
                self.update_group_widget_size(group_widget, actual_column_width)

            # 设置每列的固定宽度，使用实际计算的列宽
            for i in range(columns):
                self.grid_layout.setColumnStretch(i, 1)
                self.grid_layout.setColumnMinimumWidth(i, actual_column_width)

            # 清除多余的列拉伸因子，避免影响布局
            for i in range(columns, self.grid_layout.columnCount()):
                self.grid_layout.setColumnStretch(i, 0)

            # 添加一个可伸展的空白行，确保内容从顶部开始排列并可以正常滚动
            rows = (len(self.duplicate_groups) + columns - 1) // columns
            if rows > 0:
                # 在最后一行添加一个伸展因子，确保可以滚动
                self.grid_layout.setRowStretch(rows, 1)

        except Exception as e:
            # 捕获并记录布局更新时的错误
            print(f"更新网格布局时出错: {str(e)}")

    def toggle_log(self):
        """切换日志区域的显示/隐藏"""
        is_visible = self.log_area.isVisible()
        self.log_area.setVisible(not is_visible)
        # 更新按钮文本
        if not is_visible:
            self.log_btn.setText("📋 隐藏日志")
        else:
            self.log_btn.setText("📋 日志")

    def on_grid_size_changed(self, value):
        """处理网格列数改变事件"""
        self.grid_size = value
        self.grid_size_value_label.setText(str(value))
        # 更新网格布局
        self.update_grid_layout()

    def update_group_widget_size(self, group_widget, column_width):
        """更新组控件尺寸"""
        # 确保列宽是正数
        if column_width > 0:
            # 更新组控件的缩略图显示
            group_widget.update_thumbnails(column_width)
            # 刷新缩略图显示
            group_widget.refresh_thumbnails()
            
            # 强制更新布局以确保正确显示
            group_widget.updateGeometry()
            group_widget.update()
