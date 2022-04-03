from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from werkzeug.utils import cached_property
from communication import HARDWARE_TEST_PAGE, READ, sendPacket
from styles import *
from paths import *
import math

class WebEngineView(QWebEngineView):
    def __init__(self, parent):
        QWebEngineView.__init__(self, parent)
        self.isLoaded = False
        self.loadFinished.connect(self.setIsLoaded)

    def setIsLoaded(self):
        self.isLoaded = True



class PowerOption(QFrame):
    shutdown = pyqtSignal()
    restart  = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumSize(QSize(385, 0))
        self.setMaximumSize(QSize(16777215, 0))
        self.setStyleSheet(POWER_OPTION_L)
        self.verticalLayout_1 = QVBoxLayout(self)
        self.verticalLayout_1.setContentsMargins(-1, 10, 47, -1)
        self.verticalLayout_1.setSpacing(0)
        self.verticalLayout_1.setObjectName("verticalLayout_81")
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setSpacing(0)
        self.horizontalLayout_1.setObjectName("horizontalLayout_81")
        self.label_1 = QLabel(self)
        self.label_1.setStyleSheet("QLabel {\n"
"    border-top-left-radius: 15px;\n"
"    padding: 5px 0px;\n"
"    color: rgb(255, 255, 255);\n"
"    margin-top:20px;\n"
"\n"
"}")
        self.label_1.setText("")
        self.label_1.setObjectName("label_15")
        self.horizontalLayout_1.addWidget(self.label_1)
        self.label_2 = QLabel(self)
        self.label_2.setStyleSheet("QLabel {\n"
"    border-top-right-radius: 20px;\n"
"    border-top-left-radius: 20px;\n"
"    padding: 5px 0px;\n"
"    max-width:40px;\n"
"    min-width:40px;\n"
"    color: rgb(12, 12, 12);\n"
"}")
        self.label_2.setText("")
        self.label_2.setObjectName("label_16")
        self.horizontalLayout_1.addWidget(self.label_2)
        self.label_3 = QLabel(self)
        self.label_3.setStyleSheet("QLabel {\n"
"    border-top-right-radius: 15px;\n"
"    padding: 5px 0px;\n"
"    color: rgb(255, 255, 255);\n"
"    margin-top:20px;\n"
"}")
        self.label_3.setText("")
        self.label_3.setObjectName("label_17")
        self.horizontalLayout_1.addWidget(self.label_3)
        self.horizontalLayout_1.setStretch(0, 9)
        self.horizontalLayout_1.setStretch(1, 1)
        self.horizontalLayout_1.setStretch(2, 1)
        self.verticalLayout_1.addLayout(self.horizontalLayout_1)
        self.frame_1 = QFrame(self)
        self.frame_1.setStyleSheet("QFrame {\n"
"    border-bottom-left-radius: 15px;\n"
"    border-bottom-right-radius: 15px;\n"
"\n"
"}\n"
"")
        self.frame_1.setFrameShape(QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QFrame.Raised)
        self.frame_1.setObjectName("frame_8")
        self.verticalLayout_2 = QVBoxLayout(self.frame_1)
        self.verticalLayout_2.setContentsMargins(50, -1, 50, 40)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_84")
        self.btnPower = QPushButton(' Power Off', self.frame_1)
        self.btnPower.clicked.connect(self.shutdown.emit)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.btnPower.setFont(font)
        self.btnPower.setStyleSheet("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap("ui/images/poweroff.png"), QIcon.Normal, QIcon.Off)
        self.btnPower.setIcon(icon1)
        self.btnPower.setIconSize(QSize(55, 55))
        self.btnPower.setObjectName("btnPower")
        self.verticalLayout_2.addWidget(self.btnPower)
        self.btnRestart = QPushButton(' Restart     ', self.frame_1)
        self.btnRestart.clicked.connect(self.restart.emit)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.btnRestart.setFont(font)
        self.btnRestart.setStyleSheet("")
        icon2 = QIcon()
        icon2.addPixmap(QPixmap("ui/images/restart.png"), QIcon.Normal, QIcon.Off)
        self.btnRestart.setIcon(icon2)
        self.btnRestart.setIconSize(QSize(50, 50))
        self.btnRestart.setObjectName("btnRestart")
        self.verticalLayout_2.addWidget(self.btnRestart)
        self.verticalLayout_1.addWidget(self.frame_1)
        self.verticalLayout_1.setStretch(0, 1)
        self.verticalLayout_1.setStretch(1, 5)


class Relay:
    def __init__(self, btnRelay, btnPass, btnFail, field):
        self.relay = btnRelay
        self.btnPass = btnPass
        self.btnFail = btnFail
        self.field = field
        self.relay.setStyleSheet(RELAY_STYLE)
        self.btnPass.setStyleSheet(PASS_FAIL_STYLE)
        self.btnFail.setStyleSheet(PASS_FAIL_STYLE)
        self.relay.clicked.connect(self.listen)
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap(RELAY_ICON))
        self.relay.setIcon(self.icon)
        self.relay.setIconSize(QSize(100, 100))
        self.movie = QMovie(RELAY_GIF)
        self.movie.frameChanged.connect(lambda: self.relay.setIcon(QIcon(self.movie.currentPixmap())))
        self.relayTimer = QTimer()
        self.resultTimer = QTimer()
        self.isListening = False
        self.resultTimer.timeout.connect(self.result)
        self.relayTimer.timeout.connect(self.relayFinish)
        self.tests = [False, False, False]

    def setTests(self, step_status):
        step   = step_status[0]
        status = step_status[1]
        if self.isListening:
            if step == 1:
                if status == 0:
                    self.tests[0] = True
                else:
                    self.tests[0] = False

            elif step == 2:
                if status == 1:
                    self.tests[1] = True
                else:
                    self.tests[1] = False

            elif step == 3:
                if status == 0:
                    self.tests[2] = True
                else:
                    self.tests[2] = False
        
    def listen(self):
        self.isListening = True
        self.relay.setEnabled(False)
        self.movie.start()
        self.relayTimer.start(3500)
        sendPacket({'relay':self.field}, {'relay': ''}, HARDWARE_TEST_PAGE, READ)
        
    def relayFinish(self):
        self.relayTimer.stop()
        self.movie.stop()
        self.isListening = False
        self.relay.setEnabled(True)
        self.relay.setIcon(self.icon)

        if self.tests[0] and self.tests[1] and self.tests[2]:
            self.btnPass.setStyleSheet(PASS_STYLE)
        else:
             self.btnFail.setStyleSheet(FAIL_STYLE) 

        self.tests = [False, False, False]
        self.resultTimer.start(3000)

    def result(self):
        self.resultTimer.stop()
        self.btnPass.setStyleSheet(PASS_FAIL_STYLE)
        self.btnFail.setStyleSheet(PASS_FAIL_STYLE)


