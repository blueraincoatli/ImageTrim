"""
PyQt6适配器，用于将ttkbootstrap UI组件适配到PyQt6框架
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit,
                             QProgressBar, QScrollArea, QFrame, QFileDialog,
                             QMessageBox, QGroupBox, QListWidget, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette
from typing import Optional, Any, Dict, Union
import os


class PyQt6Adapter:
    """PyQt6适配器类，提供类似ttkbootstrap的接口"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = {}
    
    # Frame相关方法
    def Frame(self, parent=None, padding=0, style=""):
        """创建Frame容器"""
        frame = QFrame(parent)
        if padding:
            if isinstance(padding, int):
                frame.setContentsMargins(padding, padding, padding, padding)
            elif isinstance(padding, tuple) and len(padding) == 4:
                frame.setContentsMargins(padding[0], padding[1], padding[2], padding[3])
        
        # 设置样式
        if "Card" in style:
            frame.setStyleSheet("background-color: #1B1B1B; border: 1px solid #353535; border-radius: 5px;")
        elif "Primary" in style:
            frame.setStyleSheet("background-color: #1B1B1B;")
        elif "Secondary" in style:
            frame.setStyleSheet("background-color: #1B1B1B;")
        else:
            frame.setStyleSheet("background-color: #1B1B1B;")
            
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        return frame
    
    def Labelframe(self, parent=None, text="", padding=0):
        """创建带标签的Frame"""
        group_box = QGroupBox(text, parent)
        group_box.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        
        if padding:
            if isinstance(padding, int):
                group_box.setContentsMargins(padding, padding, padding, padding)
            elif isinstance(padding, tuple) and len(padding) == 4:
                group_box.setContentsMargins(padding[0], padding[1], padding[2], padding[3])
                
        layout = QVBoxLayout(group_box)
        layout.setContentsMargins(10, 20, 10, 10)  # 为标题留出空间
        return group_box
    
    # Label相关方法
    def Label(self, parent=None, text="", font=None, style=""):
        """创建标签"""
        label = QLabel(text, parent)
        label.setStyleSheet("color: white;")
        
        # 设置样式
        if "Inverse" in style:
            label.setStyleSheet("color: white; background-color: #353535;")
        elif "info" in style:
            label.setStyleSheet("color: #FF8C00;")
            
        # 设置字体
        if font:
            if isinstance(font, tuple):
                qfont = QFont()
                qfont.setFamily(font[0])
                if len(font) > 1:
                    qfont.setPointSize(font[1])
                if len(font) > 2 and "bold" in font[2]:
                    qfont.setBold(True)
                label.setFont(qfont)
                
        return label
    
    # Button相关方法
    def Button(self, parent=None, text="", command=None, bootstyle="", width=0):
        """创建按钮"""
        button = QPushButton(text, parent)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置宽度
        if width > 0:
            button.setFixedWidth(width * 10)  # 简单的宽度转换
            
        # 设置样式
        if "success" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        elif "danger" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        elif "warning" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
                QPushButton:pressed {
                    background-color: #d39e00;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        elif "info" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:pressed {
                    background-color: #117a8b;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        elif "primary" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0069d9;
                }
                QPushButton:pressed {
                    background-color: #0062cc;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        elif "secondary" in bootstyle:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #545b62;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #353535;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #454545;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
            
        # 绑定命令
        if command:
            button.clicked.connect(command)
            
        return button
    
    # Entry相关方法
    def Entry(self, parent=None, textvariable=None):
        """创建输入框"""
        entry = QLineEdit(parent)
        entry.setStyleSheet("""
            QLineEdit {
                background-color: #4B4B4B;
                color: white;
                border: 1px solid #6c757d;
                padding: 5px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #FF8C00;
            }
        """)
        
        # 绑定变量
        if textvariable:
            entry.setText(textvariable.value)
            # 这里需要更复杂的绑定机制，简化处理
            entry.textChanged.connect(lambda text: setattr(textvariable, 'value', text))
            
        return entry
    
    # Scale相关方法
    def Scale(self, parent=None, from_=0, to=100, variable=None, orient=Qt.Orientation.Horizontal):
        """创建滑块"""
        slider = QSlider(orient, parent)
        slider.setMinimum(int(from_))
        slider.setMaximum(int(to))
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #2B2B2B;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #FF8C00;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #FF8C00;
            }
        """)
        
        # 绑定变量
        if variable:
            slider.setValue(int(variable.value))
            slider.valueChanged.connect(lambda value: setattr(variable, 'value', value))
            
        return slider
    
    # Checkbutton相关方法
    def Checkbutton(self, parent=None, text="", variable=None, bootstyle=""):
        """创建复选框"""
        checkbox = QCheckBox(text, parent)
        checkbox.setStyleSheet("QCheckBox { color: white; }")
        
        # 绑定变量
        if variable:
            checkbox.setChecked(variable.value)
            checkbox.stateChanged.connect(lambda state: setattr(variable, 'value', state == Qt.CheckState.Checked.value))
            
        # 圆角切换样式
        if "round-toggle" in bootstyle:
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #6c757d;
                    border-radius: 9px;
                    background-color: #2B2B2B;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #FF8C00;
                    border-radius: 9px;
                    background-color: #FF8C00;
                }
            """)
            
        return checkbox
    
    # Progressbar相关方法
    def Progressbar(self, parent=None, bootstyle=""):
        """创建进度条"""
        progressbar = QProgressBar(parent)
        progressbar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #6c757d;
                border-radius: 4px;
                text-align: center;
                background-color: #2B2B2B;
            }
            QProgressBar::chunk {
                background-color: #FF8C00;
            }
        """)
        
        # 条纹样式
        if "striped" in bootstyle:
            progressbar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #6c757d;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #2B2B2B;
                }
                QProgressBar::chunk {
                    background-color: #FF8C00;
                }
            """)
            
        return progressbar
    
    # Text相关方法
    def Text(self, parent=None, height=10, state="normal"):
        """创建文本框"""
        text_edit = QTextEdit(parent)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #6c757d;
                border-radius: 4px;
            }
        """)
        
        # 设置高度
        if height:
            text_edit.setMaximumHeight(height * 20)  # 简单的高度转换
            
        # 设置状态
        if state == "disabled":
            text_edit.setReadOnly(True)
            
        return text_edit
    
    # Scrollbar相关方法
    def Scrollbar(self, parent=None, orient=Qt.Orientation.Vertical):
        """创建滚动条"""
        # PyQt6中滚动条通常由容器自动创建，这里返回None表示使用默认滚动条
        return None
    
    # Listbox相关方法
    def Listbox(self, parent=None, height=4):
        """创建列表框"""
        list_widget = QListWidget(parent)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #6c757d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #FF8C00;
                color: black;
            }
        """)
        
        return list_widget
    
    # 布局方法
    def pack(self, widget, **kwargs):
        """模拟pack布局"""
        # 在PyQt6中，布局由父控件的布局管理器处理
        # 这里只需要确保控件被添加到父控件中
        pass
    
    def grid(self, widget, **kwargs):
        """模拟grid布局"""
        # 在PyQt6中，布局由父控件的布局管理器处理
        # 这里只需要确保控件被添加到父控件中
        pass
    
    # 常量
    BOTH = Qt.Orientation.Horizontal | Qt.Orientation.Vertical
    X = Qt.Orientation.Horizontal
    Y = Qt.Orientation.Vertical
    HORIZONTAL = Qt.Orientation.Horizontal
    VERTICAL = Qt.Orientation.Vertical
    LEFT = Qt.AlignmentFlag.AlignLeft
    RIGHT = Qt.AlignmentFlag.AlignRight
    TOP = Qt.AlignmentFlag.AlignTop
    BOTTOM = Qt.AlignmentFlag.AlignBottom
    CENTER = Qt.AlignmentFlag.AlignCenter
    W = Qt.AlignmentFlag.AlignLeft
    E = Qt.AlignmentFlag.AlignRight
    N = Qt.AlignmentFlag.AlignTop
    S = Qt.AlignmentFlag.AlignBottom
    NW = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
    NE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
    SW = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
    SE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
    EXPAND = Qt.AlignmentFlag.AlignJustify
    FILL = Qt.AlignmentFlag.AlignJustify


