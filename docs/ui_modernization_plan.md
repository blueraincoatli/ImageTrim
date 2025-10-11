# UI 现代化改进规划

> **项目名称**: ImageTrim (图简) - 智能图片去重与压缩工具
> **版本**: 1.0.0
> **创建日期**: 2024年
> **目标**: 打造现代、流畅、专业的跨平台桌面应用

---

## 📋 目录

1. [应用品牌设计](#1-应用品牌设计)
2. [视觉增强方案](#2-视觉增强方案)
3. [关于与版权信息](#3-关于与版权信息)
4. [跨平台打包配置](#4-跨平台打包配置)
5. [实施步骤](#5-实施步骤)

---

## 1. 应用品牌设计

### 1.1 应用命名方案

**确定方案: ImageTrim (图简)**

**品牌定位**:
- ✅ **核心价值**: Trim = 修剪/精简，完美体现"去重+压缩"双重功能
- ✅ **简洁专业**: 9个字母，易读易记，适合国际化推广
- ✅ **中文绝配**: "图简"二字简洁有力，朗朗上口
- ✅ **双关含义**: Trim既有"修剪"(去重)又有"精简"(压缩)之意
- ✅ **品牌独特性**: 区别于通用的"图片编辑"或"AIGC"工具

**品牌标识**:
- **主标题**: ImageTrim
- **中文名**: 图简
- **副标题**: 智能去重，高效压缩
- **Slogan**: Trim your images, Save your space (修剪图片，节省空间)

---

### 1.2 图标设计方案

#### 创意核心：被修剪的字母 "I"

**设计理念**:
- 使用大写粗体衬线字体的字母 "I" 作为主体
- 在上方 1/3 处创造一个光滑的切口
- 上半部分向右倾斜约 12-15 度，营造"即将掉落"的动感
- 隐喻：被修剪(Trim)的部分即将被移除 = 去除冗余/节省空间

**视觉元素**:
```
     ╱│╲        ← 上半部分(向右倾斜15°，快要掉落)
    ╱ │ ╲         透明度 90%，暗示"即将消失"
   ╱  │  ╲
  ────────     ← 光滑切口(象征 smooth 操作)
      │
      │         ← 下半部分(稳固垂直，100%不透明)
      │
   ═══╧═══
```

**设计要素**:

1. **字体选择**:
   - **推荐**: Didot, Bodoni, Playfair Display (经典衬线体，粗细对比强烈)
   - **备选**: Trajan Pro, Cinzel (罗马柱式衬线，庄重稳重)
   - **特点**: 粗体、带饰线、现代感

2. **切口设计**:
   - **平滑切口** - 象征操作的流畅性 (smooth trim)
   - 切口边缘使用稍深的橙色 #FF6B35 强调断裂感
   - 无锯齿，体现精准和专业

3. **倾斜与动感**:
   - 上半部分向右倾斜 **12-15 度**
   - 既有动态感又保持稳重
   - 可在 hover 时增加倾斜角度作为交互动画

4. **配色方案**:
   - **主体**: 橙色渐变 #FF8C00 → #FF6B35
   - **切口边缘**: 深橙色 #FF6B35 (强调断裂)
   - **上半部分**: 90% 不透明度，增强"即将消失"感
   - **下半部分**: 100% 不透明度，强调稳固
   - **背景**: 深色 #1E1E1E 或白色 #FFFFFF (根据系统主题)
   - **圆角**: 18% 半径 (现代 iOS/macOS 风格)

5. **阴影效果**:
   - **上半部分**: 向右下投影，强化"掉落"感
   - **下半部分**: 轻微底部阴影，强化"稳固"感
   - **整体**: 柔和外阴影增加深度

**视觉隐喻**:
- ✅ "I" 被 Trim 后的状态 = 图片被精简的过程
- ✅ 上部分掉落 = 冗余数据被移除
- ✅ 下部分稳固 = 保留精华内容
- ✅ 光滑切口 = 流畅高效的操作体验

---

### 1.3 图标文件生成清单

#### Windows 平台
```
app/resources/icons/
├── imagetrim.ico          # 主图标（包含16x16, 32x32, 48x48, 256x256）
├── imagetrim_16.png       # 任务栏小图标
├── imagetrim_32.png       # 标题栏图标
├── imagetrim_48.png       # 快捷方式图标
└── imagetrim_256.png      # 安装程序图标
```

#### macOS 平台
```
app/resources/icons/
├── imagetrim.icns         # macOS 图标集（包含所有尺寸）
├── imagetrim_16.png       # Dock 图标
├── imagetrim_32.png
├── imagetrim_64.png
├── imagetrim_128.png
├── imagetrim_256.png
└── imagetrim_512.png
```

#### Linux 平台
```
app/resources/icons/
├── imagetrim.svg          # 矢量图标（推荐）
├── imagetrim_16.png
├── imagetrim_32.png
├── imagetrim_48.png
├── imagetrim_64.png
├── imagetrim_128.png
└── imagetrim_256.png
```

---

### 1.4 图标集成代码

#### 主窗口图标设置
**文件**: `app/main.py` 或 `app/ui/main_window.py`

```python
from PyQt6.QtGui import QIcon
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_app_icon()

    def set_app_icon(self):
        """设置应用图标"""
        # 获取图标路径
        icon_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')

        # Windows/Linux
        icon_path = os.path.join(icon_dir, 'imagetrim.ico')
        if not os.path.exists(icon_path):
            # macOS fallback
            icon_path = os.path.join(icon_dir, 'imagetrim.icns')
        if not os.path.exists(icon_path):
            # PNG fallback
            icon_path = os.path.join(icon_dir, 'imagetrim_256.png')

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
```

#### 系统托盘图标（可选）
```python
from PyQt6.QtWidgets import QSystemTrayIcon

def create_tray_icon(self):
    """创建系统托盘图标"""
    icon_path = os.path.join('resources', 'icons', 'imagetrim_32.png')
    self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
    self.tray_icon.setToolTip("ImageTrim - 图片去重工具")
    self.tray_icon.show()
```

---

### 1.5 应用标题栏设置

**文件**: `app/ui/main_window.py`

```python
def init_ui(self):
    """初始化UI"""
    # 设置窗口标题
    self.setWindowTitle("ImageTrim - 智能图片去重与压缩工具")

    # 设置窗口图标
    self.set_app_icon()

    # 设置最小窗口尺寸
    self.setMinimumSize(1200, 800)

    # 其他UI初始化...
```

---

## 2. 视觉增强方案

### 2.1 阴影与深度效果

#### 2.1.1 功能卡片阴影优化

**文件**: `app/ui/function_panel.py`

**当前代码** (第45-73行):
```python
self.setStyleSheet("""
    FunctionCard {
        text-align: left;
        border: none;
        border-radius: 6px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #ffcce6, stop: 0.25 #cce6ff, stop: 0.5 #ffe6cc,
            stop: 0.75 #e6ccff, stop: 1 #ccffe6);
        padding: 15px;
        outline: none;
    }
    /* ... */
""")
```

**优化后代码**:
```python
self.setStyleSheet("""
    FunctionCard {
        text-align: left;
        border: 1px solid rgba(255, 140, 0, 0.1);
        border-radius: 8px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #ffcce6, stop: 0.25 #cce6ff, stop: 0.5 #ffe6cc,
            stop: 0.75 #e6ccff, stop: 1 #ccffe6);
        padding: 15px;
        outline: none;
    }

    FunctionCard:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #ffddee, stop: 0.25 #ddeeff, stop: 0.5 #ffeedd,
            stop: 0.75 #eeddff, stop: 1 #ddeeef);
        border: 1px solid rgba(255, 140, 0, 0.3);
        /* 注意: PyQt6 QSS 不支持 box-shadow，需要用 QGraphicsDropShadowEffect */
    }

    FunctionCard:checked {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #ff66b3, stop: 0.25 #66b3ff, stop: 0.5 #ffcc66,
            stop: 0.75 #cc66ff, stop: 1 #66ffcc);
        border: 2px solid #FF8C00;
    }

    FunctionCard:focus {
        outline: none;
        border: none;
    }
""")
```

**添加程序化阴影效果**:
```python
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

def init_ui(self):
    """初始化UI"""
    # ... 现有代码 ...

    # 添加阴影效果
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)  # 模糊半径
    shadow.setColor(QColor(0, 0, 0, 50))  # 黑色，透明度50
    shadow.setOffset(0, 4)  # 水平偏移0，垂直偏移4像素
    self.setGraphicsEffect(shadow)
```

#### 2.1.2 设置面板容器阴影

**文件**: `app/ui/settings_panel.py`

**当前代码** (第40-47行):
```python
container.setStyleSheet("""
    QFrame {
        background-color: #2d2d30;
        border: none;
        border-radius: 8px;
    }
""")
```

**优化后代码**:
```python
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

# 在 init_ui 方法中添加:
container.setStyleSheet("""
    QFrame {
        background-color: #2d2d30;
        border: none;
        border-radius: 8px;
    }
""")

# 添加阴影效果
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(20)
shadow.setColor(QColor(0, 0, 0, 80))
shadow.setOffset(0, 2)
container.setGraphicsEffect(shadow)
```

---

### 2.2 动画与过渡效果

#### 2.2.1 进度条平滑动画

**文件**: `app/modules/deduplication/results_panel.py`

**优化位置**: 第 915-935 行（进度条样式）

**添加动画控制代码**:
```python
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class DeduplicationResultsPanel(QWidget):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.init_ui()
        self.connect_signals()

        # 创建进度条动画
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(300)  # 300ms 过渡时间
        self.progress_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def update_progress(self, value: float, message: str):
        """更新进度（带动画）"""
        self.progress_label.setText(message)

        # 使用动画更新进度条
        current_value = self.progress_bar.value()
        target_value = int(value)

        self.progress_animation.setStartValue(current_value)
        self.progress_animation.setEndValue(target_value)
        self.progress_animation.start()
```

#### 2.2.2 卡片悬停缩放效果

**文件**: `app/ui/function_panel.py`

**在 FunctionCard 类中添加**:
```python
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

class FunctionCard(QPushButton):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.init_ui()

        # 创建缩放动画
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.original_geometry = None

    def enterEvent(self, event):
        """鼠标悬停事件"""
        super().enterEvent(event)

        # 保存原始尺寸
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

        # 计算放大后的尺寸（1.02倍）
        rect = self.geometry()
        center = rect.center()
        new_width = int(rect.width() * 1.02)
        new_height = int(rect.height() * 1.02)
        new_rect = QRect(0, 0, new_width, new_height)
        new_rect.moveCenter(center)

        # 启动放大动画
        self.scale_animation.setStartValue(rect)
        self.scale_animation.setEndValue(new_rect)
        self.scale_animation.start()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)

        # 恢复原始尺寸
        if self.original_geometry:
            self.scale_animation.setStartValue(self.geometry())
            self.scale_animation.setEndValue(self.original_geometry)
            self.scale_animation.start()
```

---

### 2.3 排版与字体优化

#### 2.3.1 全局字体配置

**文件**: `app/main.py` 或 应用入口文件

**在应用启动时设置全局字体**:
```python
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import sys

def main():
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont()
    font.setFamily("Segoe UI, Microsoft YaHei UI, PingFang SC, sans-serif")
    font.setPointSize(10)
    app.setFont(font)

    # 设置全局样式表
    app.setStyleSheet("""
        * {
            font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
        }

        QLabel {
            line-height: 1.5;
        }

        QPushButton {
            font-weight: 500;
        }
    """)

    # ... 其他初始化代码 ...
```

#### 2.3.2 标题字体层级

**文件**: 各个模块的 UI 文件

**标题样式规范**:
```python
# 一级标题 (主标题)
title_style = """
    font-size: 20px;
    font-weight: 600;
    color: white;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
"""

# 二级标题 (分组标题)
subtitle_style = """
    font-size: 16px;
    font-weight: 600;
    color: white;
    margin-bottom: 8px;
"""

# 三级标题 (卡片标题)
card_title_style = """
    font-size: 14px;
    font-weight: 600;
    color: black;
"""

# 正文
body_style = """
    font-size: 12px;
    font-weight: 400;
    color: white;
    line-height: 1.5;
"""
```

**应用示例** - `app/ui/function_panel.py`:
```python
# 第97行附近，修改标题样式
title = QLabel("🔧 功能选择")
title.setObjectName("panel-title")
title.setStyleSheet("""
    #panel-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
        color: white;
        letter-spacing: 0.5px;
    }
""")
```

---

### 2.4 配色方案统一

#### 2.4.1 全局颜色变量定义

**创建新文件**: `app/ui/theme.py`

```python
"""
ImageTrim 应用主题配置
"""

class Theme:
    """主题颜色配置"""

    # 主色调
    PRIMARY = "#FF8C00"           # 橙色（主色）
    PRIMARY_LIGHT = "#FFA500"     # 浅橙色
    PRIMARY_DARK = "#FF6B35"      # 深橙色

    # 背景色
    BG_DARK = "#1E1E1E"          # 深色背景
    BG_MEDIUM = "#2d2d30"        # 中度背景
    BG_LIGHT = "#3A3A3A"         # 浅色背景

    # 文本色
    TEXT_PRIMARY = "#FFFFFF"      # 主文本（白色）
    TEXT_SECONDARY = "#B0B0B0"    # 次要文本（灰色）
    TEXT_DISABLED = "#6C757D"     # 禁用文本

    # 边框色
    BORDER_LIGHT = "#4C4C4C"      # 浅边框
    BORDER_DARK = "#353535"       # 深边框

    # 状态色
    SUCCESS = "#28A745"           # 成功（绿色）
    WARNING = "#FFC107"           # 警告（黄色）
    ERROR = "#DC3545"             # 错误（红色）
    INFO = "#17A2B8"              # 信息（蓝色）

    # 渐变色
    GRADIENT_ORANGE = f"""
        qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY}, stop:0.5 {PRIMARY_DARK}, stop:1 {PRIMARY})
    """

    @staticmethod
    def rgba(hex_color: str, alpha: float) -> str:
        """将十六进制颜色转换为 RGBA"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
```

#### 2.4.2 使用主题变量

**示例** - `app/ui/function_panel.py`:
```python
from ui.theme import Theme

class FunctionCard(QPushButton):
    def init_ui(self):
        """初始化UI"""
        self.setFixedHeight(100)
        self.setCheckable(True)

        # ... 布局代码 ...

        # 使用主题颜色
        self.setStyleSheet(f"""
            FunctionCard {{
                border: 1px solid {Theme.rgba(Theme.PRIMARY, 0.1)};
                border-radius: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffcce6, stop: 0.25 #cce6ff, stop: 0.5 #ffe6cc,
                    stop: 0.75 #e6ccff, stop: 1 #ccffe6);
                padding: 15px;
                outline: none;
            }}

            FunctionCard:hover {{
                border: 1px solid {Theme.rgba(Theme.PRIMARY, 0.3)};
            }}

            FunctionCard:checked {{
                border: 2px solid {Theme.PRIMARY};
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ff66b3, stop: 0.25 #66b3ff, stop: 0.5 #ffcc66,
                    stop: 0.75 #cc66ff, stop: 1 #66ffcc);
            }}
        """)
```

---

### 2.5 间距与布局优化

#### 2.5.1 统一间距规范

**创建间距常量** - 在 `app/ui/theme.py` 中添加:
```python
class Spacing:
    """间距规范"""
    XS = 4    # 超小间距
    SM = 8    # 小间距
    MD = 12   # 中等间距
    LG = 16   # 大间距
    XL = 24   # 超大间距
    XXL = 32  # 极大间距
```

#### 2.5.2 应用间距规范

**示例** - `app/ui/settings_panel.py`:
```python
from ui.theme import Spacing

def init_ui(self):
    """初始化UI"""
    layout = QVBoxLayout(self)
    layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
    layout.setSpacing(Spacing.LG)

    # ... 其他UI代码 ...
```

**示例** - `app/ui/function_panel.py`:
```python
def init_ui(self):
    """初始化UI"""
    layout = QVBoxLayout(self)
    layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
    layout.setSpacing(Spacing.SM)
```

---

### 2.6 图标系统现代化

#### 2.6.1 使用矢量图标

**推荐图标库**: [Phosphor Icons](https://phosphoricons.com/) 或 [Feather Icons](https://feathericons.com/)

**实现方式1: SVG 内嵌**
```python
from PyQt6.QtSvg import QSvgWidget

def create_svg_icon(svg_path: str, size: int = 24) -> QSvgWidget:
    """创建 SVG 图标组件"""
    icon_widget = QSvgWidget(svg_path)
    icon_widget.setFixedSize(size, size)
    return icon_widget
```

**实现方式2: Unicode Emoji（当前方案保持）**
```python
# 保持现有的 emoji 图标，但优化字体大小
title_label = QLabel(f"{self.module.icon} {self.module.display_name}")
title_label.setStyleSheet("""
    font-weight: bold;
    font-size: 16px;  /* 增大图标大小 */
    color: black;
""")
```

#### 2.6.2 图标资源组织

**创建图标资源目录**:
```
app/resources/icons/
├── ui/                    # UI 图标
│   ├── search.svg
│   ├── settings.svg
│   ├── refresh.svg
│   └── delete.svg
├── brands/                # 品牌图标
│   ├── imageflow.ico
│   ├── imageflow.icns
│   └── imageflow.svg
└── file-types/            # 文件类型图标
    ├── image.svg
    ├── folder.svg
    └── unknown.svg
```

---

### 2.7 响应式布局优化

#### 2.7.1 窗口自适应

**文件**: `app/ui/main_window.py` (假设这是主窗口)

```python
from PyQt6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 设置最小尺寸
        self.setMinimumSize(QSize(1000, 700))

        # 设置初始尺寸为屏幕的70%
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.7)
        height = int(screen.height() * 0.7)
        self.resize(width, height)

        # 居中显示
        self.center_on_screen()

    def center_on_screen(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)

        # 根据窗口宽度调整布局
        window_width = self.width()

        # 如果窗口宽度小于1200，调整为紧凑布局
        if window_width < 1200:
            self.apply_compact_layout()
        else:
            self.apply_normal_layout()

    def apply_compact_layout(self):
        """应用紧凑布局"""
        # 减小边距和间距
        # ... 实现细节 ...
        pass

    def apply_normal_layout(self):
        """应用正常布局"""
        # 恢复默认边距和间距
        # ... 实现细节 ...
        pass
```

#### 2.7.2 文字自适应缩放

```python
from PyQt6.QtGui import QFont

def adjust_font_size(base_size: int, window_width: int) -> int:
    """根据窗口宽度调整字体大小"""
    if window_width < 1200:
        return max(base_size - 2, 9)  # 最小9px
    elif window_width > 1600:
        return base_size + 1
    else:
        return base_size
```

---

## 3. 关于与版权信息

### 3.1 关于对话框设计

#### 3.1.1 UI 设计方案

**创建新文件**: `app/ui/about_dialog.py`

```python
#!/usr/bin/env python3
"""
关于对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextBrowser, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import os

class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 ImageTrim")
        self.setFixedSize(500, 600)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # ===== 应用图标和名称 =====
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 应用图标
        icon_label = QLabel()
        icon_path = os.path.join('resources', 'icons', 'imagetrim_128.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 应用名称
        name_label = QLabel("ImageTrim")
        name_font = QFont()
        name_font.setPointSize(24)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #FF8C00;")
        header_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 副标题
        subtitle_label = QLabel("智能去重，高效压缩")
        subtitle_label.setStyleSheet("color: #B0B0B0; font-size: 14px;")
        header_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(header_layout)

        # ===== 分隔线 =====
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #4C4C4C;")
        layout.addWidget(line)

        # ===== 版本信息 =====
        version_layout = QHBoxLayout()
        version_label = QLabel("版本:")
        version_label.setStyleSheet("color: white; font-weight: bold;")
        version_value = QLabel("1.0.0")
        version_value.setStyleSheet("color: #B0B0B0;")
        version_layout.addWidget(version_label)
        version_layout.addWidget(version_value)
        version_layout.addStretch()
        layout.addLayout(version_layout)

        # ===== 版权信息 =====
        copyright_text = QTextBrowser()
        copyright_text.setOpenExternalLinks(True)
        copyright_text.setStyleSheet("""
            QTextBrowser {
                background-color: #2d2d30;
                color: white;
                border: 1px solid #4C4C4C;
                border-radius: 6px;
                padding: 15px;
                font-size: 12px;
            }
        """)
        copyright_text.setHtml("""
            <h3 style="color: #FF8C00;">📝 版权信息</h3>
            <p><b>Copyright © 2024 ImageTrim Team</b></p>
            <p>保留所有权利。</p>

            <h3 style="color: #FF8C00; margin-top: 20px;">👨‍💻 开发团队</h3>
            <p><b>作者:</b> Your Name</p>
            <p><b>邮箱:</b> <a href="mailto:contact@imagetrim.com" style="color: #FF8C00;">contact@imagetrim.com</a></p>
            <p><b>网站:</b> <a href="https://imagetrim.com" style="color: #FF8C00;">https://imagetrim.com</a></p>

            <h3 style="color: #FF8C00; margin-top: 20px;">📜 开源协议</h3>
            <p>本软件基于 <b>MIT License</b> 开源协议发布。</p>

            <h3 style="color: #FF8C00; margin-top: 20px;">🙏 致谢</h3>
            <p>感谢以下开源项目:</p>
            <ul>
                <li>PyQt6 - GUI 框架</li>
                <li>Pillow - 图像处理</li>
                <li>imagehash - 感知哈希算法</li>
            </ul>
        """)
        layout.addWidget(copyright_text)

        # ===== 关闭按钮 =====
        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #FF6B35;
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
```

#### 3.1.2 触发方式

**方案A: 菜单栏触发（推荐）**

**文件**: `app/ui/main_window.py`

```python
from PyQt6.QtWidgets import QMenuBar
from ui.about_dialog import AboutDialog

class MainWindow(QMainWindow):
    def init_ui(self):
        """初始化UI"""
        # ... 现有代码 ...

        # 创建菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 退出
        exit_action = file_menu.addAction("退出")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于
        about_action = help_menu.addAction("关于 ImageTrim")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()
```

**方案B: 设置面板中的关于按钮**

**文件**: `app/ui/settings_panel.py`

```python
from ui.about_dialog import AboutDialog

class SettingsPanel(QWidget):
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        # ... 现有代码 ...

        # 添加关于按钮到底部
        about_btn = QPushButton("ℹ️ 关于 ImageTrim")
        about_btn.clicked.connect(self.show_about_dialog)
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FF8C00;
                border: 1px solid #FF8C00;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 140, 0, 0.1);
            }
        """)
        layout.addWidget(about_btn)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()
```

---

### 3.2 状态栏信息显示

**文件**: `app/ui/main_window.py`

```python
from PyQt6.QtWidgets import QStatusBar, QLabel

class MainWindow(QMainWindow):
    def init_ui(self):
        """初始化UI"""
        # ... 现有代码 ...

        # 创建状态栏
        self.create_status_bar()

    def create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # 版权信息标签（左侧）
        copyright_label = QLabel("© 2024 ImageTrim Team")
        copyright_label.setStyleSheet("color: #B0B0B0; padding: 2px 10px;")
        statusbar.addWidget(copyright_label)

        # 弹性空间
        statusbar.addStretch(1)

        # 版本信息（右侧）
        version_label = QLabel("版本 1.0.0")
        version_label.setStyleSheet("color: #B0B0B0; padding: 2px 10px;")
        statusbar.addPermanentWidget(version_label)

        # 状态栏样式
        statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d30;
                border-top: 1px solid #4C4C4C;
            }
        """)
```

---

## 4. 跨平台打包配置

### 4.1 PyInstaller 配置

#### 4.1.1 创建打包脚本

**创建文件**: `build.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/resources', 'resources'),  # 包含资源文件
        ('app/modules', 'modules'),      # 包含模块
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',
        'PIL',
        'imagehash',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageTrim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/icons/imagetrim.ico',  # Windows 图标
)

# macOS 应用打包
app = BUNDLE(
    exe,
    name='ImageTrim.app',
    icon='app/resources/icons/imagetrim.icns',  # macOS 图标
    bundle_identifier='com.imagetrim.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Image Files',
                'CFBundleTypeRole': 'Viewer',
                'LSItemContentTypes': ['public.image'],
            }
        ]
    },
)
```

#### 4.1.2 打包命令

**Windows**:
```bash
# 安装 PyInstaller
pip install pyinstaller

# 单文件打包
pyinstaller --onefile --windowed --icon=app/resources/icons/imagetrim.ico app/main.py

# 或使用 spec 文件
pyinstaller build.spec
```

**macOS**:
```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为 .app
pyinstaller build.spec

# 签名（可选）
codesign --force --deep --sign - dist/ImageTrim.app
```

**Linux**:
```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --icon=app/resources/icons/imagetrim.png app/main.py
```

---

### 4.2 依赖管理

#### 4.2.1 requirements.txt

**创建文件**: `requirements.txt`

```txt
PyQt6>=6.5.0
Pillow>=10.0.0
imagehash>=4.3.0
numpy>=1.24.0
```

#### 4.2.2 虚拟环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

### 4.3 安装程序制作

#### 4.3.1 Windows (NSIS)

**创建文件**: `installer.nsi`

```nsis
; ImageTrim 安装脚本

!define APP_NAME "ImageTrim"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "ImageTrim Team"
!define APP_URL "https://imagetrim.com"
!define APP_EXE "ImageTrim.exe"

Name "${APP_NAME}"
OutFile "ImageTrim_Setup_${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Page directory
Page instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\*.*"

    ; 创建桌面快捷方式
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\imagetrim.ico"

    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载.lnk" "$INSTDIR\Uninstall.exe"

    ; 写入卸载信息
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
SectionEnd
```

**编译安装程序**:
```bash
makensis installer.nsi
```

#### 4.3.2 macOS (DMG)

**创建 DMG 脚本**: `create_dmg.sh`

```bash
#!/bin/bash

APP_NAME="ImageTrim"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}_${VERSION}.dmg"

# 创建临时目录
mkdir -p dmg_temp
cp -R dist/${APP_NAME}.app dmg_temp/

# 创建 DMG
hdiutil create -volname "${APP_NAME}" -srcfolder dmg_temp -ov -format UDZO ${DMG_NAME}

# 清理
rm -rf dmg_temp

echo "DMG 创建完成: ${DMG_NAME}"
```

**运行**:
```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

#### 4.3.3 Linux (AppImage)

**使用 linuxdeploy**:
```bash
# 下载 linuxdeploy
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage

# 打包
./linuxdeploy-x86_64.AppImage --appdir AppDir --executable dist/ImageTrim --desktop-file imagetrim.desktop --icon-file app/resources/icons/imagetrim.png --output appimage
```

---

## 5. 实施步骤

### 5.1 第一阶段: 品牌与图标（1-2天）

**优先级**: 🔴 高

**任务清单**:
- [ ] 确认应用名称: ImageTrim (图简)
- [ ] 设计应用图标（被修剪的字母 I）
- [ ] 生成多平台图标文件（.ico, .icns, .png）
- [ ] 集成图标到主窗口和托盘
- [ ] 更新窗口标题

**负责文件**:
- `app/resources/icons/` (新建)
- `app/main.py`
- `app/ui/main_window.py`

---

### 5.2 第二阶段: 视觉增强（2-3天）

**优先级**: 🔴 高

**任务清单**:
- [ ] 创建主题配置文件 `app/ui/theme.py`
- [ ] 添加阴影效果到卡片和面板
- [ ] 实现进度条平滑动画
- [ ] 优化卡片悬停效果
- [ ] 统一配色方案
- [ ] 优化排版和间距

**负责文件**:
- `app/ui/theme.py` (新建)
- `app/ui/function_panel.py`
- `app/ui/settings_panel.py`
- `app/modules/deduplication/results_panel.py`
- `app/modules/avif_converter/ui.py`

---

### 5.3 第三阶段: 关于与版权（1天）

**优先级**: 🟡 中

**任务清单**:
- [ ] 创建关于对话框 `app/ui/about_dialog.py`
- [ ] 添加菜单栏和"关于"菜单项
- [ ] 添加状态栏版权信息
- [ ] 填写实际的联系方式和团队信息

**负责文件**:
- `app/ui/about_dialog.py` (新建)
- `app/ui/main_window.py`

---

### 5.4 第四阶段: 跨平台打包（2-3天）

**优先级**: 🟡 中

**任务清单**:
- [ ] 配置 PyInstaller 打包脚本 `build.spec`
- [ ] 测试 Windows 打包
- [ ] 测试 macOS 打包
- [ ] 测试 Linux 打包
- [ ] 创建安装程序（NSIS/DMG/AppImage）
- [ ] 编写打包文档

**负责文件**:
- `build.spec` (新建)
- `requirements.txt` (更新)
- `installer.nsi` (新建)
- `create_dmg.sh` (新建)
- `docs/packaging.md` (新建)

---

### 5.5 第五阶段: 测试与优化（1-2天）

**优先级**: 🟢 低

**任务清单**:
- [ ] 测试所有平台的图标显示
- [ ] 测试响应式布局
- [ ] 测试动画流畅度
- [ ] 性能优化
- [ ] 修复发现的 Bug

---

## 📊 进度跟踪

| 阶段 | 状态 | 预计时间 | 实际时间 |
|------|------|----------|----------|
| 品牌与图标 | ⏳ 待开始 | 1-2天 | - |
| 视觉增强 | ⏳ 待开始 | 2-3天 | - |
| 关于与版权 | ⏳ 待开始 | 1天 | - |
| 跨平台打包 | ⏳ 待开始 | 2-3天 | - |
| 测试与优化 | ⏳ 待开始 | 1-2天 | - |

**总预计时间**: 7-11 天

---

## 📝 备注

1. **图标设计**: 建议使用专业设计工具（Figma, Adobe XD）或委托设计师
2. **动画性能**: 注意在低配设备上测试动画流畅度
3. **跨平台测试**: 务必在所有目标平台上测试打包后的应用
4. **版权信息**: 记得替换文档中的占位符（Your Name, contact@imagetrim.com 等）

---

**文档版本**: 1.0
**最后更新**: 2024年
**维护者**: ImageTrim Team
