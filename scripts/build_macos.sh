#!/bin/bash
# macOS 构建脚本（使用 uv 虚拟环境）

set -e  # 遇到错误时退出

echo "🍎 ImageTrim macOS 构建脚本 (uv)"
echo "============================"

# 检查是否在 macOS 上运行
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误: 此脚本只能在 macOS 上运行"
    exit 1
fi

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "📦 安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
uv python --version

# 安装系统依赖
echo "📦 检查系统依赖..."
if ! command -v brew &> /dev/null; then
    echo "💡 建议安装 Homebrew 来管理系统依赖"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
fi

# 使用 uv 创建和管理虚拟环境
echo "🔧 使用 uv 管理虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 安装 Python 依赖..."
uv pip install --upgrade pip
uv pip install -r requirements.txt
uv pip install pyinstaller

# 安装图标转换工具（如果需要）
if [ ! -f "app/resources/icons/imagetrim.icns" ] && [ -f "app/resources/icons/imagetrim.png" ]; then
    echo "🎨 转换图标格式..."
    if command -v sips &> /dev/null; then
        # 使用 sips 创建不同尺寸的图标
        mkdir -p app/resources/icons/icon.iconset
        sips -z 16 16 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_16x16.png 2>/dev/null || true
        sips -z 32 32 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_16x16@2x.png 2>/dev/null || true
        sips -z 32 32 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_32x32.png 2>/dev/null || true
        sips -z 64 64 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_32x32@2x.png 2>/dev/null || true
        sips -z 128 128 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_128x128.png 2>/dev/null || true
        sips -z 256 256 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_128x128@2x.png 2>/dev/null || true
        sips -z 256 256 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_256x256.png 2>/dev/null || true
        sips -z 512 512 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_256x256@2x.png 2>/dev/null || true
        sips -z 512 512 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_512x512.png 2>/dev/null || true
        sips -z 1024 1024 app/resources/icons/imagetrim.png --out app/resources/icons/icon.iconset/icon_512x512@2x.png 2>/dev/null || true

        # 创建 icns 文件
        if command -v iconutil &> /dev/null; then
            iconutil -c icns app/resources/icons/icon.iconset -o app/resources/icons/imagetrim.icns
            echo "✅ 图标转换完成: app/resources/icons/imagetrim.icns"
        else
            echo "⚠️  iconutil 未找到，跳过图标转换"
        fi
    else
        echo "⚠️  sips 未找到，跳过图标转换"
    fi
fi

# 运行跨平台构建脚本
echo "🚀 开始构建..."
python build_cross_platform.py

# 创建 DMG 安装包（可选）
if [ -f "dist/ImageTrim.app" ]; then
    echo "📦 创建 DMG 安装包..."

    # 创建临时目录
    mkdir -p dmg_temp

    # 复制应用到临时目录
    cp -R "dist/ImageTrim.app" dmg_temp/

    # 创建应用程序文件夹链接
    ln -s /Applications dmg_temp/Applications

    # 创建 DMG
    if command -v hdiutil &> /dev/null; then
        hdiutil create -volname "ImageTrim" -srcfolder dmg_temp -ov -format UDZO "archives/ImageTrim-1.0.0-macos.dmg"
        echo "✅ DMG 安装包创建完成: archives/ImageTrim-1.0.0-macos.dmg"
    else
        echo "⚠️  hdiutil 未找到，跳过 DMG 创建"
    fi

    # 清理临时目录
    rm -rf dmg_temp
fi

echo "============================"
echo "🎉 macOS 构建完成!"
echo "📁 输出文件位置:"
if [ -f "dist/ImageTrim.app" ]; then
    echo "   - 应用程序: dist/ImageTrim.app"
fi
echo "   - 归档文件: archives/"
echo ""
echo "💡 使用 uv 的优势:"
echo "   - 更快的依赖安装"
echo "   - 更好的依赖解析"
echo "   - 更小的虚拟环境"