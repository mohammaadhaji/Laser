from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from lang import TEXT
from promotions import *
from case import *
from paths import *
from user import *
from styles import *
from itertools import chain
from pathlib import Path 
import sys


def layout_widgets(layout):
    return (layout.itemAt(i).widget() for i in range(layout.count())) 

def get_layout_btn(layout):
    return (layout.itemAt(i).widget() for i in range(layout.count()) if isinstance(layout.itemAt(i).widget(), QPushButton)) 

def getDiff(date):
    today = jdatetime.datetime.today().togregorian()
    nextSessionDate = date.togregorian()
    return (nextSessionDate - today).days + 1

def addExtenstion(file):
    files = os.listdir(TUTORIALS_DIR)
    files.remove('.gitignore')
    for f in files:
        path = os.path.join(TUTORIALS_DIR, f)
        if file == Path(path).stem:
            return file + Path(path).suffix

class MainWin(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWin, self).__init__(*args, **kwargs)
        uic.loadUi(APP_UI, self)
        self.setupUi()
        self.tutorials()
        self.setupSensors()
        self.checkBoxLang.toggle()

    def setupUi(self):
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidgetLaser.setCurrentIndex(0)
        self.stackedWidgetSex.setCurrentIndex(0)
        self.stackedWidgetSettings.setCurrentIndex(0)
        self.stackedWidget.setTransitionDirection(Qt.Vertical)
        self.stackedWidget.setTransitionSpeed(500)
        self.stackedWidget.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidget.setSlideTransition(True)
        self.stackedWidgetSex.setTransitionDirection(Qt.Vertical)
        self.stackedWidgetSex.setTransitionSpeed(500)
        self.stackedWidgetSex.setTransitionEasingCurve(QEasingCurve.OutBack)
        self.stackedWidgetSex.setSlideTransition(True)
        self.stackedWidgetLaser.setTransitionDirection(Qt.Horizontal)
        self.stackedWidgetLaser.setTransitionSpeed(500)
        self.stackedWidgetLaser.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidgetLaser.setSlideTransition(True)
        self.stackedWidgetSettings.setTransitionDirection(Qt.Horizontal)
        self.stackedWidgetSettings.setTransitionSpeed(500)
        self.stackedWidgetSettings.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidgetSettings.setSlideTransition(True)
        self.loginLabelTimer = QTimer()
        self.submitLabelTimer = QTimer()
        self.editLabelTimer = QTimer()
        self.nextSessionLabelTimer = QTimer()
        self.incEPFTimer = QTimer()
        self.decEPFTimer = QTimer()
        self.incDaysTimer = QTimer()
        self.decDaysTimer = QTimer()
        self.loginLabelTimer.timeout.connect(lambda: self.clearLabel('login'))
        self.submitLabelTimer.timeout.connect(lambda: self.clearLabel('submit'))
        self.editLabelTimer.timeout.connect(lambda: self.clearLabel('edit'))
        self.nextSessionLabelTimer.timeout.connect(lambda: self.clearLabel('nextSession'))
        self.incEPFTimer.timeout.connect(lambda: self.setEPF('inc'))
        self.decEPFTimer.timeout.connect(lambda: self.setEPF('dec'))
        self.incDaysTimer.timeout.connect(lambda: self.incDecDay('inc'))
        self.decDaysTimer.timeout.connect(lambda: self.incDecDay('dec'))
        self.user = None
        self.userNextSession = None
        self.sortBySession = False
        self.shift = False
        self.farsi = False
        self.sex = 'female'
        self.bodyPart = ''
        self.case = 'I'
        self.EPF = 'E'
        self.cooling = 0
        self.language = 0 # en = 0, fa = 1
        self.checkBoxLang.setFixedSize(110, 48)
        self.checkBoxReady.setFixedSize(150, 48)
        self.checkBoxLang._active_color = '#777'
        self.checkBoxLang.toggled.connect(self.changeLang)
        self.btnSort.clicked.connect(self.sort)
        self.txtNumber.returnPressed.connect(self.login)
        self.btnEndSession.clicked.connect(lambda: self.setNextSession('lazer'))
        self.btnPower.clicked.connect(self.close)
        self.btnLogin.clicked.connect(self.login)
        self.btnSubmit.clicked.connect(self.submit)
        self.btnBackNewSession.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.loginPage))
        self.btnBackManagement.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.loginPage))
        self.btnBackManagement.clicked.connect(lambda: self.txtSearch.clear())
        self.btnBackLaser.clicked.connect(self.backLaser)
        self.btnBackSettings.clicked.connect(self.backSettings)
        self.btnBackEditUser.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnBackEditUser.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.userManagementPage))
        self.btnSettings.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnSettings.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        self.btnUiSettings.clicked.connect(lambda: self.stackedWidgetSettings.setCurrentWidget(self.uiPage))
        self.btnUmSettings.clicked.connect(lambda: self.stackedWidgetSettings.setCurrentWidget(self.uMPage))        
        self.btnHwSettings.clicked.connect(lambda: self.stackedWidgetSettings.setCurrentWidget(self.hWPage))
        self.btnUserManagement.clicked.connect(self.loadToTabel)
        self.btnSaveInfo.clicked.connect(self.saveUserInfo)
        self.btnDeleteUser.clicked.connect(self.deleteUser)
        self.btnUserManagement.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnUserManagement.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.userManagementPage))
        self.btnNotify.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnNotify.clicked.connect(self.futureSessions)
        self.btnNotify.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.notifyPage))
        self.btnBackNotify.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.loginPage))
        self.btnTutorials.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnTutorials.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.tutorialPage))
        self.btnBackTutorials.clicked.connect(self.pause)
        self.btnBackTutorials.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.loginPage))
        self.btnNextSession.clicked.connect(lambda: self.changeAnimation('vertical'))
        self.btnNextSession.clicked.connect(lambda: self.setNextSession('edit'))
        self.btnCancelNS.clicked.connect(self.cancelNextSession)
        self.usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usersTable.verticalHeader().setDefaultSectionSize(75)
        self.usersTable.horizontalHeader().setFixedHeight(60)
        self.usersTable.verticalHeader().setVisible(False)
        self.tableToday.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableToday.verticalHeader().setDefaultSectionSize(70)
        self.tableToday.horizontalHeader().setFixedHeight(60)
        self.tableToday.verticalHeader().setVisible(False)
        self.tableTomorrow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableTomorrow.verticalHeader().setDefaultSectionSize(70)
        self.tableTomorrow.horizontalHeader().setFixedHeight(60)
        self.tableTomorrow.verticalHeader().setVisible(False)
        self.userInfoTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.userInfoTable.verticalHeader().setDefaultSectionSize(70)
        self.userInfoTable.horizontalHeader().setFixedHeight(60)
        self.userInfoTable.verticalHeader().setVisible(False)
        self.txtNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtNumberSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtNameSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditName.fIn.connect(lambda: self.keyboard('show'))
        self.textEditNote.fIn.connect(lambda: self.keyboard('show'))
        self.txtSearch.fIn.connect(lambda: self.keyboard('show'))
        self.txtDate.fIn.connect(lambda: self.keyboard('show'))
        self.txtDays.fIn.connect(lambda: self.keyboard('show'))
        self.btnCancelNS.clicked.connect(lambda: self.keyboard('hide'))
        self.btnOkNS.clicked.connect(lambda: self.keyboard('hide'))
        self.btnDecDay.clicked.connect(lambda: self.incDecDay('dec'))
        self.btnIncDay.clicked.connect(lambda: self.incDecDay('inc'))
        self.txtDays.textChanged.connect(self.setDateText)
        self.txtDate.textChanged.connect(self.setDaysText)
        self.btnOkNS.clicked.connect(self.saveNextSession)
        reg_ex = QRegExp("[0-9\(\)]*")
        input_validator = QRegExpValidator(reg_ex, self.txtDays)
        self.txtDays.setValidator(input_validator)
        self.txtDays.setText('30')
        self.txtSearch.textChanged.connect(self.search)
        self.btnMale.clicked.connect(lambda: self.setSex('male'))
        self.btnFemale.clicked.connect(lambda: self.setSex('female'))
        self.btnEnergy.clicked.connect(lambda: self.selectEPF('E'))
        self.btnIncEPF.pressed.connect(lambda: self.incEPFTimer.start(100))
        self.btnIncEPF.released.connect(lambda: self.incEPFTimer.stop())
        self.btnDecEPF.pressed.connect(lambda: self.decEPFTimer.start(100))
        self.btnDecEPF.released.connect(lambda: self.decEPFTimer.stop())
        self.btnIncDay.pressed.connect(lambda: self.incDaysTimer.start(100))
        self.btnIncDay.released.connect(lambda: self.incDaysTimer.stop())
        self.btnDecDay.pressed.connect(lambda: self.decDaysTimer.start(100))
        self.btnDecDay.released.connect(lambda: self.decDaysTimer.stop())
        self.btnPulseWidth.clicked.connect(lambda: self.selectEPF('P'))
        self.btnFrequency.clicked.connect(lambda: self.selectEPF('F'))
        self.btnMale.clicked.connect(lambda: self.stackedWidgetSex.setCurrentWidget(self.malePage))
        self.btnFemale.clicked.connect(lambda: self.stackedWidgetSex.setCurrentWidget(self.femalePage))
        self.btnIncEPF.clicked.connect(lambda: self.setEPF('inc'))
        self.btnDecEPF.clicked.connect(lambda: self.setEPF('dec'))
        self.btnDecCooling.clicked.connect(lambda: self.setCooling('dec'))
        self.btnIncCooling.clicked.connect(lambda: self.setCooling('inc'))
        self.btnSaveCase.clicked.connect(self.saveCase)
        self.bodyPartsSignals()
        self.keyboardSignals()
        self.casesSignals()

    def tutorials(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = VideoWidget()
        self.videoLayout.addWidget(self.videoWidget)
        self.btnPlay.clicked.connect(self.play)
        self.listWidgetVideos.itemClicked.connect(self.videoSelected)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.setVolume(self.sliderVolume.value())
        self.sliderVolume.valueChanged.connect(self.mediaPlayer.setVolume)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.playIco = QIcon()
        self.pauseIco = QIcon()
        self.playIco.addPixmap(QPixmap(PLAY_ICON))
        self.pauseIco.addPixmap(QPixmap(PAUSE_ICON))
        self.btnPlay.setIcon(self.playIco)
        self.btnPlay.setIconSize(QSize(100, 100))
        self.length = '00:00:00'
        self.lblLength.setText(self.length)

        tutoriasl = os.listdir(TUTORIALS_DIR)
        tutoriasl.remove('.gitignore')
        for file in tutoriasl:
            path = os.path.join(TUTORIALS_DIR, file) 
            name = Path(path).stem
            self.listWidgetVideos.addItem(name)
        
    def videoSelected(self, video):
        stem = video.text()
        self.lblTitle.setText(stem)
        path = join(TUTORIALS_DIR, addExtenstion(stem))
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def mediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.btnPlay.setIcon(self.pauseIco)
        else:
            self.btnPlay.setIcon(self.playIco)

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        seconds = int((position/1000) % 60)
        minutes = int((position/60000) % 60)
        hours = int((position/3600000) % 24)
        current = '{:02d}:{:02d}:{:02d} / '.format(hours, minutes, seconds) + self.length
        self.lblLength.setText(current)

    def durationChanged(self, duration):
        seconds = int((duration/1000) % 60)
        minutes = int((duration/60000) % 60)
        hours = int((duration/3600000) % 24)
        self.length = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        self.lblLength.setText('00:00:00 / ' + self.length)
        self.positionSlider.setRange(0, duration)

    def pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.btnPlay.setIcon(self.playIco)

        self.mediaPlayer.setPosition(0)

    def changeAnimation(self, animation):
        if animation == 'horizontal':
            self.stackedWidget.setTransitionDirection(Qt.Horizontal)

        elif animation == 'vertical':
            self.stackedWidget.setTransitionDirection(Qt.Vertical)

    def isDateValid(self):
        try:
            text = self.txtDate.text()
            text = text.replace(' ', '').split('/')
            year, month, day = tuple([int(x) for x in text])
            nextSessionDate = jdatetime.datetime(year, month, day)
            return True, nextSessionDate
        except Exception:
            return False, None

    def saveNextSession(self):
        try:
            text = self.txtDate.text()
            text = text.replace(' ', '').split('/')
            year, month, day = tuple([int(x) for x in text])
            try:
                date = jdatetime.datetime(year, month, day)
                if getDiff(date) <= -1:
                    self.setLabel(TEXT['passedDate'][self.language], 'nextSession')
                    return
                self.userNextSession.setNextSession(date)
                self.userNextSession.save()
                if self.userNextSession.currentSession == 'started':
                    self.endSession()
                else:
                    self.edit(self.userNextSession.phoneNumber)
            except ValueError as e:
                self.setLabel(str(e).capitalize() + '.', 'nextSession')

        except Exception:
            self.setLabel(TEXT['invalidDateF'][self.language], 'nextSession')

    def cancelNextSession(self):
        if self.userNextSession.currentSession == 'started':
            self.userNextSession.setNextSession(None)
            self.changeAnimation('vertical')
            self.endSession()
        else:
            self.edit(self.userNextSession.phoneNumber)

    def incDecDay(self, operation):
        if not self.txtDays.text():
            self.txtDays.setText('1')
        else:
            num = int(self.txtDays.text())
            num = num + 1 if operation == 'inc' else num - 1

            if num in range(0, 10000):
                self.txtDays.setText(str(num))
        
    def setDateText(self, num):
        if num and int(num) in range(0, 10000):
            today = jdatetime.datetime.today()
            afterNday = jdatetime.timedelta(int(num))
            nextSessionDate = today + afterNday
            year = str(nextSessionDate.year)
            month = str(nextSessionDate.month).zfill(2)
            day = str(nextSessionDate.day).zfill(2)
            self.txtDate.setText(year + ' / ' + month + ' / ' + day)

    def setDaysText(self):
        valid, nextSessionDate = self.isDateValid()
        if valid:
            diff = getDiff(nextSessionDate)
            if 0 <= diff < 10000:
                self.txtDays.setText(str(diff))

    def setNextSession(self, page):
        if page == 'lazer':
            self.userNextSession = self.user
        elif page == 'edit':
            self.userNextSession = self.userInfo
            
        self.changeAnimation('vertical')
        self.stackedWidget.setCurrentWidget(self.nextSessionPage)

    def setupSensors(self):
        self.waterCirIco = QIcon()
        self.waterCirWarIco = QIcon()
        self.waterLvlIco = QIcon()
        self.waterLvlWarIco = QIcon()
        self.tempIco = QIcon()
        self.tempWarIco = QIcon()
        self.lockIco = QIcon()
        self.unlockIco = QIcon()
        self.waterCirIco.addPixmap(QPixmap(WATERCIRCULATION))
        self.waterCirWarIco.addPixmap(QPixmap(WATERCIRCULATIONWARNING))
        self.waterLvlIco.addPixmap(QPixmap(WATERLEVEL))
        self.waterLvlWarIco.addPixmap(QPixmap(WATERLEVELWARNING))
        self.tempIco.addPixmap(QPixmap(TEMP))
        self.tempWarIco.addPixmap(QPixmap(TEMPWARNING))
        self.lockIco.addPixmap(QPixmap(LOCK))
        self.unlockIco.addPixmap(QPixmap(UNLOCK))
        self.waterCirTimer = QTimer()
        self.waterLevelTimer = QTimer()
        self.tempTimer = QTimer()
        self.waterCirTimer.timeout.connect(lambda: self.blinkSensorsIcon('waterCir'))
        self.waterLevelTimer.timeout.connect(lambda: self.blinkSensorsIcon('waterLevel'))
        self.tempTimer.timeout.connect(lambda: self.blinkSensorsIcon('temp'))
        self.btnWaterCirculation.setIcon(self.waterCirIco)
        self.btnTemp.setIcon(self.tempIco)
        self.btnWaterLevel.setIcon(self.waterLvlIco)
        self.btnLock.setIcon(self.lockIco)
        self.btnWaterCirculation.setIconSize(QSize(80, 80))
        self.btnTemp.setIconSize(QSize(80, 80))
        self.btnWaterLevel.setIconSize(QSize(80, 80))
        self.btnLock.setIconSize(QSize(80, 80))
        self.waterCirculanFlag = False
        self.waterCirculanWar = False
        self.waterLevelFlag = False
        self.waterLevelWar = False
        self.tempFlag = False
        self.tempWar = False
        self.lockFlag = True
        self.setTemp(0)
        self.setLock(True)

    def setCooling(self, operation):
        buttons = layout_widgets(self.coolingLayout)
        icon = QIcon()
        if operation == 'inc':
            if self.cooling < 5:
                self.cooling += 1
                for btn in buttons:
                    coolingNum = int(btn.objectName().split('Cooling')[1])
                    if coolingNum == self.cooling:
                        icon.addPixmap(QPixmap(COOLING_ON))
                        btn.setIcon(icon)
                        btn.setIconSize(QSize(50, 50))
        else:
            if self.cooling >= 1:
                for btn in buttons:
                    coolingNum = int(btn.objectName().split('Cooling')[1])
                    if coolingNum == self.cooling:
                        icon.addPixmap(QPixmap(COOLING_OFF)) 
                        btn.setIcon(icon)
                        btn.setIconSize(QSize(50, 50))
                        
                self.cooling -= 1       

    def setEPF(self, operation):
        if self.EPF == 'E':
            energy = int(self.txtEnergy.text().split(' ')[0])
            energy = energy + 1 if operation == 'inc' else energy - 1
            self.txtEnergy.setText(str(energy) + ' J/cm²')
        elif self.EPF == 'P':
            pulseWidth = int(self.txtPulseWidth.text().split(' ')[0])
            pulseWidth = pulseWidth + 1 if operation == 'inc' else pulseWidth - 1
            self.txtPulseWidth.setText(str(pulseWidth) + ' Ms')
        elif self.EPF == 'F':
            frequency = int(self.txtFrequency.text().split(' ')[0])
            frequency = frequency + 1 if operation == 'inc' else frequency - 1
            self.txtFrequency.setText(str(frequency) + ' Hz')
        
    def saveCase(self):
        energy = int(self.txtEnergy.text().split(' ')[0])
        pulseWidth = int(self.txtPulseWidth.text().split(' ')[0])
        frequency = int(self.txtFrequency.text().split(' ')[0])
        case = openCase(self.case)
        case.save(self.sex, self.bodyPart, (energy, pulseWidth, frequency))

    def bodyPartsSignals(self):
        buttons = chain(
            get_layout_btn(self.fBodyPartsLayout),
            get_layout_btn(self.mBodyPartsLayout)
        )

        for btn in buttons:
            btn.clicked.connect(lambda: self.stackedWidgetLaser.setCurrentWidget(self.laserPage))
            sex = btn.objectName().split('btn')[1][0].lower()
            bodyPart = btn.objectName().split('btn')[1][1:].lower()
            btn.clicked.connect(self.setBodyPart(sex, bodyPart))
            btn.clicked.connect(self.fillEPF)

    def fillEPF(self):
        self.loadCase()
        
    def setBodyPart(self, sex, bodyPart):
        def wrapper():
            self.bodyPart = bodyPart
            icon = QIcon()
            key = sex + ' ' + bodyPart
            self.lblSelectedBodyPart.setText(TEXT[bodyPart][self.language])
            icon.addPixmap(QPixmap(BODY_PART_ICONS[key]))
            self.btnSelectedBodyPart.setIcon(icon)
            self.btnSelectedBodyPart.setIconSize(QSize(180, 170))
            
        return wrapper

    def setSex(self, sex):
        if sex == 'male':
            self.btnMale.setStyleSheet(SELECTED_SEX)
            self.btnFemale.setStyleSheet(NOT_SELECTED_SEX)
            self.sex = 'male'
        else:
            self.btnMale.setStyleSheet(NOT_SELECTED_SEX)
            self.btnFemale.setStyleSheet(SELECTED_SEX)
            self.sex = 'female'

    def casesSignals(self):
        buttons = layout_widgets(self.casesLayout)

        for btn in buttons:
            caseName = btn.objectName().split('Case')[1]
            btn.clicked.connect(self.setCase(caseName))
            btn.clicked.connect(self.fillEPF)

    def setCase(self, case):
        def wrapper():
            self.case = case
            buttons = layout_widgets(self.casesLayout)
            for btn in buttons:
                btn.setStyleSheet(NOT_SELECTED_CASE)
                caseName = btn.objectName().split('Case')[1]
                if caseName == case:
                    btn.setStyleSheet(SELECTED_CASE)

        return wrapper

    def selectEPF(self, parameter):
        if parameter == 'E':
            self.btnEnergy.setStyleSheet(EPF_SELECTED)
            self.btnPulseWidth.setStyleSheet(EPF_NOT_SELECTED)
            self.btnFrequency.setStyleSheet(EPF_NOT_SELECTED)
            self.EPF = 'E'
        elif parameter == 'P':
            self.btnEnergy.setStyleSheet(EPF_NOT_SELECTED)
            self.btnPulseWidth.setStyleSheet(EPF_SELECTED)
            self.btnFrequency.setStyleSheet(EPF_NOT_SELECTED)
            self.EPF = 'P'
        elif parameter == 'F':
            self.btnEnergy.setStyleSheet(EPF_NOT_SELECTED)
            self.btnPulseWidth.setStyleSheet(EPF_NOT_SELECTED)
            self.btnFrequency.setStyleSheet(EPF_SELECTED)
            self.EPF = 'F'

    def loadCase(self):
        case = openCase(self.case)
        enrgy, pl, freq = case.getValue(self.sex, self.bodyPart)
        self.txtEnergy.setText(str(enrgy) + ' J/cm²')
        self.txtPulseWidth.setText(str(pl) + ' Ms')
        self.txtFrequency.setText(str(freq) + ' Hz')

    def backLaser(self):
        if self.stackedWidgetLaser.currentIndex() == 0:
            self.stackedWidget.setCurrentWidget(self.loginPage)
        else:
            self.stackedWidgetLaser.setCurrentWidget(self.bodyPartPage)      

    def backSettings(self):
        if self.stackedWidgetSettings.currentIndex() == 0:
            self.stackedWidget.setCurrentWidget(self.loginPage)
        else:
            self.stackedWidgetSettings.setCurrentWidget(self.mainPage) 

    def blinkSensorsIcon(self, sensor):
        if sensor == 'waterCir':
            self.waterCirculanFlag = not self.waterCirculanFlag
            if self.waterCirculanFlag:
                self.btnWaterCirculation.setIcon(self.waterCirWarIco)
            else:
                self.btnWaterCirculation.setIcon(self.waterCirIco)

        elif sensor == 'waterLevel':
            self.waterLevelFlag = not self.waterLevelFlag
            if self.waterLevelFlag:
                self.btnWaterLevel.setIcon(self.waterLvlWarIco)
            else:
                self.btnWaterLevel.setIcon(self.waterLvlIco)

        elif sensor == 'temp':
            self.tempFlag = not self.tempFlag
            if self.tempFlag:
                self.btnTemp.setIcon(self.tempWarIco)
            else:
                self.btnTemp.setIcon(self.tempIco)

    def stopSensorWarning(self, sensor):
        if sensor == 'waterCir':
            self.waterCirTimer.stop()
            self.waterCirculanWar = False
            self.btnTemp.setIcon(self.tempIco)
            
        elif sensor == 'waterLevel':
            self.waterLevelTimer.stop()
            self.waterLevelWar = False
            self.btnWaterLevel.setIcon(self.waterLvlIco)

        elif sensor == 'temp':
            self.tempTimer.stop()
            self.tempWar = False
            self.btnTemp.setIcon(self.tempIco)

    def startSensorWarning(self, sensor):
        if sensor == 'waterCir':
            if not self.tempWar:
                self.tempTimer.start(500)
                self.tempWar = True

        elif sensor == 'waterLevel':
            if not self.waterLevelWar:
                self.waterLevelTimer.start(500)
                self.waterLevelWar = True

        elif sensor == 'temp':
            if not self.tempWar:
                self.tempTimer.start(500)
                self.tempWar = True

    def setLock(self, lock=True):
        if lock:
            self.btnLock.setIcon(self.lockIco)
            self.lockFlag = True
        
        else:
            self.btnLock.setIcon(self.unlockIco)
            self.lockFlag = False

    def setTemp(self, value):
        self.txtTemp.setText(str(value) + ' °C')
        if not (5 <= value <= 40):
            self.startSensorWarning('temp')
        else:
            self.stopSensorWarning('temp')

    def search(self):
        name = self.txtSearch.text().lower()
        for row in range(self.usersTable.rowCount()):
            item = self.usersTable.item(row, 0)
            self.usersTable.setRowHidden(row, name not in item.text().lower())

    def type(self, letter):
        def wrapper():
            widget = QApplication.focusWidget()
            lang = 0
            if self.farsi:
                lang = 2

            if letter() == 'backspace':
                if isinstance(widget, QLineEdit):
                    widget.backspace()

                elif isinstance(widget, QTextEdit):
                    widget.textCursor().deletePreviousChar()  

            elif letter() == 'enter':
                if isinstance(widget, QTextEdit):
                    widget.append('') 

            elif len(letter()) == 3: # then it's a letter
                if isinstance(widget, QLineEdit):
                    widget.insert(letter()[lang])

                elif  isinstance(widget, QTextEdit):
                    widget.insertPlainText(letter()[lang])

            elif len(letter()) == 1: # then it's a number
                if isinstance(widget, QLineEdit):
                    widget.insert(letter())

                elif  isinstance(widget, QTextEdit):
                    widget.insertPlainText(letter())

        return wrapper

    def mousePressEvent(self, event):
        left = (self.width() - self.keyboardFrame.width()) / 2
        right = left + self.keyboardFrame.width()
        bottom = 0
        top = self.keyboardFrame.height() 

        x = left < event.x() < right
        y = bottom < self.height() - event.y() < top

        if not (x and y):
            self.keyboard('hide')

    def keyboardSignals(self):
        buttons = chain(
            layout_widgets(self.keyboardRow1),
            layout_widgets(self.keyboardRow2),
            layout_widgets(self.keyboardRow3),
            layout_widgets(self.numRow1),
            layout_widgets(self.numRow2),
            layout_widgets(self.numRow3)
        )

        for btn in buttons:
            btn.clicked.connect(self.type(btn.text))

        self.btnBackspace.clicked.connect(self.type(lambda: 'backspace'))
        self.btnEnter.clicked.connect(self.type(lambda: 'enter'))
        self.btnSpace.clicked.connect(self.type(lambda: '   '))
        self.btnShift.clicked.connect(self.shiftPressed)
        self.btnFa.clicked.connect(self.farsiPressed)

    def shiftPressed(self):
        self.shift = not self.shift

        buttons = chain(
            layout_widgets(self.keyboardRow1),
            layout_widgets(self.keyboardRow2),
            layout_widgets(self.keyboardRow3),
        )
            
        if self.shift:
            self.btnShift.setStyleSheet(SHIFT_PRESSED)
            self.btnH.setText('H\nآ')
            for btn in buttons:
                btn.setText(btn.text().upper())

        else:
            self.btnShift.setStyleSheet(SHIFT)
            self.btnH.setText('h\nا')
            for btn in buttons:
                btn.setText(btn.text().lower())

    def farsiPressed(self):
        self.farsi = not self.farsi
        
        if self.farsi:
            self.btnFa.setStyleSheet(FARSI_PRESSED)
        else:
            self.btnFa.setStyleSheet('')

    def keyboard(self, i):
        height = self.keyboardFrame.height()
        if i == 'hide' and height == 0:
            return

        if i == 'show' and height > 0:
            return

        if i == 'hide':
            height = 300
            newHeight = 0
        else:
            height = 0
            newHeight = 300

        self.animation = QPropertyAnimation(self.keyboardFrame, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(height)
        self.animation.setEndValue(newHeight)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def sort(self):
        self.sortBySession = not self.sortBySession

        if self.sortBySession:
            self.usersTable.sortItems(2, Qt.DescendingOrder)
        else:
            self.usersTable.sortItems(2, Qt.AscendingOrder)

    def loadToTabel(self):
        users = loadAllUsers()
        self.usersTable.setRowCount(len(users))
        if self.language == 1:
            text = f'{len(users)} :تعداد کل'
        else:
            text = f'Total Users: {len(users)}'

        self.lblTotalUsers.setText(text)
        row = 0
        for user in users:
            action = Action(self.usersTable, user.phoneNumber)
            action.edit.connect(self.edit)
            self.usersTable.setCellWidget(row, 3, action)
            number = QTableWidgetItem(user.phoneNumber)
            name = QTableWidgetItem(user.name)
            sessions = QTableWidgetItem(str(user.sessionNumber - 1))
            number.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            name.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            sessions.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.usersTable.setItem(row, 0, number)
            self.usersTable.setItem(row, 1, name)
            self.usersTable.setItem(row, 2, sessions)
            row += 1

    def edit(self, num):
        self.stackedWidget.setCurrentWidget(self.editUserPage)
        self.userInfo = loadUser(num)
        nextSessionDate = self.userInfo.nextSession
        if not nextSessionDate:
            self.txtNextSession.setText(TEXT['notSet'][self.language])
        else:
            diff = getDiff(nextSessionDate)

            if diff == 0:
                self.txtNextSession.setText(TEXT['today'][self.language])
            elif diff == -1:
                self.txtNextSession.setText(TEXT['1dayPassed'][self.language])
            elif diff < -1:
                self.txtNextSession.setText(f'{abs(diff)} {TEXT["nDayPassed"][self.language]}')
            elif diff == 1:
                self.txtNextSession.setText(TEXT['1dayleft'][self.language])
            else:
                self.txtNextSession.setText(f'{diff} {TEXT["nDayLeft"][self.language]}')

        self.txtEditNumber.setText(self.userInfo.phoneNumber)
        self.txtEditName.setText(self.userInfo.name)
        self.textEditNote.setPlainText(self.userInfo.note)
        sessions = self.userInfo.sessions
        totalSessions = len(sessions)+1 if len(sessions) > 0 else 0
        self.userInfoTable.setRowCount(totalSessions)
        for sn in sessions:
            date = TableWidgetItem(str(sessions[sn]['date'].date()))
            face = TableWidgetItem(str(sessions[sn]['face']))
            armpit = TableWidgetItem(str(sessions[sn]['armpit']))
            arm = TableWidgetItem(str(sessions[sn]['arm']))
            body = TableWidgetItem(str(sessions[sn]['body']))
            bikini = TableWidgetItem(str(sessions[sn]['bikini']))
            leg = TableWidgetItem(str(sessions[sn]['leg']))
            dateShots = [shot for key, shot in sessions[sn].items() if key != 'date']
            totalRow = TableWidgetItem(str(sum(dateShots)))

            self.userInfoTable.setItem(sn - 1, 0, date)
            self.userInfoTable.setItem(sn - 1, 1, face)
            self.userInfoTable.setItem(sn - 1, 2, armpit)
            self.userInfoTable.setItem(sn - 1, 3, arm)
            self.userInfoTable.setItem(sn - 1, 4, body)
            self.userInfoTable.setItem(sn - 1, 5, bikini)
            self.userInfoTable.setItem(sn - 1, 6, leg)
            self.userInfoTable.setItem(sn - 1, 7, totalRow)

        lastRow = len(sessions)
        text = 'Total' if self.language == 0 else 'جمع کل'
        lastRowTitle = TableWidgetItem(text)
        font = QFont('Arial', 18)
        font.setBold(True)
        lastRowTitle.setFont(font)
        self.userInfoTable.setItem(lastRow, 0, lastRowTitle)

        bodyParts = self.userInfo.shot.keys()
        totalColumn = dict.fromkeys(bodyParts, 0)
        for shots in sessions.values():
            for part in bodyParts:
                totalColumn[part] += shots[part] 

        face = TableWidgetItem(str(totalColumn['face']))
        armpit = TableWidgetItem(str(totalColumn['armpit']))
        arm = TableWidgetItem(str(totalColumn['arm']))
        body = TableWidgetItem(str(totalColumn['body']))
        bikini = TableWidgetItem(str(totalColumn['bikini']))
        leg = TableWidgetItem(str(totalColumn['leg']))
        datesShots = sum(totalColumn.values())
        totalShots = TableWidgetItem(str(datesShots))
        
        self.userInfoTable.setItem(lastRow, 1, face)
        self.userInfoTable.setItem(lastRow, 2, armpit)
        self.userInfoTable.setItem(lastRow, 3, arm)
        self.userInfoTable.setItem(lastRow, 4, body)
        self.userInfoTable.setItem(lastRow, 5, bikini)
        self.userInfoTable.setItem(lastRow, 6, leg)
        self.userInfoTable.setItem(lastRow, 7, totalShots)

    def futureSessions(self):
        users = loadAllUsers()
        rowToday = 0
        rowTomorrow = 0
        for user in users:
            if user.sessionNumber == 1:
                nextSession = user.nextSession
                num = TableWidgetItem(user.phoneNumber)
                text = 'First Time' if self.language == 0 else 'اولین جلسه' 
                lastSession = TableWidgetItem(text)
                sn = TableWidgetItem(str(user.sessionNumber))
                if nextSession and getDiff(nextSession) == 0:
                    self.tableToday.setRowCount(rowToday +1)
                    self.tableToday.setItem(rowToday, 0, num)
                    self.tableToday.setItem(rowToday, 1, lastSession)
                    self.tableToday.setItem(rowToday, 2, sn)
                    rowToday += 1
                elif nextSession and getDiff(nextSession) == 1:
                    self.tableTomorrow.setRowCount(rowTomorrow +1)
                    self.tableTomorrow.setItem(rowTomorrow, 0, num)
                    self.tableTomorrow.setItem(rowTomorrow, 1, lastSession)
                    self.tableTomorrow.setItem(rowTomorrow, 2, sn)
                    rowTomorrow += 1

            else:
                nextSession = user.nextSession
                lastSession = user.sessions[user.sessionNumber -1]['date']
                lastSession = TableWidgetItem(str(lastSession.date()))
                num = TableWidgetItem(user.phoneNumber)
                sn = TableWidgetItem(str(user.sessionNumber))
                if nextSession and getDiff(nextSession) == 0:
                    self.tableToday.setRowCount(rowToday +1)
                    self.tableToday.setItem(rowToday, 0, num)
                    self.tableToday.setItem(rowToday, 1, lastSession)
                    self.tableToday.setItem(rowToday, 2, sn)
                    rowToday += 1
                elif nextSession and getDiff(nextSession) == 1:
                    self.tableTomorrow.setRowCount(rowTomorrow +1)
                    self.tableTomorrow.setItem(rowTomorrow, 0, num)
                    self.tableTomorrow.setItem(rowTomorrow, 1, lastSession)
                    self.tableTomorrow.setItem(rowTomorrow, 2, sn)
                    rowTomorrow += 1

        if self.language == 1:
            textToday = f'{rowToday} → امروز'
            textTomorrow = f'{rowTomorrow} → فردا'
        
        else:
            textToday = f'Today → {rowToday}'
            textTomorrow = f'Tomorrow → {rowTomorrow}'

        self.lblToday.setText(textToday)
        self.lblTomorrow.setText(textTomorrow)
        self.tableToday.setRowCount(rowToday)
        self.tableTomorrow.setRowCount(rowTomorrow)

    def saveUserInfo(self):
        numberEdit = self.txtEditNumber.text()
        nameEdit = self.txtEditName.text()
        noteEdit = self.textEditNote.toPlainText()

        if not numberEdit:
            self.setLabel(TEXT['emptyNumber'][self.language], 'edit')
            self.txtEditNumber.setFocus()
            return

        if not userExists(self.userInfo.phoneNumber):
            self.setLabel(TEXT['userBeenDeleted'][self.language], 'edit')
            return

        if numberEdit != self.userInfo.phoneNumber:
            if userExists(numberEdit):
                self.setLabel(
                    TEXT['alreadyExists'][self.language], 'edit'
                )
                self.txtEditNumber.setFocus()
                return

            oldNumber = self.userInfo.phoneNumber
            if self.user and self.user.phoneNumber == oldNumber:
                self.user.setPhoneNumber(numberEdit)

            self.userInfo.setPhoneNumber(numberEdit)
            newNumber = self.userInfo.phoneNumber
            renameUserFile(oldNumber, newNumber)

        if not nameEdit:
            nameEdit = 'Nobody'

        self.userInfo.setName(nameEdit)
        self.userInfo.setNote(noteEdit)

        if self.user and self.user.phoneNumber == self.userInfo.phoneNumber:
            self.user.setName(nameEdit)
            self.user.setNote(noteEdit)

        self.userInfo.save()
        self.setLabel(TEXT['userUpdated'][self.language], 'edit')
        self.loadToTabel()

    def deleteUser(self):
        number = self.userInfo.phoneNumber        
        deleteUser(number)
        self.loadToTabel()
        self.changeAnimation('horizontal')
        self.stackedWidget.setCurrentWidget(self.userManagementPage)

    def submit(self):
        number = self.txtNumberSubmit.text()
        name = self.txtNameSubmit.text()

        if not number:
            self.setLabel(TEXT['emptyNumber'][self.language], 'submit')
            return

        if userExists(number):
            self.setLabel(TEXT['alreadyExistsSub'][self.language], 'submit')
            return

        user = User(number, name)
        user.save()
        self.txtNumber.setText(number)
        self.txtNumberSubmit.clear()
        self.txtNameSubmit.clear()
        self.stackedWidget.setCurrentWidget(self.loginPage)

    def login(self):
        numberEntered = self.txtNumber.text()

        if (not self.user) or (self.user.currentSession == 'finished'):

            if not numberEntered:
                self.setLabel(TEXT['emptyNumber'][self.language], 'login')
                return

            self.user = loadUser(numberEntered)

            if not self.user:
                self.txtNumberSubmit.setText(numberEntered)
                self.txtNameSubmit.setFocus()
                self.changeAnimation('vertical')
                self.stackedWidget.setCurrentWidget(self.newSessionPage)
                return

            self.user.setCurrentSession('started')
            self.keyboard('hide')
            self.changeAnimation('horizontal')
            self.stackedWidget.setCurrentWidget(self.laserMainPage)

        elif self.user and self.user.currentSession == 'started':
            if not userExists(self.user.phoneNumber):
                    self.setLabel(TEXT['userBeenDeleted'][self.language], 'login')
                    self.user = None
                    return
            elif numberEntered != self.user.phoneNumber:
                if self.language == 0:
                    text = f'{TEXT["sssionNotOver"][self.language]} <{self.user.name}> ({self.user.phoneNumber})'
                else:
                    text = f'({self.user.phoneNumber}) <{self.user.name}> {TEXT["sssionNotOver"][self.language]}'

                self.setLabel(text, 'login')
                return
            else:
                if not userExists(self.user.phoneNumber):
                    self.setLabel(TEXT['userBeenDeleted'][self.language], 'login')
                    self.user = None
                    return
                    
                self.user.setCurrentSession('started')
                self.keyboard('hide')
                self.changeAnimation('horizontal')
                self.stackedWidget.setCurrentWidget(self.laserMainPage)

    def endSession(self):
        self.user.setCurrentSession('finished')
        self.user.addSession()
        self.user.save()
        self.user = None
        self.stackedWidget.setCurrentWidget(self.loginPage)
        self.stackedWidgetLaser.setCurrentIndex(0)

    def setLabel(self, text, label, sec=5):
        if label == 'login':
            self.lblLogin.setText(text)
            self.txtNumber.setFocus()
            self.txtNumber.selectAll()
            self.loginLabelTimer.start(sec * 1000)
        
        elif label == 'submit':
            self.lblSubmit.setText(text)
            self.txtNumber.setFocus()
            self.txtNumber.selectAll()
            self.submitLabelTimer.start(sec * 1000)

        elif label == 'edit':
            self.lblEditUser.setText(text)
            self.editLabelTimer.start(sec * 1000)

        elif label == 'nextSession':
            self.lblErrNextSession.setText(text)
            self.nextSessionLabelTimer.start(sec * 1000)

    def clearLabel(self, label):
        if label == 'login':
            self.lblLogin.clear()
            self.loginLabelTimer.stop()
        
        elif label == 'submit':
            self.lblSubmit.clear()
            self.submitLabelTimer.stop()

        elif label == 'edit':
            self.lblEditUser.clear()
            self.editLabelTimer.stop()

        elif label == 'nextSession':
            self.lblErrNextSession.clear()
            self.nextSessionLabelTimer.stop()

    def changeLang(self):
        global app
        if self.checkBoxLang.isChecked():
            app.setStyleSheet('*{font-family:"Tahoma"}')
            self.lblEn.setStyleSheet("font-family:'Arial'")
            self.language = 1
            self.userInfoFrame.setLayoutDirection(Qt.RightToLeft)
            self.nextSessionFrame.setLayoutDirection(Qt.RightToLeft)
        else:
            app.setStyleSheet('*{font-family:"Arial"}')
            self.lblFa.setStyleSheet("font-family:'Tahoma'")
            self.userInfoFrame.setLayoutDirection(Qt.LeftToRight)
            self.nextSessionFrame.setLayoutDirection(Qt.LeftToRight)
            self.language = 0

        self.lblLanguage.setText(TEXT['lblLanguage'][self.language])
        self.lblSettingsHeader.setText(TEXT['lblSettingsHeader'][self.language])
        self.btnHwSettings.setText(TEXT['btnHwSettings'][self.language])
        self.btnUmSettings.setText(TEXT['btnUmSettings'][self.language])
        self.btnUiSettings.setText(TEXT['btnUiSettings'][self.language])
        self.lblUserNumber.setText(TEXT['lblUserNumber'][self.language])
        self.txtNumber.setPlaceholderText(TEXT['txtNumber'][self.language])
        self.btnLogin.setText(TEXT['btnLogin'][self.language])
        self.lblHeaderTutorials.setText(TEXT['lblHeaderTutorials'][self.language])        
        self.lblVideos.setText(TEXT['lblVideos'][self.language])
        self.lblTitle.setText(TEXT['lblTitle'][self.language])
        self.lblHeaderFsessions.setText(TEXT['lblHeaderFsessions'][self.language])
        self.tableToday.horizontalHeaderItem(0).setText(TEXT['tbFsessions0'][self.language])
        self.tableToday.horizontalHeaderItem(1).setText(TEXT['tbFsessions1'][self.language])
        self.tableToday.horizontalHeaderItem(2).setText(TEXT['tbFsessions2'][self.language])
        self.tableTomorrow.horizontalHeaderItem(0).setText(TEXT['tbFsessions0'][self.language])
        self.tableTomorrow.horizontalHeaderItem(1).setText(TEXT['tbFsessions1'][self.language])
        self.tableTomorrow.horizontalHeaderItem(2).setText(TEXT['tbFsessions2'][self.language])
        self.lblHeaderUm.setText(TEXT['lblHeaderUm'][self.language])
        self.usersTable.horizontalHeaderItem(0).setText(TEXT['usersTable0'][self.language])
        self.usersTable.horizontalHeaderItem(1).setText(TEXT['usersTable1'][self.language])
        self.usersTable.horizontalHeaderItem(2).setText(TEXT['usersTable2'][self.language])
        self.usersTable.horizontalHeaderItem(3).setText(TEXT['usersTable3'][self.language])
        self.btnSort.setText(TEXT['btnSort'][self.language])
        self.txtSearch.setPlaceholderText(TEXT['txtSearch'][self.language])
        self.lblNote.setText(TEXT['lblNote'][self.language])
        self.lblName.setText(TEXT['lblName'][self.language])
        self.lblPhoneNumber.setText(TEXT['lblPhoneNumber'][self.language])
        self.lblNextSession.setText(TEXT['lblNextSession'][self.language])
        self.lblHeaderUserInfo.setText(TEXT['lblHeaderUserInfo'][self.language])
        self.btnNextSession.setText(TEXT['btnNextSession'][self.language])
        self.btnSaveInfo.setText(TEXT['btnSaveInfo'][self.language])
        self.btnDeleteUser.setText(TEXT['btnDeleteUser'][self.language])
        self.userInfoTable.horizontalHeaderItem(0).setText(TEXT['userInfoTable0'][self.language])        
        self.userInfoTable.horizontalHeaderItem(1).setText(TEXT['userInfoTable1'][self.language])        
        self.userInfoTable.horizontalHeaderItem(2).setText(TEXT['userInfoTable2'][self.language])        
        self.userInfoTable.horizontalHeaderItem(3).setText(TEXT['userInfoTable3'][self.language])        
        self.userInfoTable.horizontalHeaderItem(4).setText(TEXT['userInfoTable4'][self.language])        
        self.userInfoTable.horizontalHeaderItem(5).setText(TEXT['userInfoTable5'][self.language])        
        self.userInfoTable.horizontalHeaderItem(6).setText(TEXT['userInfoTable6'][self.language])        
        self.userInfoTable.horizontalHeaderItem(7).setText(TEXT['userInfoTable7'][self.language])
        self.lblDate.setText(TEXT['lblDate'][self.language])
        self.lblDays.setText(TEXT['lblDays'][self.language])
        self.lblDaysAfter.setText(TEXT['lblDaysAfter'][self.language])        
        self.btnCancelNS.setText(TEXT['btnCancelNS'][self.language])
        self.btnOkNS.setText(TEXT['btnOkNS'][self.language])        
        self.lblHeaderNextSession.setText(TEXT['lblHeaderNextSession'][self.language])
        self.lblHeaderNewUser.setText(TEXT['lblHeaderNewUser'][self.language])
        self.lblEnterUserInfo.setText(TEXT['lblEnterUserInfo'][self.language])
        self.txtNumberSubmit.setPlaceholderText(TEXT['txtNumberSubmit'][self.language])
        self.txtNameSubmit.setPlaceholderText(TEXT['txtNameSubmit'][self.language])
        self.btnSubmit.setText(TEXT['btnSubmit'][self.language])   
        self.btnEndSession.setText(TEXT['btnEndSession'][self.language])
        self.btnFemale.setText(TEXT['btnFemale'][self.language])        
        self.btnMale.setText(TEXT['btnMale'][self.language])
        self.btnFemale.setText(TEXT['btnFemale'][self.language])
        self.btnMale.setText(TEXT['btnMale'][self.language])
        self.lblFFace.setText(TEXT['lblFFace'][self.language])
        self.lblFArmpit.setText(TEXT['lblFArmpit'][self.language])
        self.lblFArm.setText(TEXT['lblFArm'][self.language])
        self.lblFBody.setText(TEXT['lblFBody'][self.language])
        self.lblFBikini.setText(TEXT['lblFBikini'][self.language])
        self.lblFLeg.setText(TEXT['lblFLeg'][self.language])
        self.lblMFace.setText(TEXT['lblMFace'][self.language])
        self.lblMArmpit.setText(TEXT['lblMArmpit'][self.language])
        self.lblMArm.setText(TEXT['lblMArm'][self.language])
        self.lblMBody.setText(TEXT['lblMBody'][self.language])
        self.lblMBikini.setText(TEXT['lblMBikini'][self.language])
        self.lblMLeg.setText(TEXT['lblMLeg'][self.language])
        self.lblEnergy.setText(TEXT['lblEnergy'][self.language])
        self.lblFrequency.setText(TEXT['lblFrequency'][self.language])
        self.lblPulseWidth.setText(TEXT['lblPulseWidth'][self.language])
        self.lblCounter.setText(TEXT['lblCounter'][self.language])
        self.lblReady.setText(TEXT['lblReady'][self.language])    
        self.lblStandby.setText(TEXT['lblStandby'][self.language])            


app = QApplication(sys.argv)
mainWin = MainWin()
mainWin.showFullScreen()
sys.exit(app.exec_())





