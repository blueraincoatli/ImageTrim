# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个现代化的图片去重工具项目，目前包含现有版本（ImageDedupUI_Confidence.py）和重构规划文档。项目主要功能是扫描用户指定目录下的图片文件，找出重复或相似的图片，并提供处理这些重复图片的功能。

## 常用开发命令

### 运行不同版本
```bash
# 运行现有单一文件版本
python ImageDedupUI_Confidence.py

# 运行新的模块化版本（需要ttkbootstrap）
python modern_ui_framework.py

# 运行AVIF转换功能
python convert_to_avif.py

# 测试功能模块系统
python function_modules.py
```

### 打包命令
```bash
# 打包现有版本
python build_confidence_exe.py

# 使用PyInstaller打包现有版本
pyinstaller ImageDedup_Confidence.spec

# 打包新版本（需要先配置spec文件）
pyinstaller modern_ui_framework.spec
```

### 开发环境设置
```bash
# 安装基础依赖
pip install pillow numpy

# 安装现代化UI依赖（可选）
pip install ttkbootstrap

# 安装AVIF支持
pip install pillow-avif-plugin

# 设置Python路径（根据build_confidence_exe.py中的配置）
# Python路径: D:\CleanPython\python.exe
```

## 代码架构

### 现有代码结构
当前项目包含现有版本和新的模块化架构：

#### 原有单一文件架构（ImageDedupUI_Confidence.py）
1. **ConfidenceCalculator** - 多维置信度计算
   - 图片相似度权重：60%
   - 文件名相似度权重：20%
   - 文件大小相似度权重：20%

2. **DuplicateGroup** - 重复组数据结构
   - 管理文件路径、置信度、匹配类型
   - 支持精确匹配和相似匹配

3. **DuplicateGroupManager** - 重复组管理器
   - 添加、排序、过滤重复组
   - 按置信度范围分组

4. **ConfidenceImageDedupUI** - 主界面类
   - 双标签页设计：扫描设置、重复图片处理
   - 支持单组处理和批量选择两种模式

#### 新模块化架构（function_modules.py）
1. **BaseFunctionModule** - 功能模块基类
   - 标准化功能接口
   - UI面板生成
   - 参数验证和执行

2. **FunctionManager** - 功能管理器
   - 插件化模块注册
   - 功能切换和生命周期管理
   - UI回调系统

3. **具体功能模块**
   - **DedupModule** - 图片去重功能适配器
   - **AvifConvertModule** - AVIF格式转换功能
   - **BatchRenameModule** - 批量重命名（预留）
   - **ImageOptimizerModule** - 图片优化（预留）

4. **ModernImageToolUI** - 现代化UI框架（modern_ui_framework.py）
   - 3栏式布局：功能选择、设置控制、主工作区
   - 基于ttkbootstrap的现代化界面
   - 支持功能热切换

### 重构规划架构
根据docs目录中的设计文档，计划重构为现代化架构：

1. **技术栈升级**
   - UI框架：tkinter → ttkbootstrap
   - 架构模式：单一文件 → 简化版MVP模式
   - 布局设计：传统布局 → 3栏式现代化布局

2. **目标目录结构**
   ```
   ImageDedupTool/
   ├── main.py              # 程序入口
   ├── app_model.py         # 数据模型
   ├── main_view.py         # 主界面
   ├── scanner.py           # 扫描逻辑
   ├── ui_panels.py         # UI面板
   ├── helpers.py           # 工具函数
   ├── config/              # 配置文件
   ├── resources/           # 资源文件
   └── docs/               # 文档
   ```

## 核心功能特性

### 已实现功能

#### 图片去重功能
- 多维度相似度计算（图片内容、文件名、文件大小）
- 置信度分级：高(>0.8)、中(0.5-0.8)、低(<0.5)
- 支持精确匹配（基于哈希）和相似匹配（基于内容）
- 双模式操作：单组处理、批量选择
- 缩略图预览和文件信息显示
- 拖放支持和路径选择

