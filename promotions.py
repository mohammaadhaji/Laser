from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from paths import INFORMATION_ICON


class Action(QWidget):
    edit = pyqtSignal(str)
    def __init__(self, parent, number):
        super().__init__(parent)
        self.number = number
        stylesheet = """QPushButton {
                            border-radius:10px;
                            outline:0;
                        }
                        QPushButton:pressed{
                        margin: 10px 0 0 0;
                        }
                        """
                    
        layout = QHBoxLayout(self)
        btn_edit = QPushButton(self)
        editIcon = QIcon()
        editIcon.addPixmap(QPixmap(INFORMATION_ICON), QIcon.Normal, QIcon.Off)
        btn_edit.setIcon(editIcon)
        btn_edit.setIconSize(QSize(60, 60))
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

class VideoWidget(QVideoWidget):
        def __init__(self, parent = None):
            QVideoWidget.__init__(self, parent)

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Escape and self.isFullScreen():
                self.setFullScreen(False)
                event.accept()
            elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
                self.setFullScreen(not self.isFullScreen())
                event.accept()

        def mouseDoubleClickEvent(self, event):
            self.setFullScreen(not self.isFullScreen())
            event.accept()

class ToggleButton(QCheckBox):
    def __init__(
        self,
        width=120,
        bgColor="#777",
        circleColor="#DDD",
        activeColor="#00BCff",
        animationCurve=QEasingCurve.Linear,
    ):
        QCheckBox.__init__(self)
        # self.setFixedSize(width, 48)
        self.setCursor(Qt.PointingHandCursor)

        self._bg_color = bgColor
        self._circle_color = circleColor
        self._active_color = activeColor
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circle_position")

        self.animation.setEasingCurve(animationCurve)
        self.animation.setDuration(200)
        self.stateChanged.connect(self.start_transition)

    @pyqtProperty(int)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_transition(self, value):
        self.animation.setStartValue(self.circle_position)
        if value:
            self.animation.setEndValue(self.width() - 45)
        else:
            self.animation.setEndValue(3)
        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(Qt.NoPen)

        rect = QRect(0, 0, self.width(), self.height())

        if not self.isChecked():
            p.setBrush(QColor(self._bg_color))
            p.drawRoundedRect(
                0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2
            )
        
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._circle_position, 3, 42, 42)
        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(
                0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2
            )

            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._circle_position, 3, 42, 42)


class Label(QLabel):
    clicked=pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()
