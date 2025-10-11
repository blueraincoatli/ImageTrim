#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageTrim ICO 图标生成脚本
将PNG图标打包为Windows .ico 文件（保留透明度）
"""

import os
import sys
from pathlib import Path

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from PIL import Image
except ImportError:
    print("[ERROR] 缺少 Pillow 库，请先安装：")
    print("   pip install Pillow")
    exit(1)

# 配置
ICO_SIZES = [16, 32, 48, 256]  # Windows ICO 推荐尺寸
OUTPUT_ICO = "imagetrim.ico"

# 获取脚本所在目录
script_dir = Path(__file__).parent

print("[INFO] 开始生成 Windows ICO 图标...\n")

# 检查PNG文件是否存在（支持两种文件名格式）
png_files = []
for size in ICO_SIZES:
    # 优先尝试新格式：imageTrim256px.png
    png_file = script_dir / f"imageTrim{size}px.png"
    if not png_file.exists():
        # 尝试旧格式：imagetrim_256.png
        png_file = script_dir / f"imagetrim_{size}.png"

    if not png_file.exists():
        print(f"[ERROR] 找不到PNG文件: imageTrim{size}px.png 或 imagetrim_{size}.png")
        print("   请先用 Illustrator 导出PNG文件，并确保勾选「透明背景」选项")
        exit(1)

    png_files.append(png_file)

# 打开所有PNG图像并验证透明度
images = []
print("[INFO] 检查PNG文件透明度...\n")
for png_file in png_files:
    img = Image.open(png_file)

    # 确保是RGBA模式（包含alpha通道）
    if img.mode != 'RGBA':
        print(f"[WARN] {png_file.name} 不是RGBA模式（当前: {img.mode}），转换中...")
        img = img.convert('RGBA')
        # 保存转换后的文件
        img.save(png_file)
        print(f"[OK] 已转换为RGBA模式并保存")
    else:
        print(f"[OK] {png_file.name} ({img.size[0]}x{img.size[1]}, 模式: {img.mode})")

    images.append(img)

# 生成ICO文件（关键：添加 append_images 参数以保留透明度）
print("\n[INFO] 生成ICO文件...\n")
output_path = script_dir / OUTPUT_ICO

# 使用第一张图片作为主图片，其余作为附加图片
# append_images 参数是关键，可以正确保留所有尺寸的透明度
images[0].save(
    output_path,
    format='ICO',
    sizes=[(img.size[0], img.size[1]) for img in images],
    append_images=images[1:],  # 关键参数：正确添加其他尺寸
    optimize=False  # 禁用优化以确保透明度保留
)

print(f"[SUCCESS] 成功生成: {output_path}")
print(f"[INFO] 包含尺寸: {', '.join([f'{s}x{s}' for s in ICO_SIZES])}")

print("\n[DONE] ICO 文件生成完成！")
print("\n[TIP] 使用方法：")
print("   在 PyQt6 代码中：")
print("   self.setWindowIcon(QIcon('app/resources/icons/imagetrim.ico'))")
print("\n[TIP] 如果仍看到白底：")
print("   1. 检查SVG源文件是否包含白色背景层")
print("   2. 重新从Illustrator导出PNG时，确保勾选「透明背景」选项")
print("   3. 删除所有PNG和ICO文件，重新导出生成")
