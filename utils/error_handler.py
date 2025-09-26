# -*- coding: utf-8 -*-
"""
统一错误处理机制
提供标准化的错误处理、日志记录和异常管理
"""

import os
import sys
import traceback
import logging
from datetime import datetime
from typing import Optional, Callable, Any, Dict, List, Union
from pathlib import Path
from enum import Enum

try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class ErrorLevel(Enum):
    """错误级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别枚举"""
    FILE_IO = "file_io"
    NETWORK = "network"
    PERMISSION = "permission"
    VALIDATION = "validation"
    PROCESSING = "processing"
    UI = "ui"
    UNKNOWN = "unknown"


class DeduplicationError(Exception):
    """去重应用自定义错误基类"""

    def __init__(self, message: str, error_category: ErrorCategory = ErrorCategory.UNKNOWN,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message)
        self.error_category = error_category
        self.original_error = original_error
        self.context = context or {}
        self.timestamp = datetime.now()

    def __str__(self):
        base_msg = super().__str__()
        if self.original_error:
            base_msg += f" (原始错误: {str(self.original_error)})"
        if self.context:
            base_msg += f" (上下文: {self.context})"
        return base_msg


class FileIOError(DeduplicationError):
    """文件IO错误"""

    def __init__(self, message: str, file_path: Optional[str] = None,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.FILE_IO, original_error, context)
        self.file_path = file_path


class PermissionError(DeduplicationError):
    """权限错误"""

    def __init__(self, message: str, resource: Optional[str] = None,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.PERMISSION, original_error, context)
        self.resource = resource


class ValidationError(DeduplicationError):
    """验证错误"""

    def __init__(self, message: str, field: Optional[str] = None,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.VALIDATION, original_error, context)
        self.field = field


class ProcessingError(DeduplicationError):
    """处理错误"""

    def __init__(self, message: str, operation: Optional[str] = None,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.PROCESSING, original_error, context)
        self.operation = operation


