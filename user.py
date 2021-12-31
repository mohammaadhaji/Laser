from os.path import join, isfile
from paths import USERS_DIR
import jdatetime, pickle, os

from utility import randID


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

    def __str__(self):
        return '<' + self.name + '> ' + '(' + self.phoneNumber + ')'



def saveUser(usersData):
    filePath = join(USERS_DIR, 'USERS_DATE')
    fileHandler = open(filePath, 'wb')
    usersData = pickle.dump(usersData, fileHandler)
    fileHandler.close()
   

def loadUsers():
    filePath = join(USERS_DIR, 'USERS_DATE')
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        usersData = pickle.load(fileHandler)
        fileHandler.close()
        return usersData
    else:
        usersData = {}
        fileHandler = open(filePath, 'wb')
        pickle.dump(usersData, fileHandler)
        fileHandler.close()
        return usersData



filePath = join(USERS_DIR, 'USERS_DATE')
fileHandler = open(filePath, 'rb')
usersData = pickle.load(fileHandler)
fileHandler.close()
for i in range(1000):
    num = randID(11)
    usersData[num] = User(num, randID(5))

fileHandler = open(filePath, 'wb')
usersData = pickle.dump(usersData, fileHandler)
fileHandler.close()
