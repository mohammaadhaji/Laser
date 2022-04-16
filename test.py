import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.b = QPushButton("exit", self, clicked=self.close)
        self.setWindowOpacity(.8)
        self.setStyleSheet("QMainWindow { background: 'black'}");

        self.dialog = QDialog()
        self.dialog.setModal(True)
        self.dialog.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MyWindow()
    myapp.setGeometry(app.desktop().screenGeometry())
    myapp.show()
    sys.exit(app.exec_())