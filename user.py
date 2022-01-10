from os.path import join, isfile
from paths import USERS_DIR
import jdatetime, pickle


class User:
    def __init__(self, number, name):
        self.phoneNumber = number
        self.name = name
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
    try:
        filePath = join(USERS_DIR, 'USERS_DATA')
        fileHandler = open(filePath, 'wb')
        pickle.dump(usersData, fileHandler)
        fileHandler.close()
    except Exception as e:
        print(e)

def loadUsers():
    try:
        filePath = join(USERS_DIR, 'USERS_DATA')
        if isfile(filePath):
            fileHandler = open(filePath, 'rb')
            usersData = pickle.load(fileHandler)
            fileHandler.close()
        else:
            usersData = {}
            fileHandler = open(filePath, 'wb')
            pickle.dump(usersData, fileHandler)
            fileHandler.close()

        return usersData
    except Exception as e:
        print(e)


