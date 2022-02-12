import sys

import PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi("../UI/Menu.ui", self)
        self.maximumWidth()
        self.setMaximumSize(950, 720)
        self.setMinimumSize(950, 720)
        self.setWindowTitle("MENU")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())