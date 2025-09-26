import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QTimer

class ForegroundPyQt6App(QWidget):
    """
    确保窗口在前台显示的PyQt6测试程序
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6前台测试")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("PyQt6测试窗口 - 应该在前台显示")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        info_label = QLabel("如果看到这个窗口，说明PyQt6正常工作")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        close_btn = QPushButton("关闭程序")
        close_btn.clicked.connect(self.close_application)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # 确保窗口激活
        self.activateWindow()
        self.raise_()
        
        # 定时器确保窗口保持在前台
        self.timer = QTimer()
        self.timer.timeout.connect(self.bring_to_front)
        self.timer.start(1000)  # 每秒检查一次
        
    def bring_to_front(self):
        """将窗口带到前台"""
        self.activateWindow()
        self.raise_()
        
    def close_application(self):
        """关闭应用程序"""
        self.timer.stop()
        self.close()


def main():
    print("开始创建PyQt6应用程序...")
    
    # 确保使用正确的Qt平台插件
    os.environ["QT_QPA_PLATFORM"] = "windows"
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    print("PyQt6应用程序实例已创建")
    
    # 创建窗口
    window = ForegroundPyQt6App()
    print("窗口实例已创建")
    
    # 显示窗口
    window.show()
    print("窗口已显示")
    
    # 确保窗口激活
    window.activateWindow()
    window.raise_()
    
    # 打印窗口状态
    print(f"窗口是否可见: {window.isVisible()}")
    print(f"窗口是否隐藏: {window.isHidden()}")
    
    # 运行应用程序
    print("开始运行应用程序事件循环...")
    exit_code = app.exec()
    print(f"应用程序已退出，退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    print("程序开始执行")
    main()