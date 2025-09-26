# -*- coding: utf-8 -*-
"""
工具模块包
包含核心业务逻辑、UI组件、错误处理等通用模块
"""

from .deduplication_core import (
    DeduplicationEngine,
    DeduplicationConfig,
    ScanResult,
    ImageHashCalculator,
    DuplicateFinder,
    DirectoryScanner
)

from .ui_components import (
    UIFactory,
    ScrollableFrame,
    ImageDisplayHelper,
    DialogManager,
    GridLayoutManager,
    StyleManager,
    create_standard_settings_ui
)

from .error_handler import (
    ErrorLevel, ErrorCategory,
    DeduplicationError, FileIOError, PermissionError, ValidationError,
    ProcessingError, UIError,
    ErrorHandler, SafeExecutor,
    get_global_error_handler, set_global_error_handler,
    handle_error, safe_execute,
    safe_operation, safe_file_operation, safe_image_processing,
    log_info, log_warning, log_error, log_debug
)

__all__ = [
    'DeduplicationEngine',
    'DeduplicationConfig',
    'ScanResult',
    'ImageHashCalculator',
    'DuplicateFinder',
    'DirectoryScanner',
    'UIFactory',
    'ScrollableFrame',
    'ImageDisplayHelper',
    'DialogManager',
    'GridLayoutManager',
    'StyleManager',
    'create_standard_settings_ui',
    'ErrorLevel', 'ErrorCategory',
    'DeduplicationError', 'FileIOError', 'PermissionError', 'ValidationError',
    'ProcessingError', 'UIError',
    'ErrorHandler', 'SafeExecutor',
    'get_global_error_handler', 'set_global_error_handler',
    'handle_error', 'safe_execute',
    'safe_operation', 'safe_file_operation', 'safe_image_processing',
    'log_info', 'log_warning', 'log_error', 'log_debug'
]