# 模拟ttkbootstrap.constants
class Constants:
    BOTH = Qt.Orientation.Horizontal | Qt.Orientation.Vertical
    X = Qt.Orientation.Horizontal
    Y = Qt.Orientation.Vertical
    HORIZONTAL = Qt.Orientation.Horizontal
    VERTICAL = Qt.Orientation.Vertical
    LEFT = Qt.AlignmentFlag.AlignLeft
    RIGHT = Qt.AlignmentFlag.AlignRight
    TOP = Qt.AlignmentFlag.AlignTop
    BOTTOM = Qt.AlignmentFlag.AlignBottom
    CENTER = Qt.AlignmentFlag.AlignCenter
    W = Qt.AlignmentFlag.AlignLeft
    E = Qt.AlignmentFlag.AlignRight
    N = Qt.AlignmentFlag.AlignTop
    S = Qt.AlignmentFlag.AlignBottom
    NW = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
    NE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
    SW = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
    SE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
    EXPAND = Qt.AlignmentFlag.AlignJustify
    FILL = Qt.AlignmentFlag.AlignJustify
    DISABLED = "disabled"
    NORMAL = "normal"


# 模拟变量类
class Variable:
    def __init__(self, value=None):
        self.value = value


class StringVar(Variable):
    pass


class IntVar(Variable):
    pass


class DoubleVar(Variable):
    pass


class BooleanVar(Variable):
    pass


# 模拟文件对话框
class FileDialog:
    @staticmethod
    def askdirectory():
        return QFileDialog.getExistingDirectory(None, "Select Directory")
    
    @staticmethod
    def askopenfilename():
        return QFileDialog.getOpenFileName(None, "Open File")[0]


# 模拟消息框
class MessageBox:
    @staticmethod
    def showerror(title, message):
        QMessageBox.critical(None, title, message)
        
    @staticmethod
    def showinfo(title, message):
        QMessageBox.information(None, title, message)
        
    @staticmethod
    def showwarning(title, message):
        QMessageBox.warning(None, title, message)
        
    @staticmethod
    def askyesno(title, message):
        reply = QMessageBox.question(None, title, message, 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes
        
    @staticmethod
    def askyesnocancel(title, message):
        reply = QMessageBox.question(None, title, message,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            return True
        elif reply == QMessageBox.StandardButton.No:
            return False
        else:
            return None