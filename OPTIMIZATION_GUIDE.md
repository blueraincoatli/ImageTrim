# ImageTrim 文件体积优化指南

## 问题分析

原始构建产生的文件体积过大：
- Windows: 87MB (本地构建只有54MB)
- macOS: ~102MB (ImageTrim.app + 单文件)
- Linux: 104MB

## 优化策略

### 1. PyInstaller Spec 文件优化

创建了 `ImageTrim_optimized.spec` 文件，包含以下优化：

#### 排除大型库（最大体积节省）
- **matplotlib**: 完全排除 (~50MB节省)
- **scipy**: 完全排除 (~40MB节省)
- **pandas**: 完全排除 (~20MB节省)
- **Jupyter/IPython生态**: 完全排除 (~15MB节省)

#### 排除不需要的PyQt6模块
只保留核心GUI组件：
```python
# 保留
'PyQt6.QtCore'
'PyQt6.QtGui'
'PyQt6.QtWidgets'

# 排除大型组件
'PyQt6.QtWebEngine'
'PyQt6.QtMultimedia'
'PyQt6.QtOpenGL'
'PyQt6.QtQuick'
# ... 等等
```

#### 精确化隐式导入
只包含实际需要的模块：
```python
hiddenimports = [
    # PIL图像处理核心
    'PIL.Image',
    'PIL.ImageQt',
    'PIL.ImageFilter',
    'PIL.ImageEnhance',

    # 图像哈希
    'imagehash',

    # 数值计算最小化
    'numpy.core._multiarray_umath',
    'numpy.linalg.lapack_lite',
]
```

### 2. 构建参数优化

#### 启用压缩和优化
```python
exe = EXE(
    # ...
    strip=True,      # 符号剥离
    upx=True,        # UPX压缩
    optimize=2,      # 最高Python优化级别
    # ...
)
```

### 3. 系统级优化

#### UPX压缩
- **Linux**: `sudo apt-get install upx-ucl`
- **macOS**: `brew install upx`
- **Windows**: 下载预编译版本

#### 符号剥离
- 移除调试符号减小体积
- 对性能影响微乎其微

### 4. 依赖管理优化

#### 最小化requirements.txt
检查并移除不必要的依赖：
```python
# 检查实际使用的库
pip list --outdated
pip uninstall <不用的库>
```

## 预期优化效果

基于排除的库估算：
- matplotlib: ~50MB
- scipy: ~40MB
- pandas: ~20MB
- PyQt6额外模块: ~15MB
- 开发工具: ~5MB
- UPX压缩: 20-30% 额外减少

**预期总减少**: 100-130MB
**预期最终大小**: 40-60MB (接近本地构建水平)

## 使用优化构建

### 本地构建
```bash
python build_optimized.py
```

### GitHub Actions自动构建
推送代码到main分支会触发：
```yaml
# 自动使用优化的构建脚本
.venv/Scripts/python build_optimized.py  # Windows
.venv/bin/python build_optimized.py     # Linux/macOS
```

## 验证优化效果

构建完成后检查大小：
```bash
# Windows
dist/ImageTrim.exe

# macOS
dist/ImageTrim.app

# Linux
dist/imagetrim
```

### 大小基准
- **优秀**: < 60MB
- **良好**: 60-80MB
- **可接受**: 80-100MB
- **需优化**: > 100MB

## 进一步优化选项

如果体积仍然过大，可考虑：

### 1. 更激进的库排除
```python
# 排除更多numpy组件
excludes += [
    'numpy.polynomial',
    'numpy.random',  # 如果不用随机数
    'numpy.fft',      # 如果不用FFT
]
```

### 2. 使用--onedir模式
```python
# 可能比单文件更小
exe = EXE(
    # ...
    # 但会产生目录而不是单文件
)
```

### 3. 外部依赖
将某些大库（如图像处理）放到外部文件，按需下载。

## 故障排除

### 常见问题
1. **ModuleNotFoundError**: 将需要的模块添加到`hiddenimports`
2. **运行时错误**: 检查排除的库是否实际需要
3. **UPX压缩失败**: 不使用UPX或检查版本兼容性

### 调试步骤
1. 先用简单spec测试
2. 逐步添加排除项
3. 测试所有功能确保正常

## 文件清单

优化相关文件：
- `ImageTrim_optimized.spec` - 优化的PyInstaller配置
- `build_optimized.py` - 优化的构建脚本
- `.github/workflows/build-multi-platform.yml` - 更新的CI/CD流程
- `OPTIMIZATION_GUIDE.md` - 本优化指南