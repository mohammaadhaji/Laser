from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from promotions import Action, TableWidgetItem
from itertools import chain
from case import *
from paths import *
from user import *
from styles import *
import sys


def layout_widgets(layout):
    return (layout.itemAt(i).widget() for i in range(layout.count())) 

def get_layout_btn(layout):
    return (layout.itemAt(i).widget() for i in range(layout.count()) if isinstance(layout.itemAt(i).widget(), QPushButton)) 

class MainWin(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWin, self).__init__(*args, **kwargs)
        uic.loadUi(APP_UI, self)
        self.setupUi()
        self.setupSensors()

    def setupUi(self):
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidgetLaser.setCurrentIndex(0)
        self.loginLabelTimer = QTimer()
        self.submitLabelTimer = QTimer()
        self.editLabelTimer = QTimer()
        self.incEPFTimer = QTimer()
        self.decEPFTimer = QTimer()
        self.incEPFTimer.timeout.connect(lambda: self.setEPF('inc'))
        self.decEPFTimer.timeout.connect(lambda: self.setEPF('dec'))
        self.user = None
        self.sortBySession = False
        self.shift = False
        self.farsi = False
        self.ready = False
        self.sex = 'female'
        self.bodyPart = ''
        self.case = 'I'
        self.EPF = 'E'
        self.cooling = 0
        self.loginLabelTimer.timeout.connect(lambda: self.clearLabel('login'))
        self.submitLabelTimer.timeout.connect(lambda: self.clearLabel('submit'))
        self.editLabelTimer.timeout.connect(lambda: self.clearLabel('edit'))
        self.btnSort.clicked.connect(self.sort)
        self.txtNumber.returnPressed.connect(self.login)
        self.btnEndSession.clicked.connect(self.endSession)
        self.btnPower.clicked.connect(self.close)
        self.btnLogin.clicked.connect(self.login)
        self.btnSubmit.clicked.connect(self.submit)
        self.btnBackNewSession.clicked.connect(self.stackedWidget.login)
        self.btnBackManagement.clicked.connect(self.stackedWidget.login)
        self.btnBackManagement.clicked.connect(lambda: self.txtSearch.clear())
        self.btnBackLaser.clicked.connect(self.backLaser)
        self.btnBackEditUser.clicked.connect(self.stackedWidget.userManagement)
        self.btnUserManagement.clicked.connect(self.loadToTabel)
        self.btnSaveInfo.clicked.connect(self.saveUserInfo)
        self.btnDeleteUser.clicked.connect(self.deleteUser)
        self.btnUserManagement.clicked.connect(self.stackedWidget.userManagement)
        self.usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usersTable.verticalHeader().setDefaultSectionSize(70)
        self.usersTable.verticalHeader().setVisible(False)
        self.userInfoTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.userInfoTable.horizontalHeader()
        header.setSectionResizeMode(0,  QHeaderView.ResizeToContents)
        self.userInfoTable.verticalHeader().setDefaultSectionSize(70)
        self.userInfoTable.verticalHeader().setVisible(False)
        self.txtNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtNumberSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtNameSubmit.fIn.connect(lambda: self.keyboard('show'))
        self.txtInfoNumber.fIn.connect(lambda: self.keyboard('show'))
        self.txtInfoName.fIn.connect(lambda: self.keyboard('show'))
        self.textEditNote.fIn.connect(lambda: self.keyboard('show'))
        self.txtSearch.fIn.connect(lambda: self.keyboard('show'))
        self.txtSearch.textChanged.connect(self.search)
        self.btnMale.clicked.connect(lambda: self.setSex('male'))
        self.btnFemale.clicked.connect(lambda: self.setSex('female'))
        self.btnEnergy.clicked.connect(lambda: self.selectEPF('E'))
        self.btnIncEPF.pressed.connect(lambda: self.incEPFTimer.start(100))
        self.btnIncEPF.released.connect(lambda: self.incEPFTimer.stop())
        self.btnDecEPF.pressed.connect(lambda: self.decEPFTimer.start(100))
        self.btnDecEPF.released.connect(lambda: self.decEPFTimer.stop())
        self.btnPulseWidth.clicked.connect(lambda: self.selectEPF('P'))
        self.btnFrequency.clicked.connect(lambda: self.selectEPF('F'))
        self.btnMale.clicked.connect(self.stackedWidgetSex.male)
        self.btnFemale.clicked.connect(self.stackedWidgetSex.female)
        self.btnIncEPF.clicked.connect(lambda: self.setEPF('inc'))
        self.btnDecEPF.clicked.connect(lambda: self.setEPF('dec'))
        self.btnDecCooling.clicked.connect(lambda: self.setCooling('dec'))
        self.btnIncCooling.clicked.connect(lambda: self.setCooling('inc'))
        self.btnSaveCase.clicked.connect(self.saveCase)
        self.btnReady.clicked.connect(lambda: self.setReady(True))
        self.btnStandby.clicked.connect(lambda: self.setReady(False))
        self.bodyPartsSignals()
        self.keyboardSignals()
        self.casesSignals()

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

    def setReady(self, ready):
        if ready:
            self.ready = True
            self.btnReady.setStyleSheet(READY_STANDBY_SELECTED)
            self.btnStandby.setStyleSheet(READY_STANDBY_NOT_SELECTED)
        
        else:
            self.ready = False
            self.btnReady.setStyleSheet(READY_STANDBY_NOT_SELECTED)
            self.btnStandby.setStyleSheet(READY_STANDBY_SELECTED)

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
            btn.clicked.connect(self.stackedWidgetLaser.laser)
            sex = btn.objectName().split('btn')[1][0].lower()
            bodyPart = btn.objectName().split('btn')[1][1:].lower()
            btn.clicked.connect(self.setBodyPart(sex, bodyPart))
            btn.clicked.connect(self.fillEPF)

    def fillEPF(self):
        self.loadCase(self.case)
        
    def setBodyPart(self, sex, bodyPart):
        def wrapper():
            self.bodyPart = bodyPart
            icon = QIcon()
            key = sex + ' ' + bodyPart
            self.lblSelectedBodyPart.setText(bodyPart.capitalize())
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

    def loadCase(self, name):
        case = openCase(name)
        enrgy, pl, freq = case.getValue(self.sex, self.bodyPart)
        self.txtEnergy.setText(str(enrgy) + ' J/cm²')
        self.txtPulseWidth.setText(str(pl) + ' Ms')
        self.txtFrequency.setText(str(freq) + ' Hz')

    def backLaser(self):
        if self.stackedWidgetLaser.currentIndex() == 0:
            self.stackedWidget.login()
        else:
            self.stackedWidgetLaser.bodyPart()      

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
        self.lblTotalUsers.setText('Total Users: ' + str(len(users)))
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
        self.stackedWidget.editUser()
        self.userInfo = loadUser(num)
        self.txtInfoNumber.setText(self.userInfo.phoneNumber)
        self.txtInfoName.setText(self.userInfo.name)
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

        lastRowTitle = TableWidgetItem('Total')
        font = QFont('Arial', 14)
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

    def saveUserInfo(self):
        numberEdit = self.txtInfoNumber.text()
        nameEdit = self.txtInfoName.text()
        noteEdit = self.textEditNote.toPlainText()

        if not userExists(self.userInfo.phoneNumber):
            self.setLabel('User has been deleted!', 'edit')
            return

        if numberEdit != self.userInfo.phoneNumber:
            if userExists(numberEdit):
                self.setLabel(
                    'A user with this phone number already exists!', 'edit'
                )
                return

            oldNumber = self.userInfo.phoneNumber
            self.userInfo.setPhoneNumber(numberEdit)
            newNumber = self.userInfo.phoneNumber
            renameUserFile(oldNumber, newNumber)

        if not nameEdit:
            nameEdit = 'Nobody'

        self.userInfo.setName(nameEdit)
        self.userInfo.setNote(noteEdit)
        self.userInfo.save()
        self.setLabel("User's info Updated.", 'edit')
        self.loadToTabel()

    def deleteUser(self):
        number = self.userInfo.phoneNumber

        if not userExists(number):
            self.setLabel('User has been deleted!', 'edit')
            return
            
        deleteUser(number)
        self.txtInfoNumber.clear()
        self.txtInfoName.clear()
        self.textEditNote.clear()
        self.userInfoTable.setRowCount(0)
        self.setLabel("User deleted successfully.", 'edit')
        self.loadToTabel()

    def submit(self):
        number = self.txtNumberSubmit.text()
        name = self.txtNameSubmit.text()

        if not number:
            self.setLabel('Please fill in the number.', 'submit')
            return

        if userExists(number):
            self.setLabel('User already exists!', 'submit')
            return

        user = User(number, name)
        user.save()
        self.txtNumber.setText(number)
        self.txtNumberSubmit.clear()
        self.txtNameSubmit.clear()
        self.stackedWidget.login()

    def login(self):

        numberEntered = self.txtNumber.text()

        if (not self.user) or (self.user.currentSession == 'finished'):

            if not numberEntered:
                self.setLabel('Please fill in the number.', 'login')
                return

            self.user = loadUser(numberEntered)

            if not self.user:
                self.txtNumberSubmit.setText(numberEntered)
                self.txtNameSubmit.setFocus()
                self.stackedWidget.newSession()
                return

            self.lblInfo.setText(
                'Name: ' + self.user.name + '\n\n' +
                'Session Number: ' + str(self.user.sessionNumber)
            )
            self.user.setCurrentSession('started')
            self.keyboard('hide')
            self.stackedWidget.mainLaser()

        elif self.user and self.user.currentSession == 'started':
            if not userExists(self.user.phoneNumber):
                    self.setLabel('User has been deleted!', 'login')
                    self.user = None
                    return
            elif numberEntered != self.user.phoneNumber:
                self.setLabel(
                    "The previous session is not over yet. " +
                    f"<{self.user.name}> ({self.user.phoneNumber})", 'login', 8
                )
                return
            else:
                if not userExists(self.user.phoneNumber):
                    self.setLabel('User has been deleted!', 'login')
                    self.user = None
                    return
                    
                self.lblInfo.setText(
                    'Name: ' + self.user.name + '\n\n' +
                    'Session Number: ' + str(self.user.sessionNumber)
                )
                self.user.setCurrentSession('started')
                self.keyboard('hide')
                self.stackedWidget.mainLaser()

    def endSession(self):
        self.user.setCurrentSession('finished')
        self.user.addSession()
        self.user.save()
        self.user = None
        self.stackedWidget.login()
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
        
    def clearLabel(self, label):
        if label == 'login':
            self.lblLogin.clear()
            self.loginLabelTimer.stop()
        
        elif label == 'submit':
            self.lblSubmit.clear()
            self.submitLabelTimer.stop()

        elif label == 'edit':
            self.lblEditUser.clear()
                  

def main():
    app = QApplication(sys.argv)
    mainWin = MainWin()
    mainWin.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

