# iFlow开发配置和约束指南

## 1. 项目概述

本项目是一个现代化的图片处理工具套件，采用插件化架构设计，支持多种图片处理功能的动态切换。项目目标是提供一个统一、易用的图片处理解决方案。

### 1.1 当前技术栈
- **主框架**: Python 3.8+
- **GUI框架**: ttkbootstrap (计划迁移到PyQt6)
- **图片处理**: PIL/Pillow, imagehash
- **打包工具**: PyInstaller
- **依赖管理**: pip

### 1.2 项目结构
```
E:\FFOutput\Dedup\
├── core/                     # 核心模块
├── ui/                       # UI相关模块
├── modules/                  # 功能模块
├── utils/                    # 通用工具
├── docs/                     # 文档目录
└── tests/                    # 测试目录
```

## 2. 开发约束

### 2.1 代码规范

#### 2.1.1 命名规范
1. **文件命名**
   - Python文件使用小写字母和下划线命名，如 `image_utils.py`
   - 类名使用驼峰命名法，如 `ImageProcessor`
   - 函数和变量使用下划线命名法，如 `calculate_similarity`

2. **类命名**
   - 抽象基类以 `Base` 开头，如 `BaseFunctionModule`
   - 异常类以 `Error` 或 `Exception` 结尾，如 `ModuleNotFoundError`
   - PyQt组件类以 `Widget` 或 `Dialog` 结尾，如 `SettingsWidget`

3. **函数命名**
   - 公共函数使用动词开头，如 `calculate_hash`, `load_image`
   - 私有函数以下划线开头，如 `_process_file`
   - 属性访问器使用 `get_` 和 `set_` 前缀，如 `get_file_info`

#### 2.1.2 代码格式
1. **缩进和空格**
   - 使用4个空格进行缩进，不使用Tab
   - 操作符两侧添加空格，如 `a = b + c`
   - 逗号后添加空格，如 `func(a, b, c)`

2. **行长度**
   - 每行不超过88个字符（兼容black格式化工具）
   - 长表达式使用括号换行，保持一致的缩进

3. **空行**
   - 类定义前后各空两行
   - 函数定义前后各空一行
   - 逻辑段落之间空一行

#### 2.1.3 类型提示
1. **函数类型提示**
   ```python
   def calculate_similarity(file1: str, file2: str) -> float:
       """计算两个文件的相似度"""
       pass

   def process_files(files: List[str]) -> Dict[str, Any]:
       """处理文件列表"""
       pass
   ```

2. **变量类型提示**
   ```python
   file_path: str = "/path/to/file"
   file_list: List[str] = []
   result: Optional[Dict[str, Any]] = None
   ```

### 2.2 文档规范

#### 2.2.1 模块文档字符串
```python
"""
图片处理工具模块

本模块提供了图片处理相关的功能，包括相似度计算、
哈希值计算等核心功能。

作者: Your Name
日期: 2025-09-26
"""
```

#### 2.2.2 类文档字符串
```python
class ImageProcessor:
    """
    图片处理器类
    
    用于处理图片相关的操作，包括相似度计算、格式转换等。
    
    属性:
        quality: 转换质量
        format: 目标格式
    """
```

#### 2.2.3 函数文档字符串
```python
def calculate_hash(file_path: str) -> str:
    """
    计算文件的哈希值
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件的MD5哈希值
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取错误
    """
```

### 2.3 错误处理规范

#### 2.3.1 异常处理原则
1. 优先使用具体的异常类型，而不是通用的 `Exception`
2. 提供有意义的错误信息
3. 避免忽略异常（空的except块）

#### 2.3.2 异常处理示例
```python
try:
    with open(file_path, 'rb') as f:
        # 处理文件
        pass
except FileNotFoundError:
    logger.error(f"文件未找到: {file_path}")
    raise
except IOError as e:
    logger.error(f"文件读取错误: {file_path}, {str(e)}")
    raise
```

### 2.4 日志记录规范

