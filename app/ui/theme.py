#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageTrim 应用主题配置
统一的颜色、字体、间距等设计规范
"""


class Theme:
    """主题颜色配置"""

    # ===== 主色调 =====
    PRIMARY = "#FF8C00"           # 橙色（主色）
    PRIMARY_LIGHT = "#FFA500"     # 浅橙色
    PRIMARY_DARK = "#FF6B35"      # 深橙色

    # ===== 背景色 =====
    BG_DARK = "#1E1E1E"          # 深色背景
    BG_MEDIUM = "#2d2d30"        # 中度背景
    BG_LIGHT = "#3A3A3A"         # 浅色背景
    BG_CARD = "#252526"          # 卡片背景

    # ===== 文本色 =====
    TEXT_PRIMARY = "#FFFFFF"      # 主文本（白色）
    TEXT_SECONDARY = "#B0B0B0"    # 次要文本（灰色）
    TEXT_DISABLED = "#6C757D"     # 禁用文本

    # ===== 边框色 =====
    BORDER_LIGHT = "#4C4C4C"      # 浅边框
    BORDER_DARK = "#353535"       # 深边框
    BORDER_FOCUS = "#3f3f46"      # 焦点边框

    # ===== 状态色 =====
    SUCCESS = "#28A745"           # 成功（绿色）
    WARNING = "#FFC107"           # 警告（黄色）
    ERROR = "#DC3545"             # 错误（红色）
    INFO = "#17A2B8"              # 信息（蓝色）

    # ===== 渐变色定义 =====
    @staticmethod
    def gradient_orange() -> str:
        """橙色渐变（横向）"""
        return f"""
            qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Theme.PRIMARY},
                stop:0.5 {Theme.PRIMARY_DARK},
                stop:1 {Theme.PRIMARY})
        """

    @staticmethod
    def gradient_orange_vertical() -> str:
        """橙色渐变（纵向）"""
        return f"""
            qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Theme.PRIMARY},
                stop:1 {Theme.PRIMARY_DARK})
        """

    @staticmethod
    def rgba(hex_color: str, alpha: float) -> str:
        """
        将十六进制颜色转换为 RGBA 格式

        Args:
            hex_color: 十六进制颜色值，如 "#FF8C00"
            alpha: 透明度，0.0-1.0

        Returns:
            RGBA 格式字符串，如 "rgba(255, 140, 0, 0.5)"
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"


class Spacing:
    """间距规范"""
    XS = 4    # 超小间距 (4px)
    SM = 8    # 小间距 (8px)
    MD = 12   # 中等间距 (12px)
    LG = 16   # 大间距 (16px)
    XL = 24   # 超大间距 (24px)
    XXL = 32  # 极大间距 (32px)


class FontSize:
    """字体大小规范"""
    H1 = 16   # 一级标题
    H2 = 14   # 二级标题
    H3 = 12   # 三级标题
    BODY = 10 # 正文
    SMALL = 9 # 小字


class BorderRadius:
    """圆角半径规范"""
    SM = 4    # 小圆角
    MD = 6    # 中等圆角
    LG = 8    # 大圆角
    XL = 12   # 超大圆角
    CIRCLE = 50  # 圆形（百分比）


class Shadow:
    """阴影效果配置"""

    @staticmethod
    def card_shadow() -> tuple:
        """
        卡片阴影参数（深色背景优化）
        Returns: (blur_radius, color_rgba, offset_x, offset_y)
        """
        # 在深色背景下，使用更强的黑色阴影和更大的模糊半径
        return (25, Theme.rgba("#000000", 0.6), 0, 6)

    @staticmethod
    def card_shadow_hover() -> tuple:
        """卡片悬停阴影参数"""
        return (30, Theme.rgba("#000000", 0.8), 0, 8)

    @staticmethod
    def panel_shadow() -> tuple:
        """面板阴影参数（深色背景优化）"""
        return (30, Theme.rgba("#000000", 0.7), 0, 4)

    @staticmethod
    def button_shadow() -> tuple:
        """按钮阴影参数"""
        return (15, Theme.rgba("#000000", 0.5), 0, 3)

    @staticmethod
    def inner_glow() -> tuple:
        """
        内发光效果（用于突出元素）
        Returns: (blur_radius, color_rgba, offset_x, offset_y)
        """
        # 使用橙色内发光增加视觉深度
        return (10, Theme.rgba(Theme.PRIMARY, 0.3), 0, 0)


class Animation:
    """动画时长配置（毫秒）"""
    FAST = 150      # 快速动画
    NORMAL = 300    # 正常动画
    SLOW = 500      # 慢速动画


class ProgressBarStyle:
    """进度条样式配置"""

    @staticmethod
    def get_style() -> str:
        """
        获取带平滑动画的进度条样式

        Returns:
            QSS样式字符串
        """
        return f"""
            QProgressBar {{
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: {BorderRadius.MD}px;
                text-align: center;
                background-color: {Theme.BG_MEDIUM};
                color: {Theme.TEXT_PRIMARY};
                font-size: {FontSize.BODY}px;
                font-weight: bold;
                height: 28px;
                padding: 2px;
            }}

            QProgressBar::chunk {{
                background: {Theme.gradient_orange()};
                border-radius: {BorderRadius.SM}px;
                margin: 1px;
            }}
        """
