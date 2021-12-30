from PyQt5.QtCore import QThread, pyqtSignal
from os.path import join, isfile
from paths import USERS_DIR
import jdatetime, pickle, os

from utility import randBinNumber, randID


class User:
    def __init__(self, number, name=''):
        self.phoneNumber = number
        if name:
            self.name = name
        else:
            self.name = 'User ' + str(len(os.listdir(USERS_DIR)))

        self.sessionNumber = 1
        self.sessions = {} 
        self.note = ''
        bodyParts = ['face', 'arm', 'armpit', 'body', 'bikini', 'leg']
        self.shot = dict.fromkeys(bodyParts, 0)
        self.currentSession = 'finished'
        self.nextSession = None
    
    
    def setCurrentSession(self, status):
        self.currentSession = status

    def incShot(self, part):
        self.shot[part] = self.shot[part] + 1

    def setPhoneNumber(self, number):
        self.phoneNumber = number

    def setName(self, name):
        self.name = name

    def setNote(self, note):
        self.note = note

    def setNextSession(self, date):
        self.nextSession = date

    def addSession(self):
        session = self.shot.copy()
        session['date'] = jdatetime.datetime.now()  
        self.sessions[self.sessionNumber] = session
        self.shot = dict.fromkeys(self.shot, 0)
        self.sessionNumber += 1

    def save(self):
        filePath = join(USERS_DIR, self.phoneNumber)
        fileHandler = open(filePath, 'wb')
        pickle.dump(self, fileHandler)
        fileHandler.close()

    def __str__(self):
        return '<' + self.name + '> ' + '(' + self.phoneNumber + ')'

def loadUser(number):
    filePath = join(USERS_DIR, number)
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        user = pickle.load(fileHandler)
        fileHandler.close()
        return user
    else:
        return None


def loadAllUsers2():
    numbers = os.listdir(USERS_DIR)
    if isfile(join(USERS_DIR, '.gitignore')):
        numbers.remove('.gitignore')
    users = []
    for number in numbers:
        user = loadUser(number)
        users.append(user)

    return users


def userExists(number):
    filePath = join(USERS_DIR, number)
    if isfile(filePath):
        return True
    else:
        return False

def renameUserFile(oldNumber, newNumber):
    filePath = join(USERS_DIR, oldNumber)
    newName = join(USERS_DIR, newNumber)
    os.rename(filePath, newName)

def deleteUser(number):
    filePath = join(USERS_DIR, number)
    os.remove(filePath)


def countUsers():
    numbers = os.listdir(USERS_DIR)
    if isfile(join(USERS_DIR, '.gitignore')):
        numbers.remove('.gitignore')
    
    return len(numbers)


class LoadAllUsers(QThread):
    user = pyqtSignal(dict)
    count = pyqtSignal(int)
    finish = pyqtSignal()

    def run(self):
        numbers = os.listdir(USERS_DIR)
        if isfile(join(USERS_DIR, '.gitignore')):
            numbers.remove('.gitignore')
        
        self.count.emit(len(numbers))
        for number in numbers:
            userInfo = loadUser(number)
            x = {
                'name':  userInfo.name,
                'phoneNumber': userInfo.phoneNumber,
                'sessionNumber': str(userInfo.sessionNumber - 1)
            }

            self.user.emit(x)
        
        self.finish.emit()
        
# for i in range(1000):
#     number = randID(11)
#     name = randID(5)
#     user = User(number, name)
#     user.save()