#### 2.4.1 日志级别使用
- `DEBUG`: 详细信息，通常只在诊断问题时使用
- `INFO`: 确认事情按预期工作
- `WARNING`: 表示发生了意外情况，但程序仍能正常工作
- `ERROR`: 由于严重问题，程序的某些功能无法执行
- `CRITICAL`: 严重错误，程序可能无法继续运行

#### 2.4.2 日志记录示例
```python
import logging

logger = logging.getLogger(__name__)

def process_image(file_path: str):
    logger.info(f"开始处理图片: {file_path}")
    try:
        # 处理逻辑
        pass
    except Exception as e:
        logger.error(f"处理图片失败: {file_path}, 错误: {str(e)}")
        raise
```

## 3. 架构设计约束

### 3.1 插件化架构规范

#### 3.1.1 功能模块接口
所有功能模块必须继承 `BaseFunctionModule` 基类并实现以下抽象方法：
```python
class BaseFunctionModule(ABC):
    @abstractmethod
    def create_settings_ui(self, parent) -> Optional[ttk.Frame]:
        """创建并返回功能对应的"设置"UI面板"""
        pass

    @abstractmethod
    def create_workspace_ui(self, parent) -> Optional[ttk.Frame]:
        """创建并返回功能对应的"工作区"UI面板"""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]):
        """执行功能的核心逻辑"""
        pass

    @abstractmethod
    def stop_execution(self):
        """停止正在执行的操作"""
        pass
```

#### 3.1.2 功能管理器规范
```python
class FunctionManager:
    def register_module(self, module: BaseFunctionModule) -> bool:
        """注册功能模块"""
        pass

    def activate_module(self, name: str) -> bool:
        """激活指定功能模块"""
        pass

    def get_module(self, name: str) -> Optional[BaseFunctionModule]:
        """获取指定模块"""
        pass
```

### 3.2 UI设计约束

#### 3.2.1 布局规范
1. **整体布局**：采用左右布局，左侧分为功能选择和设置区，右侧为操作区
2. **比例分配**：
   - 左栏（功能选择和设置）：30% 宽度
     - 功能选择区域：40% 高度
     - 设置与进度区域：60% 高度
   - 右栏（功能工作区）：70% 宽度

#### 3.2.2 主题规范
1. **基础主题**：使用深色主题
2. **颜色方案**：
   - 主背景：#2B2B2B (深灰)
   - 面板背景：#343A40 (稍浅的深灰)
   - 未选中卡片：#353535 (中灰)
   - 选中卡片：#404040 (浅灰)
   - 强调色：#FF8C00 (橙色)

#### 3.2.3 组件规范
1. **按钮样式**：使用圆角设计，统一视觉风格
2. **卡片设计**：功能卡片采用统一的视觉设计和交互模式
3. **进度显示**：实时进度条和状态文本反馈

### 3.3 性能约束

#### 3.3.1 多线程处理
1. 耗时操作必须在后台线程执行
2. 通过信号机制与主线程通信
3. 提供停止操作的功能

#### 3.3.2 资源管理
1. 及时释放不用的UI资源和图片数据
2. 合理使用缓存机制提高响应速度
3. 避免内存泄漏

## 4. 开发流程约束

### 4.1 代码审查要点

#### 4.1.1 审查清单
- [ ] 命名是否符合规范
- [ ] 是否有适当的类型提示
- [ ] 文档字符串是否完整
- [ ] 错误处理是否恰当
- [ ] 日志记录是否合理
- [ ] 资源是否正确释放
- [ ] 性能是否有优化空间
- [ ] 是否有对应的单元测试

### 4.2 测试规范

#### 4.2.1 单元测试
1. 每个模块都应该有对应的测试文件
2. 测试文件命名以 `test_` 开头，如 `test_image_utils.py`
3. 使用pytest框架编写测试

#### 4.2.2 测试示例
```python
def test_calculate_similarity():
    """测试相似度计算功能"""
    file1 = "test1.jpg"
    file2 = "test2.jpg"
    similarity = calculate_similarity(file1, file2)
    assert 0 <= similarity <= 1
```

### 4.3 版本控制约束

#### 4.3.1 提交信息规范
1. 提交信息应清晰描述变更内容
2. 使用祈使句格式，如"添加图片去重功能"
3. 关联相关问题或任务编号