class SensorTest:
    def __init__(self, **kwarg):
        self.widgets = kwarg

    def setOk(self, ok):
        if ok:
            self.widgets['btnOk'].setStyleSheet(SENSOR_OK_TEST_STYLE)
            self.widgets['btnNotOk'].setStyleSheet(SENSOR_TEST_STYLE)
        else:
            self.widgets['btnOk'].setStyleSheet(SENSOR_TEST_STYLE)
            self.widgets['btnNotOk'].setStyleSheet(SENSOR_NOT_OK_TEST_STYLE)

    def setValue(self, value):
        self.widgets['txt'].setText(f"{value}  {self.widgets['unit']}")


class DriverCurrent:
    def __init__(self, btnStart, gauge, field):
        self.btnStart = btnStart
        self.gauge = gauge
        self.field = field
        self.btnStart.clicked.connect(self.start)
        self.isListening = False
        self.timer = QTimer()
        self.resetTimer = QTimer()
        self.timer.timeout.connect(self.finish)
        self.resetTimer.timeout.connect(self.reset)
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap(DRIVER_CURRENT))
        self.btnStart.setIcon(self.icon)
        self.movie = QMovie(RELAY_GIF)
        self.movie.frameChanged.connect(
            lambda: self.btnStart.setIcon(QIcon(self.movie.currentPixmap()))
        )
        
    def reset(self):
        self.resetTimer.stop()
        self.gauge.updateValue(0)
    
    def start(self):
        self.isListening = True
        self.timer.start(2000)
        self.movie.start()
        self.btnStart.setEnabled(False)
        sendPacket({'driver': self.field}, {'driver': ''}, HARDWARE_TEST_PAGE, READ)

    def setValue(self, value):
        if self.isListening:
            self.gauge.updateValue(value)
            self.resetTimer.start(3000)
            self.finish()
            
        
    def finish(self):
        self.movie.stop()
        self.timer.stop()
        self.isListening = False
        self.btnStart.setEnabled(True)
        self.btnStart.setIcon(self.icon)
                

