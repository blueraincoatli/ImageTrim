# 图片处理工具套件

## 项目概述

这是一个现代化的多功能图片处理工具套件，采用插件化架构设计，支持多种图片处理功能的动态切换。项目目标是提供一个统一、易用的图片处理解决方案。

### 当前功能

1. **图片去重功能**：查找并处理重复或相似的图片
2. **AVIF格式转换功能**：将图片转换为AVIF格式以节省存储空间

### 技术架构

- **主框架**: Python 3.8+
- **GUI框架**: ttkbootstrap
- **图片处理**: PIL/Pillow, imagehash
- **打包工具**: PyInstaller

## 安装和运行

### 环境要求

- Python 3.8+
- 必需的Python包：
  - ttkbootstrap
  - Pillow
  - imagehash
  - numpy

### 安装步骤

1. 克隆项目代码：
   ```bash
   git clone https://github.com/blueraincoatli/DeDupImg.git
   cd DeDupImg
   ```

2. 安装依赖：
   ```bash
   pip install ttkbootstrap Pillow imagehash numpy
   ```

3. 运行应用：
   ```bash
   python improved_main_app_v3.py
   ```

## 使用说明

### 图片去重功能

1. 在左侧功能选择区选择"Improved Image Deduplication"
2. 在设置区域添加要扫描的图片目录
3. 调整相似度阈值和其他设置
4. 点击"Start Scan"开始扫描
5. 在右侧结果区域查看重复图片组
6. 选择要处理的图片，点击"Delete Selected"或"Move Selected"进行操作

### AVIF格式转换功能

1. 在左侧功能选择区选择"AVIF Converter"
2. 设置源目录和目标目录
3. 调整转换质量等参数
4. 点击"Start Conversion"开始转换
5. 在右侧区域查看转换进度和结果

## 开发指南

### 项目结构

```
E:\FFOutput\Dedup\
├── core/                     # 核心模块
├── ui/                       # UI相关模块
├── modules/                  # 功能模块
├── utils/                    # 通用工具
├── docs/                     # 文档目录
├── tests/                    # 测试目录
├── improved_main_app_v3.py   # 主应用入口
├── function_modules.py       # 功能模块基类
└── IFLOW.md                  # 开发配置和约束指南
```

### 添加新功能模块

1. 继承 `BaseFunctionModule` 基类
2. 实现必需的抽象方法：
   - `create_settings_ui()`: 创建设置UI面板
   - `create_workspace_ui()`: 创建工作区UI面板
   - `execute()`: 执行功能核心逻辑
   - `stop_execution()`: 停止执行操作
3. 在 `modules/` 目录下创建模块文件
4. 应用会自动加载符合命名规范的模块

### 开发约束

请参考 [IFLOW.md](IFLOW.md) 文件了解详细的开发约束和规范。

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。