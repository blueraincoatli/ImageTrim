#!/bin/bash
# Linux 构建脚本（使用 uv 虚拟环境）

set -e  # 遇到错误时退出

echo "🐧 ImageTrim Linux 构建脚本 (uv)"
echo "=========================="

# 检查是否在 Linux 上运行
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 错误: 此脚本只能在 Linux 上运行"
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

# 检查系统包管理器
if command -v apt-get &> /dev/null; then
    PACKAGE_MANAGER="apt-get"
    INSTALL_CMD="sudo apt-get update && sudo apt-get install -y"
elif command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
    INSTALL_CMD="sudo yum install -y"
elif command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
    INSTALL_CMD="sudo dnf install -y"
elif command -v pacman &> /dev/null; then
    PACKAGE_MANAGER="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
else
    echo "⚠️  未识别的包管理器，请手动安装以下依赖:"
    echo "   - python3-tk"
    echo "   - python3-dev"
    echo "   - libgl1-mesa-glx"
    echo "   - libglib2.0-0"
    echo "   - libsm6"
    echo "   - libxext6"
    echo "   - libxrender-dev"
    echo "   - libgomp1"
fi

# 安装系统依赖
if [ -n "$PACKAGE_MANAGER" ]; then
    echo "📦 安装系统依赖..."
    case $PACKAGE_MANAGER in
        "apt-get")
            $INSTALL_CMD python3-tk python3-dev libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libxcb-xinerama0
            ;;
        "yum"|"dnf")
            $INSTALL_CMD python3-tkinter python3-devel mesa-libGL glib2 libSM libXext libXrender libgomp
            ;;
        "pacman")
            $INSTALL_CMD tk python libgl glib2 libsm libxext libxrender libgomp
            ;;
    esac
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

# 创建 .desktop 文件图标目录
mkdir -p ~/.local/share/icons
mkdir -p ~/.local/share/applications

# 复制图标（如果存在）
if [ -f "app/resources/icons/imagetrim.png" ]; then
    cp app/resources/icons/imagetrim.png ~/.local/share/icons/imagetrim.png
    echo "✅ 图标已安装到 ~/.local/share/icons/imagetrim.png"
fi

# 运行跨平台构建脚本
echo "🚀 开始构建..."
python build_cross_platform.py

# 创建 AppImage（可选）
if [ -f "dist/imagetrim" ]; then
    echo "📦 创建 AppImage..."

    # 安装 appimagetool（如果需要）
    if ! command -v appimagetool &> /dev/null; then
        echo "📦 下载 appimagetool..."
        wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
        chmod +x appimagetool
    fi

    # 创建 AppDir
    mkdir -p ImageTrim.AppDir/usr/bin
    mkdir -p ImageTrim.AppDir/usr/share/applications
    mkdir -p ImageTrim.AppDir/usr/share/icons/hicolor/256x256/apps

    # 复制可执行文件
    cp dist/imagetrim ImageTrim.AppDir/usr/bin/

    # 复制 .desktop 文件
    cp build/linux/imagetrim.desktop ImageTrim.AppDir/usr/share/applications/

    # 复制图标
    if [ -f "app/resources/icons/imagetrim.png" ]; then
        cp app/resources/icons/imagetrim.png ImageTrim.AppDir/usr/share/icons/hicolor/256x256/apps/imagetrim.png
    fi

    # 创建 AppRun
    cat > ImageTrim.AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${HERE}/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/imagetrim" "$@"
EOF
    chmod +x ImageTrim.AppDir/AppRun

    # 创建 AppImage
    if [ -f "appimagetool" ]; then
        ./appimagetool ImageTrim.AppDir "archives/ImageTrim-1.0.0-linux.AppImage"
        echo "✅ AppImage 创建完成: archives/ImageTrim-1.0.0-linux.AppImage"
    fi

    # 清理
    rm -rf ImageTrim.AppDir
fi

# 创建 Debian/Ubuntu 包（可选）
if command -v dpkg-deb &> /dev/null && [ -f "dist/imagetrim" ]; then
    echo "📦 创建 Debian 包..."

    # 创建包目录结构
    mkdir -p imagetrim-deb/DEBIAN
    mkdir -p imagetrim-deb/usr/bin
    mkdir -p imagetrim-deb/usr/share/applications
    mkdir -p imagetrim-deb/usr/share/icons/hicolor/256x256/apps

    # 复制文件
    cp dist/imagetrim imagetrim-deb/usr/bin/
    cp build/linux/imagetrim.desktop imagetrim-deb/usr/share/applications/

    if [ -f "app/resources/icons/imagetrim.png" ]; then
        cp app/resources/icons/imagetrim.png imagetrim-deb/usr/share/icons/hicolor/256x256/apps/imagetrim.png
    fi

    # 创建 control 文件
    cat > imagetrim-deb/DEBIAN/control << EOF
Package: imagetrim
Version: 1.0.0
Section: graphics
Priority: optional
Architecture: amd64
Depends: libgl1, libglib2.0-0, libsm6, libxext6, libxrender1, libgomp1
Maintainer: ImageTrim Team
Description: Image deduplication and conversion tool
 A modern GUI tool for image deduplication and format conversion.
 Supports JPEG, PNG, WebP, and AVIF formats with an intuitive interface.
EOF

    # 计算 Installed-Size
    INSTALLED_SIZE=$(du -s imagetrim-deb | cut -f1)
    echo "Installed-Size: $INSTALLED_SIZE" >> imagetrim-deb/DEBIAN/control

    # 构建 .deb 包
    dpkg-deb --build imagetrim-deb "archives/ImageTrim-1.0.0-linux.deb"
    echo "✅ Debian 包创建完成: archives/ImageTrim-1.0.0-linux.deb"

    # 清理
    rm -rf imagetrim-deb
fi

echo "=========================="
echo "🎉 Linux 构建完成!"
echo "📁 输出文件位置:"
if [ -f "dist/imagetrim" ]; then
    echo "   - 可执行文件: dist/imagetrim"
fi
echo "   - 归档文件: archives/"
if [ -f "archives/ImageTrim-1.0.0-linux.AppImage" ]; then
    echo "   - AppImage: archives/ImageTrim-1.0.0-linux.AppImage"
fi
if [ -f "archives/ImageTrim-1.0.0-linux.deb" ]; then
    echo "   - Debian 包: archives/ImageTrim-1.0.0-linux.deb"
fi
echo ""
echo "💡 安装说明:"
echo "   - 直接运行: ./dist/imagetrim"
echo "   - AppImage: 下载后 chmod +x && ./ImageTrim-1.0.0-linux.AppImage"
echo "   - Debian:   sudo dpkg -i ImageTrim-1.0.0-linux.deb"
echo ""
echo "💡 使用 uv 的优势:"
echo "   - 更快的依赖安装"
echo "   - 更好的依赖解析"
echo "   - 更小的虚拟环境"