class UIError(DeduplicationError):
    """用户界面错误"""

    def __init__(self, message: str, component: Optional[str] = None,
                 original_error: Optional[Exception] = None, context: Optional[Dict] = None):
        super().__init__(message, ErrorCategory.UI, original_error, context)
        self.component = component


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self, log_file: Optional[str] = None, enable_gui: bool = True):
        self.log_file = log_file or self._get_default_log_file()
        self.enable_gui = enable_gui and TKINTER_AVAILABLE
        self.error_callbacks: Dict[ErrorLevel, List[Callable]] = {
            level: [] for level in ErrorLevel
        }
        self._setup_logging()

    def _get_default_log_file(self) -> str:
        """获取默认日志文件路径"""
        app_dir = Path.home() / ".image_dedup"
        app_dir.mkdir(exist_ok=True)
        return str(app_dir / "error_log.txt")

    def _setup_logging(self):
        """设置日志系统"""
        # 配置日志格式
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=logging.DEBUG,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        # 设置logger
        self.logger = logging.getLogger("ImageDedup")
        self.logger.setLevel(logging.DEBUG)

    def add_error_callback(self, level: ErrorLevel, callback: Callable[[DeduplicationError], None]):
        """添加错误回调函数"""
        if level in self.error_callbacks:
            self.error_callbacks[level].append(callback)

    def remove_error_callback(self, level: ErrorLevel, callback: Callable[[DeduplicationError], None]):
        """移除错误回调函数"""
        if level in self.error_callbacks and callback in self.error_callbacks[level]:
            self.error_callbacks[level].remove(callback)

    def handle_error(self, error: Union[Exception, str], level: ErrorLevel = ErrorLevel.ERROR,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    context: Optional[Dict] = None, show_user: bool = True):
        """
        统一错误处理入口

        Args:
            error: 错误对象或错误消息
            level: 错误级别
            category: 错误类别
            context: 错误上下文
            show_user: 是否向用户显示
        """
        # 标准化错误对象
        dedup_error = self._normalize_error(error, category, context)

        # 记录日志
        self._log_error(dedup_error, level)

        # 调用回调函数
        self._invoke_callbacks(dedup_error, level)

        # 向用户显示
        if show_user and self.enable_gui:
            self._show_error_to_user(dedup_error, level)

    def _normalize_error(self, error: Union[Exception, str], category: ErrorCategory,
                        context: Optional[Dict]) -> DeduplicationError:
        """标准化错误对象"""
        if isinstance(error, DeduplicationError):
            return error
        elif isinstance(error, Exception):
            # 根据异常类型创建对应的错误
            if isinstance(error, (FileNotFoundError, PermissionError, OSError)):
                return DeduplicationError(
                    str(error), ErrorCategory.FILE_IO, error, context
                )
            elif isinstance(error, ValueError):
                return ValidationError(str(error), original_error=error, context=context)
            else:
                return DeduplicationError(
                    str(error), category, error, context
                )
        else:
            # 字符串错误消息
            return DeduplicationError(str(error), category, context=context)

    def _log_error(self, error: DeduplicationError, level: ErrorLevel):
        """记录错误日志"""
        log_method = {
            ErrorLevel.DEBUG: self.logger.debug,
            ErrorLevel.INFO: self.logger.info,
            ErrorLevel.WARNING: self.logger.warning,
            ErrorLevel.ERROR: self.logger.error,
            ErrorLevel.CRITICAL: self.logger.critical
        }.get(level, self.logger.error)

        # 构造日志消息
        log_msg = f"[{error.error_category.value}] {str(error)}"
        if error.context:
            log_msg += f" | Context: {error.context}"
        if error.original_error:
            log_msg += f" | Original: {type(error.original_error).__name__}: {str(error.original_error)}"

        log_method(log_msg)

        # 如果是严重错误，记录堆栈跟踪
        if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL] and error.original_error:
            self.logger.error(traceback.format_exc())

    def _invoke_callbacks(self, error: DeduplicationError, level: ErrorLevel):
        """调用错误回调函数"""
        for callback in self.error_callbacks[level]:
            try:
                callback(error)
            except Exception as e:
                self.logger.error(f"Error in error callback: {str(e)}")

    def _show_error_to_user(self, error: DeduplicationError, level: ErrorLevel):
        """向用户显示错误信息"""
        if not TKINTER_AVAILABLE:
            return

        # 根据错误级别和类别构造用户友好的消息
        user_message = self._create_user_message(error, level)

        try:
            if level == ErrorLevel.CRITICAL:
                messagebox.showerror("严重错误", user_message)
            elif level == ErrorLevel.ERROR:
                messagebox.showerror("错误", user_message)
            elif level == ErrorLevel.WARNING:
                messagebox.showwarning("警告", user_message)
            elif level == ErrorLevel.INFO:
                messagebox.showinfo("信息", user_message)
        except Exception as e:
            self.logger.error(f"Failed to show error dialog: {str(e)}")

    def _create_user_message(self, error: DeduplicationError, level: ErrorLevel) -> str:
        """创建用户友好的错误消息"""
        # 基础消息
        message = str(error)

        # 根据错误类别添加建议
        suggestions = {
            ErrorCategory.FILE_IO: [
                "请检查文件是否存在且有访问权限。",
                "确保磁盘空间充足。",
                "检查文件是否被其他程序占用。"
            ],
            ErrorCategory.PERMISSION: [
                "请以管理员身份运行程序。",
                "检查文件/目录权限设置。",
                "确保有足够的访问权限。"
            ],
            ErrorCategory.VALIDATION: [
                "请检查输入参数是否正确。",
                "确保文件格式受支持。",
                "检查设置值是否在有效范围内。"
            ],
            ErrorCategory.PROCESSING: [
                "请尝试重新操作。",
                "检查系统资源是否充足。",
                "如果问题持续，请重启应用程序。"
            ],
            ErrorCategory.UI: [
                "请刷新界面或重新启动应用。",
                "检查系统显示设置。",
                "如果界面无响应，请强制关闭应用。"
            ]
        }

        # 添加建议
        if error.error_category in suggestions:
            suggestion = suggestions[error.error_category][0]
            message += f"\n\n建议: {suggestion}"

        # 添加操作建议
        if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
            message += "\n\n如果问题持续存在，请查看日志文件或联系技术支持。"

        return message


