from os import stat
from PyQt5 import uic
from communication import *
from promotions import *
from utility import *
from styles import *
from lang import *
from case import *
from user import *
from lock import *
from itertools import chain
from pathlib import Path
import jdatetime, math, sys


class MainWin(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWin, self).__init__(*args, **kwargs)
        uic.loadUi(APP_UI, self)
        self.setupUi()
        
    def setupUi(self):
        # self.setCursor(Qt.BlankCursor)
        self.configs = loadConfigs()
        self.usersData = loadUsers()
        self.usersList = list(self.usersData.values())
        if RPI_VERSION == '3':
            self.serialC = SerialTimer()
        else:
            self.serialC = SerialThread()
        self.serialC.sensorFlags.connect(self.setSensors)
        self.serialC.tempValue.connect(self.setTemp)
        self.serialC.shot.connect(self.shot)
        self.serialC.serialNumber.connect(self.txtSerialNumber.setText)
        self.serialC.productionDate.connect(self.txtProductionDate.setText)
        self.serialC.laserEnergy.connect(self.txtLaserDiodeEnergy.setText)
        self.serialC.firmwareVesion.connect(self.txtFirmwareVersion.setText)
        self.serialC.readCooling.connect(
            lambda: laserPage({'cooling': self.cooling})
        )
        self.serialC.readEnergy.connect(
            lambda: laserPage({'energy': self.energy})
        )
        self.serialC.readPulseWidht.connect(
            lambda: laserPage({'pulseWidht': self.pulseWidth})
        )
        self.serialC.readFrequency.connect(
            lambda: laserPage({'frequency': self.frequency})
        )
        self.serialC.sysDate.connect(self.receiveDate)
        self.serialC.sysClock.connect(self.adjustTime)
        self.updateT = UpdateFirmware()
        self.updateT.result.connect(self.updateResult)
        self.license = self.configs['LICENSE']
        self.movie = QMovie(LOCK_GIF)
        self.movie.frameChanged.connect(self.unlock)
        self.lblLock.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        self.lblSplash.setPixmap(QPixmap(SPLASH))
        self.lblSplash.clicked.connect(lambda: self.changeAnimation('vertical'))
        self.lblSplash.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.ownerInfoSplash = QLabel(self.lblSplash)
        self.ownerInfoSplash.setText('')
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont(IRAN_NASTALIQ)
        font_id = font_db.addApplicationFont(IRANIAN_SANS)
        self.ownerInfoSplash.setFont(QFont("IranNastaliq", 40))
        ownerInfo = self.configs['OwnerInfo']
        if ownerInfo and isFarsi(ownerInfo):
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_FA)
        else:
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_EN)
        self.ownerInfoSplash.setText(ownerInfo)
        if not ownerInfo:
            self.ownerInfoSplash.setVisible(False)
        self.ownerInfoSplash.move(self.geometry().bottomLeft())     
        self.time(edit=True)
        self.changeTheme(self.configs['theme'])
        self.initSounds()       
        self.initPages()
        self.initTimers()
        self.initButtons()
        self.initTables()
        self.initTextboxes()
        self.user = None
        self.userNextSession = None
        self.sortBySession = False
        self.selectedUsers = []
        self.shift = False
        self.farsi = False
        self.sex = 'female'
        self.bodyPart = ''
        self.case = 'I'
        self.cooling = 0
        self.energy = MIN_ENRGEY
        self.pulseWidth = MIN_PULSE_WIDTH
        self.frequency = MIN_FREQUENCY
        self.currentCounter = 0
        self.receivedTime = ()
        self.startupEditTime = False
        self.ready = False
        self.langIndex = 0 if self.configs['LANGUAGE'] == 'en' else 1
        icon = QPixmap(SELECTED_LANG_ICON)
        self.lblEnSelected.setPixmap(icon.scaled(70, 70))
        icon = QPixmap(SPARK_ICON)
        self.lblSpark.setPixmap(icon.scaled(120, 120))
        self.lblSpark.setVisible(False)
        self.lblLasing.setVisible(False)
        if self.configs['LANGUAGE'] == 'fa':
            self.changeLang(self.configs['LANGUAGE'])
        self.shortcut = QShortcut(QKeySequence("Ctrl+x"), self)
        self.shortcut.activated.connect(self.close)
        self.chbSlideTransition.setFixedSize(150, 48)
        self.chbSlideTransition.setCheckState(
            2 if self.configs['slideTransition'] else 0
        )
        self.chbSlideTransition.pressed.connect(self.touchSound.play)
        self.chbSlideTransition.stateChanged.connect(self.setTransition)
        self.chbTouchSound.setFixedSize(150, 48)
        self.chbTouchSound.setCheckState(
            2 if self.configs['touchSound'] else 0
        )
        self.chbTouchSound.pressed.connect(self.touchSound.play)
        self.chbTouchSound.stateChanged.connect(self.setTouchSound)
        self.loadLocksTable()
        self.bodyPartsSignals()
        self.keyboardSignals()
        self.casesSignals()
        self.tutorials()
        self.initSensors()
        self.checkUUID()
        readTime()

    def setTouchSound(self, state):
        volume = 100 if state == 2 else 0
        self.keyboardSound.setVolume(volume)
        self.touchSound.setVolume(volume)
        self.configs['touchSound'] = True if state == 2 else False 
        saveConfigs(self.configs)

    def initSounds(self):
        self.keyboardSound = QMediaPlayer()
        self.touchSound = QMediaPlayer()
        self.shotSound = QMediaPlayer()
        self.keyboardSound.setVolume(100 if self.configs['touchSound'] else 0)
        self.touchSound.setVolume(100 if self.configs['touchSound'] else 0)        
        self.keyboardSound.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(KEYBOARD_SOUND)
            )
        )
        self.touchSound.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(TOUCH_SOUND)
            )
        )
        self.shotSound.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(SHOT_SOUND)
            )
        )

    def playTouchSound(self):
        self.touchSound.stop()
        self.touchSound.play()

    def initPages(self):
        self.stackedWidget.setCurrentWidget(self.splashPage)
        self.stackedWidgetLaser.setCurrentIndex(0)
        self.stackedWidgetSex.setCurrentIndex(0)
        self.stackedWidgetSettings.setCurrentIndex(0)
        self.stackedWidget.setTransitionDirection(Qt.Vertical)
        self.stackedWidget.setTransitionSpeed(500)
        self.stackedWidget.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidget.setSlideTransition(self.configs['slideTransition'])
        self.stackedWidgetSex.setTransitionDirection(Qt.Vertical)
        self.stackedWidgetSex.setTransitionSpeed(500)
        self.stackedWidgetSex.setTransitionEasingCurve(QEasingCurve.OutBack)
        self.stackedWidgetSex.setSlideTransition(self.configs['slideTransition'])
        self.stackedWidgetLaser.setTransitionDirection(Qt.Horizontal)
        self.stackedWidgetLaser.setTransitionSpeed(500)
        self.stackedWidgetLaser.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidgetLaser.setSlideTransition(self.configs['slideTransition'])
        self.stackedWidgetSettings.setTransitionDirection(Qt.Horizontal)
        self.stackedWidgetSettings.setTransitionSpeed(500)
        self.stackedWidgetSettings.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.stackedWidgetSettings.setSlideTransition(self.configs['slideTransition'])
        self.hwStackedWidget.setTransitionDirection(Qt.Vertical)
        self.hwStackedWidget.setTransitionSpeed(500)
        self.hwStackedWidget.setTransitionEasingCurve(QEasingCurve.OutQuart)
        self.hwStackedWidget.setSlideTransition(self.configs['slideTransition'])

    def setTransition(self, state):
        checked = True if state == 2 else False
        self.stackedWidget.setSlideTransition(checked)
        self.stackedWidgetSex.setSlideTransition(checked)
        self.stackedWidgetLaser.setSlideTransition(checked)
        self.stackedWidgetSettings.setSlideTransition(checked)
        self.hwStackedWidget.setSlideTransition(checked)
        self.configs['slideTransition'] = checked
        saveConfigs(self.configs)

    def initTimers(self):
        if RPI_VERSION == '3':
            self.checkBuffer = QTimer()
            self.checkBuffer.timeout.connect(self.serialC.checkBuffer)
            self.checkBuffer.start(10)
        else:
            self.serialC.start()
        self.loginLabelTimer = QTimer()
        self.submitLabelTimer = QTimer()
        self.editLabelTimer = QTimer()
        self.nextSessionLabelTimer = QTimer()
        self.hwUpdatedLabelTimer = QTimer()
        self.incDaysTimer = QTimer()
        self.decDaysTimer = QTimer()
        self.backspaceTimer = QTimer()
        self.passwordLabelTimer = QTimer()
        self.hwWrongPassTimer = QTimer()
        self.uuidPassLabelTimer = QTimer()
        self.sysTimeStatusLabelTimer = QTimer()
        self.lockErrorLabel = QTimer()
        self.updateFirmwareLabelTimer = QTimer()
        self.systemTimeTimer = QTimer()
        self.readyErrorTimer =  QTimer()
        self.monitorSensorsTimer = QTimer()
        self.sparkTimer = QTimer()
        self.restartTimer = QTimer()
        self.loadUsersTimer = QTimer()
        self.restartCounter = 6
        self.loadUsersTimer.timeout.connect(self.addUsersTable)
        self.loadUsersTimer.start(20)
        self.restartTimer.timeout.connect(self.restartForUpdate)
        self.systemTimeTimer.timeout.connect(self.time)
        self.loginLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblLogin, self.loginLabelTimer)
        )
        self.submitLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblSubmit, self.submitLabelTimer)
        )
        self.editLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblEditUser, self.editLabelTimer)
        )
        self.nextSessionLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblErrNextSession, self.nextSessionLabelTimer)
        )
        self.hwUpdatedLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblSaveHw, self.hwUpdatedLabelTimer)
        )
        self.passwordLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblPassword, self.passwordLabelTimer)
        )
        self.uuidPassLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblPassUUID, self.uuidPassLabelTimer)
        )
        self.sysTimeStatusLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblSystemTimeStatus, self.sysTimeStatusLabelTimer)
        )
        self.lockErrorLabel.timeout.connect(
            lambda: self.clearLabel(self.lblLockError, self.lockErrorLabel)
        )
        self.readyErrorTimer.timeout.connect(
            lambda: self.clearLabel(self.lblReadyError, self.readyErrorTimer)
        )
        self.updateFirmwareLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblUpdateFirmware, self.updateFirmwareLabelTimer)
        )
        self.incDaysTimer.timeout.connect(lambda: self.incDecDay('inc'))
        self.decDaysTimer.timeout.connect(lambda: self.incDecDay('dec'))
        self.backspaceTimer.timeout.connect(self.type(lambda: 'backspace'))
        self.hwWrongPassTimer.timeout.connect(self.hwWrongPass)
        self.sparkTimer.timeout.connect(self.hideSpark)
        self.monitorSensorsTimer.timeout.connect(self.monitorSensors)
        self.monitorSensorsTimer.start(1000)

    def initTables(self):
        self.usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usersTable.verticalHeader().setDefaultSectionSize(75)
        self.usersTable.horizontalHeader().setFixedHeight(60)
        self.usersTable.verticalHeader().setVisible(False)
        self.tableTomorrow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableTomorrow.verticalHeader().setDefaultSectionSize(70)
        self.tableTomorrow.horizontalHeader().setFixedHeight(60)
        self.tableTomorrow.verticalHeader().setVisible(False)
        self.tableAfterTomorrow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableAfterTomorrow.verticalHeader().setDefaultSectionSize(70)
        self.tableAfterTomorrow.horizontalHeader().setFixedHeight(60)
        self.tableAfterTomorrow.verticalHeader().setVisible(False)
        self.userInfoTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.userInfoTable.verticalHeader().setDefaultSectionSize(70)
        self.userInfoTable.horizontalHeader().setFixedHeight(60)
        self.userInfoTable.verticalHeader().setVisible(False)
        self.tableLock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableLock.verticalHeader().setDefaultSectionSize(70)
        self.tableLock.horizontalHeader().setFixedHeight(60)
        self.tableLock.verticalHeader().setVisible(False)
        header = self.userInfoTable.horizontalHeader()
        header.setSectionResizeMode(0,  QHeaderView.ResizeToContents)

    def initButtons(self):
        self.btnEnLang.clicked.connect(lambda: self.changeLang('en'))
        self.btnFaLang.clicked.connect(lambda: self.changeLang('fa'))
        self.btnEnter.clicked.connect(self.unlockLIC)
        self.btnSort.clicked.connect(self.sort)
        self.btnEndSession.clicked.connect(lambda: self.setNextSession('lazer'))
        self.btnEndSession.clicked.connect(lambda: enterPage(MAIN_PAGE))
        self.btnPowerOption.clicked.connect(lambda: self.powerOption('show'))
        self.btnPower.clicked.connect(self.powerOff)
        self.btnRestart.clicked.connect(self.restart)
        self.btnPower_2.clicked.connect(self.powerOff)
        self.btnPower_3.clicked.connect(self.powerOff)
        self.btnStartSession.clicked.connect(self.startSession)
        self.btnSubmit.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnSubmit.clicked.connect(self.submit)
        self.btnBackNewSession.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnBackManagement.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnBackManagement.clicked.connect(lambda: self.txtSearch.clear())
        self.btnBackManagement.clicked.connect(lambda: saveUser(self.usersData))
        self.btnBackSettings.clicked.connect(self.backSettings)
        self.btnBackSettings.clicked.connect(self.systemTimeTimer.stop)
        self.btnBackEditUser.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnBackEditUser.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.userManagementPage))
        self.btnSettings.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnSettings.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        self.btnUiSettings.clicked.connect(lambda: self.stackedWidgetSettings.setCurrentWidget(self.uiPage))
        self.btnEnterHw.clicked.connect(self.loginHw)
        self.btnHwSettings.clicked.connect(self.btnHwsettingClicked)
        # self.btnUserManagement.clicked.connect(self.loadToTabel)
        self.btnSaveInfo.clicked.connect(self.saveUserInfo)
        self.btnDeleteUser.clicked.connect(self.deleteUser)
        self.btnUserManagement.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnUserManagement.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.userManagementPage))
        self.btnNotify.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnNotify.clicked.connect(self.futureSessions)
        self.btnNotify.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.notifyPage))
        self.btnBackNotify.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnTutorials.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnTutorials.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.tutorialPage))
        self.btnBackTutorials.clicked.connect(self.pause)
        self.btnBackTutorials.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnNextSession.clicked.connect(lambda: self.changeAnimation('vertical'))
        self.btnNextSession.clicked.connect(lambda: self.setNextSession('edit'))
        self.btnCancelNS.clicked.connect(self.cancelNextSession)
        self.btnCancelNS.clicked.connect(lambda: self.keyboard('hide'))
        self.btnOkNS.clicked.connect(lambda: self.keyboard('hide'))
        self.btnDecDay.clicked.connect(lambda: self.incDecDay('dec'))
        self.btnIncDay.clicked.connect(lambda: self.incDecDay('inc'))
        self.btnOkNS.clicked.connect(self.saveNextSession)
        self.btnMale.clicked.connect(lambda: self.setSex('male'))
        self.btnFemale.clicked.connect(lambda: self.setSex('female'))
        self.btnBackspace.pressed.connect(lambda: self.backspaceTimer.start(100))
        self.btnBackspace.released.connect(lambda: self.backspaceTimer.stop())
        self.btnIncDay.pressed.connect(lambda: self.incDaysTimer.start(100))
        self.btnIncDay.released.connect(lambda: self.incDaysTimer.stop())
        self.btnDecDay.pressed.connect(lambda: self.decDaysTimer.start(100))
        self.btnDecDay.released.connect(lambda: self.decDaysTimer.stop())
        self.btnIncE.clicked.connect(lambda: self.setEnergy('inc'))
        self.btnDecE.clicked.connect(lambda: self.setEnergy('dec'))
        self.sliderEnergy.sliderMoved.connect(self.sldrSetEnergy)
        self.btnIncP.clicked.connect(lambda: self.setPulseWidth('inc'))
        self.btnDecP.clicked.connect(lambda: self.setPulseWidth('dec'))
        self.sliderPulseWidth.sliderMoved.connect(self.sldrSetPulseWidth)
        self.btnIncF.clicked.connect(lambda: self.setFrequency('inc'))
        self.btnDecF.clicked.connect(lambda: self.setFrequency('dec'))
        self.sliderFrequency.sliderMoved.connect(self.sldrSetFrequency)
        self.btnMale.clicked.connect(lambda: self.stackedWidgetSex.setCurrentWidget(self.malePage))
        self.btnFemale.clicked.connect(lambda: self.stackedWidgetSex.setCurrentWidget(self.femalePage))
        self.btnDecCooling.clicked.connect(lambda: self.setCooling('dec'))
        self.btnIncCooling.clicked.connect(lambda: self.setCooling('inc'))
        self.btnSaveCase.clicked.connect(self.saveCase)
        self.btnSaveCase.pressed.connect(lambda: self.sliderChgColor('pressed'))
        self.btnSaveCase.released.connect(lambda: self.sliderChgColor('released'))
        self.btnSaveHw.clicked.connect(self.saveHwSettings)
        self.btnResetCounter.clicked.connect(self.resetTotalShot)
        self.btnReady.clicked.connect(lambda: self.setReady(True))
        self.btnStandby.clicked.connect(lambda: self.setReady(False))
        self.btnUnqEnter.clicked.connect(self.unlockUUID)
        self.btnHwinfo.clicked.connect(lambda: self.hwStackedWidget.setCurrentWidget(self.infoPage))
        self.btnHwinfo.clicked.connect(lambda: self.enterSettingPage(REPORT))
        self.btnSystemLock.clicked.connect(lambda: self.hwStackedWidget.setCurrentWidget(self.lockSettingsPage))
        self.btnSystemLock.clicked.connect(lambda: lockPage(REPORT))
        self.btnSystemLock.clicked.connect(lambda: self.systemTimeTimer.start(1000))
        self.btnAddLock.clicked.connect(self.addLock)
        self.btnBackLaser.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnBackLaser.clicked.connect(lambda: self.stackedWidgetLaser.setCurrentWidget(self.bodyPartPage))
        self.btnBackLaser.clicked.connect(lambda: self.btnBackLaser.setVisible(False))
        self.btnBackLaser.clicked.connect(lambda: self.setReady(False))
        self.btnBackLaser.clicked.connect(lambda: enterPage(BODY_PART_PAGE))
        self.btnBackLaser.setVisible(False)
        self.btnUpdateFirmware.clicked.connect(self.updateSystem)
        self.btnShowSplash.clicked.connect(self.showSplash)
        self.btnDelSelectedUsers.clicked.connect(self.removeSelectedUsers)
        self.btnColor1.setStyleSheet(BTN_COLOR1)
        self.btnColor2.setStyleSheet(BTN_COLOR2)
        self.btnColor3.setStyleSheet(BTN_COLOR3)
        self.btnColor4.setStyleSheet(BTN_COLOR4)
        self.btnTheme1.setStyleSheet(BTN_THEME1)
        self.btnTheme2.setStyleSheet(BTN_THEME2)
        self.btnTheme3.setStyleSheet(BTN_THEME3)
        self.btnTheme4.setStyleSheet(BTN_THEME4)
        self.btnColor1.clicked.connect(lambda: self.changeTheme('C1'))
        self.btnColor2.clicked.connect(lambda: self.changeTheme('C2'))
        self.btnColor3.clicked.connect(lambda: self.changeTheme('C3'))
        self.btnColor4.clicked.connect(lambda: self.changeTheme('C4'))
        self.btnTheme1.clicked.connect(lambda: self.changeTheme('T1'))
        self.btnTheme2.clicked.connect(lambda: self.changeTheme('T2'))        
        self.btnTheme3.clicked.connect(lambda: self.changeTheme('T3'))
        self.btnTheme4.clicked.connect(lambda: self.changeTheme('T4'))        
        sensors = [
            'btnPhysicalDamage', 'btnOverHeat', 'btnTemp',
            'btnLock', 'btnWaterLevel', 'btnWaterflow',
        ]
        keyboardButtons = list(chain(
            layout_widgets(self.keyboardRow1),
            layout_widgets(self.keyboardRow2),
            layout_widgets(self.keyboardRow3),
            layout_widgets(self.numRow1),
            layout_widgets(self.numRow2),
            layout_widgets(self.numRow3)
        ))
        keyboardButtons.append(self.btnBackspace)
        keyboardButtons.append(self.btnReturn)
        keyboardButtons.append(self.btnShift)
        keyboardButtons.append(self.btnFa)
        keyboardButtons.append(self.btnSpace)
        self.touchSignals = {}
        allButtons = self.findChildren(QPushButton)
        for btn in allButtons:
            if btn.objectName() == 'btnSelectedBodyPart':
                continue

            elif btn in keyboardButtons:
                self.touchSignals[btn.objectName()] = btn.pressed.connect(
                    self.keyboardSound.play
                )
            elif btn.objectName() not in sensors:
                self.touchSignals[btn.objectName()] = btn.pressed.connect(
                    self.playTouchSound
                )

    def initTextboxes(self):
        self.txtNumber.returnPressed.connect(self.startSession)
        self.txtNameSubmit.returnPressed.connect(self.submit)
        self.txtNumberSubmit.returnPressed.connect(self.submit)
        self.txtNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtNumberSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtNameSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditName.fIn.connect(lambda: self.keyboard('show'))
        self.textEditNote.fIn.connect(lambda: self.keyboard('show'))
        self.txtSearch.fIn.connect(lambda: self.keyboard('show'))
        self.txtDate.fIn.connect(lambda: self.keyboard('show'))
        self.txtDays.fIn.connect(lambda: self.keyboard('show'))
        self.txtPassword.fIn.connect(lambda: self.keyboard('show'))
        self.txtHwPass.fIn.connect(lambda: self.keyboard('show'))
        self.txtSerialNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtTotalShotCounter.fIn.connect(lambda: self.keyboard('show'))
        self.txtLaserDiodeEnergy.fIn.connect(lambda: self.keyboard('show'))
        self.txtLaserBarType.fIn.connect(lambda: self.keyboard('show'))
        self.txtLaserWavelength.fIn.connect(lambda: self.keyboard('show'))
        self.txtDriverVersion.fIn.connect(lambda: self.keyboard('show'))
        self.txtMainControlVersion.fIn.connect(lambda: self.keyboard('show'))
        self.txtFirmwareVersion.fIn.connect(lambda: self.keyboard('show'))
        self.txtProductionDate.fIn.connect(lambda: self.keyboard('show'))
        self.txtPassUUID.fIn.connect(lambda: self.keyboard('show'))
        self.txtGuiVersion.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditMinute.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditHour.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditYear.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditMonth.fIn.connect(lambda: self.keyboard('show'))
        self.txtEditDay.fIn.connect(lambda: self.keyboard('show'))
        self.txtLockYear.fIn.connect(lambda: self.keyboard('show'))
        self.txtLockMonth.fIn.connect(lambda: self.keyboard('show'))
        self.txtLockDay.fIn.connect(lambda: self.keyboard('show'))
        self.txtOwnerInfo.fIn.connect(lambda: self.keyboard('show'))
        self.txtOwnerInfo.setText(self.configs['OwnerInfo'])
        self.txtOwnerInfo.textChanged.connect(self.setOwnerInfo)
        self.txtDays.textChanged.connect(self.setDateText)
        self.txtDate.textChanged.connect(self.setDaysText)
        reg_ex = QRegExp("[0-9\(\)]*")
        input_validator = QRegExpValidator(reg_ex, self.txtDays)
        self.txtDays.setValidator(input_validator)
        self.txtEditMinute.setValidator(input_validator)
        self.txtEditHour.setValidator(input_validator)
        self.txtLockYear.setValidator(input_validator)        
        self.txtLockMonth.setValidator(input_validator)
        self.txtLockDay.setValidator(input_validator)
        self.txtEditDay.setValidator(input_validator)
        self.txtEditMonth.setValidator(input_validator)
        self.txtEditYear.setValidator(input_validator)        
        self.txtDays.setText('30')
        self.txtSearch.textChanged.connect(self.search)

    def initSensors(self):
        self.waterflowIco = QIcon()
        self.waterflowWarIco = QIcon()
        self.waterLvlIco = QIcon()
        self.waterLvlWarIco = QIcon()
        self.tempIco = QIcon()
        self.tempWarIco = QIcon()
        self.lockIco = QIcon()
        self.unlockIco = QIcon()
        self.lockWarIco = QIcon()
        self.waterflowIco.addPixmap(QPixmap(WATERFLOW))
        self.waterflowWarIco.addPixmap(QPixmap(WATERFLOW_WARNING))
        self.waterLvlIco.addPixmap(QPixmap(WATERLEVEL))
        self.waterLvlWarIco.addPixmap(QPixmap(WATERLEVEL_WARNING))
        self.tempIco.addPixmap(QPixmap(TEMP))
        self.tempWarIco.addPixmap(QPixmap(TEMP_WARNING))
        self.lockIco.addPixmap(QPixmap(LOCK))
        self.unlockIco.addPixmap(QPixmap(UNLOCK))
        self.lockWarIco.addPixmap(QPixmap(LOCK_WARNING))
        self.waterflowTimer = QTimer()
        self.waterLevelTimer = QTimer()
        self.physicalDamageTimer = QTimer()
        self.overHeatTimer = QTimer()
        self.interLockTimer = QTimer()
        self.tempTimer = QTimer()
        self.waterflowTimer.timeout.connect(lambda: self.blinkSensorsIcon('waterflow'))
        self.waterLevelTimer.timeout.connect(lambda: self.blinkSensorsIcon('waterLevel'))
        self.tempTimer.timeout.connect(lambda: self.blinkSensorsIcon('temp'))
        self.physicalDamageTimer.timeout.connect(lambda: self.blinkSensorsIcon('physicalDamage'))
        self.overHeatTimer.timeout.connect(lambda: self.blinkSensorsIcon('overHeat'))
        self.interLockTimer.timeout.connect(lambda: self.blinkSensorsIcon('interLock'))
        self.btnWaterflow.setIcon(self.waterflowIco)
        self.btnTemp.setIcon(self.tempIco)
        self.btnWaterLevel.setIcon(self.waterLvlIco)
        self.btnLock.setIcon(self.lockIco)
        self.btnWaterflow.setIconSize(QSize(80, 80))
        self.btnTemp.setIconSize(QSize(80, 80))
        self.btnWaterLevel.setIconSize(QSize(80, 80))
        self.btnLock.setIconSize(QSize(80, 80))
        self.btnPhysicalDamage.setVisible(False)
        self.btnOverHeat.setVisible(False)
        self.waterflowFlag = False
        self.waterflowWar = False
        self.physicalDamageFlag = False
        self.physicalDamageWar = False
        self.overHeatFlag = False
        self.overHeatWar = False
        self.waterLevelFlag = False
        self.waterLevelWar = False
        self.tempFlag = False
        self.tempWar = False
        self.lockFlag = False
        self.lockWar = False
        self.interLockError = False
        self.waterLevelError = False
        self.waterflowError = False
        self.physicalDamage = False
        self.overHeatError = False
        self.temperature = 0
        self.setTemp(0)
        self.setWaterflowError(True)
        self.setWaterLevelError(True)
        self.setLock(True)

    def changeTheme(self, theme):
        inc = QIcon()
        dec = QIcon()
        if theme in ['C1', 'C2', 'C4']:
            self.sliderEnergy.setStyleSheet(SLIDER_GB)
            self.sliderFrequency.setStyleSheet(SLIDER_GB)
            self.sliderPulseWidth.setStyleSheet(SLIDER_GB)
            inc.addPixmap(QPixmap(INC_BLACK))
            dec.addPixmap(QPixmap(DEC_BLACK))
        else:
            self.sliderEnergy.setStyleSheet(SLIDER_GW)                
            self.sliderFrequency.setStyleSheet(SLIDER_GW)                
            self.sliderPulseWidth.setStyleSheet(SLIDER_GW)
            inc.addPixmap(QPixmap(INC_BLUE))
            dec.addPixmap(QPixmap(DEC_BLUE))

        self.btnDecE.setIcon(dec)
        self.btnDecP.setIcon(dec)
        self.btnDecF.setIcon(dec)
        self.btnIncE.setIcon(inc)
        self.btnIncP.setIcon(inc)
        self.btnIncF.setIcon(inc)
        self.btnDecE.setIconSize(QSize(120, 120))                
        self.btnDecP.setIconSize(QSize(120, 120))                
        self.btnDecF.setIconSize(QSize(120, 120))                
        self.btnIncE.setIconSize(QSize(120, 120))                
        self.btnIncP.setIconSize(QSize(120, 120))                
        self.btnIncF.setIconSize(QSize(120, 120)) 

        if theme == 'T1':
            self.centralWidget().setStyleSheet(THEME1)
        elif theme == 'T2':
            self.centralWidget().setStyleSheet(THEME2)
        elif theme == 'T3':
            self.centralWidget().setStyleSheet(THEME3)
        elif theme == 'T4':
            self.centralWidget().setStyleSheet(THEME4)
        elif theme == 'C1':
            self.centralWidget().setStyleSheet(COLOR1)
        elif theme == 'C2':
            self.centralWidget().setStyleSheet(COLOR2)
        elif theme == 'C3':
            self.centralWidget().setStyleSheet(COLOR3)
        elif theme == 'C4':
            self.centralWidget().setStyleSheet(COLOR4)


        self.configs['theme'] = theme
        saveConfigs(self.configs)
            
    def setOwnerInfo(self, text):
        self.ownerInfoSplash.setText(text)
        self.ownerInfoSplash.adjustSize()
        self.configs['OwnerInfo'] = text
        saveConfigs(self.configs)
        if not text:
            self.ownerInfoSplash.setVisible(False)
        else:
            self.ownerInfoSplash.setVisible(True)
        if text and isFarsi(text):
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_FA)
        else:
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_EN)

    def showSplash(self):
        self.keyboard('hide')
        index = self.stackedWidget.indexOf(self.splashPage)
        self.stackedWidget.setCurrentIndex(index) 
        self.stackedWidgetSettings.setCurrentWidget(self.settingsMenuPage)  

    def receiveDate(self, date):
        self.receivedTime += date

    def adjustTime(self, clock):
        self.receivedTime += clock + (0,)
        try:
            if not self.startupEditTime:
                setSystemTime(self.receivedTime)
                self.startupEditTime = True
                nextDate = jdatetime.datetime.now() + jdatetime.timedelta(120) 
                self.txtLockYear.setText(str(nextDate.year))
                self.txtLockMonth.setText(str(nextDate.month))
                self.txtLockDay.setText(str(nextDate.day)) 
                self.unlockLIC(auto=True)
        except Exception:
            pass

    def powerOff(self):
        enterPage(SHUTDONW_PAGE)
        self.serialC.closePort()
        if platform.system() == 'Windows':
            self.close()
        else:
            os.system('poweroff')
        
    def restart(self):
        enterPage(SHUTDONW_PAGE)
        if platform.system() == 'Windows':
            self.close()
        else:
            os.system('reboot')

    def restartForUpdate(self):
        self.restartCounter -= 1
        self.lblUpdateFirmware.setText(
            f'Your system will restart in {self.restartCounter} seconds...'
        )
        if self.restartCounter == -1:
            self.restartTimer.stop()
            self.serialC.closePort()
            os.system('reboot')

    def updateResult(self, result):
        if result == 'Done':
            self.restartTimer.start(1000)
        else:
            self.setLabel(
                result, 
                self.lblUpdateFirmware,
                self.updateFirmwareLabelTimer
            )

    def updateSystem(self):
        self.lblUpdateFirmware.setText('Please wait...')
        self.updateT.start()

    def setSensors(self, flags):
        self.setLock(flags[0])
        self.setWaterLevelError(flags[1])
        self.setWaterflowError(flags[2])
        self.setOverHeatError(flags[3])
        self.setPhysicalDamage(flags[4])

    def shot(self):
        self.currentCounter += 1
        self.user.incShot(self.bodyPart)
        self.lblCounterValue.setText(f'{self.currentCounter}')
        self.sparkTimer.start(1000/self.frequency + 100)
        self.lblSpark.setVisible(True)
        self.lblLasing.setVisible(True)
        self.shotSound.stop()
        self.shotSound.play()

    def hideSpark(self):
        self.sparkTimer.stop()
        self.lblLasing.setVisible(False)
        self.lblSpark.setVisible(False)

    def monitorSensors(self):
        if not 5 <= self.temperature <= 40:
            if self.ready:
                self.setReady(False)

        elif self.waterflowError:
            if self.ready:
                self.setReady(False)
        
        elif self.waterLevelError:
            if self.ready:
                self.setReady(False)
        
        elif self.interLockError:
            if self.ready:
                self.setReady(False)

        elif self.overHeatError:
            if self.ready:
                self.setReady(False)

        elif self.physicalDamage:
            if self.ready:
                self.setReady(False)

    def time(self, edit=False):
        now = jdatetime.datetime.now()
        hour = "{:02d}".format(now.hour) 
        minute = "{:02d}".format(now.minute)
        second = now.second
        year = str(now.year)
        month = "{:02d}".format(now.month)
        day = "{:02d}".format(now.day)
        self.txtSysClock.setText(now.strftime('%H : %M : %S'))
        self.txtSysDate.setText(now.strftime('%Y / %m / %d'))

        if second == 0 or edit:
            if edit:
                nextDate = jdatetime.datetime.today() + jdatetime.timedelta(120) 
                self.txtLockYear.setText(str(nextDate.year))
                self.txtLockMonth.setText(str(nextDate.month))
                self.txtLockDay.setText(str(nextDate.day))
            self.txtEditYear.setText(year)
            self.txtEditMonth.setText(month)
            self.txtEditDay.setText(day)
            self.txtEditHour.setText(hour)
            self.txtEditMinute.setText(minute)

    def getLocks(self):
        locks = []
        for lock in self.configs['LOCK']:
            if not lock.paid and lock.getStatus() <= 0:
                locks.append(lock)

        locks.sort(key=lambda x: x.date)
        return locks

    def anyLockBefor(self, date):
        for lock in self.configs['LOCK']:
            if (date - lock.date).days <= 0:
                return True
    
        return False

    def addLock(self):
        try:
            year = int(self.txtLockYear.text())
            month = int(self.txtLockMonth.text())
            day = int(self.txtLockDay.text())
        except ValueError:
            self.setLabel(
                'Please fill in the fields.', 
                self.lblLockError, 
                self.lockErrorLabel, 4
            )
            return

        try:
            date = jdatetime.datetime(year, month, day)
        except Exception as e:
            self.setLabel(
                    str(e).capitalize() + '.', 
                    self.lblLockError, self.lockErrorLabel, 4
                )
            return

        numOfLocks = len(self.configs['LOCK'])

        if numOfLocks == 3:
            self.setLabel(
                    TEXT['maxLock'][self.langIndex], 
                    self.lblLockError, 
                    self.lockErrorLabel, 5
                )
            return

        if getDiff(date) <= -1:
            self.setLabel(
                    TEXT['passedDate'][self.langIndex],
                    self.lblLockError, 
                    self.lockErrorLabel, 4
                )
            return

        if self.anyLockBefor(date):
            self.setLabel(
                    TEXT['anyLockBefor'][self.langIndex], 
                    self.lblLockError, 
                    self.lockErrorLabel, 5
                )
            return  

        
        license = self.license[f'LICENSE{numOfLocks + 1}']
        lock = Lock(date, license)
        self.configs['LOCK'].append(lock)
        saveConfigs(self.configs)
        nextDate = date + jdatetime.timedelta(120) 
        self.txtLockYear.setText(str(nextDate.year))
        self.txtLockMonth.setText(str(nextDate.month))
        self.txtLockDay.setText(str(nextDate.day))        
        self.loadLocksTable()

    def loadLocksTable(self):
        self.configs['LOCK'].sort(key=lambda x: x.date)
        locks = self.configs['LOCK']
        self.tableLock.setRowCount(len(locks))
        for i, lock in enumerate(locks):
            date = TableWidgetItem(str(lock.date.date()))
            self.tableLock.setItem(i, 0, date)
            diff = lock.getStatus()
            status = ''
            if diff == 0:
                status = TEXT['today'][self.langIndex]
            elif diff == -1:
                status = TEXT['1dayPassed'][self.langIndex]
            elif diff < -1:
                status = f'{abs(diff)} {TEXT["nDayPassed"][self.langIndex]}'
            elif diff == 1:
                status = TEXT['1dayleft'][self.langIndex]
            else:
                status = f'{diff} {TEXT["nDayLeft"][self.langIndex]}'

            status = TableWidgetItem(status)
            self.tableLock.setItem(i, 1, status)
            paid = TableWidgetItem(TEXT['yes'][self.langIndex] if lock.paid else TEXT['no'][self.langIndex])
            self.tableLock.setItem(i, 2, paid)
            btnDelete = QPushButton(self)
            deleteIcon = QIcon()
            deleteIcon.addPixmap(QPixmap(DELETE_ICON), QIcon.Normal, QIcon.Off)
            btnDelete.setIcon(deleteIcon)
            btnDelete.setIconSize(QSize(60, 60))
            btnDelete.setStyleSheet(ACTION_BTN)
            btnDelete.clicked.connect(self.removeLock)
            btnDelete.pressed.connect(self.playTouchSound)
            self.tableLock.setCellWidget(i, 3, btnDelete)

    def removeLock(self):
        button = qApp.focusWidget()
        index = self.tableLock.indexAt(button.pos())
        if index.isValid():
            year, month, day = self.tableLock.item(index.row(), 0).text().split('-')
            date = jdatetime.datetime(int(year), int(month), int(day))
            for lock in self.configs['LOCK']:
                if (date - lock.date).days == 0:
                    self.configs['LOCK'].remove(lock)
                    saveConfigs(self.configs)

            self.loadLocksTable()

    def unlockUUID(self):
        user_pass = self.txtPassUUID.text().upper()
        hwid = getID()
        hwid += '@mohammaad_haji'
        
        if hashlib.sha256(hwid.encode()).hexdigest()[:10].upper() == user_pass:
            index = self.stackedWidget.indexOf(self.splashPage)
            self.stackedWidget.setCurrentIndex(index)
            self.configs['PASSWORD'] = user_pass
            saveConfigs(self.configs)
            self.keyboard('hide')
        else:
            self.setLabel(
                'Password is not correct.', 
                self.lblPassUUID, 
                self.uuidPassLabelTimer, 4
            )

    def checkUUID(self):
        hwid = getID()
        self.txtUUID.setText(hwid)
        hwid += '@mohammaad_haji'
        if hashlib.sha256(hwid.encode()).hexdigest()[:10].upper() == self.configs['PASSWORD']:
            index = self.stackedWidget.indexOf(self.splashPage)
            self.stackedWidget.setCurrentIndex(index)
        else:
            index = self.stackedWidget.indexOf(self.UUIDPage)
            self.stackedWidget.setCurrentIndex(index)

    def unlockLIC(self, auto=False):
        userPass = self.txtPassword.text().strip()
        locks = self.getLocks()

        if len(locks) > 0:
            index = self.stackedWidget.indexOf(self.loginPage)
            self.stackedWidget.setCurrentIndex(index)
            self.txtID.setText(str(locks[0].license))
            self.centralWidget().setStyleSheet(APP_LOCK_BG)
        else:
            self.checkUUID()
        
        for lock in locks:
            if lock.checkPassword(userPass):
                saveConfigs(self.configs)
                self.keyboard('hide')
                self.movie.start()
                self.txtPassword.clear()
                self.mediaPlayer.setMedia(
                    QMediaContent(
                        QUrl.fromLocalFile(WELLCOME_SOUND)
                    )
                )
                self.mediaPlayer.play()
                return

            else:
                if not auto:
                    self.setLabel(
                            'Password is not correct.', 
                            self.lblPassword, 
                            self.passwordLabelTimer, 4
                            )

    def unlock(self, frameNumber):
        if frameNumber == self.movie.frameCount() - 1: 
            self.movie.stop()
            os.chdir(CURRENT_FILE_DIR)
            self.serialC.closePort()
            QApplication.processEvents()
            if platform.system() == 'Windows':
                os.system('python app.py')
            else:
                os.system('python3 app.py -platform linuxfb')
            exit(0)  

    def loginHw(self):
        password = self.txtHwPass.text()
        self.hwStackedWidget.setCurrentIndex(0)
        txts = chain(
            get_layout_widget(self.prodGridLayout, QLineEdit),
            get_layout_widget(self.laserGridLayout, QLineEdit),
            get_layout_widget(self.driverGridLayout, QLineEdit),
            get_layout_widget(self.embeddGridLayout, QLineEdit)
        )

        if password == '1':
            for txt in txts:
                txt.setReadOnly(False)
                txt.setDisabled(False)

            self.txtRpiVersion.setReadOnly(True)
            self.txtMonitor.setReadOnly(True)
            self.txtOsSpecification.setReadOnly(True)
            self.txtTotalShotCounter.setReadOnly(True)
            self.txtRpiVersion.setDisabled(True)
            self.txtMonitor.setDisabled(True)            
            self.txtOsSpecification.setDisabled(True)
            self.txtTotalShotCounter.setDisabled(True)
            self.keyboard('hide')
            self.readHwInfo()
            self.loadLocksTable()
            self.hwbtnsFrame.show()
            self.txtRpiVersion.setVisible(True)
            self.lblRpiVersion.setVisible(True)            
            self.txtHwPass.clear()
            self.stackedWidgetSettings.setCurrentWidget(self.hWPage)
            self.enterSettingPage(REPORT)

        elif password == '0':
            self.enterSettingPage(REPORT)
            for txt in txts:
                txt.setReadOnly(True)
                txt.setDisabled(True)

            self.keyboard('hide')
            self.readHwInfo()
            self.hwbtnsFrame.hide()
            self.txtRpiVersion.setVisible(False)
            self.lblRpiVersion.setVisible(False)
            self.txtHwPass.clear()
            self.stackedWidgetSettings.setCurrentWidget(self.hWPage)
            
        else:
            self.txtHwPass.setStyleSheet(TXT_HW_WRONG_PASS)
            self.hwWrongPassTimer.start(4000)

    def hwWrongPass(self):
        self.hwWrongPassTimer.stop()
        self.txtHwPass.setStyleSheet(TXT_HW_PASS)

    def readHwInfo(self):
        self.txtOsSpecification.setText(OS_SPEC)
        self.txtRpiVersion.setText(RPI_MODEL)
        self.txtMonitor.setText(monitorInfo())
        self.txtSerialNumber.setText(self.configs['SerialNumber'])                
        self.txtTotalShotCounter.setText(str(self.configs['TotalShotCounter']))              
        self.txtLaserDiodeEnergy.setText(self.configs['LaserDiodeEnergy'])                
        self.txtLaserBarType.setText(self.configs['LaserBarType'])                
        self.txtLaserWavelength.setText(self.configs['LaserWavelength'])                
        self.txtDriverVersion.setText(self.configs['DriverVersion'])                
        self.txtMainControlVersion.setText(self.configs['MainControlVersion'])                
        self.txtFirmwareVersion.setText(self.configs['FirmwareVersion'])
        self.txtProductionDate.setText(self.configs['ProductionDate']) 
        self.txtGuiVersion.setText(self.configs['GuiVersion'])

    def saveHwSettings(self):
        self.configs['SerialNumber'] = self.txtSerialNumber.text()            
        self.configs['TotalShotCounter'] = int(self.txtTotalShotCounter.text())
        self.configs['LaserDiodeEnergy'] = self.txtLaserDiodeEnergy.text()            
        self.configs['LaserBarType'] = self.txtLaserBarType.text()            
        self.configs['LaserWavelength'] = self.txtLaserWavelength.text()            
        self.configs['DriverVersion'] = self.txtDriverVersion.text()            
        self.configs['MainControlVersion'] = self.txtMainControlVersion.text()            
        self.configs['FirmwareVersion'] = self.txtFirmwareVersion.text()
        self.configs['ProductionDate'] = self.txtProductionDate.text()
        self.configs['GuiVersion'] = self.txtGuiVersion.text()  
        saveConfigs(self.configs)
        lockIndex = self.hwStackedWidget.indexOf(self.lockSettingsPage)
        if self.hwStackedWidget.currentIndex() == lockIndex:
            try:
                year = int(self.txtEditYear.text())
                month = int(self.txtEditMonth.text())
                day = int(self.txtEditDay.text())
                gregorian = jdatetime.datetime(year, month, day).togregorian()
                year = gregorian.year
                month = gregorian.month
                day = gregorian.day
                hour = int(self.txtEditHour.text())
                minute = int(self.txtEditMinute.text())
                second = jdatetime.datetime.now().second
                milisecond = 0
                time = (year, month, day, hour, minute, second, milisecond)
                setSystemTime(time)
                nextDate = jdatetime.datetime.now() + jdatetime.timedelta(120) 
                self.txtLockYear.setText(str(nextDate.year))
                self.txtLockMonth.setText(str(nextDate.month))
                self.txtLockDay.setText(str(nextDate.day)) 
            except Exception:
                self.setLabel(
                        TEXT['systemTimeStatus'][self.langIndex], 
                        self.lblSystemTimeStatus, 
                        self.sysTimeStatusLabelTimer, 4
                    )

            lockPage(WRITE)
        
        else:
            self.enterSettingPage(WRITE)

        self.setLabel(
                TEXT['saveHw'][self.langIndex], 
                self.lblSaveHw, 
                self.hwUpdatedLabelTimer, 2
            )
        
        self.loadLocksTable()

    def enterSettingPage(self, cmdType):
        fieldValues = {
            'serial': self.txtSerialNumber.text(),
            'totalCounter': self.txtTotalShotCounter.text(), 
            'pDate': self.txtProductionDate.text(),
            'LaserEnergy': self.txtLaserDiodeEnergy.text(), 
            'waveLength': self.txtLaserWavelength.text(), 
            'LaserBarType': self.txtLaserBarType.text(),
            'DriverVersion': self.txtDriverVersion.text(), 
            'controlVersion': self.txtMainControlVersion.text(), 
            'firmware': self.txtFirmwareVersion.text(),
            'monitor': self.txtMonitor.text(),
            'os': self.txtOsSpecification.text(),
            'gui': self.txtGuiVersion.text(),
            'rpi': self.txtRpiVersion.text()
        }
        settingsPage(fieldValues, cmdType)

    def resetTotalShot(self):
        self.txtTotalShotCounter.setText('0')
        self.configs['TotalShotCounter'] = 0
        saveConfigs(self.configs)

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
        if '.gitignore' in tutoriasl:
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
                    self.setLabel(
                            TEXT['passedDate'][self.langIndex], 
                            self.lblErrNextSession, 
                            self.nextSessionLabelTimer
                        )
                    return
                self.userNextSession.setNextSession(date)
                if self.userNextSession.currentSession == 'started':
                    self.endSession()
                else:
                    self.info(self.userNextSession.phoneNumber)
            except ValueError as e:
                self.setLabel(
                        str(e).capitalize() + '.', 
                        self.lblErrNextSession,
                        self.nextSessionLabelTimer
                    )

        except Exception:
            self.setLabel(
                    TEXT['invalidDateF'][self.langIndex], 
                    self.lblErrNextSession, 
                    self.nextSessionLabelTimer
                )

    def cancelNextSession(self):
        if self.userNextSession.currentSession == 'started':
            self.userNextSession.setNextSession(None)
            self.changeAnimation('vertical')
            self.endSession()
        else:
            self.info(self.userNextSession.phoneNumber)

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
        self.laserMainPage.setVisible(False)
        if page == 'lazer':
            self.userNextSession = self.user
            self.setReady(False)
        elif page == 'edit':
            self.userNextSession = self.userInfo
            
        self.changeAnimation('vertical')
        self.stackedWidget.setCurrentWidget(self.nextSessionPage)

    def setReady(self, ready):
        if ready:
            if not 5 <= self.temperature <= 40:
                self.setLabel(
                    TEXT['tempError'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )

            elif self.waterflowError:
                self.setLabel(
                    TEXT['waterflowError'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )
                
            elif self.waterLevelError:
                self.setLabel(
                    TEXT['waterLevelError'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )
            
            elif self.interLockError:
                self.setLabel(
                    TEXT['interLockError'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )

            elif self.overHeatError:
                self.setLabel(
                    TEXT['overHeatError'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )

            elif self.physicalDamage:
                self.setLabel(
                    TEXT['physicalDamage'][self.langIndex],
                    self.lblReadyError,
                    self.readyErrorTimer, 4
                )
            else:
                self.ready = True
                laserPage({'ready-standby': 'Ready'})
                fields = {
                    'cooling': self.cooling , 'energy': self.energy,
                    'pulseWidth': self.pulseWidth,'frequency': self.frequency, 
                    'couter': self.currentCounter
                } 
                
                laserPage(fields)
                self.btnStandby.setStyleSheet(READY_NOT_SELECTED)
                self.btnReady.setStyleSheet(READY_SELECTED)
                self.epfSkinGradeLayout.setEnabled(False)
                if self.configs['theme'] in ['C1', 'C2', 'C4']:
                    self.sliderEnergy.setStyleSheet(SLIDER_DISABLED_GB)
                    self.sliderFrequency.setStyleSheet(SLIDER_DISABLED_GB)
                    self.sliderPulseWidth.setStyleSheet(SLIDER_DISABLED_GB)
                else:
                    self.sliderEnergy.setStyleSheet(SLIDER_DISABLED_GW)
                    self.sliderFrequency.setStyleSheet(SLIDER_DISABLED_GW)
                    self.sliderPulseWidth.setStyleSheet(SLIDER_DISABLED_GW)

        else:
            self.ready = False
            laserPage({'ready-standby': 'StandBy'})
            self.btnStandby.setStyleSheet(READY_SELECTED)
            self.btnReady.setStyleSheet(READY_NOT_SELECTED)
            self.epfSkinGradeLayout.setEnabled(True)
            if self.configs['theme'] in ['C1', 'C2', 'C4']:
                self.sliderEnergy.setStyleSheet(SLIDER_GB)
                self.sliderFrequency.setStyleSheet(SLIDER_GB)
                self.sliderPulseWidth.setStyleSheet(SLIDER_GB)
            else:
                self.sliderEnergy.setStyleSheet(SLIDER_GW)                
                self.sliderFrequency.setStyleSheet(SLIDER_GW)                
                self.sliderPulseWidth.setStyleSheet(SLIDER_GW)                    

    def setCooling(self, operation):
        buttons = layout_widgets(self.coolingLayout)
        icon = QIcon()
        if operation == 'inc':
            if self.cooling < 5:
                self.cooling += 1
                laserPage({'cooling': self.cooling})
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
                laserPage({'cooling': self.cooling})

    def sliderChgColor(self, i):
        if i == 'pressed':
            if self.configs['theme'] in ['C1', 'C2', 'C4']:
                self.sliderEnergy.setStyleSheet(SLIDER_SAVED_GB)
                self.sliderFrequency.setStyleSheet(SLIDER_SAVED_GB)
                self.sliderPulseWidth.setStyleSheet(SLIDER_SAVED_GB)         
            else:
                self.sliderEnergy.setStyleSheet(SLIDER_SAVED_GW)                
                self.sliderFrequency.setStyleSheet(SLIDER_SAVED_GW)                
                self.sliderPulseWidth.setStyleSheet(SLIDER_SAVED_GW) 

        else:
            if self.configs['theme'] in ['C1', 'C2', 'C4']:
                self.sliderEnergy.setStyleSheet(SLIDER_GB)
                self.sliderFrequency.setStyleSheet(SLIDER_GB)
                self.sliderPulseWidth.setStyleSheet(SLIDER_GB)
            else:
                self.sliderEnergy.setStyleSheet(SLIDER_GW)                
                self.sliderFrequency.setStyleSheet(SLIDER_GW)                
                self.sliderPulseWidth.setStyleSheet(SLIDER_GW)               

    def setEnergy(self, operation):
        e = self.energy
        e = e + 1 if operation == 'inc' else e - 1
        if MIN_ENRGEY <= e <= MAX_ENERGY:
            self.energy = e
            self.sliderEnergy.setValue(e)
            self.lblEnergyValue.setText(str(e))

    def sldrSetEnergy(self, value):
        self.energy = value
        self.lblEnergyValue.setText(str(value))

    def setPulseWidth(self, operation):
        pl = self.pulseWidth
        pl = pl + 1 if operation == 'inc' else pl - 1
        if MIN_PULSE_WIDTH <= pl <= MAX_PULSE_WIDTH:
            self.pulseWidth = pl
            self.sliderPulseWidth.setValue(pl)
            self.lblPulseWidthValue.setText(str(pl))
            maxF_pl = 1000 / (2 * self.pulseWidth)
            maxF_pl_con = MAX_FREQUENCY >= maxF_pl
            if maxF_pl_con and self.frequency >= maxF_pl:
                self.frequency = math.floor(maxF_pl)
                self.sliderFrequency.setValue(self.frequency)
                self.lblFrequencyValue.setText(str(self.frequency))

    def sldrSetPulseWidth(self, value):
        self.pulseWidth = value
        self.lblPulseWidthValue.setText(str(value))
        maxF_pl = 1000 / (2 * self.pulseWidth)
        maxF_pl_con = MAX_FREQUENCY >= maxF_pl
        if maxF_pl_con and self.frequency >= maxF_pl:
            self.frequency = math.floor(maxF_pl)
            self.sliderFrequency.setValue(self.frequency)
            self.lblFrequencyValue.setText(str(self.frequency))

    def setFrequency(self, operation):
        freq = self.frequency
        freq = freq + 1 if operation == 'inc' else freq - 1
        if MIN_FREQUENCY <= freq <= MAX_FREQUENCY:
            self.frequency = freq
            self.sliderFrequency.setValue(freq)
            self.lblFrequencyValue.setText(str(freq))
            maxPl_f = 1000 / (2 * self.frequency)
            maxPl_f_con = MAX_PULSE_WIDTH >= maxPl_f
            if maxPl_f_con and self.pulseWidth >= maxPl_f:
                self.pulseWidth = math.floor(maxPl_f)
                self.sliderPulseWidth.setValue(self.pulseWidth)
                self.lblPulseWidthValue.setText(str(self.pulseWidth))
 
    def sldrSetFrequency(self, value):
        self.frequency = value
        self.lblFrequencyValue.setText(str(value))
        maxPl_f = 1000 / (2 * self.frequency)
        maxPl_f_con = MAX_PULSE_WIDTH >= maxPl_f
        if maxPl_f_con and self.pulseWidth >= maxPl_f:
            self.pulseWidth = math.floor(maxPl_f)
            self.sliderPulseWidth.setValue(self.pulseWidth)
            self.lblPulseWidthValue.setText(str(self.pulseWidth))
        
    def saveCase(self):
        case = openCase(self.case)
        case.save(
            self.sex, self.bodyPart, (self.energy, self.pulseWidth, self.frequency)
        )

    def bodyPartsSignals(self):
        buttons = chain(
            get_layout_widget(self.fBodyPartsLayout, QPushButton),
            get_layout_widget(self.mBodyPartsLayout, QPushButton)
        )

        for btn in buttons:
            btn.clicked.connect(lambda: self.stackedWidgetLaser.setCurrentWidget(self.laserPage))
            btn.clicked.connect(lambda: self.btnBackLaser.setVisible(True))
            sex = btn.objectName().split('btn')[1][0].lower()
            bodyPart = btn.objectName().split('btn')[1][1:].lower()
            btn.clicked.connect(self.setBodyPart(sex, bodyPart))
            btn.clicked.connect(self.loadCase)
            btn.clicked.connect(self.sendLaserFields)
        
    def sendLaserFields(self):
        fields = {
            'cooling': self.cooling , 'energy': self.energy,
            'pulseWidth': self.pulseWidth,'frequency': self.frequency, 
            'couter': self.currentCounter, 
        }
        laserPage(fields)
    
    def setBodyPart(self, sex, bodyPart):
        def wrapper():
            self.bodyPart = bodyPart
            icon = QIcon()
            key = sex + ' ' + bodyPart
            self.lblSelectedBodyPart.setText(TEXT[bodyPart][self.langIndex])
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
        buttons = get_layout_widget(self.casesLayout, QPushButton)

        for btn in buttons:
            caseName = btn.objectName().split('Case')[1]
            btn.clicked.connect(self.setCase(caseName))
            btn.clicked.connect(self.loadCase)

    def setCase(self, case):
        def wrapper():
            self.case = case
            buttons = get_layout_widget(self.casesLayout, QPushButton)
            for btn in buttons:
                btn.setStyleSheet(NOT_SELECTED_CASE)
                caseName = btn.objectName().split('Case')[1]
                if caseName == case:
                    btn.setStyleSheet(SELECTED_CASE)

        return wrapper

    def loadCase(self):
        case = openCase(self.case)
        energy, pl, freq = case.getValue(self.sex, self.bodyPart)
        self.energy = energy
        self.pulseWidth = pl
        self.frequency = freq
        self.sliderEnergy.setValue(energy)
        self.sliderPulseWidth.setValue(pl)
        self.sliderFrequency.setValue(freq)
        self.lblEnergyValue.setText(str(energy))
        self.lblPulseWidthValue.setText(str(pl))
        self.lblFrequencyValue.setText(str(freq))

    def backSettings(self):
        self.hwPass('hide') 
        index = self.stackedWidgetSettings.indexOf(self.settingsMenuPage)
        if self.stackedWidgetSettings.currentIndex() == index:
            self.stackedWidget.setCurrentWidget(self.mainPage)
        else:
            self.stackedWidgetSettings.setCurrentWidget(self.settingsMenuPage)
            self.hWPage.setVisible(False)
            enterPage(MAIN_PAGE) 

    def blinkSensorsIcon(self, sensor):
        if sensor == 'waterflow':
            self.waterflowFlag = not self.waterflowFlag
            if self.waterflowFlag:
                self.btnWaterflow.setIcon(self.waterflowWarIco)
            else:
                self.btnWaterflow.setIcon(self.waterflowIco)

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

        elif sensor == 'interLock':
            self.lockFlag = not self.lockFlag
            if self.lockFlag:
                self.btnLock.setIcon(self.lockWarIco)
            else:
                self.btnLock.setIcon(self.lockIco)

        elif sensor == 'overHeat':
            self.overHeatFlag = not self.overHeatFlag
            if self.overHeatFlag:
                self.btnOverHeat.setVisible(True)
            else:
                self.btnOverHeat.setVisible(False)

        elif sensor == 'physicalDamage':
            self.physicalDamageFlag = not self.physicalDamageFlag
            if self.physicalDamageFlag:
                self.btnPhysicalDamage.setVisible(True)
            else:
                self.btnPhysicalDamage.setVisible(False)

    def stopSensorWarning(self, sensor):
        if sensor == 'waterflow':
            self.waterflowTimer.stop()
            self.waterflowWar = False
            self.btnWaterflow.setIcon(self.waterflowIco)
            
        elif sensor == 'waterLevel':
            self.waterLevelTimer.stop()
            self.waterLevelWar = False
            self.btnWaterLevel.setIcon(self.waterLvlIco)

        elif sensor == 'temp':
            self.tempTimer.stop()
            self.tempWar = False
            self.btnTemp.setIcon(self.tempIco)

        elif sensor == 'interLock':
            self.interLockTimer.stop()
            self.lockWar = False
            self.btnLock.setIcon(self.unlockIco)

        elif sensor == 'overHeat':
            self.overHeatTimer.stop()
            self.overHeatWar = False
            self.btnOverHeat.setVisible(False)

        elif sensor == 'physicalDamage':
            self.physicalDamageTimer.stop()
            self.physicalDamageWar = False
            self.btnPhysicalDamage.setVisible(False)

    def startSensorWarning(self, sensor):
        if sensor == 'waterflow':
            if not self.waterflowWar:
                self.waterflowTimer.start(500)
                self.waterflowWar = True

        elif sensor == 'waterLevel':
            if not self.waterLevelWar:
                self.waterLevelTimer.start(500)
                self.waterLevelWar = True

        elif sensor == 'temp':
            if not self.tempWar:
                self.tempTimer.start(500)
                self.tempWar = True
                
        elif sensor == 'interLock':
            if not self.lockWar:
                self.interLockTimer.start(500)
                self.lockWar = True
        
        elif sensor == 'overHeat':
            if not self.overHeatWar:
                self.overHeatTimer.start(500)
                self.overHeatWar = True

        elif sensor == 'physicalDamage':
            if not self.physicalDamageWar:
                self.physicalDamageTimer.start(500)
                self.physicalDamageWar = True

    def setLock(self, lock):
        self.interLockError = lock
        if lock:
            self.startSensorWarning('interLock')
        else:
            self.stopSensorWarning('interLock')

    def setTemp(self, value):
        self.txtTemp.setText(str(value) + ' °C')
        self.temperature = value
        if not (5 <= value <= 40):
            self.startSensorWarning('temp')
        else:
            self.stopSensorWarning('temp')

    def setWaterflowError(self, status):
        self.waterflowError = status
        if self.waterflowError:
            self.startSensorWarning('waterflow')
        else:
            self.stopSensorWarning('waterflow')

    def setWaterLevelError(self, status):
        self.waterLevelError = status
        if self.waterLevelError:
            self.startSensorWarning('waterLevel')
        else:
            self.stopSensorWarning('waterLevel')

    def setOverHeatError(self, status):
        self.overHeatError = status
        if self.overHeatError:
            self.startSensorWarning('overHeat')
        else:
            self.stopSensorWarning('overHeat')

    def setPhysicalDamage(self, status):
        self.physicalDamage = status
        if self.physicalDamage:
            self.startSensorWarning('physicalDamage')
        else:
            self.stopSensorWarning('physicalDamage')

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

        self.powerOption('hide')
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
        self.btnReturn.clicked.connect(self.type(lambda: 'enter'))
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
            height = 350
            newHeight = 0
        else:
            height = 0
            newHeight = 350

        self.animation = QPropertyAnimation(self.keyboardFrame, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(height)
        self.animation.setEndValue(newHeight)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def hwPass(self, i):
        height = self.hwPassFrame.height()
        if i == 'hide' and height == 0:
            return

        if i == 'show' and height > 0:
            return

        if i == 'hide':
            height = 90
            newHeight = 0
        else:
            height = 0
            newHeight = 90

        self.animation2 = QPropertyAnimation(self.hwPassFrame, b"maximumHeight")
        self.animation2.setDuration(500)
        self.animation2.setStartValue(height)
        self.animation2.setEndValue(newHeight)
        self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation2.start()

    def powerOption(self, i):
        height = self.powerFrame.height()
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

        self.animation3 = QPropertyAnimation(self.powerFrame, b"maximumHeight")
        self.animation3.setDuration(500)
        self.animation3.setStartValue(height)
        self.animation3.setEndValue(newHeight)
        self.animation3.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation3.start()

    def btnHwsettingClicked(self):
        self.hwPass('show')
        self.keyboard('show')
        self.txtHwPass.setFocus()

    def sort(self):
        self.sortBySession = not self.sortBySession

        if self.sortBySession:
            self.usersTable.sortItems(2, Qt.DescendingOrder)
        else:
            self.usersTable.sortItems(2, Qt.AscendingOrder)

    def addUsersTable(self):
        for i in range(5):
            if len(self.usersList) == 0:
                self.loadUsersFinished()
                return
            self.insertToTabel(self.usersList[0])
            self.usersList.pop(0)

    def loadUsersFinished(self):
        self.loadUsersTimer.stop()

    def insertToTabel(self, user):
        rowPosition = self.usersTable.rowCount()
        self.usersTable.insertRow(rowPosition)
        action = Action(self.usersTable, user.phoneNumber)
        action.btnInfo.pressed.connect(self.playTouchSound)
        action.info.connect(self.info)
        action.chbDel.toggled.connect(self.playTouchSound)
        action.delete.connect(self.selecetCheckedUsers)
        # action.delete.connect(self.removeUser)
        self.usersTable.setCellWidget(rowPosition, 3, action)
        number = QTableWidgetItem(user.phoneNumber)
        name = QTableWidgetItem(user.name)
        sessions = QTableWidgetItem(str(user.sessionNumber - 1))
        number.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        name.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        sessions.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.usersTable.setItem(rowPosition, 0, number)
        self.usersTable.setItem(rowPosition, 1, name)
        self.usersTable.setItem(rowPosition, 2, sessions)
        self.lblTotalUsersCount.setText(f'{self.usersTable.rowCount()}')


    def selecetCheckedUsers(self, number):
        if number in self.selectedUsers:
            self.selectedUsers.remove(number)
        else:
            self.selectedUsers.append(number)
        
        self.lblSelectedUsersValue.setText(f'{len(self.selectedUsers)}')

    def removeSelectedUsers(self):
        for num in self.selectedUsers:
            self.removeUser(num)
            del self.usersData[num]
        
        self.lblSelectedUsersValue.setText('0')
        self.selectedUsers.clear()

    def removeUser(self, number=None):
        if number:
            for row in range(self.usersTable.rowCount()):
                if self.usersTable.model().index(row, 0).data() == number:
                    self.usersTable.removeRow(row)
                    self.lblTotalUsersCount.setText(f'{self.usersTable.rowCount()}')
                    return
                    
        else:
            button = self.sender()
            if button:
                row = self.usersTable.indexAt(button.pos()).row()
                number = self.usersTable.item(row, 0).text()
                del self.usersData[number]
                self.usersTable.removeRow(row)
                totalUsers = len(self.usersData)
                self.lblTotalUsersCount.setText(f'{totalUsers}')

    def info(self, num):
        self.stackedWidget.setCurrentWidget(self.editUserPage)
        self.userInfo = self.usersData[num]
        nextSessionDate = self.userInfo.nextSession
        if not nextSessionDate:
            self.txtNextSession.setText(TEXT['notSet'][self.langIndex])
        else:
            diff = getDiff(nextSessionDate)

            if diff == 0:
                self.txtNextSession.setText(TEXT['today'][self.langIndex])
            elif diff == -1:
                self.txtNextSession.setText(TEXT['1dayPassed'][self.langIndex])
            elif diff < -1:
                self.txtNextSession.setText(f'{abs(diff)} {TEXT["nDayPassed"][self.langIndex]}')
            elif diff == 1:
                self.txtNextSession.setText(TEXT['1dayleft'][self.langIndex])
            else:
                self.txtNextSession.setText(f'{diff} {TEXT["nDayLeft"][self.langIndex]}')

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
        text = TEXT['total'][self.langIndex]
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
        users = self.usersData.values()
        rowTomorrow = 0
        rowAfterTomorrow = 0
        for user in users:
            if user.sessionNumber == 1:
                nextSession = user.nextSession
                num = TableWidgetItem(user.phoneNumber)
                name = TableWidgetItem(user.name)
                text = TEXT['firstTime'][self.langIndex] 
                lastSession = TableWidgetItem(text)
                sn = TableWidgetItem(str(user.sessionNumber))
                if nextSession and getDiff(nextSession) == 1:
                    self.tableTomorrow.setRowCount(rowTomorrow +1)
                    self.tableTomorrow.setItem(rowTomorrow, 0, num)
                    self.tableTomorrow.setItem(rowTomorrow, 1, name)
                    self.tableTomorrow.setItem(rowTomorrow, 2, sn)
                    # self.tableTomorrow.setItem(rowTomorrow, 2, lastSession)
                    rowTomorrow += 1
                elif nextSession and getDiff(nextSession) == 2:
                    self.tableAfterTomorrow.setRowCount(rowAfterTomorrow +1)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 0, num)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 1, name)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 2, sn)
                    # self.tableAfterTomorrow.setItem(rowAfterTomorrow, 2, lastSession)
                    rowAfterTomorrow += 1

            else:
                nextSession = user.nextSession
                lastSession = user.sessions[user.sessionNumber -1]['date']
                lastSession = TableWidgetItem(str(lastSession.date()))
                num = TableWidgetItem(user.phoneNumber)
                name = TableWidgetItem(user.name)
                sn = TableWidgetItem(str(user.sessionNumber))
                if nextSession and getDiff(nextSession) == 1:
                    self.tableTomorrow.setRowCount(rowTomorrow +1)
                    self.tableTomorrow.setItem(rowTomorrow, 0, num)
                    self.tableTomorrow.setItem(rowTomorrow, 1, name)
                    self.tableTomorrow.setItem(rowTomorrow, 2, sn)
                    # self.tableTomorrow.setItem(rowTomorrow, 2, lastSession)
                    rowTomorrow += 1
                elif nextSession and getDiff(nextSession) == 2:
                    self.tableAfterTomorrow.setRowCount(rowAfterTomorrow +1)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 0, num)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 1, name)
                    self.tableAfterTomorrow.setItem(rowAfterTomorrow, 2, sn)
                    # self.tableAfterTomorrow.setItem(rowAfterTomorrow, 2, lastSession)
                    rowAfterTomorrow += 1

        self.lblTomorrowCount.setText(f'{rowTomorrow}')
        self.lblAfterTomorrowCount.setText(f'{rowAfterTomorrow}')
        self.tableTomorrow.setRowCount(rowTomorrow)
        self.tableAfterTomorrow.setRowCount(rowAfterTomorrow)

    def saveUserInfo(self):
        numberEdit = self.txtEditNumber.text()
        nameEdit = self.txtEditName.text()
        noteEdit = self.textEditNote.toPlainText()
        numberEdited = False

        if not numberEdit:
            self.setLabel(
                    TEXT['emptyNumber'][self.langIndex], 
                    self.lblEditUser,
                    self.editLabelTimer
                )
            self.txtEditNumber.setFocus()
            return

        if numberEdit != self.userInfo.phoneNumber:
            if numberEdit in self.usersData:
                self.setLabel(
                    TEXT['alreadyExists'][self.langIndex], 
                    self.lblEditUser,
                    self.editLabelTimer
                )
                self.txtEditNumber.setFocus()
                return

            oldNumber = self.userInfo.phoneNumber
            self.userInfo.setPhoneNumber(numberEdit)
            newNumber = self.userInfo.phoneNumber
            self.usersData[newNumber] = self.usersData.pop(oldNumber)
            numberEdited = True
            self.removeUser(oldNumber)


        if not nameEdit:
            nameEdit = 'Nobody'

        self.userInfo.setName(nameEdit)
        self.userInfo.setNote(noteEdit)

        if not numberEdited:
            self.removeUser(self.userInfo.phoneNumber)

        self.insertToTabel(self.userInfo)

        self.setLabel(
                TEXT['userUpdated'][self.langIndex],
                self.lblEditUser,
                self.editLabelTimer, 3
            )

    def deleteUser(self):
        number = self.userInfo.phoneNumber        
        del self.usersData[number]
        self.removeUser(number)
        saveUser(self.usersData)
        self.changeAnimation('horizontal')
        self.stackedWidget.setCurrentWidget(self.userManagementPage)

    def submit(self):
        number = self.txtNumberSubmit.text()
        name = self.txtNameSubmit.text()
        name = name if name else 'User ' + str(len(self.usersData) + 1)

        if not number:
            self.setLabel(
                    TEXT['emptyNumber'][self.langIndex], 
                    self.lblSubmit, 
                    self.submitLabelTimer
                )
            self.txtNumberSubmit.setFocus()
            return

        if number in self.usersData:
            self.setLabel(
                    TEXT['alreadyExistsSub'][self.langIndex], 
                    self.lblSubmit, 
                    self.submitLabelTimer
                )
            self.txtNumberSubmit.setFocus()
            return

        self.usersData[number] = User(number, name)
        self.insertToTabel(self.usersData[number])
        self.txtNumber.setText(number)
        self.txtNumberSubmit.clear()
        self.txtNameSubmit.clear()
        self.newUserPage.setVisible(False)
        self.startSession()

    def startSession(self):
        numberEntered = self.txtNumber.text()

        if (not self.user) or (self.user.currentSession == 'finished'):

            if not numberEntered:
                self.setLabel(
                        TEXT['emptyNumber'][self.langIndex], 
                        self.lblLogin, 
                        self.loginLabelTimer
                    )
                self.txtNumber.setFocus()
                self.txtNumber.selectAll()
                return


            if not numberEntered in  self.usersData:
                self.txtNumberSubmit.setText(numberEntered)
                self.txtNameSubmit.setFocus()
                self.changeAnimation('vertical')
                self.stackedWidget.setCurrentWidget(self.newUserPage)
                return

            self.user = self.usersData[numberEntered]
            self.user.setCurrentSession('started')
            self.txtCurrentUser.setText(self.user.name)
            self.txtCurrentSnumber.setText(str(self.user.sessionNumber))
            self.keyboard('hide')
            self.changeAnimation('horizontal')
            self.stackedWidget.setCurrentWidget(self.laserMainPage)
            self.mainPage.setVisible(False)
            enterPage(BODY_PART_PAGE)

        elif self.user and self.user.currentSession == 'started':
            if not self.user.phoneNumber in self.usersData:
                    self.setLabel(
                            TEXT['userBeenDeleted'][self.langIndex], 
                            self.lblLogin, 
                            self.loginLabelTimer
                        )
                    self.txtNumber.setFocus()
                    self.txtNumber.selectAll()
                    self.user = None
                    return
            elif numberEntered != self.user.phoneNumber:
                text = f'{TEXT["sssionNotOver"][self.langIndex]} ({self.user.phoneNumber})'

                self.setLabel(
                        text, 
                        self.lblLogin, 
                        self.loginLabelTimer
                    )
                self.txtNumber.setFocus()
                self.txtNumber.selectAll()
                return
            else:
                if not self.user.phoneNumber in self.usersData:
                    self.setLabel(
                            TEXT['userBeenDeleted'][self.langIndex], 
                            self.lblLogin, 
                            self.loginLabelTimer
                        )
                    self.txtNumber.setFocus()
                    self.txtNumber.selectAll()
                    self.user = None
                    return
                    
                self.user.setCurrentSession('started')
                self.txtCurrentUser.setText(self.user.name)
                self.txtCurrentSnumber.setText(str(self.user.sessionNumber))
                self.keyboard('hide')
                self.changeAnimation('horizontal')
                self.stackedWidget.setCurrentWidget(self.laserMainPage)
                self.mainPage.setVisible(False)
                enterPage(BODY_PART_PAGE)

    def endSession(self):
        self.user.setCurrentSession('finished')
        self.user.addSession()
        self.removeUser(self.user.phoneNumber)
        self.insertToTabel(self.user)
        self.user = None
        self.configs['TotalShotCounter'] += self.currentCounter
        saveConfigs(self.configs)
        saveUser(self.usersData)
        self.lblCounterValue.setText('0')
        self.currentCounter = 0
        self.stackedWidget.setCurrentWidget(self.mainPage)
        self.stackedWidgetLaser.setCurrentIndex(0)
        self.btnBackLaser.setVisible(False)

    def setLabel(self, text, label, timer, sec=5):
        label.setText(text)
        timer.start(sec * 1000)

    def clearLabel(self, label, timer):
        label.clear()
        timer.stop()

    def changeLang(self, lang):
        global app
        if lang == 'fa':
            app.setStyleSheet('*{font-family:"A Iranian Sans"}')
            self.lblEn.setStyleSheet("font-family:'Arial'")
            self.userInfoFrame.setLayoutDirection(Qt.RightToLeft)
            self.nextSessionFrame.setLayoutDirection(Qt.RightToLeft)
            self.hwFrame.setLayoutDirection(Qt.RightToLeft)
            self.currentUserFrame.setLayoutDirection(Qt.RightToLeft)
            icon = QPixmap(SELECTED_LANG_ICON)
            self.lblFaSelected.setPixmap(icon.scaled(70, 70))
            self.lblEnSelected.clear()
            self.configs['LANGUAGE'] = 'fa'
            self.langIndex = 1
        else:
            app.setStyleSheet('*{font-family:"Arial"}')
            self.lblFa.setStyleSheet("font-family:'A Iranian Sans'")
            self.userInfoFrame.setLayoutDirection(Qt.LeftToRight)
            self.nextSessionFrame.setLayoutDirection(Qt.LeftToRight)
            self.hwFrame.setLayoutDirection(Qt.LeftToRight)
            self.currentUserFrame.setLayoutDirection(Qt.LeftToRight)
            icon = QPixmap(SELECTED_LANG_ICON)
            self.lblEnSelected.setPixmap(icon.scaled(70, 70))
            self.lblFaSelected.clear()
            self.configs['LANGUAGE'] = 'en'
            self.langIndex = 0

        saveConfigs(self.configs)
        self.ownerInfoSplash.adjustSize()
        txt = self.ownerInfoSplash.text()
        if txt and isFarsi(txt):
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_FA)
        else:
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_EN)

        for lbl in self.findChildren(QLabel):
            if lbl.objectName() in TEXT.keys():
                lbl.setText(TEXT[lbl.objectName()][self.langIndex])

        for btn in self.findChildren(QPushButton):
            if btn.objectName() in TEXT.keys():
                btn.setText(TEXT[btn.objectName()][self.langIndex])

        for txt in self.findChildren(QLineEdit):
            if txt.objectName() in TEXT.keys():
                txt.setPlaceholderText(TEXT[txt.objectName()][self.langIndex])

        for i in range(3):
            self.tableTomorrow.horizontalHeaderItem(i).setText(
                TEXT[f'tbFsessions{i}'][self.langIndex]
            )
            self.tableAfterTomorrow.horizontalHeaderItem(i).setText(
                TEXT[f'tbFsessions{i}'][self.langIndex]
            )

        for i in range(4):
            self.usersTable.horizontalHeaderItem(i).setText(
                TEXT[f'usersTable{i}'][self.langIndex]
            )
            self.tableLock.horizontalHeaderItem(i).setText(
                TEXT[f'tableLock{i}'][self.langIndex]
            )

        for i in range(8):
            self.userInfoTable.horizontalHeaderItem(i).setText(
                TEXT[f'userInfoTable{i}'][self.langIndex]
            )        
        
        
        

app = QApplication(sys.argv)
mainWin = MainWin()
mainWin.showFullScreen()
sys.exit(app.exec_())
