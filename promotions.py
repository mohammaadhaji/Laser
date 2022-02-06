from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtCore
from styles import *
from paths import *
import math


class Sensor(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.styleOk = SENSOR_OK
        self.styleNotOk = SENSOR_NOT_OK
        self.error = False
        self.flag = False
        self.warning = False

    def blink(self):
        self.flag = not self.flag
        if self.flag:
            self.setStyleSheet(self.styleNotOk)
        else:
            self.setStyleSheet(self.styleOk)

    def stopWarning(self):
        self.timer.stop()
        self.warning = False
        self.setStyleSheet(SENSOR_OK)

    def startWarning(self):
        if not self.warning:
            self.timer.start(500)
            self.warning = True

    def setError(self, status):
        self.error = status
        if self.error:
            self.startWarning()
        else:
            self.stopWarning()

class TempSensor(Sensor):
    def __init__(self, parent):
        super().__init__(parent)
        self.temperature = 0

    def setError(self, value):
        self.temperature = value
        if 5 <= value <= 40:
            self.stopWarning()
            self.error = False
        else:
            self.startWarning()
            self.error = True


class InterLockSensor(Sensor):
    def __init__(self, parent):
        super().__init__(parent)
        self.lockIco = QIcon()
        self.unlockIco = QIcon()
        self.lockIco.addPixmap(QPixmap(LOCK))
        self.unlockIco.addPixmap(QPixmap(UNLOCK))

    def stopWarning(self):
        self.timer.stop()
        self.warning = False
        self.setIcon(self.unlockIco)
        self.setStyleSheet(SENSOR_OK)

    def startWarning(self):
        if not self.warning:
            self.timer.start(500)
            self.warning = True
            self.setIcon(self.lockIco)

class HiddenSensor(Sensor):
    def __init__(self, parent):
        super().__init__(parent)
        self.styleOk = HIDDEN_SENSOR_OK
        self.styleNotOk = HIDDEN_SENSOR_NOT_OK

    def stopWarning(self):
        self.timer.stop()
        self.warning = False
        self.setVisible(False)

    def startWarning(self):
        if not self.warning:
            self.timer.start(500)
            self.warning = True
            self.setVisible(True)
        

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


class AnalogGaugeWidget(QWidget):
    """Fetches rows from a Bigtable.
    Args: 
        none
    
    """
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(AnalogGaugeWidget, self).__init__(parent)

        self.use_timer_event = False

        self.setNeedleColor(0, 0, 0, 255)

        self.NeedleColorReleased = self.NeedleColor

        self.setNeedleColorOnDrag(255, 0, 00, 255)

        self.setScaleValueColor(255, 255, 255, 255)

        self.setDisplayValueColor(255, 255, 255, 255)

        self.set_CenterPointColor(0, 0, 0, 255)

        self.value_needle_count = 3

        self.value_needle = QObject

        self.minValue = 0
        self.maxValue = 1000
        self.value = self.minValue

        self.value_offset = 0

        self.valueNeedleSnapzone = 0.25
        self.last_value = 0


        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        self.scale_angle_start_value = 135
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

        self.setEnableBarGraph(True)
        self.setEnableScalePolygon(True)
        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True

        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        self.setMouseTracking(True)

        self.units = "A"

        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        self.setGaugeTheme(0)

        self.rescale_method()

    def setScaleFontFamily(self, font):
        self.scale_fontname = str(font)

    def setValueFontFamily(self, font):
        self.value_fontname = str(font)

    def setBigScaleColor(self, color):
        self.bigScaleMarker = QColor(color)      

    def setFineScaleColor(self, color):
        self.fineScaleColor = QColor(color)    

    def setGaugeTheme(self, Theme = 1):
        if Theme == 0 or Theme == None:
            self.set_scale_polygon_colors([[.00, Qt.red],
                                    [.1, Qt.yellow],
                                    [.15, Qt.green],
                                    [1, Qt.transparent]])

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

        if Theme == 1:
            self.set_scale_polygon_colors([[.75, Qt.red],
                                     [.5, Qt.yellow],
                                     [.25, Qt.green]])

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

        if Theme == 2:
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

        elif Theme == 3:
            self.set_scale_polygon_colors([[.00, Qt.white]])

            self.needle_center_bg = [
                                    [0, Qt.white], 
                                    ]

            self.outer_circle_bg =  [
                                    [0, Qt.white], 
                                    ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 4:
            self.set_scale_polygon_colors([[1, Qt.black]])

            self.needle_center_bg = [
                                    [0, Qt.black], 
                                    ]

            self.outer_circle_bg =  [
                                    [0, Qt.black], 
                                    ]

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 5:
            self.set_scale_polygon_colors([[1, QColor("#029CDE")]])  

            self.needle_center_bg = [
                                    [0, QColor("#029CDE")], 
                                    ]

            self.outer_circle_bg =  [
                                    [0, QColor("#029CDE")], 
                                    ]

        elif Theme == 6:
            self.set_scale_polygon_colors([[.75, QColor("#01ADEF")],
                                     [.5, QColor("#0086BF")],
                                     [.25, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)], 
                                    [0.322581, QColor(1, 173, 239, 255)], 
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
                                    ]

            self.outer_circle_bg =  [
                                    [0.0645161, QColor(0, 85, 116, 255)], 
                                    [0.37788, QColor(1, 173, 239, 255)], 
                                    [1, QColor(0, 69, 94, 255)]
                                    ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 7:
            self.set_scale_polygon_colors([[.25, QColor("#01ADEF")],
                                     [.5, QColor("#0086BF")],
                                     [.75, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)], 
                                    [0.322581, QColor(1, 173, 239, 255)], 
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
                                    ]

            self.outer_circle_bg =  [
                                    [0.0645161, QColor(0, 85, 116, 255)], 
                                    [0.37788, QColor(1, 173, 239, 255)], 
                                    [1, QColor(0, 69, 94, 255)]
                                    ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 8:
            self.setCustomGaugeTheme(
                color1 = "#ffaa00",
                color2= "#7d5300",
                color3 = "#3e2900"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 9:
            self.setCustomGaugeTheme(
                color1 = "#3e2900",
                color2= "#7d5300",
                color3 = "#ffaa00"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 10:
            self.setCustomGaugeTheme(
                color1 = "#ff007f",
                color2= "#aa0055",
                color3 = "#830042"
            )


            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 11:
            self.setCustomGaugeTheme(
                color1 = "#830042",
                color2= "#aa0055",
                color3 = "#ff007f"
            )
            
            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 12:
            self.setCustomGaugeTheme(
                color1 = "#ffe75d",
                color2= "#896c1a",
                color3 = "#232803"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 13:
            self.setCustomGaugeTheme(
                color1 = "#ffe75d",
                color2= "#896c1a",
                color3 = "#232803"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 14:
            self.setCustomGaugeTheme(
                color1 = "#232803",
                color2= "#821600",
                color3 = "#ffe75d"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 15:
            self.setCustomGaugeTheme(
                color1 = "#00FF11",
                color2= "#00990A",
                color3 = "#002603"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 16:
            self.setCustomGaugeTheme(
                color1 = "#002603",
                color2= "#00990A",
                color3 = "#00FF11"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 17:
            self.setCustomGaugeTheme(
                color1 = "#00FFCC",
                color2= "#00876C",
                color3 = "#00211B"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 18:
            self.setCustomGaugeTheme(
                color1 = "#00211B",
                color2= "#00876C",
                color3 = "#00FFCC"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 19:
            self.setCustomGaugeTheme(
                color1 = "#001EFF",
                color2= "#001299",
                color3 = "#000426"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 20:
            self.setCustomGaugeTheme(
                color1 = "#000426",
                color2= "#001299",
                color3 = "#001EFF"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 21:
            self.setCustomGaugeTheme(
                color1 = "#F200FF",
                color2= "#85008C",
                color3 = "#240026"
            )

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 22:
            self.setCustomGaugeTheme(
                color1 = "#240026",
                color2= "#85008C",
                color3 = "#F200FF"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 23:
            self.setCustomGaugeTheme(
                color1 = "#FF0022",
                color2= "#080001",
                color3 = "#009991"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 24:
            self.setCustomGaugeTheme(
                color1 = "#009991",
                color2= "#080001",
                color3 = "#FF0022"
            )

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

    def setCustomGaugeTheme(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.set_scale_polygon_colors([[.25, QColor(str(colors['color1']))],
                                            [.5, QColor(str(colors['color2']))],
                                            [.75, QColor(str(colors['color3']))]])

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color3']))], 
                                            [0.322581, QColor(str(colors['color1']))], 
                                            [0.571429, QColor(str(colors['color2']))],
                                            [1, QColor(str(colors['color3']))]
                                            ]

                    self.outer_circle_bg =  [
                                            [0.0645161, QColor(str(colors['color3']))], 
                                            [0.36, QColor(str(colors['color1']))], 
                                            [1, QColor(str(colors['color2']))]
                                            ]

                else:

                    self.set_scale_polygon_colors([[.5, QColor(str(colors['color1']))],
                                             [1, QColor(str(colors['color2']))]])

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color2']))], 
                                            [1, QColor(str(colors['color1']))]
                                            ]

                    self.outer_circle_bg =  [
                                            [0, QColor(str(colors['color2']))], 
                                            [1, QColor(str(colors['color2']))]
                                            ]

            else:

                self.set_scale_polygon_colors([[1, QColor(str(colors['color1']))]])

                self.needle_center_bg = [
                                        [1, QColor(str(colors['color1']))]
                                        ]

                self.outer_circle_bg =  [
                                        [1, QColor(str(colors['color1']))]
                                        ]

        else:

            self.setGaugeTheme(0)
            print("color1 is not defined")

    def setScalePolygonColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.set_scale_polygon_colors([[.25, QColor(str(colors['color1']))],
                                            [.5, QColor(str(colors['color2']))],
                                            [.75, QColor(str(colors['color3']))]])

                else:

                    self.set_scale_polygon_colors([[.5, QColor(str(colors['color1']))],
                                             [1, QColor(str(colors['color2']))]])

            else:

                self.set_scale_polygon_colors([[1, QColor(str(colors['color1']))]])

        else:
            print("color1 is not defined")

    def setNeedleCenterColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color3']))], 
                                            [0.322581, QColor(str(colors['color1']))], 
                                            [0.571429, QColor(str(colors['color2']))],
                                            [1, QColor(str(colors['color3']))]
                                            ]

                else:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color2']))], 
                                            [1, QColor(str(colors['color1']))]
                                            ]

            else:

                self.needle_center_bg = [
                                        [1, QColor(str(colors['color1']))]
                                        ]
        else:
            print("color1 is not defined")

    def setOuterCircleColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.outer_circle_bg =  [
                                            [0.0645161, QColor(str(colors['color3']))], 
                                            [0.37788, QColor(str(colors['color1']))], 
                                            [1, QColor(str(colors['color2']))]
                                            ]

                else:

                    self.outer_circle_bg =  [
                                            [0, QColor(str(colors['color2']))], 
                                            [1, QColor(str(colors['color2']))]
                                            ]

            else:

                self.outer_circle_bg =  [
                                        [1, QColor(str(colors['color1']))]
                                        ]

        else:
            print("color1 is not defined")



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

    def updateAngleOffset(self, offset):
        self.angle_offset = offset
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

    def setEnableNeedlePolygon(self, enable = True):
        self.enable_Needle_Polygon = enable

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

    def setEnableValueText(self, enable = True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableCenterPoint(self, enable = True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScalePolygon(self, enable = True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBigScaleGrid(self, enable = True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()


    def setEnableFineScaleGrid(self, enable = True):
        self.enable_fine_scaled_marker = enable

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

    def setTotalScaleAngleSize(self, value):
        self.scale_angle_size = value

        if not self.use_timer_event:
            self.update()

    def setGaugeColorOuterRadiusFactor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000

        if not self.use_timer_event:
            self.update()

    def setGaugeColorInnerRadiusFactor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000

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

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(self.value_fontsize / 1.5), QFont.Bold))

      
        angle_end = float(self.scale_angle_start_value + self.scale_angle_size + 180)
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

    def mouseReleaseEvent(self, QMouseEvent):
        self.NeedleColor = self.NeedleColorReleased

        if not self.use_timer_event:
            self.update()
        pass

    def leaveEvent(self, event):
        self.NeedleColor = self.NeedleColorReleased
        self.update() 

    def mouseMoveEvent(self, event):
        x, y = event.x() - (self.width() / 2), event.y() - (self.height() / 2)
        if not x == 0: 
            angle = math.atan2(y, x) / math.pi * 180
            value = (float(math.fmod(angle - self.scale_angle_start_value + 720, 360)) / \
                     (float(self.scale_angle_size) / float(self.maxValue - self.minValue))) + self.minValue
            temp = value
            fmod = float(math.fmod(angle - self.scale_angle_start_value + 720, 360))
            state = 0
            if (self.value - (self.maxValue - self.minValue) * self.valueNeedleSnapzone) <= \
                    value <= \
                    (self.value + (self.maxValue - self.minValue) * self.valueNeedleSnapzone):
                self.NeedleColor = self.NeedleColorDrag
                state = 9
                if value >= self.maxValue and self.last_value < (self.maxValue - self.minValue) / 2:
                    state = 1
                    value = self.maxValue
                    self.last_value = self.minValue
                    self.valueChanged.emit(int(value))

                elif value >= self.maxValue >= self.last_value:
                    state = 2
                    value = self.maxValue
                    self.last_value = self.maxValue
                    self.valueChanged.emit(int(value))


                else:
                    state = 3
                    self.last_value = value
                    self.valueChanged.emit(int(value))

                self.updateValue(value)  