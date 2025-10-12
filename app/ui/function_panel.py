#!/usr/bin/env python3
"""
功能选择面板
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QFrame, QPushButton, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty
from PyQt6.QtGui import QColor
from core.function_manager import FunctionManager
from ui.theme import Theme, Spacing, Shadow, BorderRadius


class FunctionCard(QPushButton):
    """
    功能卡片组件（带悬停缩放动画）
    """

    def __init__(self, module):
        super().__init__()
        self.module = module
        self._scale = 1.0  # 缩放比例
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        """初始化UI"""
        # 让卡片均分可用空间
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 宽度填充
            QSizePolicy.Policy.Expanding   # 高度均分可用空间
        )
        self.setCheckable(True)

        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # 功能图标和名称
        title_label = QLabel(f"{self.module.icon} {self.module.display_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: black;")

        desc_label = QLabel(self.module.description)
        desc_label.setStyleSheet("font-size: 11px; color: black;")
        desc_label.setWordWrap(True)

        layout.addStretch()  # 上方弹性空间
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()  # 下方弹性空间，让内容垂直居中

        # 设置样式（使用主题变量）- 减小padding
        self.setStyleSheet(f"""
            FunctionCard {{
                text-align: left;
                border: 1px solid {Theme.rgba(Theme.PRIMARY, 0.1)};
                border-radius: {BorderRadius.LG}px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffcce6, stop: 0.25 #cce6ff, stop: 0.5 #ffe6cc,
                    stop: 0.75 #e6ccff, stop: 1 #ccffe6);
                padding: 10px;
                outline: none;
            }}

            FunctionCard:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffddee, stop: 0.25 #ddeeff, stop: 0.5 #ffeedd,
                    stop: 0.75 #eeddff, stop: 1 #ddeeef);
                border: 1px solid {Theme.rgba(Theme.PRIMARY, 0.3)};
            }}

            FunctionCard:checked {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ff66b3, stop: 0.25 #66b3ff, stop: 0.5 #ffcc66,
                    stop: 0.75 #cc66ff, stop: 1 #66ffcc);
                border: 2px solid {Theme.PRIMARY};
            }}

            FunctionCard:focus {{
                outline: none;
                border: none;
            }}
        """)

        # 添加阴影效果
        self.add_shadow_effect()

    def setup_animations(self):
        """设置动画"""
        # 只创建阴影动画，不使用尺寸动画（避免布局问题）
        self.shadow_animation = QPropertyAnimation(self.graphicsEffect(), b"blurRadius")
        self.shadow_animation.setDuration(200)
        self.shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def add_shadow_effect(self):
        """添加阴影效果"""
        blur_radius, color_rgba, offset_x, offset_y = Shadow.card_shadow()

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(blur_radius)
        self.shadow.setColor(QColor(color_rgba))
        self.shadow.setOffset(offset_x, offset_y)
        self.setGraphicsEffect(self.shadow)

    def enterEvent(self, event):
        """鼠标进入事件 - 增强阴影"""
        super().enterEvent(event)

        # 增强阴影效果
        hover_blur, _, _, _ = Shadow.card_shadow_hover()
        self.shadow_animation.stop()
        self.shadow_animation.setStartValue(self.shadow.blurRadius())
        self.shadow_animation.setEndValue(hover_blur)
        self.shadow_animation.start()

    def leaveEvent(self, event):
        """鼠标离开事件 - 恢复阴影"""
        super().leaveEvent(event)

        # 恢复原始阴影
        normal_blur, _, _, _ = Shadow.card_shadow()
        self.shadow_animation.stop()
        self.shadow_animation.setStartValue(self.shadow.blurRadius())
        self.shadow_animation.setEndValue(normal_blur)
        self.shadow_animation.start()


class FunctionPanel(QWidget):
    """
    功能选择面板
    """
    
    # 功能选择信号
    function_selected = pyqtSignal(str)

    def __init__(self, function_manager: FunctionManager):
        super().__init__()
        self.function_manager = function_manager
        self.function_cards = {}
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(Spacing.SM)

        # 标题
        title = QLabel("🔧 功能选择")
        title.setObjectName("panel-title")
        title.setStyleSheet("""
            #panel-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: white;
            }
        """)
        layout.addWidget(title)

        # 功能列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平方向扩展
            QSizePolicy.Policy.Expanding   # 垂直方向扩展以填充空间
        )
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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

        # 功能列表容器
        self.function_list_widget = QFrame()
        self.function_list_widget.setObjectName("function-list")
        self.function_list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平方向扩展
            QSizePolicy.Policy.Expanding   # 垂直方向也扩展，填充整个滚动区域
        )
        self.function_list_widget.setStyleSheet("""
            #function-list {
                background-color: transparent;
                border: none;
            }
        """)
        self.function_list_layout = QVBoxLayout(self.function_list_widget)
        self.function_list_layout.setSpacing(Spacing.SM)  # 卡片间距
        self.function_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.function_list_layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)

        scroll_area.setWidget(self.function_list_widget)
        # 使用 stretch=1 让滚动区域占据所有可用的垂直空间
        layout.addWidget(scroll_area, 1)
        
    def update_modules(self):
        """更新模块列表"""
        # 清除现有卡片
        for i in reversed(range(self.function_list_layout.count())):
            widget = self.function_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.function_cards.clear()

        # 创建新卡片
        for module_name in self.function_manager.get_module_names():
            module = self.function_manager.get_module(module_name)
            if module:
                card = FunctionCard(module)
                card.clicked.connect(lambda checked, name=module_name: self.on_card_selected(name))
                # 使用 stretch=1 让每个卡片均分可用空间
                self.function_list_layout.addWidget(card, 1)
                self.function_cards[module_name] = card
                
    def on_card_selected(self, module_name: str):
        """处理卡片选择事件"""
        # 取消其他卡片的选中状态
        for name, card in self.function_cards.items():
            if name != module_name:
                card.setChecked(False)
                
        # 发出功能选择信号
        self.function_selected.emit(module_name)