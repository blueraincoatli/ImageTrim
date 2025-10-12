#!/bin/bash

# ImageTrim Linux/macOS 打包脚本

set -e

echo "===================================="
echo "   ImageTrim 打包脚本"
echo "===================================="
echo

cd "$(dirname "$0")/.."

# 清理构建目录
echo "🧹 清理构建目录..."
rm -rf build dist

# 安装构建工具
echo "📦 安装构建工具..."
python3 -m pip install --upgrade pip
pip3 install pyinstaller setuptools wheel

# 检测平台
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 检测到 Linux 平台"
    python3 packaging/build.py
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 检测到 macOS 平台"
    python3 packaging/build.py
else
    echo "❌ 不支持的平台: $OSTYPE"
    exit 1
fi

echo
echo "✅ 构建完成！"
echo "📁 输出目录: dist/"
echo