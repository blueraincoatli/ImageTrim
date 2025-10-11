#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageTrim ICO 图标生成脚本（终极修复版）
使用append_images参数正确嵌入所有尺寸
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

print("[INFO] ImageTrim ICO 生成工具（多尺寸嵌入版）\n")

# 检查并加载所有PNG文件
images = []
for size in ICO_SIZES:
    # 尝试新格式
    png_file = script_dir / f"imageTrim{size}px.png"
    if not png_file.exists():
        # 尝试旧格式
        png_file = script_dir / f"imagetrim_{size}.png"

    if not png_file.exists():
        print(f"[ERROR] 找不到PNG文件: imageTrim{size}px.png")
        exit(1)

    img = Image.open(png_file)

    # 确保是RGBA模式
    if img.mode != 'RGBA':
        print(f"[WARN] {png_file.name} 转换为RGBA模式")
        img = img.convert('RGBA')

    # 验证尺寸
    if img.size != (size, size):
        print(f"[WARN] {png_file.name} 调整尺寸 {img.size} -> ({size}x{size})")
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    images.append(img)
    print(f"[OK] {size}x{size} - {png_file.name}")

output_path = script_dir / OUTPUT_ICO

print(f"\n[INFO] 保存ICO文件...")

# 关键：使用append_images参数将所有图像嵌入
# 第一张图片作为主图片，其余通过append_images添加
images[0].save(
    str(output_path),
    format='ICO',
    append_images=images[1:],  # 添加剩余图像
    sizes=[(16, 16), (32, 32), (48, 48), (256, 256)]  # 明确指定所有尺寸
)

print(f"[SUCCESS] ICO文件已生成: {output_path}")
print(f"[INFO] 包含尺寸: 16x16, 32x32, 48x48, 256x256")

# 验证文件大小
file_size = output_path.stat().st_size
print(f"[INFO] 文件大小: {file_size} bytes ({file_size/1024:.1f} KB)")

if file_size < 2000:
    print("[WARN] 文件较小，可能只包含部分尺寸")
    print("       正常的多尺寸ICO应该在15-50KB之间")
else:
    print("[OK] 文件大小正常，应该包含所有尺寸")

print("\n[DONE] 完成！")
print("\n[TIP] 任务栏显示说明:")
print("  - Windows会根据任务栏大小和DPI自动选择合适的图标尺寸")
print("  - 如果看起来模糊，可能是因为:")
print("    1. Windows缩放比例不是100%（如125%, 150%）")
print("    2. 需要重启应用或重启资源管理器")
print("    3. 图标缓存需要清理")
