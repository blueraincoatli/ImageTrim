#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageTrim 图标生成脚本
使用 Inkscape 从SVG生成多尺寸PNG图标
"""

import os
import subprocess
from pathlib import Path

# 配置
SVG_FILE = "imagetrim_final.svg"
OUTPUT_SIZES = [16, 32, 48, 64, 128, 256, 512]

# 获取脚本所在目录
script_dir = Path(__file__).parent

# 检查SVG文件是否存在
svg_path = script_dir / SVG_FILE
if not svg_path.exists():
    print(f"找不到SVG文件: {svg_path}")
    exit(1)

print(f"SVG源文件: {svg_path}")
print(f"开始生成 {len(OUTPUT_SIZES)} 个尺寸的PNG图标...\n")

# 尝试使用 Inkscape
inkscape_paths = [
    r"C:\Program Files\Inkscape\bin\inkscape.exe",
    r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
    "inkscape"  # 如果在PATH中
]

inkscape_exe = None
for path in inkscape_paths:
    try:
        subprocess.run([path, "--version"], capture_output=True, check=True)
        inkscape_exe = path
        break
    except:
        continue

if not inkscape_exe:
    print("未找到 Inkscape，请手动转换：")
    print("1. 用 Illustrator 打开 SVG")
    print("2. 导出为 PNG，设置以下尺寸：")
    for size in OUTPUT_SIZES:
        print(f"   - {size}x{size}px -> imagetrim_{size}.png")
    exit(1)

# 使用 Inkscape 生成PNG
for size in OUTPUT_SIZES:
    output_file = script_dir / f"imagetrim_{size}.png"

    try:
        cmd = [
            inkscape_exe,
            str(svg_path),
            "--export-type=png",
            f"--export-filename={output_file}",
            f"--export-width={size}",
            f"--export-height={size}"
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        print(f"OK {size}x{size}px -> {output_file.name}")

    except Exception as e:
        print(f"FAIL {size}x{size}px: {e}")

print("\nPNG图标生成完成！")
print("\n下一步：运行 generate_ico.py 生成 .ico 文件")
