import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6测试窗口")
        self.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout()
        label = QLabel("如果看到这个窗口，说明PyQt6正常工作！")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

def main():
    print("创建QApplication...")
    app = QApplication(sys.argv)
    print("QApplication创建成功")
    
    print("创建窗口...")
    window = TestWindow()
    print("窗口创建成功")
    
    print("显示窗口...")
    window.show()
    print("窗口显示成功")
    
    print("运行事件循环...")
    result = app.exec()
    print(f"事件循环结束，返回值: {result}")
    return result

if __name__ == "__main__":
    print("程序开始")
    exit_code = main()
    print(f"程序结束，退出码: {exit_code}")
    sys.exit(exit_code)