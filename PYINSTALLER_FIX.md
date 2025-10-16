# PyInstaller TOC 错误修复指南

## ❌ 错误信息

```
File "ImageTrim_windows.spec", line 155, in <module>
    exe = EXE(
        pyz,
        ...
        icon=icon_path,
    )
ValueError: not enough values to unpack (expected 3, got 2)
```

**错误位置**: `PyInstaller/building/datastruct.py` 的 `normalize_toc` 函数

## 🔍 问题分析

### 根本原因
PyInstaller 的 TOC (Table of Contents) 条目必须是**三元组**格式：

```python
(dest_name, src_name, typecode)
```

但某些配置可能产生了**二元组**格式：

```python
(dest_name, src_name)  # ❌ 错误！缺少 typecode
```

### 常见错误来源

1. **错误的 `datas` 配置**:
```python
# ❌ 错误
datas = [
    ('app/resources', 'resources'),  # 缺少 typecode
]

# ✅ 正确
datas = [
    ('app/resources', 'resources', 'DATA'),
]
```

2. **错误的 `binaries` 配置**:
```python
# ❌ 错误
binaries = [
    ('some.dll', '.'),  # 缺少 typecode
]

# ✅ 正确
binaries = [
    ('some.dll', '.', 'BINARY'),
]
```

3. **错误的 `Tree` 使用**:
```python
# ❌ 错误
datas += Tree('app/resources', prefix='resources')  # 可能产生错误格式

# ✅ 正确
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files('app.resources')
```

## 🔧 修复方法

### 方法 1: 检查 `.spec` 文件

查找所有 `datas`、`binaries`、`Tree` 相关的配置，确保格式正确。

**示例修复**:

```python
# 修复前
a = Analysis(
    ['app/main.py'],
    datas=[
        ('app/resources/icons', 'resources/icons'),  # ❌ 缺少 typecode
        ('app/resources/images', 'resources/images'),  # ❌ 缺少 typecode
    ],
    ...
)

# 修复后
a = Analysis(
    ['app/main.py'],
    datas=[
        ('app/resources/icons', 'resources/icons', 'DATA'),  # ✅ 添加 typecode
        ('app/resources/images', 'resources/images', 'DATA'),  # ✅ 添加 typecode
    ],
    ...
)
```

### 方法 2: 使用辅助函数

PyInstaller 提供了辅助函数来自动生成正确格式的 TOC：

```python
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 收集数据文件
datas = collect_data_files('app.resources')

# 收集动态库
binaries = collect_dynamic_libs('some_package')
```

### 方法 3: 手动规范化 TOC

如果必须手动构建 TOC，确保每个条目都是三元组：

```python
def normalize_datas(datas_list):
    """确保所有 datas 条目都是三元组"""
    normalized = []
    for item in datas_list:
        if len(item) == 2:
            # 二元组，添加 'DATA' typecode
            normalized.append((item[0], item[1], 'DATA'))
        elif len(item) == 3:
            # 已经是三元组
            normalized.append(item)
        else:
            raise ValueError(f"Invalid datas item: {item}")
    return normalized

# 使用
datas = normalize_datas([
    ('app/resources/icons', 'resources/icons'),
    ('app/resources/images', 'resources/images'),
])
```

## 📝 完整的 `.spec` 文件示例

```python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集数据文件（自动生成正确的 TOC 格式）
datas = []
datas += collect_data_files('app.resources')

# 或者手动指定（确保是三元组）
datas += [
    ('app/resources/icons', 'resources/icons', 'DATA'),
    ('app/resources/images', 'resources/images', 'DATA'),
]

# 收集隐藏导入
hiddenimports = []
hiddenimports += collect_submodules('PyQt6')
hiddenimports += ['pillow_avif', 'pillow_avif._avif', 'send2trash']

# 排除不需要的模块
excludes = [
    'matplotlib',
    'scipy',
    'pandas',
    'numpy.testing',
    'tkinter',
]

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],  # 如果需要添加，确保是三元组格式
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name='ImageTrim',
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
)
```

## 🧪 验证修复

### 1. 本地测试
```bash
# 清理旧的构建文件
rm -rf build/ dist/

# 使用修复后的 spec 文件构建
pyinstaller ImageTrim_windows.spec
```

### 2. 检查 TOC 格式
在 `.spec` 文件中添加调试代码：

```python
# 在 Analysis 之后添加
print("=== Checking TOC format ===")
for item in a.datas:
    if len(item) != 3:
        print(f"ERROR: Invalid TOC item: {item}")
    else:
        print(f"OK: {item[0]} -> {item[1]} ({item[2]})")
```

### 3. 运行测试
```bash
# Windows
dist\ImageTrim.exe

# Linux/macOS
./dist/ImageTrim
```

## ⚠️ 注意事项

1. **不要混用格式**: 确保所有 TOC 条目都是三元组
2. **使用辅助函数**: 优先使用 PyInstaller 提供的辅助函数
3. **测试完整性**: 修复后测试所有功能，确保资源文件正确包含
4. **版本兼容**: 不同版本的 PyInstaller 可能有不同的要求

## 🎯 推荐方案

虽然可以修复 PyInstaller 的错误，但我们**强烈推荐迁移到 Nuitka**：

### PyInstaller vs Nuitka

| 方面 | PyInstaller | Nuitka |
|------|-------------|--------|
| **配置复杂度** | 高（`.spec` 文件） | 低（命令行参数） |
| **错误频率** | 较高（TOC 格式等） | 较低 |
| **启动速度** | 慢（3-5秒） | 快（1-2秒） |
| **运行性能** | 解释执行 | 原生机器码 |
| **维护成本** | 高 | 低 |

### 迁移到 Nuitka

参考 `NUITKA_CI_GUIDE.md` 文档，迁移步骤简单：

1. 安装 Nuitka: `pip install nuitka`
2. 使用 `build_nuitka.py` 脚本
3. 更新 GitHub Actions 工作流

## 📚 参考资料

- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec 文件格式](https://pyinstaller.org/en/stable/spec-files.html)
- [PyInstaller Hooks](https://pyinstaller.org/en/stable/hooks.html)

## 🆘 仍然无法解决？

如果按照上述方法仍然无法解决问题：

1. **查看完整错误日志**: 运行 `pyinstaller --log-level DEBUG ImageTrim_windows.spec`
2. **检查 PyInstaller 版本**: `pip show pyinstaller`
3. **尝试降级/升级**: `pip install pyinstaller==5.13.0`
4. **迁移到 Nuitka**: 这是最可靠的解决方案

## ✅ 总结

PyInstaller 的 TOC 错误通常是由于数据文件配置格式不正确导致的。修复方法：

1. ✅ 确保所有 TOC 条目都是三元组 `(dest, src, typecode)`
2. ✅ 使用 PyInstaller 提供的辅助函数
3. ✅ 本地测试验证修复
4. ✅ 或者直接迁移到 Nuitka（推荐）

**推荐**: 直接使用 Nuitka，避免 PyInstaller 的各种配置问题！

