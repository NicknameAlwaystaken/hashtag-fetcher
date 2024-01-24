import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from gui import mainwindow
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = mainwindow.MainWindow()
    window.resize(1000, 800)
    window.show()

    app.exec()