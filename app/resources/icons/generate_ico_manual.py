#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用原始PNG数据生成ICO（无压缩版本）
"""

import sys
import struct
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image

ICO_SIZES = [16, 32, 48, 256]
script_dir = Path(__file__).parent

print("[INFO] 手动构建ICO文件（无压缩）\n")

# 加载PNG文件
png_data_list = []
for size in ICO_SIZES:
    png_file = script_dir / f"imageTrim{size}px.png"
    if not png_file.exists():
        print(f"[ERROR] 找不到: {png_file.name}")
        exit(1)

    # 直接读取PNG原始数据
    with open(png_file, 'rb') as f:
        png_data = f.read()

    png_data_list.append((size, png_data))
    print(f"[OK] {png_file.name}: {len(png_data)} bytes")

# 构建ICO文件
output_path = script_dir / "imagetrim.ico"

with open(output_path, 'wb') as ico:
    # ICO文件头
    ico.write(struct.pack('<HHH', 0, 1, len(ICO_SIZES)))  # 保留字, 类型(1=ICO), 图像数量

    # 计算每个图像的偏移量
    offset = 6 + (16 * len(ICO_SIZES))  # 头部 + 目录项

    # 写入目录项
    for size, png_data in png_data_list:
        width = size if size < 256 else 0  # 256用0表示
        height = size if size < 256 else 0
        ico.write(struct.pack('<BBBB', width, height, 0, 0))  # 宽, 高, 颜色数, 保留
        ico.write(struct.pack('<HH', 1, 32))  # 颜色平面, 位深度
        ico.write(struct.pack('<I', len(png_data)))  # 图像数据大小
        ico.write(struct.pack('<I', offset))  # 图像数据偏移
        offset += len(png_data)

    # 写入PNG数据
    for size, png_data in png_data_list:
        ico.write(png_data)

file_size = output_path.stat().st_size
print(f"\n[SUCCESS] ICO已生成: {output_path}")
print(f"[INFO] 文件大小: {file_size} bytes ({file_size/1024:.1f} KB)")
print(f"[INFO] 包含图像: {len(ICO_SIZES)} 个")

for size, png_data in png_data_list:
    print(f"  - {size}x{size}: {len(png_data)} bytes")

print("\n[DONE] 完成！这个ICO文件包含完整的PNG数据，不应该模糊")
