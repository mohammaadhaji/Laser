import math
import os

from PyQt5.QtMultimedia import (
    QMediaPlayer,
    QMediaPlaylist,
    QMediaContent,
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from werkzeug.utils import cached_property

from communication import HARDWARE_TEST_PAGE, READ, sendPacket
from utility import calcPosition
from styles import *
from paths import *

class WebEngineView(QWebEngineView):
    def __init__(self, parent):
        QWebEngineView.__init__(self, parent)
        self.isLoaded = False
        self.loadFinished.connect(self.setIsLoaded)

    def setIsLoaded(self):
        self.isLoaded = True


class SelectedBodyPart(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet('''
            QFrame{
                border-radius: 300px; 
                background-color: rgb(235, 235, 235);
            }'''
        )
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("frame")
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(70, 80, 221, 211))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.label.setText("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        icon = QPixmap(BODY_PART_ICONS['f arm'])
        self.label.setPixmap(icon.scaled(200,200))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setStyleSheet('color: black;')
        font = QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.verticalLayout.setStretch(0, 4)
        self.verticalLayout.setStretch(1, 1)

    def setIcon(self, path):
        icon = QPixmap(path)
        self.label.setPixmap(icon.scaled(140,140))

    def setText(self, txt):
        self.label_2.setText(txt)


class SkinGrade(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        minWidth = 100
        maxWidth = 200
        self.setStyleSheet('''
            QFrame{
                background-color: none;
            }
            QPushButton {
                height:200px;
                min-width:100px;
                max-width:200px;
                margin:0px;
                border:0px solid black;
                background-color: rgb(179, 196, 255);
                outline:0;
            }
            QLabel {
                font: 20pt \"Arial\";
            }
        ''')
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("frame")
        self.btnCaseI = QPushButton(self)
        self.btnCaseI.setGeometry(QRect(1, 101, 200, 112))
        self.btnCaseI.setMinimumSize(QSize(minWidth, 0))
        self.btnCaseI.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnCaseI.setStyleSheet('background-color: rgb(128, 157, 255);')
        self.btnCaseI.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(CASE_I), QIcon.Normal, QIcon.Off)
        self.btnCaseI.setIcon(icon)
        self.btnCaseI.setIconSize(QSize(80, 80))
        self.btnCaseI.setObjectName("btnCaseI")
        self.btnCaseII = QPushButton(self)
        self.btnCaseII.setGeometry(QRect(1, 213, 100, 111))
        self.btnCaseII.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnCaseII.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(CASE_II), QIcon.Normal, QIcon.Off)
        self.btnCaseII.setIcon(icon1)
        self.btnCaseII.setIconSize(QSize(80, 80))
        self.btnCaseII.setObjectName("btnCaseII")
        self.btnCaseIII = QPushButton(self)
        self.btnCaseIII.setGeometry(QRect(1, 324, 100, 112))
        self.btnCaseIII.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnCaseIII.setText("")
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(CASE_II), QIcon.Normal, QIcon.Off)
        self.btnCaseIII.setIcon(icon2)
        self.btnCaseIII.setIconSize(QSize(80, 80))
        self.btnCaseIII.setObjectName("btnCaseIII")
        self.btnCaseIV = QPushButton(self)
        self.btnCaseIV.setGeometry(QRect(1, 436, 100, 111))
        self.btnCaseIV.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnCaseIV.setText("")
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(CASE_IV), QIcon.Normal, QIcon.Off)
        self.btnCaseIV.setIcon(icon3)
        self.btnCaseIV.setIconSize(QSize(80, 80))
        self.btnCaseIV.setObjectName("btnCaseIV")
        self.btnCaseV = QPushButton(self)
        self.btnCaseV.setGeometry(QRect(1, 547, 100, 112))
        self.btnCaseV.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnCaseV.setText("")
        icon4 = QIcon()
        icon4.addPixmap(QPixmap(CASE_V), QIcon.Normal, QIcon.Off)
        self.btnCaseV.setIcon(icon4)
        self.btnCaseV.setIconSize(QSize(80, 80))
        self.btnCaseV.setObjectName("btnCaseV")
        self.btnSave = QPushButton(self)
        self.btnSave.setGeometry(QRect(1, 659, 200, 100))
        self.btnSave.setMaximumSize(QSize(maxWidth, 16777215))
        self.btnSave.setText("Save")
        self.btnSave.setFont(QFont('Arial', 20))
        icon5 = QIcon()
        icon5.addPixmap(QPixmap(CASE_SAVE), QIcon.Normal, QIcon.Off)
        self.btnSave.setIcon(icon5)
        self.btnSave.setIconSize(QSize(70, 70))
        self.btnSave.setObjectName("save")
        self.btnSave.setStyleSheet('''
            QPushButton {
                border-bottom-right-radius: 10px;
            }
            QPushButton:pressed{
                background-color: rgb(255, 255, 255);
            }
        ''')
        self.label = QLabel(self)
        self.label.setFont(QFont('A Iranian Sans', 30))
        self.label.setText('Skin Grade')
        self.label.setGeometry(QRect(1, 1, 200, 100))
        self.label.setMinimumSize(QSize(0, 80))
        self.label.setStyleSheet('''
            background-color: rgb(230, 235, 255);
            border-top-right-radius: 10px;
            color: black;
        ''')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        self.current = self.btnCaseI
        self.allButtons = [self.btnCaseI, self.btnCaseII,
                          self.btnCaseIII, self.btnCaseIV,
                          self.btnCaseV]
        for btn in self.allButtons:
            btn.clicked.connect(self.showBtn(btn))

    def showBtn(self, btn):
        def wrapper():
            if self.current.objectName() == btn.objectName():
                return

            self.animationShow = QPropertyAnimation(btn, b"geometry")
            self.animationShow.setDuration(300)
            self.animationShow.setStartValue(self.getGeo(btn, 'hide'))
            self.animationShow.setEndValue(self.getGeo(btn, 'show'))
            self.animationShow.setEasingCurve(QEasingCurve.InOutQuart)
            self.animationShow.start()
            style = """
                background-color: rgb(128, 157, 255);
            """
            btn.setStyleSheet(style)

            self.animationHide = QPropertyAnimation(self.current, b"geometry")
            self.animationHide.setDuration(300)
            self.animationHide.setStartValue(self.getGeo(self.current, 'show'))
            self.animationHide.setEndValue(self.getGeo(self.current, 'hide'))
            self.animationHide.setEasingCurve(QEasingCurve.InOutQuart)
            self.animationHide.start()
            style = 'background-color: rgb(179, 196, 255);'
            self.current.setStyleSheet(style) 

            self.current = btn

        return wrapper

    def getGeo(self, btn, x):
        if x == 'hide':
            geo = btn.geometry()
            geo.setWidth(100)
            return geo
        else:
            geo = btn.geometry()
            geo.setWidth(200)
            return geo


