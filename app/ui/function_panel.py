#!/usr/bin/env python3
"""
功能选择面板
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from core.function_manager import FunctionManager


class FunctionCard(QPushButton):
    """
    功能卡片组件
    """
    
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置按钮样式
        self.setFixedHeight(100)  # 增加高度以容纳所有内容
        self.setCheckable(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 功能图标和名称
        title_label = QLabel(f"{self.module.icon} {self.module.display_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        desc_label = QLabel(self.module.description)
        desc_label.setStyleSheet("font-size: 12px; color: #CCCCCC;")
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()  # 添加弹性空间
        
        # 设置样式
        self.setStyleSheet("""
            FunctionCard {
                text-align: left;
                border: none;
                border-radius: 6px;
                background-color: #2d2d30;
                padding: 15px;
            }
            
            FunctionCard:hover {
                background-color: #333337;
            }
            
            FunctionCard:checked {
                background-color: #0078d7;
            }
        """)


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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
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
        self.function_list_widget.setStyleSheet("""
            #function-list {
                background-color: transparent;
                border: none;
            }
        """)
        self.function_list_layout = QVBoxLayout(self.function_list_widget)
        self.function_list_layout.setSpacing(8)
        self.function_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.function_list_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.function_list_widget)
        layout.addWidget(scroll_area)
        
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
                self.function_list_layout.addWidget(card)
                self.function_cards[module_name] = card
                
    def on_card_selected(self, module_name: str):
        """处理卡片选择事件"""
        # 取消其他卡片的选中状态
        for name, card in self.function_cards.items():
            if name != module_name:
                card.setChecked(False)
                
        # 发出功能选择信号
        self.function_selected.emit(module_name)