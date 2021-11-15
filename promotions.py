from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from paths import EDIT_ICON

class FaderWidget(QWidget):
    def __init__(self, old_widget, new_widget): 
        QWidget.__init__(self, new_widget) 
        self.pixmap_opacity = 1.0  
        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(400)
        self.resize(new_widget.size())
        self.timeline.start()  
        self.show()
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()
    
    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class StackedWidget(QStackedWidget):
    def __init__(self, parent = None):
        QStackedWidget.__init__(self, parent)
    
    def setIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        self.setCurrentIndex(index)
    
    def login(self):
        self.setIndex(0)
    
    def userManagement(self):
        self.setIndex(1)

    def editUser(self):
        self.setIndex(2)

    def mainLaser(self):
        self.setIndex(3)

    def newSession(self):
        self.setIndex(4)

    def female(self):
        self.setIndex(0)

    def male(self):
        self.setIndex(1)

    def bodyPart(self):
        self.setIndex(0)

    def laser(self):
        self.setIndex(1)



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