class Parameter(QFrame):
    inc = pyqtSignal()
    dec = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QRect(150, 90, 581, 351))
        self.setStyleSheet("background-color: none;")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.progressFrame = QFrame(self)
        self.progressFrame.setGeometry(QRect(110, 0, 350, 350))
        self.progressFrame.setFrameShape(QFrame.StyledPanel)
        self.progressFrame.setFrameShadow(QFrame.Raised)
        self.progressFrame.setObjectName("progressFrame")
        self.contentFrame = QFrame(self)
        self.contentFrame.setGeometry(QRect(125, 15, 320, 320))
        self.contentFrame.setBaseSize(QSize(0, 0))
        self.contentFrame.setStyleSheet('''
            QFrame#contentFrame{
                border-radius: 160px;
                background-color: rgb(58, 58, 102);
            }'''
        )
        self.contentFrame.setFrameShape(QFrame.StyledPanel)
        self.contentFrame.setFrameShadow(QFrame.Raised)
        self.contentFrame.setObjectName("contentFrame")
        self.frame = QFrame(self.contentFrame)
        self.frame.setGeometry(QRect(20, 40, 281, 261))
        self.frame.setObjectName("frame")
        self.layout = QGridLayout(self.frame)
        self.layout.setObjectName("layout")
        self.lblValue = QLabel(self.frame)
        font = QFont()
        font.setFamily("Roboto Thin")
        font.setPointSize(90)
        self.lblValue.setFont(font)
        self.lblValue.setStyleSheet("color: rgb(115, 185, 255); padding: 0px; background-color: none;")
        self.lblValue.setAlignment(Qt.AlignCenter)
        self.lblValue.setIndent(-1)
        self.layout.addWidget(self.lblValue, 1, 0, 1, 1)
        self.lblUnit = QLabel(self.frame)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setItalic(True)
        self.lblUnit.setFont(font)
        self.lblUnit.setStyleSheet("color: rgb(148, 148, 216); background-color: none;")
        self.lblUnit.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lblUnit, 2, 0, 1, 1)
        self.lblParameter = QLabel(self.frame)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(25)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.lblParameter.setFont(font)
        self.lblParameter.setStyleSheet("color: #FFFFFF; background-color: none;")
        self.lblParameter.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lblParameter, 0, 0, 1, 1)
        self.btnDec = QPushButton(self)
        self.btnDec.setGeometry(QRect(0, 121, 114, 110))
        self.btnDec.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(DEC_BLACK), QIcon.Normal, QIcon.Off)
        self.btnDec.setIcon(icon)
        self.btnDec.setIconSize(QSize(110, 110))
        self.btnInc = QPushButton(self)
        self.btnInc.setGeometry(QRect(460, 121, 114, 110))
        self.btnInc.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(INC_BLACK), QIcon.Normal, QIcon.Off)
        self.btnInc.setIcon(icon1)
        self.btnInc.setIconSize(QSize(110, 110))
        self.btnInc.setStyleSheet('''
            QPushButton{
                outline : 0;
                border: 0;
            }
            QPushButton:pressed{
                margin-left:20px;
            }
        ''')
        self.btnDec.setStyleSheet('''
            QPushButton{
                outline : 0;
                border: 0;
            }
            QPushButton:pressed{
                margin-right:20px;
            }
        ''')

        self.btnInc.clicked.connect(lambda: self.inc.emit())
        self.btnDec.clicked.connect(lambda: self.dec.emit())
        self.value = 0

    def setParameter(self, x):
        def setIcon(dec, inc):
            icon = QIcon()
            icon.addPixmap(QPixmap(dec), QIcon.Normal, QIcon.Off)
            self.btnDec.setIcon(icon)
            self.btnDec.setIconSize(QSize(110, 110))
            icon1 = QIcon()
            icon1.addPixmap(QPixmap(inc), QIcon.Normal, QIcon.Off)
            self.btnInc.setIcon(icon1)
            self.btnInc.setIconSize(QSize(110, 110))

        parameter = x
        self.lblParameter.setText(parameter)
        if self.lblParameter.text() == 'Energy':
            setIcon(LEFT_YELLOW, RIGHT_YELLOW)
            self.max = 100
            self.lblUnit.setText('Joule')
            self.color = 'rgba(255, 255, 26, 255)'
            self.lblValue.setStyleSheet("color: rgb(255, 255, 26); padding: 0px; background-color: none;")
            self.progressFrame.setStyleSheet('''
            QFrame{
                border-radius: 175px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(255, 255, 26, 255), stop:0.395 rgba(255, 255, 255, 0));
            }'''
        )
        elif self.lblParameter.text() == 'Pulse Width':
            setIcon(LEFT_GREEN, RIGHT_GREEN)
            self.max = 100
            self.lblUnit.setText('mSec')
            self.color = 'rgba(85, 255, 127, 255)'
            self.lblValue.setStyleSheet("color: rgb(115, 255, 171); padding: 0px; background-color: none;")
            self.progressFrame.setStyleSheet('''
            QFrame{
                border-radius: 175px;	
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.600 rgba(85, 255, 127, 255), stop:0.595 rgba(255, 255, 255, 0));
            }'''
        )
        elif self.lblParameter.text() == 'Frequency':
            setIcon(LEFT_RED, RIGHT_RED)
            self.max = 10
            self.lblUnit.setText('Hz')
            self.color = 'rgba(255, 0, 127, 255)'
            self.lblValue.setStyleSheet("color: rgb(255, 44, 174); padding: 0px; background-color: none;")
            self.progressFrame.setStyleSheet('''
            QFrame{
                border-radius: 175px;	
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.750 rgba(255, 0, 127, 255), stop:0.745 rgba(255, 255, 255, 0));
            }'''
        )
        if self.lblParameter.text() == 'Cooling':
            setIcon(LEFT_BLUE, RIGHT_BLUE)
            self.max = 5
            self.lblUnit.setText('')
            self.color = 'rgba(85, 170, 255, 255)'
            self.lblValue.setStyleSheet("color: rgb(115, 185, 255); padding: 0px; background-color: none;")
            self.progressFrame.setStyleSheet('''
            QFrame{
                border-radius: 175px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(85, 170, 255, 255), stop:0.395 rgba(255, 255, 255, 0));
            }'''
        )
        if self.lblParameter.text() == 'Counter':
            self.max = 1000
            self.btnInc.setVisible(False)
            self.btnDec.setVisible(False)
            self.lblUnit.setText('')
            self.color = 'rgba(245, 126, 42, 255)'
            self.lblValue.setStyleSheet("color: rgb(245, 126, 42); padding: 0px; background-color: none;")
            self.progressFrame.setStyleSheet('''
            QFrame{
                border-radius: 175px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(245, 126, 42, 255), stop:0.395 rgba(255, 255, 255, 0));
            }'''
        )
        if parameter == 'Energy':
            self.incTimer = QTimer()
            self.decTimer = QTimer()
            self.incTimer.timeout.connect(lambda: self.inc.emit())
            self.decTimer.timeout.connect(lambda: self.dec.emit())
            self.btnDec.pressed.connect(lambda: self.decTimer.start(100))
            self.btnDec.released.connect(lambda: self.decTimer.stop())
            self.btnInc.pressed.connect(lambda: self.incTimer.start(100))
            self.btnInc.released.connect(lambda: self.incTimer.stop())

    def setFrame(self, color):
        styleFrame = """
        QFrame{
        	border-radius: 175px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """
        styleLable = "color: {COLOR}; padding: 0px; background-color: none;"
        progress = (self.max - self.value) / self.max

        stop_1 = str(progress - 0.0001)
        stop_2 = str(progress)

        if self.value == self.max:
            stop_1 = "1.000"
            stop_2 = "1.000"

        newStyleFrame = styleFrame.replace("{STOP_1}", stop_1)\
                                  .replace("{STOP_2}", stop_2)\
                                  .replace("{COLOR}", color)

        newStyleLable = styleLable.replace("{COLOR}", color)

        self.progressFrame.setStyleSheet(newStyleFrame)
        self.lblValue.setStyleSheet(newStyleLable)

    def setValue(self, value):
        self.value = value
        htmlText = """<p align="center"><span style=" font-size:50pt;">{VALUE}</span></p>"""
        self.lblValue.setText(htmlText.replace("{VALUE}", str(value)))
        self.setFrame(self.color)
    
    def setEnabled(self, x):
        super().setEnabled(x)

        if x:
            color = self.color
        else:
            color = 'rgba(207, 203, 200, 255)'

        self.setFrame(color)
        if self.lblParameter.text() == 'Pulse Width':
            super().setEnabled(False)