class Sensors:
    def __init__(
            self, lock, wl, wf, oh, pd, temp,
            lockCalib, wlCalib, wfCalib, ohCalib, pdCalib, tempCalib,
        ):
        self.flag = False
        self.lock = lock
        self.wl = wl
        self.wf = wf
        self.oh = oh
        self.pd = pd
        self.temp = temp
        self.lockCalib = lockCalib
        self.wlCalib = wlCalib
        self.wfCalib = wfCalib
        self.ohCalib = ohCalib
        self.pdCalib = pdCalib
        self.tempCalib = tempCalib        
        self.lockIco = QIcon()
        self.unlockIco = QIcon()
        self.lockIco.addPixmap(QPixmap(LOCK))
        self.unlockIco.addPixmap(QPixmap(UNLOCK))
        self.oh.setVisible(False)
        self.pd.setVisible(False)
        self.ohCalib.setVisible(False)
        self.pdCalib.setVisible(False)

    def toggle(self, status, page):
        if page == 'Laser':
            lock, wl, wf, oh, pd, temp = self.lock, self.wl, self.wf, self.oh, self.pd, self.temp
        else:
            lock, wl, wf, oh, pd, temp = self.lockCalib, self.wlCalib, self.wfCalib, self.ohCalib, self.pdCalib, self.tempCalib

        self.flag = not self.flag
        if status[0]:
            lock.setIcon(self.lockIco)
            if self.flag:
                lock.setStyleSheet(SENSOR_NOT_OK)
            else:
                lock.setStyleSheet(SENSOR_OK)
        else:
            lock.setStyleSheet(SENSOR_OK)
            lock.setIcon(self.unlockIco)

        if status[1]:
            if self.flag:
                wl.setStyleSheet(SENSOR_NOT_OK)
            else:
                wl.setStyleSheet(SENSOR_OK)
        else:
            wl.setStyleSheet(SENSOR_OK)

        if status[2]:
            if self.flag:
                wf.setStyleSheet(SENSOR_NOT_OK)
            else:
                wf.setStyleSheet(SENSOR_OK)
        else:
            wf.setStyleSheet(SENSOR_OK)

        if status[3]:
            oh.setVisible(True)
            if self.flag:
                oh.setStyleSheet(HIDDEN_SENSOR_NOT_OK)
            else:
                oh.setStyleSheet(HIDDEN_SENSOR_OK)
        else:
            oh.setVisible(False)
            oh.setStyleSheet(HIDDEN_SENSOR_OK)

        if status[4]:
            pd.setVisible(True)
            if self.flag:
                pd.setStyleSheet(HIDDEN_SENSOR_NOT_OK)
            else:
                pd.setStyleSheet(HIDDEN_SENSOR_OK)
        else:
            pd.setVisible(False)
            pd.setStyleSheet(HIDDEN_SENSOR_OK)

        if status[5]:
            if self.flag:
                temp.setStyleSheet(SENSOR_NOT_OK)
            else:
                temp.setStyleSheet(SENSOR_OK)
        else:
            temp.setStyleSheet(SENSOR_OK)
        

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


class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=3, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** 2

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value())/self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))


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


