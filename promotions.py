from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from paths import EDIT_ICON


class Action(QWidget):
    delete = pyqtSignal(str)
    edit = pyqtSignal(str)
    def __init__(self, parent, number):
        super().__init__(parent)
        self.number = number
        stylesheet = """QPushButton {
                            border-radius:10px;
                            outline:0;
                        }
                        QPushButton:pressed{
                            border:3px solid red;
                        }"""
                    
        layout = QHBoxLayout(self)
        btn_edit = QPushButton(self)
        editIcon = QIcon()
        editIcon.addPixmap(QPixmap(EDIT_ICON), QIcon.Normal, QIcon.Off)
        btn_edit.setIcon(editIcon)
        btn_edit.setIconSize(QSize(50, 50))
        btn_edit.setStyleSheet(stylesheet)
        btn_edit.clicked.connect(lambda: self.edit.emit(self.number))

        spacerItem = QSpacerItem(
            40, 20, 
            QSizePolicy.Expanding, 
            QSizePolicy.Minimum
        )
        layout.addItem(spacerItem)
        layout.addWidget(btn_edit)
        spacerItem1 = QSpacerItem(
            40, 20, 
            QSizePolicy.Expanding, 
            QSizePolicy.Minimum
        )
        layout.addItem(spacerItem1)



class LineEdit(QLineEdit):
    fIn = pyqtSignal()
    def __init__(self, parent):
        super(LineEdit, self).__init__()
        self.parent = parent

    def mousePressEvent(self, QMouseEvent):
        super(LineEdit, self).mousePressEvent(QMouseEvent)
        self.fIn.emit()

class TextEdit(QTextEdit):
    fIn = pyqtSignal()
    def __init__(self, parent):
        super(TextEdit, self).__init__()
        self.parent = parent

    def mousePressEvent(self, QMouseEvent):
        super(TextEdit, self).mousePressEvent(QMouseEvent)
        self.fIn.emit()

class TableWidgetItem(QTableWidgetItem):
    def __init__(self, parent = None):
        QTableWidgetItem.__init__(self, parent)
        self.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