#### AVIF格式转换功能
- 批量转换JPG/PNG到AVIF格式
- 可调节压缩质量（默认85%）
- 保持目录结构
- 自动处理文件名冲突
- 详细的进度反馈和错误处理

### 用户界面特性
#### 现代化3栏式布局
- **左栏（20%）**：功能选择列表，支持图标和描述
- **中栏（25%）**：功能设置、进度显示、操作控制
- **右栏（55%）**：主要功能工作区域
- 支持ttkbootstrap深色主题

#### 统一的UI体验
- 功能热切换，无需重启应用
- 实时进度反馈和状态显示
- 统一的错误处理和用户提示
- 响应式布局设计

### 扩展架构特性
#### 插件化功能系统
- 基于BaseFunctionModule的标准化接口
- FunctionManager统一管理所有功能模块
- 支持动态注册和卸载功能
- UI回调系统支持实时状态更新

#### 预留功能扩展点
- 批量重命名功能（BatchRenameModule）
- 图片优化功能（ImageOptimizerModule）
- 其他图片处理功能可按需添加

## 开发注意事项

### 代码风格约定
- 遵循PEP 8 Python代码风格
- 使用类型提示提高代码可读性
- 类名使用驼峰命名法，函数和变量使用下划线命名法

### 性能考虑
- 图片相似度计算使用64x64小尺寸以提高性能
- 支持的图片格式：.jpg, .jpeg, .png, .gif, .bmp, .webp
- 大文件集合使用进度条显示扫描进度

### 错误处理
- 静默跳过无法读取的文件
- 提供用户友好的错误提示
- 文件操作前进行确认对话框

## 构建和部署

### 打包配置
- 使用PyInstaller进行单文件打包
- 无控制台窗口（--windowed）
- 版本信息文件：version_info.txt
- 输出目录：dist/

### 环境依赖
- Python 3.8+
- 核心依赖：Pillow, numpy, ttkbootstrap
- 构建工具：PyInstaller

## 项目文档

### 重要文档文件
- `IFLOW.md` - 项目总体说明和开发计划
- `docs/现有代码分析.md` - 当前代码结构详细分析
- `docs/新代码框架设计.md` - 重构后的架构设计
- `docs/详细开发计划.md` - 14周开发任务分解
- `docs/UI设计文档.md` - 3栏式现代化UI设计规范

### 重构计划
- 总周期：14周
- 分为5个阶段：基础架构、核心功能、UI组件、集成测试、优化发布
- 目标：实现现代化UI和MVP架构模式

## 关键技术点

### 核心算法
#### 图片相似度算法
- 使用numpy进行图片数组相关系数计算
- 图片调整到64x64统一尺寸
- 归一化互相关方法计算相似度

#### 文件哈希计算
- 使用MD5哈希进行精确匹配
- 分块读取大文件以提高性能

#### AVIF转换算法
- 使用Pillow-AVIF插件进行格式转换
- 支持可调节压缩质量
- 自动颜色空间转换（RGB/RGBA）

### 架构设计模式
#### 插件化功能系统
- 基于抽象基类的标准化接口
- 统一的功能生命周期管理
- 松耦合的模块间通信

#### 现代化UI架构
- 3栏式响应式布局设计
- 基于回调的状态同步机制
- 支持动态UI组件切换

### 扩展性设计
#### 新功能添加步骤
1. 继承BaseFunctionModule创建新模块类
2. 实现必要的抽象方法（get_ui_panel, execute, validate_params）
3. 在FunctionManager中注册新模块
4. UI会自动识别并显示新功能

#### 配置管理
- 每个功能模块独立的设置系统
- 支持设置持久化和恢复
- 统一的设置UI接口

### UI设计原则
- 深色主题+艳色强调色
- 所有矩形和按钮带圆角
- 支持国际化（中英文切换）
- 现代化的拖放和批量选择交互
- 一致的图标和视觉语言
- 无障碍设计考虑