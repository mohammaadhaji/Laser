import jdatetime, math, sys, time
start = time.time()
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
        self.langIndex = 0 if self.configs['LANGUAGE'] == 'en' else 1
        self.langIndex = 0
        icon = QPixmap(SELECTED_LANG_ICON)
        self.lblEnSelected.setPixmap(icon.scaled(70, 70))
        self.serialC = SerialTimer() if RPI_VERSION == '3' else SerialThread()
        self.serialC.sensorFlags.connect(self.setSensors)
        self.serialC.tempValue.connect(self.setTemp)
        self.serialC.shot.connect(self.shot)
        self.serialC.serialNumber.connect(self.txtSerialNumber.setText)
        self.serialC.productionDate.connect(self.txtProductionDate.setText)
        self.serialC.laserEnergy.connect(self.txtLaserDiodeEnergy.setText)
        self.serialC.firmwareVesion.connect(self.txtFirmwareVersion.setText)
        self.serialC.updateProgress.connect(self.updateProgress)
        self.serialC.readCooling.connect(lambda: laserPage({'cooling': self.cooling}))
        self.serialC.readEnergy.connect(lambda: laserPage({'energy': self.energy}))
        self.serialC.readPulseWidht.connect(lambda: laserPage({'pulseWidht': self.pulseWidth}))
        self.serialC.readFrequency.connect(lambda: laserPage({'frequency': self.frequency}))
        self.serialC.sysDate.connect(self.receiveDate)
        self.serialC.sysClock.connect(self.adjustTime)
        self.updateT = UpdateFirmware()
        self.readMusicT = ReadMusics()
        self.readMusicT.result.connect(self.readMusicResult)
        self.readMusicT.paths.connect(self.addMusics)
        self.updateT.result.connect(self.updateResult)
        self.license = self.configs['LICENSE']
        self.lockMovie = QMovie(LOCK_GIF)
        self.shutdownMovie = QMovie(SHUTDONW_GIF)
        self.musicMovie = QMovie(MUSIC_GIF)
        self.musicMovie.setCacheMode(QMovie.CacheAll)
        self.lblMusicGif.setMovie(self.musicMovie)
        self.musicMovie.start()
        self.musicMovie.stop()
        self.lblShutdownGif.setMovie(self.shutdownMovie)
        self.lockMovie.frameChanged.connect(self.unlock)
        self.lblLock.setMovie(self.lockMovie)
        self.lockMovie.start()
        self.lockMovie.stop()
        self.shotSound = QMediaPlayer()
        self.musicSound = QMediaPlayer()
        self.touchSound = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.playlist.currentIndexChanged.connect(self.playlistIndexChanged)
        self.touchSound.setMedia(QMediaContent(QUrl.fromLocalFile(TOUCH_SOUND)))
        self.shotSound.setMedia(QMediaContent(QUrl.fromLocalFile(SHOT_SOUND)))
        self.lblSplash.setPixmap(QPixmap(SPLASH).scaled(1920,1080))
        self.lblSplash.clicked.connect(lambda: self.changeAnimation('vertical'))
        self.lblSplash.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.lblSplash.clicked.connect(lambda: self.musicMovie.jumpToFrame(95))
        self.lblSplash.clicked.connect(
            lambda: self.shotSound.setMedia(QMediaContent(QUrl.fromLocalFile(SHOT_SOUND)))
        )
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont(IRAN_NASTALIQ)
        font_id = font_db.addApplicationFont(IRANIAN_SANS)
        self.ownerInfoSplash = QLabel(self.lblSplash)
        self.ownerInfoSplash.setText('')
        ownerInfo = self.configs['OwnerInfo']
        if ownerInfo and isFarsi(ownerInfo):
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_FA)
        else:
            self.ownerInfoSplash.setStyleSheet(OWNER_INFO_STYLE_EN)
        self.ownerInfoSplash.setAlignment(Qt.AlignCenter)
        self.ownerInfoSplash.setAlignment(Qt.AlignHCenter)
        self.ownerInfoSplash.setText(ownerInfo)
        self.ownerInfoSplash.move(0, 880)
        self.ownerInfoSplash.setMinimumHeight(200)
        if not ownerInfo: self.ownerInfoSplash.setVisible(False)
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
        self.findIndex = -1
        self.musicFiles = []
        self.time(edit=True)
        self.tutorials()   
        self.initPages()
        self.initTimers()
        self.initButtons()
        self.initTables()
        self.initSensors()
        self.initTextboxes()
        self.changeTheme(self.configs['theme'])
        self.loadLocksTable()
        self.bodyPartsSignals()
        self.keyboardSignals()
        self.casesSignals()
        self.initMusics()
        self.checkUUID()
        readTime()
        icon = QPixmap(SPARK_ICON)
        self.lblSpark.setPixmap(icon.scaled(120, 120))
        self.lblSpark.setVisible(False)
        self.lblLasing.setVisible(False)
        if self.configs['LANGUAGE'] == 'fa': self.changeLang(self.configs['LANGUAGE'])
        self.shortcut = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
        self.shortcut.activated.connect(self.exit)
        self.chbSlideTransition.setFixedSize(150, 48)
        self.chbSlideTransition.setChecked(self.configs['slideTransition'])
        self.chbSlideTransition.toggled.connect(self.setTransition)
        self.chbTouchSound.setFixedSize(150, 48)
        self.chbTouchSound.setChecked(self.configs['touchSound'])
        self.chbTouchSound.toggled.connect(self.setTouchSound)
        op=QGraphicsOpacityEffect(self)
        op.setOpacity(0.8) 
        self.musicFrame.setGraphicsEffect(op)
        op=QGraphicsOpacityEffect(self)
        op.setOpacity(0.8) 
        self.listWidgetVideos.setGraphicsEffect(op)
        self.shotSound.setMedia(QMediaContent(QUrl.fromLocalFile(STARTUP_SOUND)))
        self.shotSound.play()

    def setTouchSound(self, active):
        self.configs['touchSound'] = active
        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblUiError, 
                self.uiLabelTimer, 4
            )

    def playTouchSound(self, sound):
        self.touchSound.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(sound)
            )
        )
        if self.configs['touchSound']:
            self.touchSound.play()

    def initPages(self):
        self.stackedWidget.setCurrentWidget(self.splashPage)
        self.stackedWidgetLaser.setCurrentIndex(0)
        self.stackedWidgetSex.setCurrentIndex(0)
        self.stackedWidgetSettings.setCurrentIndex(0)
        for sw in self.findChildren(QStackedWidget):
            sw.setTransitionDirection(Qt.Horizontal)
            sw.setTransitionSpeed(500)
            sw.setTransitionEasingCurve(QEasingCurve.OutQuart)
            sw.setSlideTransition(self.configs['slideTransition'])

        self.stackedWidgetSex.setTransitionEasingCurve(QEasingCurve.OutBack)
        self.stackedWidgetSex.setTransitionDirection(Qt.Vertical)
        self.hwStackedWidget.setTransitionDirection(Qt.Vertical)
        
    def setTransition(self, checked):
        self.stackedWidget.setSlideTransition(checked)
        self.stackedWidgetSex.setSlideTransition(checked)
        self.stackedWidgetLaser.setSlideTransition(checked)
        self.stackedWidgetSettings.setSlideTransition(checked)
        self.hwStackedWidget.setSlideTransition(checked)
        self.configs['slideTransition'] = checked
        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblUiError, 
                self.uiLabelTimer, 4
            )

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
        self.uiLabelTimer = QTimer()
        self.sensorsReportLabelTimer = QTimer()
        self.musicRefreshLableTimer = QTimer()
        self.systemTimeTimer = QTimer()
        self.readyErrorTimer =  QTimer()
        self.monitorSensorsTimer = QTimer()
        self.sparkTimer = QTimer()
        self.loadUsersTimer = QTimer()
        self.shutdownTimer = QTimer()
        self.restartTimer = QTimer()
        self.shutdownTimer.timeout.connect(self.powerOff)
        self.restartTimer.timeout.connect(self.restart)
        self.loadUsersTimer.timeout.connect(self.addUsersTable)
        self.loadUsersTimer.start(20)
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
        self.uiLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblUiError, self.uiLabelTimer)
        )
        self.sensorsReportLabelTimer.timeout.connect(
            lambda: self.clearLabel(self.lblSensorDateError, self.sensorsReportLabelTimer)
        )
        self.musicRefreshLableTimer.timeout.connect(
            lambda: self.clearLabel(self.lblMusicRefresh, self.musicRefreshLableTimer)
        )

        self.incDaysTimer.timeout.connect(lambda: self.incDecDay('inc'))
        self.decDaysTimer.timeout.connect(lambda: self.incDecDay('dec'))
        self.backspaceTimer.timeout.connect(self.type(lambda: 'backspace'))
        self.hwWrongPassTimer.timeout.connect(self.hwWrongPass)
        self.sparkTimer.timeout.connect(self.hideSpark)
        self.monitorSensorsTimer.timeout.connect(self.monitorSensors)

    def initTables(self):
        for tbl in self.findChildren(QTableWidget):
            op=QGraphicsOpacityEffect(self)
            op.setOpacity(0.8)
            tbl.verticalHeader().setDefaultSectionSize(75)                
            tbl.horizontalHeader().setFixedHeight(60)                
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)                    
            tbl.verticalHeader().setVisible(False)                    
            tbl.setGraphicsEffect(op)
        
        header = self.userInfoTable.horizontalHeader()
        header.setSectionResizeMode(0,  QHeaderView.ResizeToContents) 
        self.tableMusic.cellClicked.connect(self.musicSelected)

    def initButtons(self):
        self.btnEnLang.clicked.connect(lambda: self.changeLang('en'))
        self.btnFaLang.clicked.connect(lambda: self.changeLang('fa'))
        self.btnEnter.clicked.connect(self.unlockLIC)
        self.btnSort.clicked.connect(self.sort)
        self.btnAdss.clicked.connect(self.adss)
        self.btnEndSession.clicked.connect(lambda: self.setNextSession('lazer'))
        self.btnEndSession.clicked.connect(lambda: enterPage(MAIN_PAGE))
        self.btnPowerOption.clicked.connect(lambda: self.powerOption('show'))
        self.btnPower.clicked.connect(lambda: self.playShutdown('powerOff'))
        self.btnPower_2.clicked.connect(lambda: self.playShutdown('powerOff'))
        self.btnPower_3.clicked.connect(lambda: self.playShutdown('powerOff'))
        self.btnRestart.clicked.connect(lambda: self.playShutdown('restart'))
        self.btnStartSession.clicked.connect(self.startSession)
        self.btnSubmit.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnSubmit.clicked.connect(self.submit)
        self.btnSystemLogs.clicked.connect(self.enterLogsPage)
        self.btnMusic.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnMusic.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.musicPage))
        self.btnBackMusic.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnBackNewSession.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnBackManagement.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        self.btnBackManagement.clicked.connect(lambda: self.txtSearch.clear())
        self.btnBackManagement.clicked.connect(self.saveUsers)
        self.btnBackSettings.clicked.connect(self.backSettings)
        self.btnBackSettings.clicked.connect(self.systemTimeTimer.stop)
        self.btnBackEditUser.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnBackEditUser.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.userManagementPage))
        self.btnSettings.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnSettings.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        self.btnUiSettings.clicked.connect(lambda: self.stackedWidgetSettings.setCurrentWidget(self.uiPage))
        self.btnEnterHw.clicked.connect(self.loginHw)
        self.btnHwSettings.clicked.connect(self.btnHwsettingClicked)
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
        self.btnTutorials.clicked.connect(lambda: self.mediaPlayer.setMedia(QMediaContent()))
        self.btnBackTutorials.clicked.connect(lambda: self.mediaPlayer.setMedia(QMediaContent()))
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
        self.btnDeleteLogs.clicked.connect(self.deleteLogs)
        self.btnPlay.clicked.connect(lambda: self.play('video'))
        self.btnPlayMusic.clicked.connect(lambda: self.play('music'))
        self.btnLoadMusic.clicked.connect(self.readMusic)
        self.btnFindNext.clicked.connect(lambda : self.findWord(self.txtSearchLogs.text()))
        self.btnFindBefor.clicked.connect(lambda : self.findWord(self.txtSearchLogs.text(), True))
        self.btnSaveCase.pressed.connect(lambda: self.chgSliderColor(SLIDER_SAVED_GB, SLIDER_SAVED_GW))
        self.btnSaveCase.released.connect(lambda: self.chgSliderColor(SLIDER_GB, SLIDER_GW))
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
        self.btnResetLock.clicked.connect(self.resetLock)
        self.btnBackLaser.clicked.connect(lambda: self.changeAnimation('horizontal'))
        self.btnBackLaser.clicked.connect(lambda: self.stackedWidgetLaser.setCurrentWidget(self.bodyPartPage))
        self.btnBackLaser.clicked.connect(lambda: self.btnBackLaser.setVisible(False))
        self.btnBackLaser.clicked.connect(lambda: self.setReady(False))
        self.btnBackLaser.clicked.connect(lambda: enterPage(BODY_PART_PAGE))
        self.btnBackLaser.setVisible(False)
        self.btnUpdateFirmware.clicked.connect(self.updateSystem)
        self.btnShowSplash.clicked.connect(self.showSplash)
        self.btnDelSelectedUsers.clicked.connect(self.removeSelectedUsers)
        self.btnSelectAll.clicked.connect(self.selectAll)
        self.selectAllFlag = False
        self.btnLoop.clicked.connect(self.setLoopMusic)
        self.LoopMusicFlag = self.configs['LoopMusic']
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
        allButtons = self.findChildren(QPushButton)

        for btn in allButtons:
            if btn.objectName() == 'btnSelectedBodyPart':
                continue

            elif btn in keyboardButtons:
                btn.pressed.connect(lambda: self.playTouchSound(KEYBOARD_SOUND))
            elif btn.objectName() not in sensors:
                btn.pressed.connect(lambda: self.playTouchSound(TOUCH_SOUND))       

    def initTextboxes(self):
        self.txtNumber.returnPressed.connect(self.startSession)
        self.txtNameSubmit.returnPressed.connect(self.submit)
        self.txtNumberSubmit.returnPressed.connect(self.submit)
        
        for txt in self.findChildren(LineEdit):
            if isinstance(txt, LineEdit):
                txt.fIn.connect(lambda: self.keyboard('show'))
        self.textEditNote.fIn.connect(lambda: self.keyboard('show'))

        self.txtOwnerInfo.setText(self.configs['OwnerInfo'])
        self.txtOwnerInfo.textChanged.connect(self.setOwnerInfo)
        self.txtDays.textChanged.connect(self.setDateText)
        self.txtNsYear.textChanged.connect(self.setDaysText)
        self.txtNsMonth.textChanged.connect(self.setDaysText)
        self.txtNsDay.textChanged.connect(self.setDaysText)
        input_validator = QRegExpValidator(QRegExp("\d*"), self.txtDays)
        self.txtDays.setValidator(input_validator)
        self.txtEditMinute.setValidator(input_validator)
        self.txtEditHour.setValidator(input_validator)
        self.txtLockYear.setValidator(input_validator)        
        self.txtLockMonth.setValidator(input_validator)
        self.txtLockDay.setValidator(input_validator)
        self.txtEditDay.setValidator(input_validator)
        self.txtEditMonth.setValidator(input_validator)
        self.txtEditYear.setValidator(input_validator)        
        self.txtNsYear.setValidator(input_validator)    
        self.txtNsMonth.setValidator(input_validator)
        self.txtNsDay.setValidator(input_validator)     
        self.txtDays.setText('30')
        self.txtSearch.textChanged.connect(self.search)
        self.txtSearchMusic.textChanged.connect(self.searchMusic)

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

    def adss(self):
        self.changeAnimation('vertical')
        self.videoLayout.removeWidget(self.videoWidget)
        self.adssLayout.addWidget(self.videoWidget)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(ADSS_DEMO)))
        self.mediaPlayer.play()
        index = self.stackedWidget.indexOf(self.adssPage)
        self.stackedWidget.setCurrentIndex(index)
    
    def adssDemoEnd(self):
        index = self.stackedWidget.indexOf(self.adssPage)
        if self.stackedWidget.currentIndex() == index:
            if not self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.setMedia(QMediaContent())
                self.stackedWidget.setCurrentWidget(self.mainPage)
                self.adssLayout.removeWidget(self.videoWidget)
                self.videoLayout.addWidget(self.videoWidget)
            
    def setSensors(self, flags):
        self.setLock(flags[0])
        self.setWaterLevelError(flags[1])
        self.setWaterflowError(flags[2])
        self.setOverHeatError(flags[3])
        self.setPhysicalDamage(flags[4])

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

        if theme.startswith('T') or theme == 'C3':
            self.powerFrame.setStyleSheet(POWER_OPTION_L)
        else:
            self.powerFrame.setStyleSheet(POWER_OPTION_D)

        self.configs['theme'] = theme
        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblUiError, 
                self.uiLabelTimer, 4
            )

    def setOwnerInfo(self, text):
        self.ownerInfoSplash.setText(text)
        self.ownerInfoSplash.adjustSize()
        self.configs['OwnerInfo'] = text
        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblUiError, 
                self.uiLabelTimer, 4
            )

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
        except Exception as e:
            log('Startup Setting Time', str(e) + '\n')
            
    def playShutdown(self, i):
        self.shotSound.setMedia(QMediaContent(QUrl.fromLocalFile(SHUTDOWN_SOUND)))
        self.shotSound.play()
        self.keyboard('hide')
        if i == 'powerOff':
            self.shutdownTimer.start(3000)
        else:
            self.restartTimer.start(3000)
            self.lblShuttingdown.setText('Restarting...')
        self.shutdownMovie.start()
        self.changeAnimation('vertical')
        self.stackedWidget.setCurrentWidget(self.shutdownPage)

    def exit(self):
        log('Exit Shortcut', 'Shortcut activated. Exiting from UI...\n')
        self.close()

    def powerOff(self):
        enterPage(SHUTDONW_PAGE)
        self.serialC.closePort()
        gpioCleanup()
        if platform.system() == 'Windows':
            self.close()
        else:
            os.system('poweroff')
        
    def restart(self):
        enterPage(SHUTDONW_PAGE)
        self.serialC.closePort()
        gpioCleanup()
        if platform.system() == 'Windows':
            self.close()
        else:
            os.system('reboot')

    def updateResult(self, result):
        if result == 'Done GUI':
            for i in range(5, -1, -1):
                self.lblUpdateFirmware.setText(
                    f'Your system will restart in {i} seconds...'
                )
                QApplication.processEvents()
                time.sleep(1)
            self.playShutdown('restart')
        else:
            self.setLabel(
                result, 
                self.lblUpdateFirmware,
                self.updateFirmwareLabelTimer
            )
            self.btnUpdateFirmware.setDisabled(False)

    def updateProgress(self, status):
        self.lblUpdateFirmware.setText(status)
        if status == 'successfully updated':
            self.btnUpdateFirmware.setDisabled(False)
            self.setLabel(
                'Successfully updated.', 
                self.lblUpdateFirmware,
                self.updateFirmwareLabelTimer
            )

    def updateSystem(self):
        self.btnUpdateFirmware.setDisabled(True)
        self.lblUpdateFirmware.setText('Please wait...')
        self.updateT.start()

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

        if self.waterflowError:
            if self.ready:
                self.setReady(False)
        
        if self.waterLevelError:
            if self.ready:
                self.setReady(False)
        
        if self.interLockError:
            if self.ready:
                self.setReady(False)

        if self.overHeatError:
            if self.ready:
                self.setReady(False)

        if self.physicalDamage:
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

        for lock in self.configs['LOCK']:
            if (date - toJalali(lock.date)).days <= 0:
                self.setLabel(
                    TEXT['anyLockBefor'][self.langIndex], 
                    self.lblLockError, 
                    self.lockErrorLabel, 5
                )
                return
        
        license = self.license[f'LICENSE{numOfLocks + 1}']
        lock = Lock(date.togregorian(), license)
        self.configs['LOCK'].append(lock)
        if not self.saveConfigs():
            self.setLabel(
                    TEXT['saveConfigError'][self.langIndex], 
                    self.lblLockError, 
                    self.lockErrorLabel, 4
                )
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
            date = TableWidgetItem(str(toJalali(lock.date).date()))
            self.tableLock.setItem(i, 0, date)
            diff = getDiff(toJalali(lock.date))
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
            paid = TableWidgetItem(
                TEXT['yes'][self.langIndex] if lock.paid else TEXT['no'][self.langIndex]
            )
            self.tableLock.setItem(i, 2, paid)
            
    def resetLock(self):
        self.configs['LOCK'] = []
        if not self.saveConfigs():
            self.setLabel(
                    TEXT['saveConfigError'][self.langIndex], 
                    self.lblLockError, 
                    self.lockErrorLabel, 4
                )
        self.time(edit=True)
        self.loadLocksTable()

    def unlockUUID(self):
        user_pass = self.txtPassUUID.text().upper()
        hwid = getID()
        hwid += '@mohammaad_haji'
        
        if hashlib.sha256(hwid.encode()).hexdigest()[:10].upper() == user_pass:
            index = self.stackedWidget.indexOf(self.splashPage)
            self.stackedWidget.setCurrentIndex(index)
            self.configs['PASSWORD'] = user_pass
            self.saveConfigs()
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
        locks = []
        for lock in self.configs['LOCK']:
            date = toJalali(lock.date)
            if not lock.paid and getDiff(date) <= 0:
                locks.append(lock)

        locks.sort(key=lambda x: x.date)

        if len(locks) > 0:
            index = self.stackedWidget.indexOf(self.loginPage)
            self.stackedWidget.setCurrentIndex(index)
            self.txtID.setText(str(locks[0].license))
            self.centralWidget().setStyleSheet(APP_LOCK_BG)
        else:
            self.checkUUID()
        
        for lock in locks:
            if lock.checkPassword(userPass):
                self.saveConfigs()
                self.keyboard('hide')
                self.lockMovie.start()
                self.txtPassword.clear()
                self.shotSound.setMedia(QMediaContent(QUrl.fromLocalFile(WELLCOME_SOUND)))
                self.shotSound.play()
                return

            else:
                if not auto:
                    self.setLabel(
                            'Password is not correct.', 
                            self.lblPassword, 
                            self.passwordLabelTimer, 4
                            )

    def unlock(self, frameNumber):
        if frameNumber == self.lockMovie.frameCount() - 1: 
            self.lockMovie.stop()
            index = self.stackedWidget.indexOf(self.splashPage)
            self.stackedWidget.setCurrentIndex(index)
            self.changeTheme(self.configs['theme']) 

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
        index = self.hwStackedWidget.indexOf(self.systemLogPage)
        if self.hwStackedWidget.currentIndex() == index:
            return
 
        index = self.hwStackedWidget.indexOf(self.lockSettingsPage)
        if self.hwStackedWidget.currentIndex() == index:
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
                lockPage(WRITE)
                self.loadLocksTable()
            except Exception as e:
                print(e)
                log('Setting Time', str(e) + '\n')
                self.setLabel(
                        TEXT['systemTimeStatusError'][self.langIndex], 
                        self.lblSystemTimeStatus, 
                        self.sysTimeStatusLabelTimer, 4
                    )
                return

            self.setLabel(
                    TEXT['systemTimeStatus'][self.langIndex], 
                    self.lblSystemTimeStatus, 
                    self.sysTimeStatusLabelTimer, 4
                )

        
        index = self.hwStackedWidget.indexOf(self.infoPage)
        if self.hwStackedWidget.currentIndex() == index:
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
            self.enterSettingPage(WRITE)

            if not self.saveConfigs():
                self.setLabel(
                    TEXT['saveConfigError'][self.langIndex], 
                    self.lblSaveHw, 
                    self.hwUpdatedLabelTimer, 4
                )
            else:
                self.setLabel(
                        TEXT['saveHw'][self.langIndex], 
                        self.lblSaveHw, 
                        self.hwUpdatedLabelTimer, 2
                    )

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
        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblSaveHw, 
                self.hwUpdatedLabelTimer, 4
            )

    def addMusics(self, paths):
        self.musicFiles = paths
        self.musicSound.setPlaylist(self.playlist)
        for path in paths:
            url = QUrl.fromLocalFile(path)
            self.playlist.addMedia(QMediaContent(url))
            name = os.path.basename(path)
            rowPosition = self.tableMusic.rowCount()
            self.tableMusic.insertRow(rowPosition)
            item = QTableWidgetItem(name)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableMusic.setItem(rowPosition, 0, item)

    def readMusicResult(self, res):
        self.setLabel(
                res, self.lblMusicRefresh, self.musicRefreshLableTimer
        )
        self.musicFiles.clear()
        self.tableMusic.setRowCount(0)
    
    def readMusic(self):
        self.musicFiles.clear()
        self.playlist.clear()
        self.tableMusic.setRowCount(0)
        self.readMusicT.start()

    def initMusics(self):
        self.musicLength = '00:00:00'
        self.lblLengthMusic.setText(self.musicLength)
        self.sliderVolumeMusic.valueChanged.connect(self.setMusicVolume)
        self.musicSound.setVolume(self.configs['MusicVolume'])
        self.sliderVolumeMusic.setValue(self.configs['MusicVolume'])
        self.musicSound.stateChanged.connect(lambda: self.mediaStateChanged('music'))
        self.musicSound.positionChanged.connect(self.positionChangedMusic)
        self.musicSound.durationChanged.connect(self.durationChangedMusic)
        self.positionSliderMusic.sliderMoved.connect(self.setPositionMusic)
        self.positionSliderMusic.setRange(0, 0)
        self.loopIco = QIcon()
        self.singleIco = QIcon()
        self.loopIco.addPixmap(QPixmap(LOOP_MUSIC_ICON))
        self.singleIco.addPixmap(QPixmap(SINGLE_MUSIC_ICON))
        if self.LoopMusicFlag:
            self.btnLoop.setIcon(self.loopIco)
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.btnLoop.setIcon(self.singleIco)
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        self.btnLoop.setIconSize(QSize(80, 80))

    def tutorials(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = VideoWidget()
        self.videoLayout.addWidget(self.videoWidget)
        self.listWidgetVideos.itemClicked.connect(self.videoSelected)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.setVolume(self.configs['VideoVolume'])
        self.sliderVolume.setValue(self.configs['VideoVolume'])
        self.sliderVolume.valueChanged.connect(self.setVideoVolume)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(lambda: self.mediaStateChanged('video'))
        self.mediaPlayer.stateChanged.connect(self.adssDemoEnd)
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

    def setVideoVolume(self, v):
        self.mediaPlayer.setVolume(v)
        self.configs['VideoVolume'] = v
        self.saveConfigs()

    def setLoopMusic(self):
        self.LoopMusicFlag = not self.LoopMusicFlag
        if self.LoopMusicFlag:
            self.btnLoop.setIcon(self.loopIco)
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.btnLoop.setIcon(self.singleIco)
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        
        self.configs['LoopMusic'] = self.LoopMusicFlag
        self.saveConfigs()

    def setMusicVolume(self, v):
        self.musicSound.setVolume(v)
        self.configs['MusicVolume'] = v
        self.saveConfigs()
        
    def videoSelected(self, video):
        stem = video.text()
        self.lblTitle.setText(stem)
        path = join(TUTORIALS_DIR, addExtenstion(stem))
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.play('video')
        
    def musicSelected(self, r, c):
        name = os.path.basename(self.musicFiles[r])
        name = name[:50] + '...' if len(name) > 50 else name
        self.lblMusicName.setText(name)
        self.musicSound.playlist().setCurrentIndex(r)
        self.musicSound.play()

    def playlistIndexChanged(self):
        name = self.playlist.currentMedia().canonicalUrl().fileName()
        name = name[:50] + '...' if len(name) > 50 else name
        self.lblMusicName.setText(name)
        self.tableMusic.clearSelection()
        self.tableMusic.selectRow(self.playlist.currentIndex())
        

    
    def play(self, i):
        if i == 'video':
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
        else:
            if self.musicSound.state() == QMediaPlayer.PlayingState:
                self.musicSound.pause()
                self.musicMovie.stop()
            else:
                self.musicSound.play()
                if self.btnPlayMusic.icon() == self.pauseIco:
                    self.musicMovie.start()

                    
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
    
    def setPositionMusic(self, position):
        self.musicSound.setPosition(position)

    def mediaStateChanged(self, i):
        if i == 'video':
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.btnPlay.setIcon(self.pauseIco)
            else:
                self.btnPlay.setIcon(self.playIco)
        else:
            if self.musicSound.state() == QMediaPlayer.PlayingState:
                self.btnPlayMusic.setIcon(self.pauseIco)
                self.musicMovie.start()
            else:
                self.btnPlayMusic.setIcon(self.playIco)
                self.musicMovie.stop()

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        current = '{:02d}:{:02d}:{:02d} / '.format(*calcPosition(position)) + self.length
        self.lblLength.setText(current)

    def positionChangedMusic(self, position):
        self.positionSliderMusic.setValue(position)
        current = '{:02d}:{:02d}:{:02d} / '.format(*calcPosition(position)) + self.musicLength
        self.lblLengthMusic.setText(current)

    def durationChanged(self, duration):
        self.length = '{:02d}:{:02d}:{:02d}'.format(*calcPosition(duration))
        self.lblLength.setText('00:00:00 / ' + self.length)
        self.positionSlider.setRange(0, duration)

    def durationChangedMusic(self, duration):
        self.musicLength = '{:02d}:{:02d}:{:02d}'.format(*calcPosition(duration))
        self.lblLengthMusic.setText('00:00:00 / ' + self.musicLength)
        self.positionSliderMusic.setRange(0, duration)

    def changeAnimation(self, animation):
        if animation == 'horizontal':
            self.stackedWidget.setTransitionDirection(Qt.Horizontal)

        elif animation == 'vertical':
            self.stackedWidget.setTransitionDirection(Qt.Vertical)

    def isDateValid(self):
        try:
            year = int(self.txtNsYear.text())
            month = int(self.txtNsMonth.text())
            day = int(self.txtNsDay.text())
            nextSessionDate = jdatetime.datetime(year, month, day)
            return True, nextSessionDate
        except Exception:
            return False, None

    def saveNextSession(self):
        try:
            year = self.txtNsYear.text()
            month = self.txtNsMonth.text()
            day = self.txtNsDay.text()
            if '' in [year, month, day]:
                self.setLabel(
                    'Please fill in the fields.', 
                    self.lblErrNextSession, 
                    self.nextSessionLabelTimer, 4
                )
                return

            date = jdatetime.datetime(int(year), int(month), int(day))
            if getDiff(date) <= -1:
                self.setLabel(
                        TEXT['passedDate'][self.langIndex], 
                        self.lblErrNextSession, 
                        self.nextSessionLabelTimer
                    )
                return
            self.userNextSession.setNextSession(date.togregorian())
            if self.userNextSession.currentSession == 'started':
                self.endSession()
            else:
                self.info(self.userNextSession.phoneNumber)

        except Exception as e:
            log('Function: saveNextSession()', str(e) + '\n')
            self.setLabel(
                    str(e).capitalize() + '.', 
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
            self.txtNsYear.setText(year)
            self.txtNsMonth.setText(month)
            self.txtNsDay.setText(day)

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
            self.btnCancelNS.setText(TEXT['btnLaterNS'][self.langIndex])
        elif page == 'edit':
            self.userNextSession = self.userInfo
            self.btnCancelNS.setText(TEXT['btnCancelNS'][self.langIndex])
            
        self.changeAnimation('vertical')
        self.stackedWidget.setCurrentWidget(self.nextSessionPage)

    def setReady(self, ready):
        if ready:
            logErrors, errors = '', ''
            error_duration = 5
            if not 5 <= self.temperature <= 40:
                errors += TEXT['tempError'][self.langIndex] + '\n'
                logErrors += TEXT['tempError'][0] + '\n'
                error_duration += 1
                
            if self.waterflowError:
                errors += TEXT['waterflowError'][self.langIndex] + '\n'
                logErrors += TEXT['waterflowError'][0] + '\n'
                error_duration += 1
                
            if self.waterLevelError:
                errors += TEXT['waterLevelError'][self.langIndex] + '\n'
                logErrors += TEXT['waterLevelError'][0] + '\n'
                error_duration += 1
            
            if self.interLockError:
                errors += TEXT['interLockError'][self.langIndex] + '\n'
                logErrors += TEXT['interLockError'][0] + '\n'
                error_duration += 1

            if self.overHeatError:
                errors += TEXT['overHeatError'][self.langIndex] + '\n'
                logErrors += TEXT['overHeatError'][0] + '\n'
                error_duration += 1

            if self.physicalDamage:
                errors += TEXT['physicalDamage'][self.langIndex] + '\n'
                logErrors += TEXT['physicalDamage'][0] + '\n'
                error_duration += 1
            
            if errors:
                self.setLabel(
                    errors,
                    self.lblReadyError,
                    self.readyErrorTimer, error_duration
                )
                log('Sensors', logErrors)

            
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
                self.chgSliderColor(SLIDER_DISABLED_GB, SLIDER_DISABLED_GW)

        else:
            self.ready = False
            laserPage({'ready-standby': 'StandBy'})
            self.btnStandby.setStyleSheet(READY_SELECTED)
            self.btnReady.setStyleSheet(READY_NOT_SELECTED)
            self.epfSkinGradeLayout.setEnabled(True)
            self.chgSliderColor(SLIDER_GB, SLIDER_GW)                    

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

    def chgSliderColor(self, c1, c2):
        if self.configs['theme'] in ['C1', 'C2', 'C4']:
            self.sliderEnergy.setStyleSheet(c1)
            self.sliderFrequency.setStyleSheet(c1)
            self.sliderPulseWidth.setStyleSheet(c1)
        else:
            self.sliderEnergy.setStyleSheet(c2)                
            self.sliderFrequency.setStyleSheet(c2)                
            self.sliderPulseWidth.setStyleSheet(c2)

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
            item1 = self.usersTable.item(row, 0)
            item2 = self.usersTable.item(row, 1)
            self.usersTable.setRowHidden(
                row, name not in item1.text().lower() and name not in item2.text().lower()
            )

    def searchMusic(self):
        name = self.txtSearchMusic.text().lower()
        for row in range(self.tableMusic.rowCount()):
            item = self.tableMusic.item(row, 0)
            self.tableMusic.setRowHidden(row, name not in item.text().lower())

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
        action.btnInfo.pressed.connect(lambda: self.playTouchSound(TOUCH_SOUND))
        action.info.connect(self.info)
        action.chbDel.pressed.connect(lambda: self.playTouchSound(TOUCH_SOUND))
        action.delete.connect(self.selecetCheckedUsers)
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

    def selectAll(self):
        self.selectAllFlag = not self.selectAllFlag

        for row in range(self.usersTable.rowCount()):
            self.usersTable.cellWidget(row, 3).chbDel.setChecked(self.selectAllFlag)

        if self.selectAllFlag:
            self.btnSelectAll.setText(TEXT['btnDeselectAll'][self.langIndex])
        else:
            self.btnSelectAll.setText(TEXT['btnSelectAll'][self.langIndex])

    def removeSelectedUsers(self):
        for num in self.selectedUsers:
            self.removeUser(num)
            del self.usersData[num]
        
        self.lblSelectedUsersValue.setText('0')
        self.btnSelectAll.setText(TEXT['btnSelectAll'][self.langIndex])
        self.selectAllFlag = False
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

    def deleteUser(self):
        number = self.userInfo.phoneNumber        
        del self.usersData[number]
        for row in range(self.usersTable.rowCount()):
            if self.usersTable.model().index(row, 0).data() == number:
                self.usersTable.cellWidget(row, 3).chbDel.setChecked(False)
        self.removeUser(number)
        self.saveUsers()
        self.changeAnimation('horizontal')
        self.stackedWidget.setCurrentWidget(self.userManagementPage)

    def info(self, num):
        self.stackedWidget.setCurrentWidget(self.editUserPage)
        self.userInfo = self.usersData[num]
        nextSessionDate = toJalali(self.userInfo.nextSession)
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
            date = TableWidgetItem(str(toJalali(sessions[sn]['date']).date()))
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
                nextSession = toJalali(user.nextSession)
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
                nextSession = toJalali(user.nextSession)
                lastSession = toJalali(user.sessions[user.sessionNumber -1]['date'])
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
        self.monitorSensorsTimer.start(1000)

    def endSession(self):
        try:
            self.monitorSensorsTimer.stop()
            self.user.setCurrentSession('finished')
            self.user.addSession()
            self.removeUser(self.user.phoneNumber)
            self.insertToTabel(self.user)
            self.user = None
            self.configs['TotalShotCounter'] += self.currentCounter
            self.currentCounter = 0
            self.lblCounterValue.setText('0')
            self.saveConfigs()
            self.saveUsers()
        except Exception as e:
            log('Function: endSession()', str(e) + '\n')

        finally:
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
            self.nsDateFrame.setLayoutDirection(Qt.LeftToRight)
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
            self.nsDateFrame.setLayoutDirection(Qt.LeftToRight)
            self.currentUserFrame.setLayoutDirection(Qt.LeftToRight)
            icon = QPixmap(SELECTED_LANG_ICON)
            self.lblEnSelected.setPixmap(icon.scaled(70, 70))
            self.lblFaSelected.clear()
            self.configs['LANGUAGE'] = 'en'
            self.langIndex = 0

        if not self.saveConfigs():
            self.setLabel(
                TEXT['saveConfigError'][self.langIndex], 
                self.lblUiError, 
                self.uiLabelTimer, 4
            )
        self.txtLogs.setFont(QFont('Consolas', 18))
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
            self.tableLock.horizontalHeaderItem(i).setText(
                TEXT[f'tableLock{i}'][self.langIndex]
            )

        for i in range(4):
            self.usersTable.horizontalHeaderItem(i).setText(
                TEXT[f'usersTable{i}'][self.langIndex]
            )

        for i in range(8):
            self.userInfoTable.horizontalHeaderItem(i).setText(
                TEXT[f'userInfoTable{i}'][self.langIndex]
            )        
        
    def enterLogsPage(self):
        if isfile(LOGS_PATH):
            EncryptDecrypt(LOGS_PATH, 15)
            f = open(LOGS_PATH, 'r')
            self.txtLogs.setText(f.read())
            f.close()
            EncryptDecrypt(LOGS_PATH, 15)

        self.hwStackedWidget.setCurrentWidget(self.systemLogPage)
        enterPage(OTHER_PAGE)

    def deleteLogs(self):
        if isfile(LOGS_PATH):
            os.remove(LOGS_PATH)
        
        self.txtLogs.setText('')

    def saveUsers(self):
        try:
            fileHandler = open(USERS_DATA, 'wb')
            pickle.dump(self.usersData, fileHandler)
            fileHandler.close()
        except Exception as e:
            print(e)
            log('Saving Users Info', str(e) + '\n')
        
    def saveConfigs(self):
        try:
            with open(CONFIG_FILE, 'wb') as f:
                pickle.dump(self.configs, f)

            EncryptDecrypt(CONFIG_FILE, 15)
            return True
        
        except Exception as e:
            print(e)
            log('Saving Configs', str(e) + '\n')
            return False

    def findWord(self, findText, reverse=False):
        findText = findText.lower()
        if findText == '':
            return
        
        text = self.txtLogs.toPlainText().lower()
        
        if reverse:
            self.findIndex = text.lower().rfind(findText, 0, self.findIndex)
        else:
            self.findIndex = text.find(findText, self.findIndex + 1)
        
        if self.findIndex == -1:
            return
        
        textCursor = self.txtLogs.textCursor()
        textCursor.setPosition(self.findIndex)
        textCursor.setPosition(self.findIndex + len(findText), QTextCursor.KeepAnchor)
        self.txtLogs.setTextCursor(textCursor)

class LoadingWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setStyleSheet('border-image: url(ui/images/splashLoading.jpg);')
        self.showFullScreen()
        self.timer = QTimer()
        self.timer.timeout.connect(self.showMain)
        self.timer.start(500)
        print(time.time() - start)
    
    def showMain(self):
        self.timer.stop()
        self.main = MainWin()
        self.main.showFullScreen()
        self.close()

app = QApplication(sys.argv)
loadingWin = LoadingWindow()
sys.exit(app.exec_())