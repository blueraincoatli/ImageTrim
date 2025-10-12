#!/usr/bin/env python3
"""
跨平台打包脚本 - 支持Windows、macOS、Linux
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# 项目配置
PROJECT_NAME = "ImageTrim"
MAIN_SCRIPT = "app/main.py"
ICON_FILE = "app/resources/icons/imagetrim.ico"
VERSION = "1.0.0"

def check_requirements():
    """检查必要的依赖"""
    print("🔍 检查打包依赖...")

    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 安装完成")

def get_platform_specific_config():
    """获取平台特定的配置"""
    current_platform = platform.system().lower()

    if current_platform == "windows":
        return {
            "icon": ICON_FILE if os.path.exists(ICON_FILE) else None,
            "name": f"{PROJECT_NAME}.exe",
            "windowed": True,
            "additional_args": [
                "--add-data", "app/resources;resources",
                "--hidden-import", "PyQt6.QtCore",
                "--hidden-import", "PyQt6.QtGui",
                "--hidden-import", "PyQt6.QtWidgets",
                "--collect-all", "PIL",
                "--exclude-module", "tkinter",
                "--exclude-module", "matplotlib",
                "--exclude-module", "numpy.testing",
                "--exclude-module", "scipy.tests"
            ]
        }
    elif current_platform == "darwin":  # macOS
        # macOS 使用 .icns 格式图标
        mac_icon = "app/resources/icons/imagetrim.icns"
        return {
            "icon": mac_icon if os.path.exists(mac_icon) else None,
            "name": PROJECT_NAME,
            "windowed": True,
            "additional_args": [
                "--add-data", "app/resources:resources",
                "--hidden-import", "PyQt6.QtCore",
                "--hidden-import", "PyQt6.QtGui",
                "--hidden-import", "PyQt6.QtWidgets",
                "--collect-all", "PIL",
                "--exclude-module", "tkinter",
                "--exclude-module", "matplotlib",
                "--exclude-module", "numpy.testing",
                "--exclude-module", "scipy.tests",
                "--osx-bundle-identifier", f"com.imagetrim.{PROJECT_NAME.lower()}"
            ]
        }
    elif current_platform == "linux":
        return {
            "icon": ICON_FILE if os.path.exists(ICON_FILE) else None,
            "name": PROJECT_NAME.lower(),
            "windowed": True,
            "additional_args": [
                "--add-data", "app/resources:resources",
                "--hidden-import", "PyQt6.QtCore",
                "--hidden-import", "PyQt6.QtGui",
                "--hidden-import", "PyQt6.QtWidgets",
                "--collect-all", "PIL",
                "--exclude-module", "tkinter",
                "--exclude-module", "matplotlib",
                "--exclude-module", "numpy.testing",
                "--exclude-module", "scipy.tests"
            ]
        }
    else:
        raise ValueError(f"不支持的平台: {current_platform}")

def create_build_dirs():
    """创建构建目录"""
    dirs_to_create = [
        "build",
        "dist",
        "build/macos",
        "build/linux"
    ]

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def create_macos_plist():
    """创建macOS Info.plist文件"""
    if platform.system().lower() != "darwin":
        return

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{PROJECT_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>{PROJECT_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.imagetrim.{PROJECT_NAME.lower()}</string>
    <key>CFBundleVersion</key>
    <string>{VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>{VERSION}</string>
    <key>CFBundleExecutable</key>
    <string>{PROJECT_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>imagetrim.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>jpg</string>
                <string>jpeg</string>
                <string>png</string>
                <string>webp</string>
                <string>avif</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Image File</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
</dict>
</plist>"""

    plist_path = Path("build/macos/Info.plist")
    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist_content)
    print("✅ macOS Info.plist 已创建")

def create_linux_desktop():
    """创建Linux .desktop文件"""
    if platform.system().lower() != "linux":
        return

    desktop_content = f"""[Desktop Entry]
Name={PROJECT_NAME}
Name[zh_CN]=图片去重工具
Comment=Image deduplication and conversion tool
Comment[zh_CN]=图片去重和格式转换工具
Exec={PROJECT_NAME.lower()}
Icon={PROJECT_NAME.lower()}
Terminal=false
Type=Application
Categories=Graphics;Photography;
MimeType=image/jpeg;image/png;image/webp;image/avif;
StartupWMClass={PROJECT_NAME}
"""

    desktop_path = Path("build/linux/imagetrim.desktop")
    with open(desktop_path, "w", encoding="utf-8") as f:
        f.write(desktop_content)
    print("✅ Linux .desktop 文件已创建")

def build_app():
    """构建应用程序"""
    current_platform = platform.system().lower()
    config = get_platform_specific_config()

    print(f"🚀 开始为 {current_platform.upper()} 构建应用程序...")

    # 创建构建目录
    create_build_dirs()

    # 创建平台特定文件
    if current_platform == "darwin":
        create_macos_plist()
    elif current_platform == "linux":
        create_linux_desktop()

    # 构建 PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--name", config["name"],
        "--onefile"
    ]

    if config["icon"]:
        cmd.extend(["--icon", config["icon"]])

    if config["windowed"]:
        cmd.append("--windowed")

    cmd.extend(config["additional_args"])
    cmd.append(MAIN_SCRIPT)

    print(f"📦 执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")

        # 显示输出文件信息
        dist_dir = Path("dist")
        output_files = list(dist_dir.glob("*"))
        print(f"📁 输出文件:")
        for file_path in output_files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   - {file_path.name} ({size_mb:.1f} MB)")

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        sys.exit(1)

def create_archives():
    """创建发布归档文件"""
    current_platform = platform.system().lower()
    platform_name = {
        "windows": "win",
        "darwin": "macos",
        "linux": "linux"
    }.get(current_platform, current_platform)

    dist_dir = Path("dist")
    archives_dir = Path("archives")
    archives_dir.mkdir(exist_ok=True)

    print(f"📦 创建发布归档...")

    for file_path in dist_dir.glob("*"):
        if file_path.is_file():
            archive_name = f"{PROJECT_NAME}-{VERSION}-{platform_name}"

            if current_platform == "windows":
                # Windows 创建 ZIP
                archive_path = archives_dir / f"{archive_name}.zip"
                shutil.make_archive(
                    str(archive_path.with_suffix("")),
                    "zip",
                    str(file_path.parent),
                    file_path.name
                )
            else:
                # macOS 和 Linux 创建 tar.gz
                archive_path = archives_dir / f"{archive_name}.tar.gz"
                with shutil.make_archive(
                    str(archive_path.with_suffix("")),
                    "gztar",
                    str(file_path.parent),
                    file_path.name
                ) as tar_path:
                    pass

            # 显示归档信息
            size_mb = archive_path.stat().st_size / (1024 * 1024)
            print(f"✅ 归档创建: {archive_path.name} ({size_mb:.1f} MB)")

def main():
    print(f"🔧 {PROJECT_NAME} 跨平台打包工具 v{VERSION}")
    print(f"🖥️  当前平台: {platform.system()}")
    print("=" * 50)

    # 检查依赖
    check_requirements()

    # 构建应用
    build_app()

    # 创建归档
    create_archives()

    print("=" * 50)
    print("🎉 打包完成!")
    print(f"📁 输出目录: dist/")
    print(f"📦 归档目录: archives/")

if __name__ == "__main__":
    main()