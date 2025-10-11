#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageTrim ICO 图标生成脚本（修复版）
确保所有尺寸正确嵌入ICO文件
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

# 检查PNG文件是否存在
png_files = []
images_dict = {}

for size in ICO_SIZES:
    # 尝试新格式
    png_file = script_dir / f"imageTrim{size}px.png"
    if not png_file.exists():
        # 尝试旧格式
        png_file = script_dir / f"imagetrim_{size}.png"

    if not png_file.exists():
        print(f"[ERROR] 找不到PNG文件: imageTrim{size}px.png 或 imagetrim_{size}.png")
        exit(1)

    png_files.append((size, png_file))

# 加载所有PNG图像
print("[INFO] 加载PNG文件...\n")
for size, png_file in png_files:
    img = Image.open(png_file)

    # 确保是RGBA模式
    if img.mode != 'RGBA':
        print(f"[WARN] {png_file.name} 不是RGBA模式，转换中...")
        img = img.convert('RGBA')

    # 确保尺寸正确
    if img.size != (size, size):
        print(f"[WARN] {png_file.name} 尺寸不匹配，调整中 ({img.size} -> ({size}, {size}))")
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    images_dict[size] = img
    print(f"[OK] {png_file.name}: {size}x{size}, 模式: {img.mode}")

# 生成ICO文件 - 使用正确的方法
output_path = script_dir / OUTPUT_ICO

print(f"\n[INFO] 生成 {OUTPUT_ICO}...")

# 方法：将所有图像作为列表传递，Pillow会自动处理多尺寸
img_list = [images_dict[size] for size in ICO_SIZES]

# 保存ICO - 关键是sizes参数必须是元组列表
img_list[0].save(
    output_path,
    format='ICO',
    sizes=[(size, size) for size in ICO_SIZES]
)

print(f"[SUCCESS] 成功生成: {output_path}")

# 验证ICO文件
print("\n[INFO] 验证ICO文件...")
ico = Image.open(output_path)
print(f"  主尺寸: {ico.size}")
print(f"  格式: {ico.format}")
print(f"  模式: {ico.mode}")

# 尝试读取所有嵌入的尺寸
print("\n[INFO] 嵌入的尺寸:")
for size in ICO_SIZES:
    try:
        ico_test = Image.open(output_path)
        ico_test.size = (size, size)  # 尝试访问特定尺寸
        print(f"  [OK] {size}x{size} - 已嵌入")
    except:
        print(f"  [WARN] {size}x{size} - 可能未正确嵌入")

print("\n[DONE] ICO 文件生成完成！")
print("\n[TIP] Windows任务栏通常使用:")
print("  - 小图标: 16x16")
print("  - 标准图标: 32x32")
print("  - 大图标: 48x48")
print("  - 高清显示: 256x256")
print("\n  如果任务栏图标模糊，请检查Windows显示设置中的缩放比例")
