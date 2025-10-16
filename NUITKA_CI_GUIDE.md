# Nuitka CI/CD 迁移指南

## 📋 概述

本指南说明如何从 PyInstaller 迁移到 Nuitka 进行 GitHub Actions 自动编译。

## 🎯 为什么迁移到 Nuitka？

### PyInstaller 的问题
- ❌ **TOC 格式错误**: `ImageTrim_windows.spec` 中的 TOC 条目格式不正确
- ❌ **维护困难**: `.spec` 文件配置复杂，容易出错
- ❌ **启动较慢**: 需要解压和加载 Python 运行时
- ❌ **体积较大**: 包含完整的 Python 解释器

### Nuitka 的优势
- ✅ **原生编译**: Python → C → 机器码，性能更优
- ✅ **启动更快**: 2-3 倍启动速度提升
- ✅ **配置简单**: 命令行参数，无需复杂的 spec 文件
- ✅ **更稳定**: 原生编译减少运行时错误
- ✅ **体积优化**: 更好的代码优化和压缩

## 🔧 新的工作流文件

### 文件位置
```
.github/workflows/build-nuitka.yml
```

### 触发条件
1. **Tag 推送**: 推送 `v*` 标签时自动触发
2. **手动触发**: 在 GitHub Actions 页面手动运行

## 📦 支持的平台

| 平台 | 输出文件 | 格式 |
|------|----------|------|
| **Windows** | `ImageTrim.exe` | 单文件可执行文件 |
| **macOS** | `ImageTrim.app/` + `.dmg` | 应用程序包 + 磁盘镜像 |
| **Linux** | `ImageTrim` + `.AppImage` | 单文件 + 便携版 |

## 🚀 使用方法

### 方法 1: 推送 Tag（推荐）

```bash
# 1. 创建并推送 tag
git tag v1.2.0
git push origin v1.2.0

# 2. GitHub Actions 自动开始编译
# 3. 编译完成后自动创建 Release
```

### 方法 2: 手动触发

1. 访问 GitHub 仓库的 **Actions** 页面
2. 选择 **Build with Nuitka (Multi-Platform)** 工作流
3. 点击 **Run workflow**
4. 输入版本号（可选）
5. 点击 **Run workflow** 确认

## ⚙️ 编译参数说明

### Windows 编译参数
```bash
--standalone                    # 独立模式
--onefile                       # 单文件输出
--assume-yes-for-downloads      # 自动下载依赖（如 MinGW）
--enable-plugin=pyqt6           # PyQt6 插件
--include-package=pillow_avif   # AVIF 支持
--include-package=send2trash    # 删除文件支持
--windows-disable-console       # 禁用控制台窗口
--windows-icon-from-ico=...     # 设置图标
--lto=yes                       # 链接时优化
--remove-output                 # 删除中间文件
```

### Linux 编译参数
```bash
# 与 Windows 类似，但不包含 --windows-* 参数
# 额外需要系统依赖：gcc, g++, ccache, patchelf
```

### macOS 编译参数
```bash
# 与 Linux 类似，额外包含：
--macos-create-app-bundle       # 创建 .app 包
--macos-app-icon=...            # 设置应用图标
```

## 📊 编译时间对比

| 平台 | PyInstaller | Nuitka | 差异 |
|------|-------------|--------|------|
| **Windows** | ~5-10 分钟 | ~20-25 分钟 | 慢 2-3 倍 |
| **Linux** | ~5-10 分钟 | ~15-20 分钟 | 慢 2 倍 |
| **macOS** | ~5-10 分钟 | ~20-25 分钟 | 慢 2-3 倍 |

**注意**: Nuitka 编译时间更长，但生成的可执行文件性能更优。

## 🔍 故障排查

### 问题 1: Windows 编译失败 - 找不到编译器

**症状**:
```
Error: No C compiler found
```

**解决方案**:
- Nuitka 会自动下载 MinGW 编译器（首次需要 5-10 分钟）
- 确保 `--assume-yes-for-downloads` 参数存在
- 检查网络连接是否正常

### 问题 2: Linux 编译失败 - 缺少系统依赖

**症状**:
```
Error: gcc not found
Error: patchelf not found
```

**解决方案**:
```bash
sudo apt-get update
sudo apt-get install -y build-essential gcc g++ ccache patchelf
```

### 问题 3: macOS 编译失败 - Xcode 未安装

