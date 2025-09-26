import sys
from PyQt6.QtWidgets import QApplication, QLabel

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("QApplication created")
    
    print("Creating label...")
    label = QLabel('Hello PyQt6!')
    label.resize(200, 100)
    label.move(300, 300)
    label.setWindowTitle('Simple PyQt6 Test')
    print("Label created")
    
    print("Showing label...")
    label.show()
    print("Label shown")
    
    print("Starting event loop...")
    result = app.exec()
    print(f"Event loop finished with result: {result}")
    return result

if __name__ == '__main__':
    print("Starting simple PyQt6 test...")
    exit_code = main()
    print(f"Program exiting with code: {exit_code}")
    sys.exit(exit_code)