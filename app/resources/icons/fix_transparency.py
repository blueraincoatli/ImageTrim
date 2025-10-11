#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复ICO文件透明度问题
从SVG生成带正确alpha通道的PNG，然后打包为ICO
"""

import os
import sys
import subprocess
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
SVG_FILE = "imagetrim_final.svg"
ICO_SIZES = [16, 32, 48, 256]
OUTPUT_ICO = "imagetrim.ico"

script_dir = Path(__file__).parent
svg_path = script_dir / SVG_FILE

if not svg_path.exists():
    print(f"[ERROR] 找不到SVG文件: {svg_path}")
    exit(1)

print("[INFO] 开始修复ICO透明度问题...\n")

# 1. 尝试使用 Inkscape 生成PNG
inkscape_paths = [
    r"C:\Program Files\Inkscape\bin\inkscape.exe",
    r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
    "inkscape"
]

inkscape_exe = None
for path in inkscape_paths:
    try:
        result = subprocess.run([path, "--version"], capture_output=True, check=True, timeout=5)
        inkscape_exe = path
        print(f"[OK] 找到 Inkscape: {path}\n")
        break
    except:
        continue

if inkscape_exe:
    # 使用 Inkscape 生成PNG（确保透明背景）
    print("[INFO] 使用 Inkscape 生成PNG（带透明度）...\n")
    png_files = []

    for size in ICO_SIZES:
        output_file = script_dir / f"imagetrim_{size}.png"
        try:
            cmd = [
                inkscape_exe,
                str(svg_path),
                "--export-type=png",
                f"--export-filename={output_file}",
                f"--export-width={size}",
                f"--export-height={size}",
                "--export-background-opacity=0"  # 关键：确保背景透明
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            print(f"[OK] {size}x{size}px -> {output_file.name}")
            png_files.append(output_file)
        except Exception as e:
            print(f"[ERROR] {size}x{size}px 失败: {e}")
            exit(1)

    print("\n[INFO] 验证PNG透明度...")
    for png_file in png_files:
        img = Image.open(png_file)
        if img.mode != 'RGBA':
            print(f"[WARN] {png_file.name} 不是RGBA模式，转换中...")
            img = img.convert('RGBA')
            img.save(png_file)
        else:
            print(f"[OK] {png_file.name} - RGBA模式正确")

    # 2. 生成ICO文件（确保保留透明度）
    print(f"\n[INFO] 生成 {OUTPUT_ICO}...")

    images = []
    for png_file in png_files:
        img = Image.open(png_file)
        # 确保是RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        images.append(img)

    output_path = script_dir / OUTPUT_ICO

    # 使用 Pillow 保存ICO，显式保留透明度
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in images],
        append_images=images[1:],  # 添加其他尺寸
        optimize=False  # 禁用优化以保留透明度
    )

    print(f"\n[SUCCESS] 成功生成: {output_path}")
    print(f"[INFO] 包含尺寸: {', '.join([f'{s}x{s}' for s in ICO_SIZES])}")
    print("\n[DONE] 透明度修复完成！")
    print("\n[TIP] 提示：")
    print("   - 新的ICO文件应该有完全透明的背景")
    print("   - 如果仍有白底，请检查SVG源文件是否包含白色背景元素")

else:
    print("[ERROR] 未找到 Inkscape")
    print("\n[INFO] 手动修复方案：")
    print("1. 用 Adobe Illustrator 打开 imagetrim_final.svg")
    print("2. 文件 → 导出 → 导出为...")
    print("3. 格式选择：PNG")
    print("4. **重要**: 勾选「透明」或「透明背景」选项")
    print("5. 导出以下尺寸：")
    for size in ICO_SIZES:
        print(f"   - {size}x{size}px -> imagetrim_{size}.png")
    print("\n6. 确保导出的PNG文件没有白色背景")
    print("7. 然后运行: python generate_ico.py")
