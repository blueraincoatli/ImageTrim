# ImageTrim 打包指南

本目录包含 ImageTrim 的多平台打包配置和脚本。

## 📁 目录结构

```
packaging/
├── build.py              # 完整的打包构建脚本
├── build_simple.py       # 简化版打包脚本（推荐）
├── build.bat             # Windows 批处理构建脚本
├── build.sh              # Linux/macOS Shell 构建脚本
├── create_installer.bat   # Windows 安装程序创建脚本
├── README.md             # 本文件
├── windows/              # Windows 特定配置
│   ├── installer.iss     # Inno Setup 安装程序脚本
│   ├── preinstall.txt    # 安装前说明
│   ├── postinstall.txt   # 安装后说明
│   └── version_info.txt  # 版本信息文件
└── linux/                # Linux 特定配置
    ├── imagetrim.desktop # 桌面文件
    └── imagetrim.metainfo.xml  # AppStream 元数据
```

## 🚀 快速开始

### Windows 平台

#### 1. 构建可执行文件
```bash
# 使用简化脚本（推荐）
python packaging/build_simple.py

# 或使用批处理脚本
packaging\build.bat
```

#### 2. 创建安装程序
```bash
# 需要 Inno Setup
packaging\create_installer.bat
```

#### 3. 输出文件
构建完成后，在 `dist/` 目录中找到：
- `ImageTrim.exe` - 单文件可执行程序
- `ImageTrim-1.0.0-windows-portable.zip` - 便携版
- `ImageTrim-1.0.0-installer.exe` - 安装程序

### Linux 平台

```bash
# 给脚本执行权限
chmod +x packaging/build.sh

# 构建应用
./packaging/build.sh
```

### macOS 平台

```bash
# 构建应用
./packaging/build.sh
```

## 📋 系统要求

### 开发环境
- Python 3.12+
- PyQt6 6.9.1+
- 所有项目依赖（见 requirements.txt）

### 构建工具
- **PyInstaller**: 用于打包可执行文件
- **Inno Setup** (Windows): 用于创建安装程序
- **create-dmg** (macOS): 用于创建 DMG 安装包
- **appimagetool** (Linux): 用于创建 AppImage

## 🔧 自定义配置

### 修改应用信息
编辑 `pyproject.toml` 文件：
```toml
[project]
name = "ImageTrim"
version = "1.0.0"
description = "现代化的图片去重和格式转换工具"
```

### 添加依赖
编辑 `pyproject.toml` 文件的 `dependencies` 部分：
```toml
dependencies = [
    "PyQt6>=6.9.1",
    "Pillow>=11.3.0",
    # 添加更多依赖...
]
```

### 修改图标
替换 `app/resources/icons/` 目录中的图标文件：
- `imageTrim256px.ico` - Windows 图标
- `imageTrim256px.icns` - macOS 图标
- `imageTrim256px.png` - Linux 图标

## 📦 打包选项

### Windows
- **单文件模式**: 所有文件打包成单个 EXE
- **目录模式**: 分离文件，启动更快
- **便携版**: 无需安装的 ZIP 压缩包
- **安装程序**: 标准 Windows 安装程序

### Linux
- **AppImage**: 通用 Linux 可执行文件
- **DEB 包**: Debian/Ubuntu 软件包
- **RPM 包**: Red Hat/Fedora 软件包
- **Flatpak**: 沙盒化应用

### macOS
- **App Bundle**: 标准 macOS 应用包
- **DMG**: 磁盘映像安装包
- **PKG**: 安装程序包

## 🐛 故障排除

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'PyQt6'
```
**解决方案**: 确保在正确的虚拟环境中运行打包脚本

#### 2. 图标缺失
**解决方案**: 检查图标文件路径是否正确

#### 3. 依赖问题
**解决方案**: 使用 `--hidden-import` 参数添加缺失的模块

#### 4. 编码问题
**解决方案**: 使用 `build_simple.py` 避免Unicode编码问题

### 调试技巧

#### 1. 使用控制台模式
修改打包脚本，移除 `--windowed` 参数以查看控制台输出

#### 2. 检查依赖
使用 `pip freeze` 检查已安装的包

#### 3. 测试构建结果
在不同的环境中测试生成的可执行文件

## 🔄 持续集成

可以配置 GitHub Actions 自动化构建：

```yaml
name: Build Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install pyinstaller

    - name: Build
      run: python packaging/build_simple.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
```

## 📝 更新日志

### v1.0.0
- 初始发布版本
- 支持图片去重和格式转换
- 现代化 PyQt6 界面
- 多平台打包支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进打包系统！

## 📄 许可证

MIT License - 详见项目根目录的 LICENSE 文件。