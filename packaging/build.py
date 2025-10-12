#!/usr/bin/env python3
"""
ImageTrim 多平台打包构建脚本

支持平台：
- Windows: .exe 单文件 + 安装程序
- macOS: .app 捆绑包 + .dmg 安装器
- Linux: AppImage + deb/rpm 包
"""

import os
import sys
import subprocess
import shutil
import platform
import json
from pathlib import Path
from datetime import datetime


class ImageTrimPackager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.version = "1.0.0"
        self.app_name = "ImageTrim"

    def clean_build(self):
        """清理构建目录"""
        print("清理构建目录...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)

    def install_pyinstaller(self):
        """安装PyInstaller"""
        print("📦 安装PyInstaller...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller>=6.0"
        ], check=True)

    def create_spec_file(self, platform):
        """创建PyInstaller规格文件"""
        print(f"🔧 创建 {platform} 平台规格文件...")

        if platform == "windows":
            spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['{self.root_dir}'],
    binaries=[],
    datas=[
        ('app/resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'scipy',
        'PyWavelets',
        'imagehash',
        'PIL',
        'requests',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/icons/imageTrim256px.ico',
    version='packaging/windows/version_info.txt',
)
"""
        elif platform == "macos":
            spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['{self.root_dir}'],
    binaries=[],
    datas=[
        ('app/resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'scipy',
        'PyWavelets',
        'imagehash',
        'PIL',
        'requests',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{self.app_name}',
)

app = BUNDLE(
    coll,
    name='{self.app_name}.app',
    icon='app/resources/icons/imageTrim256px.icns',
    bundle_identifier='com.imagetrim.app',
    version='{self.version}',
    info_plist={{
        'CFBundleDisplayName': 'ImageTrim',
        'CFBundleShortVersionString': '{self.version}',
        'CFBundleVersion': '{self.version}',
        'NSHighResolutionCapable': True,
    }},
)
"""
        else:  # linux
            spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['{self.root_dir}'],
    binaries=[],
    datas=[
        ('app/resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'scipy',
        'PyWavelets',
        'imagehash',
        'PIL',
        'requests',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/icons/imageTrim256px.png',
)
"""

        spec_file = self.root_dir / f"ImageTrim_{platform}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        return spec_file

    def build_windows(self):
        """构建Windows版本"""
        print("🪟 构建 Windows 版本...")

        # 创建版本信息文件
        version_info = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'BlueRainCoat'),
         StringStruct(u'FileDescription', u'ImageTrim - 图片精简工具'),
         StringStruct(u'FileVersion', u'{self.version}'),
         StringStruct(u'InternalName', u'ImageTrim'),
         StringStruct(u'LegalCopyright', u'Copyright © 2025 BlueRainCoat'),
         StringStruct(u'OriginalFilename', u'ImageTrim.exe'),
         StringStruct(u'ProductName', u'ImageTrim'),
         StringStruct(u'ProductVersion', u'{self.version}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

        version_file = self.root_dir / "packaging" / "windows" / "version_info.txt"
        version_file.parent.mkdir(exist_ok=True)
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)

        # 创建spec文件
        spec_file = self.create_spec_file("windows")

        # 构建exe
        subprocess.run([
            "pyinstaller", str(spec_file), "--clean", "--noconfirm"
        ], check=True)

        # 创建便携版zip
        self.create_portable_zip()

        # 创建安装程序
        self.create_installer()

    def build_macos(self):
        """构建macOS版本"""
        print("🍎 构建 macOS 版本...")

        # 转换图标格式
        self.convert_icon_to_icns()

        # 创建spec文件
        spec_file = self.create_spec_file("macos")

        # 构建app
        subprocess.run([
            "pyinstaller", str(spec_file), "--clean", "--noconfirm"
        ], check=True)

        # 创建dmg
        self.create_dmg()

    def build_linux(self):
        """构建Linux版本"""
        print("🐧 构建 Linux 版本...")

        # 创建spec文件
        spec_file = self.create_spec_file("linux")

        # 构建二进制文件
        subprocess.run([
            "pyinstaller", str(spec_file), "--clean", "--noconfirm"
        ], check=True)

        # 创建AppImage
        self.create_appimage()

        # 创建deb包
        self.create_deb_package()

    def create_portable_zip(self):
        """创建Windows便携版zip"""
        print("📦 创建便携版 ZIP...")

        portable_dir = self.build_dir / "portable"
        portable_dir.mkdir(exist_ok=True)

        # 复制exe和资源
        exe_path = self.dist_dir / "ImageTrim.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, portable_dir)

        # 复制readme
        readme_content = f"""ImageTrim {self.version} 便携版

现代化的图片去重和格式转换工具

功能特点：
• 智能图片去重，支持多种哈希算法
• 批量格式转换（AVIF, WEBP, JPEG, PNG）
• 现代化用户界面，支持深色主题
• 多线程处理，保持界面响应性
• 拖拽支持，操作简便

系统要求：
• Windows 10/11 64位
• 至少100MB可用空间
• 网络连接（用于在线图片下载）

使用方法：
1. 双击 ImageTrim.exe 启动程序
2. 无需安装，即用即走

版本：{self.version}
发布日期：{datetime.now().strftime('%Y-%m-%d')}
"""

        with open(portable_dir / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)

        # 创建zip
        zip_name = f"ImageTrim-{self.version}-windows-portable.zip"
        shutil.make_archive(
            self.dist_dir / zip_name.replace('.zip', ''),
            'zip',
            portable_dir.parent,
            "portable"
        )

    def create_installer(self):
        """创建Windows安装程序"""
        print("🔧 创建安装程序...")

        # 创建Inno Setup脚本
        iss_content = f"""[Setup]
AppName=ImageTrim
AppVersion={self.version}
DefaultDirName={{pf}}\\ImageTrim
DefaultGroupName=ImageTrim
OutputDir={self.dist_dir}
OutputBaseFilename=ImageTrim-{self.version}-installer
Compression=lzma
SolidCompression=yes
SetupIconFile=app\\resources\\icons\\imageTrim256px.ico
UninstallDisplayIcon={{app}}\\ImageTrim.exe
WizardImageFile=app\\resources\\icons\\imagetrim_final.svg
WizardSmallImageFile=app\\resources\\icons\\imageTrim256px.png

[Files]
Source: "{self.dist_dir}\\ImageTrim.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "app\\resources\\*"; DestDir: "{{app}}\\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\ImageTrim"; Filename: "{{app}}\\ImageTrim.exe"; IconFilename: "{{app}}\\resources\\icons\\imageTrim256px.ico"
Name: "{{autodesktop}}\\ImageTrim"; Filename: "{{app}}\\ImageTrim.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Run]
Filename: "{{app}}\\ImageTrim.exe"; Description: "{{cm:LaunchProgram,ImageTrim}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // 添加到PATH环境变量
    if not Exec('powershell.exe', '-Command "[Environment]::SetEnvironmentVariable(''PATH'', [Environment]::GetEnvironmentVariable(''PATH'', ''User'') + '';'' + ExpandConstant(''{{app}}''), ''User'')"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      // 处理错误
    end;
  end;
end;
"""

        iss_file = self.root_dir / "packaging" / "windows" / "installer.iss"
        with open(iss_file, 'w', encoding='utf-8') as f:
            f.write(iss_content)

        print("   请手动运行 Inno Setup 编译 installer.iss 文件")

    def convert_icon_to_icns(self):
        """转换图标为icns格式"""
        print("🎨 转换图标格式...")
        # 这里需要安装iconutil工具（macOS自带）
        icns_src = self.root_dir / "app" / "resources" / "icons"
        icns_dir = icns_src / "icon.iconset"
        icns_dir.mkdir(exist_ok=True)

        # 创建不同尺寸的图标（需要PIL支持）
        try:
            from PIL import Image

            icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
            for size in icon_sizes:
                img = Image.open(icns_src / "imageTrim256px.png")
                img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
                img_resized.save(icns_dir / f"icon_{size}x{size}.png")

            # 创建icns文件
            subprocess.run([
                "iconutil", "-c", "icns", "-o",
                icns_src / "imageTrim256px.icns",
                str(icns_dir)
            ], check=True)
        except ImportError:
            print("   警告：PIL未安装，跳过图标转换")

    def create_dmg(self):
        """创建macOS DMG安装包"""
        print("💿 创建 DMG 安装包...")
        app_path = self.dist_dir / "ImageTrim.app"

        if app_path.exists():
            dmg_name = f"ImageTrim-{self.version}-macos.dmg"
            dmg_path = self.dist_dir / dmg_name

            # 使用create-dmg工具
            try:
                subprocess.run([
                    "create-dmg",
                    "--volname", f"ImageTrim {self.version}",
                    "--volicon", "app/resources/icons/imageTrim256px.icns",
                    "--window-pos", "200", "120",
                    "--window-size", "600", "300",
                    "--icon-size", "100",
                    "--icon", "ImageTrim.app", "175", "120",
                    "--app-drop-link", "425", "120",
                    str(dmg_path),
                    str(app_path.parent)
                ], check=True)
            except FileNotFoundError:
                print("   请安装 create-dmg: brew install create-dmg")

    def create_appimage(self):
        """创建Linux AppImage"""
        print("📦 创建 AppImage...")

        app_dir = self.build_dir / "ImageTrim.AppDir"
        app_dir.mkdir(parents=True, exist_ok=True)

        # 复制二进制文件
        bin_path = self.dist_dir / "ImageTrim"
        if bin_path.exists():
            shutil.copy2(bin_path, app_dir / "usr" / "bin" / "ImageTrim")

        # 创建桌面文件
        desktop_content = f"""[Desktop Entry]
Name=ImageTrim
Comment=现代化的图片去重和格式转换工具
Exec=ImageTrim
Icon=imagetrim
Terminal=false
Type=Application
Categories=Graphics;Photography;
Version={self.version}
"""

        with open(app_dir / "usr" / "share" / "applications" / "imagetrim.desktop", 'w') as f:
            f.write(desktop_content)

        # 复制图标
        icon_src = self.root_dir / "app" / "resources" / "icons" / "imageTrim256px.png"
        if icon_src.exists():
            shutil.copy2(icon_src, app_dir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "imagetrim.png")

        # 下载并使用appimagetool
        print("   请安装 appimagetool 并手动创建 AppImage")

    def create_deb_package(self):
        """创建Debian/Ubuntu包"""
        print("📦 创建 DEB 包...")

        debian_dir = self.build_dir / "debian"
        debian_dir.mkdir(parents=True, exist_ok=True)

        # 创建control文件
        control_content = f"""Package: imagetrim
Version: {self.version}
Section: graphics
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6, python3-pil, python3-requests, python3-numpy, python3-scipy, python3-pywavelets, python3-imagehash
Maintainer: BlueRainCoat <blueraincoatli@example.com>
Description: 现代化的图片去重和格式转换工具
 ImageTrim是一个现代化的图片处理工具，支持智能去重和批量格式转换。
 特点：
  * 基于图像哈希的智能去重算法
  * 支持AVIF、WEBP、JPEG、PNG等格式转换
  * 现代化的PyQt6用户界面
  * 多线程处理，保持界面响应性
  * 简单易用的拖拽操作
"""

        with open(debian_dir / "control", 'w') as f:
            f.write(control_content)

        # 创建其他debian文件
        print("   请使用 dpkg-buildpackage 或 debhelper 创建 DEB 包")


def main():
    packager = ImageTrimPackager()

    # 清理构建目录
    packager.clean_build()

    # 安装PyInstaller
    packager.install_pyinstaller()

    # 根据当前平台构建
    current_platform = platform.system().lower()

    if current_platform == "windows":
        packager.build_windows()
    elif current_platform == "darwin":
        packager.build_macos()
    elif current_platform == "linux":
        packager.build_linux()
    else:
        print(f"❌ 不支持的平台: {current_platform}")
        sys.exit(1)

    print("✅ 构建完成！")
    print(f"📁 输出目录: {packager.dist_dir}")


if __name__ == "__main__":
    main()