class AnalogGaugeWidget(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(AnalogGaugeWidget, self).__init__(parent)

        self.use_timer_event = False

        self.setNeedleColor(255, 0, 0, 255)

        self.NeedleColorReleased = self.NeedleColor

        self.setNeedleColorOnDrag(255, 0, 00, 255)

        self.setScaleValueColor(255, 255, 255, 255)

        self.setDisplayValueColor(255, 255, 255, 255)

        self.set_CenterPointColor(0, 0, 0, 255)

        self.value_needle_count = 3

        self.value_needle = QObject

        self.minValue = 0
        self.maxValue = 100
        self.value = self.minValue

        self.value_offset = 0

        self.valueNeedleSnapzone = 0.25
        self.last_value = 0

        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        self.scale_angle_start_value = 90
        self.scale_angle_size = 270

        self.angle_offset = 0

        self.setScalaCount(10)
        self.scala_subdiv_count = 10

        self.pen = QPen(QColor(0, 0, 0))

        QFontDatabase.addApplicationFont(VAUGE_FONT)

        self.scale_polygon_colors = []

        self.bigScaleMarker = Qt.black

        self.fineScaleColor = Qt.black

        self.setEnableScaleText(True)
        self.scale_fontname = "Orbitron"
        self.initial_scale_fontsize = 14
        self.scale_fontsize = self.initial_scale_fontsize

        self.enable_value_text = True
        self.value_fontname = "Orbitron"
        self.initial_value_fontsize = 30
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.5

        self.setEnableBarGraph(False)
        self.setEnableScalePolygon(True)
        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True

        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        self.setMouseTracking(False)
        self.setScaleStartAngle(90)

        self.units = "A"

        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        self.setGaugeTheme()
        
        self.rescale_method()

    def setGaugeTheme(self, Theme = 1):

        self.set_scale_polygon_colors([[.25, Qt.red],
                                    [.5, Qt.yellow],
                                    [.75, Qt.green]])

        self.needle_center_bg = [
                                [0, QColor(35, 40, 3, 255)], 
                                [0.16, QColor(30, 36, 45, 255)], 
                                [0.225, QColor(36, 42, 54, 255)], 
                                [0.423963, QColor(19, 23, 29, 255)], 
                                [0.580645, QColor(45, 53, 68, 255)], 
                                [0.792627, QColor(59, 70, 88, 255)], 
                                [0.935, QColor(30, 35, 45, 255)], 
                                [1, QColor(35, 40, 3, 255)]
                                ]

        self.outer_circle_bg =  [
                                [0.0645161, QColor(30, 35, 45, 255)], 
                                [0.37788, QColor(57, 67, 86, 255)], 
                                [1, QColor(30, 36, 45, 255)]
                                ]


    def rescale_method(self):
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()

        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, - self.widget_diameter / 2 * self.needle_scale_factor),
            QPoint(0, - self.widget_diameter / 2 * self.needle_scale_factor - 6),
            QPoint(2, - self.widget_diameter / 2 * self.needle_scale_factor)
        ])])


        self.scale_fontsize = self.initial_scale_fontsize * self.widget_diameter / 400
        self.value_fontsize = self.initial_value_fontsize * self.widget_diameter / 400

    def change_value_needle_style(self, design):
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()

    def updateValue(self, value, mouse_controlled = False):

        if value <= self.minValue:
            self.value = self.minValue
        elif value >= self.maxValue:
            self.value = self.maxValue
        else:
            self.value = value
        self.valueChanged.emit(int(value))

        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value

    def center_vertical(self, value):
        self.center_vertical_value = value

    def setNeedleColor(self, R=50, G=50, B=50, Transparency=255):
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()

    def setNeedleColorOnDrag(self, R=50, G=50, B=50, Transparency=255):
        self.NeedleColorDrag = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        self.ScaleValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setDisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        self.DisplayValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setEnableScaleText(self, enable = True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBarGraph(self, enable = True):
        self.enableBarGraph = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScalePolygon(self, enable = True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setScalaCount(self, count):
        if count < 1:
            count = 1
        self.scalaCount = count

        if not self.use_timer_event:
            self.update()

    def setMinValue(self, min):
        if self.value < min:
            self.value = min
        if min >= self.maxValue:
            self.minValue = self.maxValue - 1
        else:
            self.minValue = min

        if not self.use_timer_event:
            self.update()

    def setMaxValue(self, max):
        if self.value > max:
            self.value = max
        if max <= self.minValue:
            self.maxValue = self.minValue + 1
        else:
            self.maxValue = max

        if not self.use_timer_event:
            self.update()

    def setScaleStartAngle(self, value):
        self.scale_angle_start_value = value

        if not self.use_timer_event:
            self.update()


    def set_scale_polygon_colors(self, color_array):
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        if not self.use_timer_event:
            self.update()

    def get_value_max(self):
        return self.maxValue

    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght, bar_graph = True):
        polygon_pie = QPolygonF()
        n = 360     # angle steps size for full circle
        w = 360 / n   # angle per step
        x = 0
        y = 0

        if not self.enableBarGraph and bar_graph:
            lenght = int(round((lenght / (self.maxValue - self.minValue)) * (self.value - self.minValue)))
            pass


        for i in range(lenght+1):                                              # add the points of polygon
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        for i in range(lenght+1):                                              # add the points of polygon
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            painter_filled_polygon.translate(self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(self.widget_diameter / 2 - 1, self.widget_diameter - 1))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                    self.angle_offset - 1)

            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            painter_filled_polygon.setBrush(grad)
           

            painter_filled_polygon.drawPolygon(colored_scale_polygon)

    def draw_big_scaled_marker(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        my_painter.translate(self.width() / 2, self.height() / 2)

        self.pen = QPen(self.bigScaleMarker)
        self.pen.setWidth(2)
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        scale_line_outer_start = self.widget_diameter/2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 20)
        for i in range(self.scalaCount+1):
            my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter/2 * text_radius_factor

        scale_per_div = int((self.maxValue - self.minValue) / self.scalaCount)

        angle_distance = (float(self.scale_angle_size) / float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            text = str(int(self.minValue + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold))
            angle = angle_distance * i + float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))

            text = [x - int(w/2), y - int(h/2), int(w), int(h), Qt.AlignCenter, text]
            painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])

    def create_fine_scaled_marker(self):
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(self.fineScaleColor)
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter/2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 40)
        for i in range((self.scalaCount * self.scala_subdiv_count)+1):
            my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, self.value_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        self.text_radius_factor = 0.65
        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(round(self.value, 1))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, self.value_fontsize, QFont.Bold))

        angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        text = [x - int(w/2), y - int(h/2), int(w), int(h), Qt.AlignCenter, text]
        painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])

    def create_units_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, int(self.value_fontsize / 2.5), QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        self.text_radius_factor = 0.78
        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(self.value_fontsize / 2), QFont.Bold))

      

        angle_end = float(self.scale_angle_start_value + self.scale_angle_size + 310)
        angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value
        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        text = [x - int(w/2), y - int(h/2), int(w), int(h), Qt.AlignCenter, text]
        painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])


    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)



        colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 8) - (self.pen.width() / 2)),
                0,
                self.scale_angle_start_value, 360, False)


        grad = QConicalGradient(QPointF(0, 0), 0)

        for eachcolor in self.needle_center_bg:
            grad.setColorAt(eachcolor[0], eachcolor[1])
        painter.setBrush(grad)

        painter.drawPolygon(colored_scale_polygon)

    def draw_outer_circle(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width())),
                (self.widget_diameter / 6),
                self.scale_angle_start_value / 10, 360, False)

        radialGradient = QRadialGradient(QPointF(0, 0), self.width())

        for eachcolor in self.outer_circle_bg:
            radialGradient.setColorAt(eachcolor[0], eachcolor[1])


        painter.setBrush(radialGradient)

        painter.drawPolygon(colored_scale_polygon)


    def draw_needle(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.value - self.value_offset - self.minValue) * self.scale_angle_size /
                        (self.maxValue - self.minValue)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])


    def resizeEvent(self, event):
        self.rescale_method()

    def paintEvent(self, event):

        self.draw_outer_circle()
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_marker()

        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        if self.enable_value_text:
            self.create_values_text()
            self.create_units_text()

        if self.enable_Needle_Polygon:
            self.draw_needle()

        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(diameter=(self.widget_diameter / 6))



    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)

        QWidget.setMouseTracking(self, flag)
        recursive_set(self)
 