#### 4.3.2 分支管理
1. 主分支 `main` 保持稳定
2. 功能开发使用特性分支
3. 发布版本使用标签管理

## 5. 规划遵循指南

### 5.1 遵循现有架构设计

#### 5.1.1 模块化设计原则
1. 每个功能都是独立的模块，便于开发和维护
2. 功能模块之间相互独立，松耦合设计
3. 标准化接口，所有功能模块实现相同的接口

#### 5.1.2 插件化架构原则
1. 功能模块按需加载，提高性能
2. 支持运行时动态切换功能，无需重启应用
3. 统一管理所有功能模块

### 5.2 遵循UI/UX设计规范

#### 5.2.1 用户体验原则
1. 界面布局清晰，操作流程简单
2. 所有操作都有明确的视觉反馈
3. 支持撤销操作，防止误操作
4. 整个应用的交互和视觉风格保持一致

#### 5.2.2 界面设计原则
1. 通过颜色、大小、间距建立视觉层次
2. 重要功能和信息更加醒目
3. 避免界面过于拥挤
4. 保持元素的对齐和间距一致

### 5.3 遵循技术实现规划

#### 5.3.1 核心技术栈
1. UI框架：PyQt6（计划迁移）
2. 插件架构：BaseFunctionModule抽象基类和FunctionManager
3. 图片处理：PIL/Pillow, pillow-avif-plugin
4. 数值计算：numpy
5. 文件操作：os, shutil, pathlib
6. 多线程：QThread (PyQt6多线程)

#### 5.3.2 关键实现点
1. 使用BaseFunctionModule实现功能模块的标准化
2. 功能模块自动生成对应的UI界面
3. FunctionManager统一管理功能模块的状态和生命周期
4. UI状态实时同步，进度和消息统一管理
5. 运行时动态切换功能，无需重启应用

### 5.4 遵循性能优化规划

#### 5.4.1 功能模块的UI只在需要时加载
1. 按需加载UI组件
2. 智能复用UI组件和资源
3. 长时间操作不阻塞UI线程
4. 及时释放不用的UI资源和图片数据
5. 缩略图和处理结果缓存，提高响应速度

## 6. 质量保证约束

### 6.1 代码质量保证
1. 遵循PEP 8规范
2. 使用类型提示
3. 实施代码审查机制
4. 编写单元测试，目标覆盖率80%+

### 6.2 用户体验保证
1. 进行用户测试
2. 收集反馈并改进
3. 持续优化体验

### 6.3 性能优化保证
1. 建立性能基准
2. 及时释放资源
3. 优化图片加载和显示

## 7. 迁移策略约束

### 7.1 渐进式迁移原则
1. 第一阶段：搭建PyQt6基础框架
2. 第二阶段：重构UI组件
3. 第三阶段：适配功能模块
4. 第四阶段：优化和完善

### 7.2 兼容性保证
1. 保持现有业务逻辑不变
2. 逐步替换UI层实现
3. 提供充分的测试验证

## 8. 风险控制约束

### 8.1 技术风险控制
1. **PyQt6学习曲线**：团队需要时间熟悉PyQt6
2. **性能问题**：PyQt6可能比tkinter消耗更多资源
3. **兼容性问题**：不同平台可能存在显示差异

### 8.2 项目风险控制
1. **进度延期**：重构工作量大可能导致延期
2. **功能缺失**：重构过程中可能遗漏某些功能
3. **用户体验下降**：新界面可能不如预期

## 9. 总结

本iFlow开发配置和约束指南旨在确保项目开发的一致性、可维护性和可扩展性。所有开发人员应严格遵守这些约束和规范，以确保项目的高质量交付。

主要约束包括：
1. 严格的代码规范和文档要求
2. 标准化的架构设计原则
3. 统一的UI/UX设计规范
4. 完善的测试和质量保证机制
5. 渐进式的迁移策略
6. 有效的风险控制措施

通过遵循这些约束和规范，我们将能够建立一个清晰、可维护和可扩展的代码架构，为项目的长期发展奠定坚实的基础。