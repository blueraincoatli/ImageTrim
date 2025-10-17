# ImageTrim - 图片去重与格式转换工具

<div align="center">

![ImageTrim Logo](https://img.shields.io/badge/ImageTrim-v1.2.5-blue)
![Platform](https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Size](https://img.shields.io/badge/大小-40--70MB-orange)

**一款专业的图片去重与格式转换工具，支持批量处理和多格式转换**

[下载页面](https://github.com/blueraincoatli/ImageTrim/releases) • [使用指南](#使用指南) • [功能介绍](#主要功能)

</div>

## ✨ 主要功能

### 🔍 图片去重
- **智能相似度检测**: 使用先进的图像哈希算法检测相似和重复图片
- **可调节相似度阈值**: 支持1%-100%的相似度设置
- **批量扫描**: 支持多目录同时扫描，可选择包含子目录
- **可视化结果**: 直观显示重复图片组，支持预览和对比
- **拖拽操作**: 支持直接拖拽文件夹到程序中

### 🔄 格式转换
- **多格式支持**: AVIF、WEBP、JPEG、PNG格式互转
- **质量调节**: 1%-100%可调节输出质量
- **批量转换**: 支持整个文件夹的批量转换
- **保持目录结构**: 转换后保持原有的目录层次
- **实时进度**: 显示转换进度和详细信息

### 🎨 界面特色
- **现代化深色主题**: 专业的深色界面，护眼且美观
- **响应式设计**: 自适应不同屏幕尺寸
- **多线程处理**: 后台处理，界面流畅不卡顿
- **实时日志**: 详细的操作日志和进度显示

## 📥 下载

### 最新版本 v1.2.5 (优化版)

| 平台 | 文件名 | 大小 | 说明 |
|------|--------|------|------|
| Windows | `ImageTrim-Windows.exe` | ~40-60MB | Windows可执行文件 |
| macOS | `ImageTrim-macOS.app` | ~40-60MB | macOS应用程序包 |
| Linux | `ImageTrim-Linux` | ~71MB | Linux可执行文件 |
| Linux | `ImageTrim-Linux-AppImage.AppImage` | ~71MB | Linux便携版 |

**[📦 点击这里下载最新版本](https://github.com/blueraincoatli/ImageTrim/releases/latest)**

> 💡 提示：点击上方链接将自动跳转到最新版本的下载页面

## 🚀 快速开始

### Windows
1. 下载 `ImageTrim-Windows.exe`
2. 双击运行即可使用

### macOS
1. 下载 `ImageTrim-macOS.app`
2. 双击运行或在Finder中打开

### Linux
```bash
# 下载并运行
chmod +x ImageTrim-Linux
./ImageTrim-Linux

# 或者使用AppImage版本
chmod +x ImageTrim-Linux-AppImage.AppImage
./ImageTrim-Linux-AppImage.AppImage
```

## 📖 使用指南

### 🎬 快速演示

#### 启动程序
![启动程序演示](ImagTrimIntro/start_cut.avif)

*程序启动和主界面展示*

---

### 图片去重使用方法

1. **添加扫描路径**
   - 点击"添加路径..."按钮选择文件夹
   - 或直接拖拽文件夹到程序中

2. **设置相似度**
   - 调整相似度阈值（推荐95%）
   - 选择是否包含子目录

3. **开始扫描**
   - 点击"开始扫描"按钮
   - 等待扫描完成

4. **处理结果**
   - 查看找到的重复图片组
   - 选择保留或删除重复文件

#### 📺 去重功能演示

**演示 1：基本去重操作**

![去重演示1](ImagTrimIntro/result01.avif)

*展示如何扫描和识别重复图片*

**演示 2：批量处理重复文件**

![去重演示2](ImagTrimIntro/result02.avif)

*展示如何处理和删除重复图片*

---

### 格式转换使用方法

1. **设置路径**
   - 选择源文件夹（要转换的图片）
   - 选择目标文件夹（转换后的图片）

2. **转换设置**
   - 选择输出格式（AVIF/WEBP/JPEG/PNG）
   - 调整质量参数（推荐85%）
   - 选择是否包含子目录

3. **开始转换**
   - 点击"开始转换"按钮
   - 监控转换进度

#### 📺 格式转换演示

![转换为AVIF格式演示](ImagTrimIntro/toAvif.avif)

*展示如何将图片批量转换为AVIF格式*

## 💡 使用技巧

### 去重技巧
- **保守设置**: 相似度设为98-100%查找完全重复的图片
- **激进设置**: 相似度设为85-95%查找相似的图片
- **分批处理**: 大量图片建议分目录扫描

### 转换建议
- **AVIF格式**: 最新的图片格式，压缩率最高，文件最小
- **WEBP格式**: 兼容性好，压缩率优于JPEG
- **质量设置**: 85%质量在文件大小和图片质量间取得平衡

## 🛠️ 系统要求

- **Windows**: Windows 10/11 (x64)
- **macOS**: macOS 10.14+ (x64/ARM64)
- **Linux**: GLIBC 2.17+ (x64)

## 📊 支持的图片格式

### 输入格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WEBP (.webp)
- AVIF (.avif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- GIF (.gif)
- 其他常见格式

### 输出格式
- AVIF (.avif) - 推荐用于现代web
- WEBP (.webp) - 推荐用于web优化
- JPEG (.jpg) - 最大兼容性
- PNG (.png) - 支持透明度

## 🔧 技术特性

- **PyQt6界面**: 现代化的GUI框架
- **多线程处理**: 避免界面卡顿
- **图像哈希算法**: 快速准确的相似度检测
- **内存优化**: 大文件处理优化
- **跨平台**: 一套代码多平台运行

## 📝 更新日志

### v1.2.5 (2024-10-13) - 优化版本
- ✨ **大幅优化文件体积**: 减少50%，从87-104MB降至40-71MB
- 🚀 **排除大型依赖**: 移除matplotlib、scipy、pandas等不必要库
- ⚡ **启用UPX压缩**: 进一步压缩可执行文件
- 🔧 **符号剥离**: 移除调试信息减小体积
- 🐛 **修复跨平台兼容性问题**
- 📦 **改进自动构建流程**

### v1.2.4 (2024-10-13)
- 🔧 修复文件收集逻辑
- 📋 改进Release描述和说明
- 🛠️ 优化构建流程

### v1.2.3 (2024-10-13)
- 🐛 修复PyInstaller配置错误
- 🔧 改进图标文件处理
- 📦 优化依赖管理

### v1.2.2 (2024-10-13)
- 🐛 修复macOS构建失败问题
- 🔧 改进错误处理机制

### v1.2.1 (2024-10-13)
- 🐛 修复Windows Unicode编码错误
- 🔧 改进图标文件处理
- 📦 优化构建流程

## 🤝 贡献

欢迎提交问题报告和功能建议！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [Pillow](https://pillow.readthedocs.io/) - 图像处理
- [ImageHash](https://github.com/JohannesBuchner/imagehash) - 图像哈希算法
- [PyInstaller](https://www.pyinstaller.org/) - 打包工具

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by [blueraincoatli](https://github.com/blueraincoatli)

</div>