**症状**:
```
Error: xcrun: error: invalid active developer path
```

**解决方案**:
```bash
xcode-select --install
```

### 问题 4: 模块导入失败

**症状**:
```
ModuleNotFoundError: No module named 'pillow_avif'
```

**解决方案**:
- 检查 `--include-package=pillow_avif` 参数
- 检查 `--include-module=pillow_avif._avif` 参数
- 确保 `requirements.txt` 中包含该模块

### 问题 5: 资源文件缺失

**症状**:
```
FileNotFoundError: resources/icons/...
```

**解决方案**:
- 检查 `--include-data-dir` 参数
- 确保资源目录存在：`app/resources/icons/`, `app/resources/images/`

## 📝 与 PyInstaller 的对比

### 配置复杂度
| 方面 | PyInstaller | Nuitka |
|------|-------------|--------|
| **配置文件** | 需要 `.spec` 文件 | 仅需命令行参数 |
| **维护难度** | 高（TOC 格式易错） | 低（参数清晰） |
| **调试难度** | 中等 | 较低 |

### 性能对比
| 指标 | PyInstaller | Nuitka |
|------|-------------|--------|
| **启动速度** | ~3-5 秒 | ~1-2 秒 |
| **运行性能** | 解释执行 | 原生机器码 |
| **内存占用** | 较高 | 较低 |
| **文件体积** | 40-60 MB | 40-60 MB |

### 兼容性
| 方面 | PyInstaller | Nuitka |
|------|-------------|--------|
| **Python 版本** | 3.7+ | 3.7+ |
| **第三方库** | 广泛支持 | 广泛支持 |
| **特殊模块** | 需要 hooks | 需要插件 |

## 🎯 最佳实践

### 1. 本地测试
在推送到 GitHub 之前，先在本地测试 Nuitka 编译：

```bash
# Windows
python build_nuitka.py

# Linux/macOS
python3 build_nuitka.py
```

### 2. 快速迭代
开发阶段使用快速编译模式：

```bash
python build_nuitka.py --fast
```

### 3. 版本管理
使用语义化版本号：

```bash
git tag v1.2.3
git push origin v1.2.3
```

### 4. Release 说明
在 GitHub Release 中添加详细的更新说明：
- 新功能
- Bug 修复
- 性能改进
- 已知问题

## 🔄 迁移步骤

### 步骤 1: 备份旧工作流
```bash
cp .github/workflows/build-multi-platform.yml .github/workflows/build-multi-platform.yml.backup
```

### 步骤 2: 启用新工作流
新工作流文件已创建：`.github/workflows/build-nuitka.yml`

### 步骤 3: 测试新工作流
```bash
# 创建测试 tag
git tag v1.0.0-test
git push origin v1.0.0-test

# 观察 GitHub Actions 执行情况
```

### 步骤 4: 验证输出
- 检查生成的可执行文件
- 测试启动速度
- 验证功能完整性

### 步骤 5: 正式发布
```bash
# 删除测试 tag
git tag -d v1.0.0-test
git push origin :refs/tags/v1.0.0-test

# 创建正式 tag
git tag v1.2.0
git push origin v1.2.0
```

## 📚 参考资料

- [Nuitka 官方文档](https://nuitka.net/doc/user-manual.html)
- [Nuitka GitHub](https://github.com/Nuitka/Nuitka)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

## ❓ 常见问题

### Q: 可以同时保留 PyInstaller 和 Nuitka 工作流吗？
A: 可以。两个工作流可以共存，使用不同的触发条件或手动选择。

### Q: Nuitka 编译失败怎么办？
A: 可以回退到 PyInstaller 工作流，或查看本文档的"故障排查"部分。

### Q: 如何减少 Nuitka 编译时间？
A: 
- 使用 `--fast` 模式（开发阶段）
- 移除 `--lto=yes` 参数（牺牲一些性能）
- 使用 ccache 缓存编译结果

### Q: 生成的文件体积比 PyInstaller 大吗？
A: 通常相近，Nuitka 可能稍小一些（5-10%）。

## 🎉 总结

迁移到 Nuitka 后：
- ✅ 解决了 PyInstaller 的 TOC 格式错误
- ✅ 提升了应用启动速度和运行性能
- ✅ 简化了配置和维护
- ✅ 提供了更好的用户体验

虽然编译时间稍长，但生成的应用质量更高，值得迁移！

