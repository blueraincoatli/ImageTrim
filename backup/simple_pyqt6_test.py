import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Test Window")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("PyQt6 is working correctly!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Add description
        description = QLabel("If you can see this window, PyQt6 is functioning properly.")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(description)
        
        # Add button
        button = QPushButton("Close")
        button.clicked.connect(self.close)
        layout.addWidget(button)
        
        # Set window background
        self.setStyleSheet("background-color: #2b2b2b;")

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("Creating main window...")
    window = TestMainWindow()
    print("Showing window...")
    window.show()
    print("Running event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()