class SafeExecutor:
    """安全执行器 - 用于包装可能出错的操作"""

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler

    def execute(self, func: Callable, error_level: ErrorLevel = ErrorLevel.ERROR,
                error_category: ErrorCategory = ErrorCategory.UNKNOWN,
                context: Optional[Dict] = None, show_user: bool = True,
                default_return: Any = None, *args, **kwargs) -> Any:
        """
        安全执行函数

        Args:
            func: 要执行的函数
            error_level: 错误级别
            error_category: 错误类别
            context: 错误上下文
            show_user: 是否向用户显示错误
            default_return: 出错时的默认返回值
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果或默认返回值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.error_handler.handle_error(
                e, error_level, error_category, context, show_user
            )
            return default_return

    def execute_file_operation(self, func: Callable, file_path: str, *args, **kwargs) -> Any:
        """安全执行文件操作"""
        context = {"file_path": file_path, "operation": func.__name__}
        return self.execute(
            func, ErrorLevel.ERROR, ErrorCategory.FILE_IO,
            context, True, None, file_path, *args, **kwargs
        )

    def execute_image_processing(self, func: Callable, image_path: str, *args, **kwargs) -> Any:
        """安全执行图片处理操作"""
        context = {"image_path": image_path, "operation": func.__name__}
        return self.execute(
            func, ErrorLevel.ERROR, ErrorCategory.PROCESSING,
            context, True, None, image_path, *args, **kwargs
        )


# 全局错误处理器实例
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_global_error_handler(handler: ErrorHandler):
    """设置全局错误处理器"""
    global _global_error_handler
    _global_error_handler = handler


def handle_error(error: Union[Exception, str], level: ErrorLevel = ErrorLevel.ERROR,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 context: Optional[Dict] = None, show_user: bool = True):
    """全局错误处理函数"""
    handler = get_global_error_handler()
    handler.handle_error(error, level, category, context, show_user)


def safe_execute(func: Callable, error_level: ErrorLevel = ErrorLevel.ERROR,
                 error_category: ErrorCategory = ErrorCategory.UNKNOWN,
                 context: Optional[Dict] = None, show_user: bool = True,
                 default_return: Any = None, *args, **kwargs) -> Any:
    """全局安全执行函数"""
    handler = get_global_error_handler()
    executor = SafeExecutor(handler)
    return executor.execute(func, error_level, error_category, context,
                          show_user, default_return, *args, **kwargs)


# 装饰器函数
def safe_operation(error_level: ErrorLevel = ErrorLevel.ERROR,
                  error_category: ErrorCategory = ErrorCategory.UNKNOWN,
                  show_user: bool = True, default_return: Any = None):
    """安全操作装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return safe_execute(func, error_level, error_category, None,
                             show_user, default_return, *args, **kwargs)
        return wrapper
    return decorator


def safe_file_operation(func):
    """安全文件操作装饰器"""
    def decorator(file_path, *args, **kwargs):
        handler = get_global_error_handler()
        executor = SafeExecutor(handler)
        return executor.execute_file_operation(func, file_path, *args, **kwargs)
    return decorator


def safe_image_processing(func):
    """安全图片处理装饰器"""
    def decorator(image_path, *args, **kwargs):
        handler = get_global_error_handler()
        executor = SafeExecutor(handler)
        return executor.execute_image_processing(func, image_path, *args, **kwargs)
    return decorator


# 便利函数
def log_info(message: str, context: Optional[Dict] = None):
    """记录信息"""
    handle_error(message, ErrorLevel.INFO, ErrorCategory.UNKNOWN, context, False)


def log_warning(message: str, context: Optional[Dict] = None):
    """记录警告"""
    handle_error(message, ErrorLevel.WARNING, ErrorCategory.UNKNOWN, context, False)


def log_error(message: str, context: Optional[Dict] = None, show_user: bool = False):
    """记录错误"""
    handle_error(message, ErrorLevel.ERROR, ErrorCategory.UNKNOWN, context, show_user)


def log_debug(message: str, context: Optional[Dict] = None):
    """记录调试信息"""
    handle_error(message, ErrorLevel.DEBUG, ErrorCategory.UNKNOWN, context, False)


# 导出
__all__ = [
    'ErrorLevel', 'ErrorCategory',
    'DeduplicationError', 'FileIOError', 'PermissionError', 'ValidationError',
    'ProcessingError', 'UIError',
    'ErrorHandler', 'SafeExecutor',
    'get_global_error_handler', 'set_global_error_handler',
    'handle_error', 'safe_execute',
    'safe_operation', 'safe_file_operation', 'safe_image_processing',
    'log_info', 'log_warning', 'log_error', 'log_debug'
]