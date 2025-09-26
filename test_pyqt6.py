import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

def main():
    app = QApplication(sys.argv)
    
    # 创建一个简单的窗口
    window = QWidget()
    window.setWindowTitle('PyQt6测试窗口')
    window.setGeometry(100, 100, 300, 200)
    
    # 添加一个标签
    layout = QVBoxLayout()
    label = QLabel('如果看到这个窗口，说明PyQt6运行正常！')
    layout.addWidget(label)
    window.setLayout(layout)
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == '__main__':
    main()