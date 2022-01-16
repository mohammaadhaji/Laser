from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtCore
from paths import *
from styles import ACTION_BTN, CHECKBOX_DEL


class Action(QWidget):
    info = pyqtSignal(str)
    delete = pyqtSignal(str)
    def __init__(self, parent, number):
        super().__init__(parent)
        self.number = number
        stylesheet = ACTION_BTN
        layout = QHBoxLayout(self)
        self.btnInfo = QPushButton(self)
        infoIcon = QIcon()
        infoIcon.addPixmap(QPixmap(INFORMATION_ICON), QIcon.Normal, QIcon.Off)
        self.btnInfo.setIcon(infoIcon)
        self.btnInfo.setIconSize(QSize(60, 60))
        self.btnInfo.setStyleSheet(stylesheet)
        self.btnInfo.clicked.connect(lambda: self.info.emit(self.number))

        self.chbDel = QCheckBox(self)
        self.chbDel.setMinimumSize(QtCore.QSize(60, 60))
        self.chbDel.setStyleSheet(CHECKBOX_DEL)
        self.chbDel.toggled.connect(lambda: self.delete.emit(self.number))

        spacerItem = QSpacerItem(
            40, 20, 
            QSizePolicy.Expanding, 
            QSizePolicy.Minimum
        )
        layout.addItem(spacerItem)
        layout.addWidget(self.btnInfo)
        spacerItem1 = QSpacerItem(
            40, 20, 
            QSizePolicy.Expanding, 
            QSizePolicy.Minimum
        )
        layout.addItem(spacerItem1)
        layout.addWidget(self.chbDel)
        spacerItem2 = QSpacerItem(
            40, 20, 
            QSizePolicy.Expanding, 
            QSizePolicy.Minimum
        )
        layout.addItem(spacerItem2)

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

    @QtCore.pyqtProperty(int)
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


class StackedWidget(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        super(QStackedWidget, self).__init__(parent)

        self.fadeTransition = False
        self.slideTransition = False
        self.transitionDirection = QtCore.Qt.Vertical
        self.transitionTime = 500
        self.fadeTime = 500
        self.transitionEasingCurve = QtCore.QEasingCurve.OutBack
        self.fadeEasingCurve = QtCore.QEasingCurve.Linear
        self.currentWidget = 0
        self.nextWidget = 0
        self._currentWidgetPosition = QtCore.QPoint(0, 0)
        self.widgetActive = False
                            
    def setTransitionDirection(self, direction):
        self.transitionDirection = direction

    def setTransitionSpeed(self, speed):
        self.transitionTime = speed

    def setFadeSpeed(self, speed):
        self.fadeTime = speed

    def setTransitionEasingCurve(self, aesingCurve):
        self.transitionEasingCurve = aesingCurve

    def setFadeCurve(self, aesingCurve):
        self.fadeEasingCurve = aesingCurve

    def setFadeTransition(self, fadeState):
        if isinstance(fadeState, bool):
            self.fadeTransition = fadeState
        else:
            raise Exception("setFadeTransition() only accepts boolean variables")

    def setSlideTransition(self, slideState):
        if isinstance(slideState, bool):
            self.slideTransition = slideState
        else:
            raise Exception("setSlideTransition() only accepts boolean variables")

    @QtCore.pyqtSlot()
    def slideToPreviousWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex > 0:
            self.slideToWidgetIndex(currentWidgetIndex - 1)

    @QtCore.pyqtSlot()
    def slideToNextWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex < (self.count() - 1):
            self.slideToWidgetIndex(currentWidgetIndex + 1)

    def slideToWidgetIndex(self, index):
        if index > (self.count() - 1):
            index = index % self.count()
        elif index < 0:
            index = (index + self.count()) % self.count()
        if self.slideTransition:
            self.slideToWidget(self.widget(index))
        else:
            self.setCurrentIndex(index)

    def slideToWidget(self, newWidget):
        if self.widgetActive:
            return

        self.widgetActive = True

        _currentWidgetIndex = self.currentIndex()
        _nextWidgetIndex = self.indexOf(newWidget)

        if _currentWidgetIndex == _nextWidgetIndex:
            self.widgetActive = False
            return

        offsetX, offsetY = self.frameRect().width(), self.frameRect().height()
        self.widget(_nextWidgetIndex).setGeometry(self.frameRect())

        if not self.transitionDirection == QtCore.Qt.Horizontal:
            if _currentWidgetIndex < _nextWidgetIndex:
                offsetX, offsetY = 0, -offsetY
            else:
                offsetX = 0
        else:
            if _currentWidgetIndex < _nextWidgetIndex:
                offsetX, offsetY = -offsetX, 0
            else:
                offsetY = 0

        nextWidgetPosition = self.widget(_nextWidgetIndex).pos()
        currentWidgetPosition = self.widget(_currentWidgetIndex).pos()
        self._currentWidgetPosition = currentWidgetPosition

        offset = QtCore.QPoint(offsetX, offsetY)
        self.widget(_nextWidgetIndex).move(nextWidgetPosition - offset)
        self.widget(_nextWidgetIndex).show()
        self.widget(_nextWidgetIndex).raise_()

        anim_group = QtCore.QParallelAnimationGroup(
            self, finished=self.animationDoneSlot
        )

        for index, start, end in zip(
            (_currentWidgetIndex, _nextWidgetIndex), 
            (currentWidgetPosition, nextWidgetPosition - offset), 
            (currentWidgetPosition + offset, nextWidgetPosition)
        ):
            animation = QtCore.QPropertyAnimation(
                self.widget(index),
                b"pos",
                duration=self.transitionTime,
                easingCurve=self.transitionEasingCurve,
                startValue=start,
                endValue=end,
            )
            anim_group.addAnimation(animation)

        self.nextWidget = _nextWidgetIndex
        self.currentWidget = _currentWidgetIndex

        self.widgetActive = True
        anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        if self.fadeTransition:
            FadeWidgetTransition(self, self.widget(_currentWidgetIndex), self.widget(_nextWidgetIndex))

    @QtCore.pyqtSlot()
    def animationDoneSlot(self):
        self.setCurrentIndex(self.nextWidget)
        self.widget(self.currentWidget).hide()
        self.widget(self.currentWidget).move(self._currentWidgetPosition)
        self.widgetActive = False

    @QtCore.pyqtSlot()
    def setCurrentWidget(self, widget):
        currentIndex = self.currentIndex()
        nextIndex = self.indexOf(widget)
        if self.currentIndex() == self.indexOf(widget):
            return
        if self.slideTransition:
            self.slideToWidgetIndex(nextIndex)

        if self.fadeTransition:
            self.fader_widget = FadeWidgetTransition(self, self.widget(self.currentIndex()), self.widget(self.indexOf(widget)))
            if not self.slideTransition:
                self.setCurrentIndex(nextIndex)

        if not self.slideTransition and not self.fadeTransition:
            self.setCurrentIndex(nextIndex)

class FadeWidgetTransition(QWidget):
    def __init__(self, animationSettings, oldWidget, newWidget):
    
        QWidget.__init__(self, newWidget)
        
        self.oldPixmap = QPixmap(newWidget.size())
        oldWidget.render(self.oldPixmap)
        self.pixmapOpacity = 1.0
        
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(animationSettings.fadeTime)
        self.timeline.setEasingCurve(animationSettings.fadeEasingCurve)
        self.timeline.start()
        
        self.resize(newWidget.size())
        self.show()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmapOpacity)
        painter.drawPixmap(0, 0, self.oldPixmap)
        painter.end()
    
    def animate(self, value):    
        self.pixmapOpacity = 1.0 - value
        self.repaint()