class ToolBoxPage(QtCore.QObject):
    destroyed = QtCore.pyqtSignal()
    def __init__(self, button, scrollArea):
        super().__init__()
        self.button = button
        self.scrollArea = scrollArea
        self.widget = scrollArea.widget()
        self.widget.destroyed.connect(self.destroyed)

    def beginHide(self, spacing):
        self.scrollArea.setMinimumHeight(1)
        self.scrollArea.setMaximumHeight(self.scrollArea.height() - spacing)
        if not self.scrollArea.verticalScrollBar().isVisible():
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)

    def beginShow(self, targetHeight):
        if self.scrollArea.widget().minimumSizeHint().height() <= targetHeight:
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)
        else:
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setMaximumHeight(0)
        self.scrollArea.show()

    def setHeight(self, height):
        if height and not self.scrollArea.minimumHeight():
            self.scrollArea.setMinimumHeight(1)
        self.scrollArea.setMaximumHeight(height)

    def finalize(self):
        self.scrollArea.setMinimumHeight(0)
        self.scrollArea.setMaximumHeight(16777215)
        self.scrollArea.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)


class AnimatedToolBox(QtWidgets.QToolBox):
    _oldPage = _newPage = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []

    @cached_property
    def animation(self):
        animation = QtCore.QVariantAnimation(self)
        animation.setDuration(250)
        animation.setStartValue(0.)
        animation.setEndValue(1.)
        animation.valueChanged.connect(self._updateSizes)
        return animation

    @QtCore.pyqtProperty(int)
    def animationDuration(self):
        return self.animation.duration()

    @animationDuration.setter
    def animationDuration(self, duration):
        self.animation.setDuration(max(50, min(duration, 500)))

    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def setCurrentIndex(self, index, now=False):
        if self.currentIndex() == index:
            return
        if now:
            if self.animation.state():
                self.animation.stop()
                self._pages[index].finalize()
            super().setCurrentIndex(index)
            return
        elif self.animation.state():
            return
        self._oldPage = self._pages[self.currentIndex()]
        self._oldPage.beginHide(self.layout().spacing())
        self._newPage = self._pages[index]
        self._newPage.beginShow(self._targetSize)
        self.animation.start()

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    @QtCore.pyqtSlot(QtWidgets.QWidget, bool)
    def setCurrentWidget(self, widget):
        for i, page in enumerate(self._pages):
            if page.widget == widget:
                self.setCurrentIndex(i)
                return

    def _index(self, page):
        return self._pages.index(page)

    def _updateSizes(self, ratio):
        if self.animation.currentTime() < self.animation.duration():
            newSize = round(self._targetSize * ratio)
            oldSize = self._targetSize - newSize
            if newSize < self.layout().spacing():
                oldSize -= self.layout().spacing()
            self._oldPage.setHeight(max(0, oldSize))
            self._newPage.setHeight(newSize)
        else:
            super().setCurrentIndex(self._index(self._newPage))
            self._oldPage.finalize()
            self._newPage.finalize()

    def _computeTargetSize(self):
        if not self.count():
            self._targetSize = 0
            return
        l, t, r, b = self.getContentsMargins()
        baseHeight = (self._pages[0].button.sizeHint().height()
            + self.layout().spacing())
        self._targetSize = self.height() - t - b - baseHeight * self.count()

    def _buttonClicked(self):
        button = self.sender()
        for i, page in enumerate(self._pages):
            if page.button == button:
                self.setCurrentIndex(i)
                return

    def _widgetDestroyed(self):
        self._pages.remove(self.sender())

    def itemInserted(self, index):
        button = self.layout().itemAt(index * 2).widget()
        button.clicked.disconnect()
        button.clicked.connect(self._buttonClicked)
        scrollArea = self.layout().itemAt(index * 2 + 1).widget()
        page = ToolBoxPage(button, scrollArea)
        self._pages.insert(index, page)
        page.destroyed.connect(self._widgetDestroyed)
        self._computeTargetSize()

    def itemRemoved(self, index):
        if self.animation.state() and self._index(self._newPage) == index:
            self.animation.stop()
        page = self._pages.pop(index)
        page.destroyed.disconnect(self._widgetDestroyed)
        self._computeTargetSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._computeTargetSize()