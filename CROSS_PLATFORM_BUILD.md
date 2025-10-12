# ImageTrim 跨平台打包指南

本指南帮助您将 ImageTrim 项目打包为 Windows、macOS 和 Linux 平台的可执行文件。

## 📋 系统要求

### 通用要求
- Python 3.8+
- uv (推荐) 或 pip
- 网络连接（用于下载依赖）

### 平台特定要求

#### Windows
- Windows 10 或更高版本
- Microsoft Visual C++ Redistributable

#### macOS
- macOS 10.14 或更高版本
- Xcode Command Line Tools
- Homebrew（推荐）

#### Linux
- 支持的发行版：Ubuntu 18.04+, CentOS 7+, Fedora 30+, Arch Linux
- 图形界面环境（X11 或 Wayland）

## 🚀 快速开始

### 1. 安装 uv（推荐）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 使用预配置脚本

#### macOS
```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

#### Linux
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

#### Windows
```cmd
python build_cross_platform.py
```

## 🔧 手动构建步骤

### 1. 准备环境

```bash
# 克隆项目
git clone https://github.com/blueraincoatli/DeDupImg.git
cd DeDupImg

# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. 安装依赖

```bash
# 安装项目依赖
uv pip install -r requirements.txt

# 安装打包工具
uv pip install pyinstaller
```

### 3. 运行构建脚本

```bash
# 跨平台构建
python build_cross_platform.py
```

## 📦 输出文件

构建完成后，您将在以下目录找到输出文件：

### Windows
- `dist/ImageTrim.exe` - 可执行文件
- `archives/ImageTrim-1.0.0-win.zip` - 压缩包

### macOS
- `dist/ImageTrim.app` - 应用程序包
- `archives/ImageTrim-1.0.0-macos.tar.gz` - 压缩包
- `archives/ImageTrim-1.0.0-macos.dmg` - DMG 安装包（可选）

### Linux
- `dist/imagetrim` - 可执行文件
- `archives/ImageTrim-1.0.0-linux.tar.gz` - 压缩包
- `archives/ImageTrim-1.0.0-linux.AppImage` - AppImage（可选）
- `archives/ImageTrim-1.0.0-linux.deb` - Debian 包（可选）

## 🎨 自定义图标

### 准备图标文件

1. **Windows ICO**：`app/resources/icons/imagetrim.ico` (256x256 像素)
2. **macOS ICNS**：`app/resources/icons/imagetrim.icns` (多尺寸)
3. **Linux PNG**：`app/resources/icons/imagetrim.png` (256x256 像素)

### 图标转换工具

#### macOS 图标转换
```bash
# 使用 sips 创建多尺寸图标
mkdir -p app/resources/icons/icon.iconset
sips -z 16 16 imagetrim.png --out app/resources/icons/icon.iconset/icon_16x16.png
sips -z 32 32 imagetrim.png --out app/resources/icons/icon.iconset/icon_32x32.png
# ... 其他尺寸

# 创建 ICNS 文件
iconutil -c icns app/resources/icons/icon.iconset -o app/resources/icons/imagetrim.icns
```

#### Linux 图标转换
```bash
# 使用 convert 命令（ImageMagick）
convert imagetrim.png -resize 256x256 app/resources/icons/imagetrim.png
```

## ⚙️ 构建配置

### PyInstaller 选项

主要配置文件：`build_cross_platform.py`

```python
# 关键配置选项
config = {
    "name": "ImageTrim",
    "icon": "app/resources/icons/imagetrim.ico",
    "windowed": True,  # 无控制台窗口
    "onefile": True,   # 单文件模式
    "additional_args": [
        "--add-data", "app/resources:resources",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--collect-all", "PIL",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib"
    ]
}
```

### 优化选项

#### 减少文件大小
```bash
# 启用 UPX 压缩
pyinstaller --upx-dir=/path/to/upx ...

# 排除不需要的模块
--exclude-module numpy.testing
--exclude-module scipy.tests
--exclude-module matplotlib
```