class CounterParameter(Parameter):
    def __init__(self, parent):
        super().__init__(parent)
        self.max = 10

    def setValue(self, value):
        htmlText = """<p align="center"><span style=" font-size:50pt;">{VALUE}</span></p>"""
        self.lblValue.setText(htmlText.replace("{VALUE}", str(value)))
        styleSheet = """
        QFrame{
        	border-radius: 175px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """
        progress = (self.max - 0) / self.max

        stop_1 = str(progress - 0.0001)
        stop_2 = str(progress)

        newStylesheet = styleSheet.replace("{STOP_1}", stop_1)\
                                  .replace("{STOP_2}", stop_2)\
                                  .replace("{COLOR}", self.color)
        self.progressFrame.setStyleSheet(newStylesheet)


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
        self.chbDel.setMinimumSize(QSize(60, 60))
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
    clicked = pyqtSignal()
    def __init__(self, parent = None):
        QVideoWidget.__init__(self, parent)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clicked.emit()
        return super().mousePressEvent(a0)


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


class DoubleSlider(QSlider):
    
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


class StackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super(QStackedWidget, self).__init__(parent)

        self.fadeTransition = False
        self.slideTransition = False
        self.transitionDirection = Qt.Vertical
        self.transitionTime = 500
        self.fadeTime = 500
        self.transitionEasingCurve = QEasingCurve.OutBack
        self.fadeEasingCurve = QEasingCurve.Linear
        self.currentWidget = 0
        self.nextWidget = 0
        self._currentWidgetPosition = QPoint(0, 0)
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

    @pyqtSlot()
    def slideToPreviousWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex > 0:
            self.slideToWidgetIndex(currentWidgetIndex - 1)

    @pyqtSlot()
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

        if not self.transitionDirection == Qt.Horizontal:
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

        offset = QPoint(offsetX, offsetY)
        self.widget(_nextWidgetIndex).move(nextWidgetPosition - offset)
        self.widget(_nextWidgetIndex).show()
        self.widget(_nextWidgetIndex).raise_()

        anim_group = QParallelAnimationGroup(
            self, finished=self.animationDoneSlot
        )

        for index, start, end in zip(
            (_currentWidgetIndex, _nextWidgetIndex), 
            (currentWidgetPosition, nextWidgetPosition - offset), 
            (currentWidgetPosition + offset, nextWidgetPosition)
        ):
            animation = QPropertyAnimation(
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
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)

        if self.fadeTransition:
            FadeWidgetTransition(self, self.widget(_currentWidgetIndex), self.widget(_nextWidgetIndex))

    @pyqtSlot()
    def animationDoneSlot(self):
        self.setCurrentIndex(self.nextWidget)
        self.widget(self.currentWidget).hide()
        self.widget(self.currentWidget).move(self._currentWidgetPosition)
        self.widgetActive = False

    @pyqtSlot()
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
 

