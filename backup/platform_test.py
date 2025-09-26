import sys
from PyQt6.QtWidgets import QApplication

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print(f"Platform name: {app.platformName()}")
    print("Test completed")

if __name__ == '__main__':
    main()