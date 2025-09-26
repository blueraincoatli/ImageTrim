import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.pyqt6_deduplication_module import PyQt6DeduplicationModule
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
import threading

class DedupTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.module = PyQt6DeduplicationModule()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("选择一个文件夹来测试去重功能")
        layout.addWidget(self.label)
        
        self.btn = QPushButton("选择文件夹")
        self.btn.clicked.connect(self.select_folder)
        layout.addWidget(self.btn)
        
        self.setLayout(layout)
        self.setWindowTitle("去重模块测试")
        self.setGeometry(300, 300, 300, 200)
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.test_dedup(folder)
            
    def test_dedup(self, folder):
        self.label.setText(f"正在扫描文件夹: {folder}")
        
        # 在单独的线程中运行去重功能
        def run_dedup():
            try:
                params = {
                    'paths': [folder],
                    'sensitivity': 95.0,
                    'subdirs': True
                }
                self.module.execute(params)
                self.label.setText("扫描完成")
            except Exception as e:
                self.label.setText(f"错误: {str(e)}")
                
        thread = threading.Thread(target=run_dedup)
        thread.start()

def main():
    app = QApplication(sys.argv)
    window = DedupTestApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()