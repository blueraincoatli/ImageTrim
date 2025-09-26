import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class DebugPyQt6App(QWidget):
    """
    带调试信息的PyQt6测试程序
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6调试测试")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("PyQt6测试窗口")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel("如果看到这个窗口，说明PyQt6正常工作")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # 打印调试信息
        print("窗口已创建")
        print(f"窗口标题: {self.windowTitle()}")
        print(f"窗口几何位置: {self.geometry()}")


def main():
    print("开始创建PyQt6应用程序...")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    print("PyQt6应用程序实例已创建")
    
    # 创建窗口
    window = DebugPyQt6App()
    print("窗口实例已创建")
    
    # 显示窗口
    window.show()
    print("窗口已显示")
    
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