#### 提高启动速度
```bash
# 使用目录模式（调试用）
--onedir

# 优化导入
--optimize 2
```

## 🐛 故障排除

### 常见问题

#### 1. PyQt6 导入错误
```bash
# 解决方案：明确指定 PyQt6 模块
--hidden-import PyQt6.QtCore
--hidden-import PyQt6.QtGui
--hidden-import PyQt6.QtWidgets
```

#### 2. PIL/Pillow 图像处理问题
```bash
# 解决方案：收集所有 PIL 模块
--collect-all PIL
--hidden-import PIL.Image
--hidden-import PIL.ImageTk
```

#### 3. 资源文件找不到
```bash
# 解决方案：正确添加资源文件
--add-data "app/resources;resources"  # Windows
--add-data "app/resources:resources"  # macOS/Linux
```

#### 4. Linux 字体问题
```bash
# 安装字体包
sudo apt-get install fonts-liberation fonts-dejavu-core

# 或在代码中指定字体路径
```

#### 5. macOS 公证问题
```bash
# 对应用程序进行公证
codesign --force --deep --sign "Developer ID Application: Your Name" ImageTrim.app
xcrun altool --notarize-app --primary-bundle-id "com.imagetrim.app" \
             --username "your@email.com" --password "@keychain:AC_PASSWORD" \
             --file ImageTrim.app.zip
```

### 调试技巧

#### 1. 使用单文件模式调试
```bash
# 临时使用目录模式获取更多错误信息
pyinstaller --onedir --debug all app/main.py
```

#### 2. 检查导入依赖
```bash
# 分析导入依赖
pyi-archive_viewer dist/imagetrim
```

#### 3. 查看详细日志
```bash
# 启用详细输出
pyinstaller --log-level DEBUG ...
```

## 📋 部署清单

### 发布前检查

- [ ] 测试所有目标平台
- [ ] 验证图标显示正确
- [ ] 检查文件路径处理
- [ ] 测试图片格式支持
- [ ] 确认字体渲染正常
- [ ] 验证权限设置

### 各平台特定检查

#### Windows
- [ ] 测试 Windows 10/11
- [ ] 检查防病毒软件兼容性
- [ ] 验证安装包数字签名

#### macOS
- [ ] 测试最新版本 macOS
- [ ] 检查 Gatekeeper 设置
- [ ] 验证沙盒权限
- [ ] 测试 Retina 显示器

#### Linux
- [ ] 测试主流发行版
- [ ] 检查依赖库兼容性
- [ ] 验证桌面集成
- [ ] 测试不同显示服务器

## 🔄 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Build Multi-Platform

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    runs-on: ${{ matrix.os }}

    steps:
    - uses: actions/checkout@v3

    - name: Install uv
      uses: astral-sh/setup-uv@v1

    - name: Build
      run: python build_cross_platform.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.os }}-build
        path: archives/
```

## 📚 参考资源

- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [PyQt6 部署指南](https://www.riverbankcomputing.com/static/Docs/PyQt6/deployment.html)
- [macOS 应用分发指南](https://developer.apple.com/distribute/applications/)
- [Linux AppImage 官网](https://appimage.org/)

## 💡 提示和最佳实践

1. **使用 uv**：比传统 pip 更快、更可靠
2. **测试所有平台**：在真实环境中测试构建的应用
3. **版本控制**：为每个平台版本创建独立的标签
4. **文档更新**：保持构建文档与实际脚本同步
5. **自动化**：使用 CI/CD 自动化构建过程

## 🆘 获取帮助

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的 GitHub Issues
3. 在相应的平台社区寻求帮助
4. 查看官方文档获取最新信息

---

**注意**：构建过程可能需要一些时间，特别是在首次构建时。请耐心等待，并确保网络连接稳定。