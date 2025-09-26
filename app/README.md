# 图片处理工具套件 - PyQt6版本

这是一个基于PyQt6的现代化图片处理工具套件，采用模块化架构设计，支持功能动态扩展。旨在为用户提供统一、易用的图片管理解决方案。

## 项目结构

```
app/
├── core/                    # 核心模块
│   ├── base_module.py       # 功能模块基类
│   └── function_manager.py  # 功能管理器
├── ui/                      # UI模块
│   ├── main_window.py       # 主窗口
│   ├── function_panel.py    # 功能选择面板
│   ├── settings_panel.py    # 设置面板
│   ├── workspace_panel.py   # 工作区面板
│   ├── components/          # UI组件
│   └── themes/              # 主题管理
├── modules/                 # 功能模块
│   ├── deduplication/       # 图片去重模块
│   └── avif_converter/      # AVIF转换模块
├── utils/                   # 工具模块
├── assets/                  # 资源文件
├── tests/                   # 测试文件
├── main.py                 # 程序入口
└── requirements.txt        # 依赖列表
```

## 主要特性

- **插件化架构**：新功能可通过模块化方式轻松集成
- **现代化UI**：基于PyQt6构建直观的操作界面，深色主题
- **高内聚低耦合**：遵循软件设计原则，便于维护和扩展
- **可配置参数**：支持调整相似度阈值、输出质量等设置
- **多线程处理**：耗时操作在后台线程执行，保持界面响应性

## 核心功能

### 1. 图片去重
基于图像哈希算法识别视觉上相同或高度相似的图片，并支持删除或移动操作。

### 2. AVIF格式转换
将常见图片格式（如JPG/PNG）批量转换为更高效的AVIF格式，节省存储空间。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

### Windows:
```bash
start.bat
```

### Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

### 直接运行:
```bash
python main.py
```

## 技术栈

- **GUI框架**: PyQt6
- **图片处理**: Pillow, imagehash
- **数值计算**: numpy
- **打包工具**: PyInstaller (可选)

## 开发规范

- 遵循PEP 8代码规范
- 使用类型提示
- 模块化设计，高内聚低耦合
- 统一接口定义