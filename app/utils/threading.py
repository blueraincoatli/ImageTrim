#!/usr/bin/env python3
"""
多线程处理工具
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any, Optional


class WorkerThread(QThread):
    """
    工作线程类
    """
    
    # 定义信号
    progress_updated = pyqtSignal(float, str)  # 进度更新 (百分比, 消息)
    log_message = pyqtSignal(str, str)         # 日志消息 (消息, 级别)
    finished_signal = pyqtSignal(object)       # 执行完成 (结果)

    def __init__(self, target: Callable, *args, **kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result: Optional[Any] = None

    def run(self):
        """执行任务"""
        try:
            self.result = self.target(*self.args, **self.kwargs)
            self.finished_signal.emit(self.result)
        except Exception as e:
            self.log_message.emit(str(e), "error")
            self.finished_signal.emit(None)