class ToolBoxPage(QObject):
    destroyed = pyqtSignal()
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
                Qt.ScrollBarAlwaysOff)

    def beginShow(self, targetHeight):
        if self.scrollArea.widget().minimumSizeHint().height() <= targetHeight:
            self.scrollArea.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff)
        else:
            self.scrollArea.setVerticalScrollBarPolicy(
                Qt.ScrollBarAsNeeded)
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
            Qt.ScrollBarAsNeeded)


class AnimatedToolBox(QToolBox):
    _oldPage = _newPage = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []

    @cached_property
    def animation(self):
        animation = QVariantAnimation(self)
        animation.setDuration(250)
        animation.setStartValue(0.)
        animation.setEndValue(1.)
        animation.valueChanged.connect(self._updateSizes)
        return animation

    @pyqtProperty(int)
    def animationDuration(self):
        return self.animation.duration()

    @animationDuration.setter
    def animationDuration(self, duration):
        self.animation.setDuration(max(50, min(duration, 500)))

    @pyqtSlot(int)
    @pyqtSlot(int, bool)
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

    @pyqtSlot(QWidget)
    @pyqtSlot(QWidget, bool)
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


class Player(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QRect(20, 0, 1200, 680))
        self.resize(0, 0)
        self.setStyleSheet("""
            QFrame#frame{
                background-color: rgb(0, 0, 0);
                border:5px solid rgb(5, 0, 48);
                border-radius:10px;
            }
            QLabel{color:rgb(255, 255, 255);}
        """)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("frame")
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.topFrame = QFrame(self)
        self.topFrame.setMaximumSize(QSize(16777215, 0))
        self.topFrame.setStyleSheet("""
            QFrame{
                background-color: rgb(5, 0, 48);
                border-top-left-radius: 10px;
	            border-top-right-radius: 10px;
            }
        """)
        self.topFrame.setFrameShape(QFrame.StyledPanel)
        self.topFrame.setFrameShadow(QFrame.Raised)
        self.topFrame.setObjectName("topFrame")
        self.horizontalLayout = QHBoxLayout(self.topFrame)
        self.horizontalLayout.setContentsMargins(20, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblTitle = QLabel(self.topFrame)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.lblTitle.setFont(font)
        self.lblTitle.setText("")
        self.lblTitle.setObjectName("lblTitle")
        self.horizontalLayout.addWidget(self.lblTitle)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnClose = QPushButton(self.topFrame)
        self.btnClose.setMaximumSize(QSize(50, 50))
        # self.btnClose.setStyleSheet("QPushButton {outline:0;border-radius:25px;border:0px;}")
        self.btnClose.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(CLOSE_FILM), QIcon.Normal, QIcon.Off)
        self.btnClose.setIcon(icon)
        self.btnClose.setIconSize(QSize(50, 50))
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout.addWidget(self.btnClose)
        self.verticalLayout.addWidget(self.topFrame)
        self.widgetFrame = QFrame(self)
        self.widgetFrame.setFrameShape(QFrame.StyledPanel)
        self.widgetFrame.setFrameShadow(QFrame.Raised)
        self.widgetFrame.setObjectName("widgetFrame")
        self.widgetFrame.setStyleSheet("background-color: black;")
        self.verticalLayout_4 = QVBoxLayout(self.widgetFrame)
        self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget = VideoWidget(self.widgetFrame)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4.addWidget(self.widget)
        self.verticalLayout.addWidget(self.widgetFrame)
        self.bottomFrame = QFrame(self)
        self.bottomFrame.setMaximumSize(QSize(16777215, 0))
        self.bottomFrame.setStyleSheet("background-color: rgb(5, 0, 48);")
        self.bottomFrame.setFrameShape(QFrame.StyledPanel)
        self.bottomFrame.setFrameShadow(QFrame.Raised)
        self.bottomFrame.setObjectName("bottomFrame")
        self.horizontalLayout_2 = QHBoxLayout(self.bottomFrame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(23, -1, 23, -1)
        self.sliderVolume = QSlider(self.bottomFrame)
        self.sliderVolume.setMinimumSize(QSize(50, 0))
        self.sliderVolume.setStyleSheet("""
            QSlider::groove:vertical {
                background: red;
                position: absolute; 
                left: 4px; right: 4px;
                width: 10px;
            }

            QSlider::handle:vertical {
                height: 30px;
                width: 30px;
                border-radius:5px;
                background: rgb(85, 170, 255);
                margin: 0 -20px; 
            }

            QSlider::add-page:vertical {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #ABCD44, 
                stop: 0.5 #ABCD44,
                stop: 0.51 #A1C72E,
                stop: 0.54 #A1C72E,
                stop: 1.0 #9CC322);
            }

            QSlider::sub-page:vertical {
                background: #fff;
            }
            QSlider::handle:vertical:pressed {
                background-color: rgb(65, 255, 195);
            }
        """)
        self.sliderVolume.setMaximum(50)
        self.sliderVolume.setProperty("value", 50)
        self.sliderVolume.setOrientation(Qt.Vertical)
        self.sliderVolume.setObjectName("sliderVolume")
        self.horizontalLayout_2.addWidget(self.sliderVolume)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnPlay = QPushButton(self.bottomFrame)
        self.btnPlay.setStyleSheet("""
            QPushButton{
                outline : 0;
                background-color: rgb(213, 213, 213);
                border-radius: 50px;
                border:10px solid rgb(74, 74, 74);
            }
            QPushButton:pressed{
                background-color: rgb(0, 170, 255);
            }
        """)
        self.btnPlay.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(PLAY_ICON), QIcon.Normal, QIcon.Off)
        self.btnPlay.setIcon(icon1)
        self.btnPlay.setIconSize(QSize(80, 80))
        self.btnPlay.setObjectName("btnPlay")
        self.horizontalLayout_2.addWidget(self.btnPlay)
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(self.bottomFrame)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.positionSlider = QSlider(self.bottomFrame)
        self.positionSlider.setMinimumSize(QSize(0, 70))
        self.positionSlider.setStyleSheet("QSlider {\n"
"min-height:70px;\n"
"}\n"
"QSlider::groove:horizontal {\n"
"    border-radius: 1px;\n"
"    height: 10px;\n"
"    margin: 0px;\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    background-color: rgb(85, 170, 255);\n"
"    border: none;\n"
"    height: 70px;\n"
"    width: 60px;\n"
"    border-radius:25px;\n"
"    margin: -25px 0;\n"
"    padding: -25px 0px;\n"
"}\n"
"QSlider::handle:horizontal:pressed {\n"
"    background-color: rgb(65, 255, 195);\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"  stop: 0 #ABCD44, \n"
"  stop: 0.5 #ABCD44,\n"
"  stop: 0.51 #A1C72E,\n"
"  stop: 0.54 #A1C72E,\n"
"  stop: 1.0 #9CC322);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"")
        self.positionSlider.setOrientation(Qt.Horizontal)
        self.positionSlider.setObjectName("positionSlider")
        self.verticalLayout_3.addWidget(self.positionSlider)
        self.lblLength = QLabel(self.bottomFrame)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.lblLength.setFont(font)
        self.lblLength.setStyleSheet("color:rgb(255, 255, 255)")
        self.lblLength.setAlignment(Qt.AlignCenter)
        self.lblLength.setObjectName("lblLength")
        self.verticalLayout_3.addWidget(self.lblLength)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.btnFullscreen = QPushButton(self.bottomFrame)
        self.btnFullscreen.setText("")
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(FULLSCREEN_ICON), QIcon.Normal, QIcon.Off)
        self.btnFullscreen.setIcon(icon2)
        self.btnFullscreen.setIconSize(QSize(50, 50))
        self.btnFullscreen.setObjectName("btnFullscreen")
        self.horizontalLayout_2.addWidget(self.btnFullscreen)
        self.horizontalLayout_2.setStretch(4, 1)
        self.verticalLayout.addWidget(self.bottomFrame)
        self.verticalLayout.setStretch(1, 1)

        self.widget.clicked.connect(lambda: self.control('show'))

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.control('hide'))
        self.btnFullscreen.clicked.connect(self.showFullScreen)
        self.btnFullscreen.setCheckable(True)

        self.playIcon = QIcon()
        self.pauseIcon = QIcon()
        self.playIcon.addPixmap(QPixmap(PLAY_ICON))
        self.pauseIcon.addPixmap(QPixmap(PAUSE_ICON))

        self.length = '00:00:00'
        self.lblLength.setText("00:00:00")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.widget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.btnPlay.clicked.connect(self.play)
        self.sliderVolume.valueChanged.connect(self.setVideoVolume)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderPressed.connect(lambda: self.timer.start(5000))
        self.sliderVolume.sliderPressed.connect(lambda: self.timer.start(5000))
        self.btnPlay.clicked.connect(lambda: self.timer.start(5000))
        self.btnClose.clicked.connect(self.close)
        self.close()

        

    def play(self):    
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.btnPlay.setIcon(self.pauseIcon)
        else:
            self.btnPlay.setIcon(self.playIcon)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        current = '{:02d}:{:02d}:{:02d} / '.format(*calcPosition(position)) + self.length
        self.lblLength.setText(current)

    def durationChanged(self, duration):
        self.length = '{:02d}:{:02d}:{:02d}'.format(*calcPosition(duration))
        self.lblLength.setText('00:00:00 / ' + self.length)
        self.positionSlider.setRange(0, duration)

    def setVideoVolume(self, v):
        self.mediaPlayer.setVolume(v)

    def videoSelected(self, name):
        path = join(TUTORIALS_DIR, name)
        self.lblTitle.setText(name)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.play()
    
    def showFullScreen(self, full):
        icon = QIcon()
        if full:
            icon.addPixmap(QPixmap(NOT_FULLSCREEN_ICON))
            pos = QRect(-2, -2, 1924, 1084)
            self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
            self.setStyleSheet("""
                QFrame#frame{
                    background-color: rgb(0, 0, 0);
                    border:5px solid black;
                    border-radius:1px;
                }
                QLabel{color:rgb(255, 255, 255);}
            """)
        else:
            icon.addPixmap(QPixmap(FULLSCREEN_ICON))
            ax = (1920 - 1200) / 2
            ay = (1080 - 680) / 2
            pos = QRect(ax, ay, 1200, 680)
            self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
            self.setStyleSheet("""
                QFrame#frame{
                    background-color: rgb(0, 0, 0);
                    border:5px solid rgb(5, 0, 48);
                    border-radius:10px;
                }
                QLabel{color:rgb(255, 255, 255);}
            """)

        self.btnFullscreen.setIcon(icon)   
        self.setGeometry(pos)
        self.timer.start(5000)
                
    def control(self, i, force=False):
        topH = self.topFrame.size().height()
        if not force: 
            if i == 'hide' and topH == 0:
                return
            
            if i == 'show' and topH > 0:
                return

        if i == 'hide':
            topH = 65
            newTopH = 0
            newBottomH = 0
            self.timer.stop()
            
        else:
            topH = 0
            newTopH = 65
            newBottomH = 165
            self.timer.start(5000)

        self.topFrame.setMaximumHeight(newTopH)
        self.bottomFrame.setMaximumHeight(newBottomH)
        
    def close(self, fast=False):
        self.mediaPlayer.setMedia(QMediaContent())
        self.animation = QPropertyAnimation(self, b"geometry")
        time = 500
        if fast:
            time = 0
        self.animation.setDuration(time)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(1920 // 2, 1080 // 2, 0, 0))
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def onOpen(self, btn):
        def wrapper():
            if self.width() <= 1: 
                self.btnPlay.setIcon(self.playIcon)
                self.animation = QPropertyAnimation(self, b"geometry")
                self.animation.setDuration(500)
                self.animation.setStartValue(self.lower(btn.geometry()))
                ax = (1920 - 1200) / 2
                ay = (1080 - 680) / 2
                self.animation.setEndValue(QRect(ax, ay , 1200, 680))
                self.animation.setEasingCurve(QEasingCurve.InOutQuart)
                self.animation.start()
                self.animation.finished.connect(lambda :self.videoSelected(btn.text()))
            else:
                self.videoSelected(btn.text())
                
            self.control('show', force=True)
        
        return wrapper

    def lower(self, pos):
        return QRect(pos.left(), pos.top() + 130, pos.width()+ 10, pos.height())
