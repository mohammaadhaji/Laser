from os.path import join, isfile
from paths import USERS_DIR
import jdatetime
import pickle
import os


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
        self.shot = {
            'face': 0, 'armpit': 0,
            'arm': 0, 'body': 0,
            'bikini': 0, 'leg': 0
        }
        self.currentSession = 'finished'
    
    
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


def loadUser(number):
    filePath = join(USERS_DIR, number)
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        user = pickle.load(fileHandler)
        fileHandler.close()
        return user


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


def loadAllUsers():
    numbers = os.listdir(USERS_DIR)
    numbers.remove('.gitignore')
    users = []
    for number in numbers:
        user = loadUser(number)
        users.append(user)

    return users