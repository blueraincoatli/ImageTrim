# ImageTrim API 文档

## 📖 目录

1. [核心架构](#核心架构)
2. [基础模块](#基础模块)
3. [功能模块](#功能模块)
4. [UI组件](#ui组件)
5. [工具函数](#工具函数)
6. [扩展接口](#扩展接口)

---

## 🏗️ 核心架构

### BaseFunctionModule

所有功能模块的基类，定义了模块的标准接口和生命周期。

```python
class BaseFunctionModule(QObject):
    """
    功能模块基类

    定义了所有功能模块必须实现的标准接口，包括模块信息、
    UI创建、执行控制等功能。
    """

    # 信号定义
    execution_started = pyqtSignal()
    progress_updated = pyqtSignal(float, str)
    log_message = pyqtSignal(str, str)
    execution_finished = pyqtSignal(dict)
    execution_stopped = pyqtSignal()

    def __init__(self, name: str, display_name: str, description: str, icon: str):
        """
        初始化功能模块

        Args:
            name: 模块唯一标识符
            display_name: 显示名称
            description: 功能描述
            icon: 图标(emoji或图标路径)
        """

    @abstractmethod
    def create_settings_ui(self) -> QWidget:
        """
        创建设置UI面板

        Returns:
            QWidget: 设置UI面板实例
        """

    @abstractmethod
    def create_workspace_ui(self) -> QWidget:
        """
        创建工作区UI面板

        Returns:
            QWidget: 工作区UI面板实例
        """

    @abstractmethod
    def execute(self, params: dict):
        """
        执行模块功能

        Args:
            params: 执行参数字典
        """

    def stop_execution(self):
        """停止执行当前操作"""
        pass
```

### FunctionManager

功能模块管理器，负责模块的注册、加载和切换。

```python
class FunctionManager:
    """
    功能模块管理器

    负责所有功能模块的注册、管理、加载和切换操作。
    实现了模块的生命周期管理和事件分发。
    """

    def __init__(self):
        """初始化功能管理器"""
        self.modules: Dict[str, BaseFunctionModule] = {}
        self.active_module: Optional[BaseFunctionModule] = None

    def register_module(self, module: BaseFunctionModule) -> bool:
        """
        注册功能模块

        Args:
            module: 要注册的模块实例

        Returns:
            bool: 注册是否成功
        """

    def activate_module(self, module_name: str) -> bool:
        """
        激活指定模块

        Args:
            module_name: 模块名称

        Returns:
            bool: 激活是否成功
        """

    def get_module(self, module_name: str) -> Optional[BaseFunctionModule]:
        """
        获取模块实例

        Args:
            module_name: 模块名称

        Returns:
            Optional[BaseFunctionModule]: 模块实例，不存在返回None
        """

    def get_all_modules(self) -> Dict[str, BaseFunctionModule]:
        """
        获取所有已注册的模块

        Returns:
            Dict[str, BaseFunctionModule]: 模块字典
        """
```

---

## 📷 图片去重模块

### DeduplicationModule

图片去重功能模块，提供基于图像哈希的重复图片检测。

```python
class DeduplicationModule(BaseFunctionModule):
    """
    图片去重模块

    基于图像哈希算法检测重复图片，支持多种哈希算法和
    可配置的相似度阈值。
    """

    def __init__(self):
        super().__init__(
            name="deduplication",
            display_name="🔍 图片去重",
            description="检测和清理重复图片，释放存储空间",
            icon="🔍"
        )

        # 配置参数
        self.similarity_threshold: float = 0.85
        self.hash_algorithm: str = "average"
        self.min_file_size: int = 1024
        self.include_subdirs: bool = True

    def create_settings_ui(self) -> QWidget:
        """创建设置UI面板"""
        # 返回设置UI实例

    def create_workspace_ui(self) -> QWidget:
        """创建工作区UI面板"""
        # 返回工作区UI实例

    def execute(self, params: dict):
        """
        执行图片去重

        Args:
            params: 执行参数
                - directory: 扫描目录
                - similarity_threshold: 相似度阈值
                - hash_algorithm: 哈希算法
                - min_file_size: 最小文件大小
                - include_subdirs: 是否包含子目录
        """
```

### DeduplicationLogic

图片去重业务逻辑类，处理核心算法和数据处理。

```python
class DeduplicationLogic:
    """
    图片去重业务逻辑

    处理图片相似度计算、重复项检测和结果处理等核心业务逻辑。
    """

    def __init__(self, module: DeduplicationModule):
        """
        初始化逻辑处理器

        Args:
            module: 所属的功能模块
        """

    def calculate_similarity(self, file1: str, file2: str, algorithm: str = "average") -> float:
        """
        计算两个图片的相似度

        Args:
            file1: 第一个图片路径
            file2: 第二个图片路径
            algorithm: 哈希算法类型

        Returns:
            float: 相似度分数(0.0-1.0)
        """

    def find_duplicates(self, directory: str, **kwargs) -> Dict[str, List[str]]:
        """
        查找重复图片

        Args:
            directory: 扫描目录
            **kwargs: 其他参数

        Returns:
            Dict[str, List[str]]: 重复图片字典，键为原始文件，值为重复文件列表
        """

    def process_directory(self, directory: str, callback: Callable = None) -> Dict[str, List[str]]:
        """
        处理目录查找重复图片

        Args:
            directory: 要处理的目录
            callback: 进度回调函数

        Returns:
            Dict[str, List[str]]: 查找到的重复图片
        """
```

---

## 🔄 AVIF转换模块

### AVIFConverterModule

AVIF格式转换功能模块，提供图片格式转换功能。

```python
class AVIFConverterModule(BaseFunctionModule):
    """
    AVIF转换模块

    支持将常见图片格式转换为AVIF、WEBP等现代格式，
    提供批量处理和质量控制功能。
    """

    def __init__(self):
        super().__init__(
            name="avif_converter",
            display_name="🔄 AVIF转换",
            description="将图片转换为AVIF等现代格式，节省存储空间",
            icon="🔄"
        )

        # 配置参数
        self.source_path: str = ""
        self.target_path: str = ""
        self.quality: int = 85
        self.output_format: str = "AVIF"
        self.include_subdirs: bool = True

    def create_settings_ui(self) -> QWidget:
        """创建设置UI面板"""
        # 返回设置UI实例

    def create_workspace_ui(self) -> QWidget:
        """创建工作区UI面板"""
        # 返回工作区UI实例

    def execute(self, params: dict):
        """
        执行格式转换

        Args:
            params: 执行参数
                - source_path: 源目录
                - target_path: 目标目录
                - quality: 输出质量(1-100)
                - output_format: 输出格式
                - include_subdirs: 是否包含子目录
        """
```

### AVIFConverterLogic

AVIF转换业务逻辑类，处理格式转换和批量操作。

```python
class AVIFConverterLogic:
    """
    AVIF转换业务逻辑

    处理图片格式转换、质量控制、批量处理等核心业务逻辑。
    """

    def __init__(self, module: AVIFConverterModule):
        """
        初始化逻辑处理器

        Args:
            module: 所属的功能模块
        """

    def convert_image(self, source_path: str, target_path: str,
                     output_format: str = "AVIF", quality: int = 85) -> bool:
        """
        转换单个图片格式

        Args:
            source_path: 源图片路径
            target_path: 目标图片路径
            output_format: 输出格式
            quality: 输出质量

        Returns:
            bool: 转换是否成功
        """

    def batch_convert(self, source_dir: str, target_dir: str,
                    output_format: str = "AVIF", quality: int = 85,
                    include_subdirs: bool = True, callback: Callable = None) -> Dict[str, Any]:
        """
        批量转换图片格式

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            output_format: 输出格式
            quality: 输出质量
            include_subdirs: 是否包含子目录
            callback: 进度回调函数

        Returns:
            Dict[str, Any]: 转换结果统计
        """

    def get_supported_formats(self) -> List[str]:
        """
        获取支持的输出格式列表

        Returns:
            List[str]: 支持的格式列表
        """
```

---

## 🎨 UI组件

### FunctionPanel

功能选择面板，显示所有可用的功能模块。

```python
class FunctionPanel(QWidget):
    """
    功能选择面板

    显示所有可用的功能模块，支持模块选择和切换。
    提供直观的功能卡片界面。
    """

    # 信号
    function_selected = pyqtSignal(str)

    def __init__(self, function_manager: FunctionManager):
        """
        初始化功能面板

        Args:
            function_manager: 功能管理器实例
        """

    def update_modules(self):
        """更新功能模块列表"""

    def create_function_card(self, module: BaseFunctionModule) -> QWidget:
        """
        创建功能卡片

        Args:
            module: 功能模块实例

        Returns:
            QWidget: 功能卡片组件
        """
```

### SettingsPanel

设置面板，显示当前激活模块的设置选项。

```python
class SettingsPanel(QWidget):
    """
    设置面板

    显示当前激活模块的设置选项，提供参数配置界面。
    """

    def __init__(self, function_manager: FunctionManager):
        """
        初始化设置面板

        Args:
            function_manager: 功能管理器实例
        """

    def update_ui(self, module: BaseFunctionModule):
        """
        更新设置界面

        Args:
            module: 当前激活的功能模块
        """
```

### WorkspacePanel

工作区面板，显示当前模块的工作界面。

```python
class WorkspacePanel(QWidget):
    """
    工作区面板

    显示当前激活模块的工作界面，处理功能操作和结果展示。
    """

    def __init__(self, function_manager: FunctionManager):
        """
        初始化工作区面板

        Args:
            function_manager: 功能管理器实例
        """

    def update_ui(self, module: BaseFunctionModule):
        """
        更新工作区界面

        Args:
            module: 当前激活的功能模块
        """
```

---

## 🔧 工具函数

### ImageUtils

图片处理工具函数集合。

```python
class ImageUtils:
    """
    图片处理工具类

    提供图片加载、缩放、缓存等通用功能。
    """

    @staticmethod
    def get_thumbnail(file_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[QPixmap]:
        """
        获取图片缩略图

        Args:
            file_path: 图片文件路径
            size: 缩略图尺寸

        Returns:
            Optional[QPixmap]: 缩略图，失败返回None
        """

    @staticmethod
    def get_image_info(file_path: str) -> Dict[str, Any]:
        """
        获取图片信息

        Args:
            file_path: 图片文件路径

        Returns:
            Dict[str, Any]: 图片信息字典
        """

    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        """
        检查是否为有效的图片文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否为有效图片
        """
```

### HashUtils

哈希算法工具函数集合。

```python
class HashUtils:
    """
    哈希算法工具类

    提供多种图片哈希算法的实现。
    """

    @staticmethod
    def calculate_average_hash(image_path: str) -> str:
        """
        计算感知哈希(Average Hash)

        Args:
            image_path: 图片路径

        Returns:
            str: 哈希值字符串
        """

    @staticmethod
    def calculate_difference_hash(image_path: str) -> str:
        """
        计算差异哈希(Difference Hash)

        Args:
            image_path: 图片路径

        Returns:
            str: 哈希值字符串
        """

    @staticmethod
    def calculate_wavelet_hash(image_path: str) -> str:
        """
        计算小波哈希(Wavelet Hash)

        Args:
            image_path: 图片路径

        Returns:
            str: 哈希值字符串
        """

    @staticmethod
    def calculate_similarity(hash1: str, hash2: str) -> float:
        """
        计算两个哈希值的相似度

        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值

        Returns:
            float: 相似度分数(0.0-1.0)
        """
```

---

## 🔌 扩展接口

### 模块扩展接口

```python
# 自定义模块示例
class CustomModule(BaseFunctionModule):
    """
    自定义功能模块示例

    展示如何扩展ImageTrim添加新功能。
    """

    def __init__(self):
        super().__init__(
            name="custom_module",
            display_name="🎯 自定义功能",
            description="自定义功能模块示例",
            icon="🎯"
        )

    def create_settings_ui(self) -> QWidget:
        """创建设置UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 添加自定义设置控件
        label = QLabel("自定义功能设置")
        layout.addWidget(label)

        return widget

    def create_workspace_ui(self) -> QWidget:
        """创建工作区UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 添加自定义工作区控件
        label = QLabel("自定义功能工作区")
        layout.addWidget(label)

        return widget

    def execute(self, params: dict):
        """执行自定义功能"""
        # 实现自定义功能逻辑
        pass
```

### 插件注册示例

```python
# 在应用启动时注册自定义模块
def register_custom_modules(function_manager: FunctionManager):
    """
    注册自定义功能模块

    Args:
        function_manager: 功能管理器实例
    """
    # 创建并注册自定义模块
    custom_module = CustomModule()
    function_manager.register_module(custom_module)

    # 可以注册更多模块
    # another_module = AnotherCustomModule()
    # function_manager.register_module(another_module)
```

### 信号处理示例

```python
class CustomModuleWorkspace(QWidget):
    """
    自定义模块工作区示例

    展示如何处理模块信号和UI更新。
    """

    def __init__(self, module: BaseFunctionModule):
        super().__init__()
        self.module = module

        # 连接模块信号
        self.module.progress_updated.connect(self.on_progress_updated)
        self.module.log_message.connect(self.on_log_message)

    def on_progress_updated(self, value: float, message: str):
        """处理进度更新"""
        # 更新进度条或状态显示
        pass

    def on_log_message(self, message: str, level: str):
        """处理日志消息"""
        # 显示日志信息
        pass
```

---

## 📝 使用示例

### 基本使用

```python
# 创建功能管理器
function_manager = FunctionManager()

# 注册内置模块
dedup_module = DeduplicationModule()
avif_module = AVIFConverterModule()

function_manager.register_module(dedup_module)
function_manager.register_module(avif_module)

# 激活模块
function_manager.activate_module("deduplication")

# 执行功能
params = {
    "directory": "/path/to/images",
    "similarity_threshold": 0.8,
    "include_subdirs": True
}
dedup_module.execute(params)
```

### 自定义扩展

```python
# 创建自定义模块
class WatermarkModule(BaseFunctionModule):
    """图片水印模块"""

    def __init__(self):
        super().__init__(
            name="watermark",
            display_name="💧 水印添加",
            description="为图片添加水印",
            icon="💧"
        )

    def create_settings_ui(self) -> QWidget:
        # 创建水印设置界面
        pass

    def create_workspace_ui(self) -> QWidget:
        # 创建水印工作区界面
        pass

    def execute(self, params: dict):
        # 执行水印添加逻辑
        pass

# 注册自定义模块
watermark_module = WatermarkModule()
function_manager.register_module(watermark_module)
```

---

## 🔄 版本历史

### v1.0.0 (2025-10-12)
- ✅ 初始API文档
- ✅ 核心模块接口
- ✅ UI组件接口
- ✅ 工具函数接口
- ✅ 扩展接口定义

---

## 📄 许可证

© 2025 ImageTrim
小红书: 919722379

本API文档受项目许可证保护，仅供项目开发使用。